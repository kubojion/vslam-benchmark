#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path


RESULTS_SCRIPTS = Path(__file__).resolve().parents[1]
RUN_SCRIPTS = RESULTS_SCRIPTS.parent / "run"
sys.path.insert(0, str(RESULTS_SCRIPTS))
from validate_run import validate_measurements, validate_provenance  # noqa: E402
from provenance_requirements import REQUIREMENTS  # noqa: E402


def load_enricher():
    spec = importlib.util.spec_from_file_location("enricher", RUN_SCRIPTS / "_enrich_run_meta.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def load_script(name: str):
    spec = importlib.util.spec_from_file_location(name, RESULTS_SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def load_run_script(name: str):
    spec = importlib.util.spec_from_file_location(name, RUN_SCRIPTS / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    spec.loader.exec_module(module)
    return module


def sha() -> str:
    return "a" * 64


def commit() -> str:
    return "b" * 40


def valid_basalt_meta() -> dict:
    return {
        "algo": "basalt",
        "run_type": "vio",
        "process": {"exit_code": 0, "accepted_nonzero_exit": False, "failure_reason": None},
        "provenance_schema": 2,
        "provenance": {
            "artifacts": [
                {"role": "camera_calibration", "path": "configs/calib.json", "size_bytes": 2, "sha256": sha()},
                {"role": "estimator_config", "path": "configs/estimator.json", "size_bytes": 2, "sha256": sha()},
            ],
            "binaries": [{"role": "estimator", "path": "basalt_vio", "size_bytes": 6, "sha256": sha()}],
            "sources": [],
            "parameters": {"use_imu": True, "num_threads": 0, "playback_rate": "offline"},
            "workspace": {"commit": commit(), "dirty": False, "diff_sha256": None},
        },
    }


class ProvenanceValidationTests(unittest.TestCase):
    def write_meta(self, directory: Path, data: dict) -> None:
        directory.mkdir(parents=True)
        (directory / "run_meta.json").write_text(json.dumps(data))

    def test_valid_contract(self):
        with tempfile.TemporaryDirectory() as raw:
            run = Path(raw) / "run1"
            self.write_meta(run, valid_basalt_meta())
            self.assertEqual(validate_provenance(run, required_schema=2), [])

    def test_legacy_metadata_remains_valid(self):
        with tempfile.TemporaryDirectory() as raw:
            run = Path(raw) / "run1"
            self.write_meta(run, {"algo": "basalt"})
            self.assertEqual(validate_provenance(run, required_schema=None), [])
            self.assertTrue(validate_provenance(run, required_schema=2))

    def test_missing_role_and_nonzero_exit_are_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            run = Path(raw) / "run1"
            meta = valid_basalt_meta()
            meta["provenance"]["artifacts"].pop()
            meta["process"]["exit_code"] = 9
            self.write_meta(run, meta)
            errors = validate_provenance(run, required_schema=2)
            self.assertTrue(any("estimator_config" in error for error in errors))
            self.assertTrue(any("exit code 9" in error for error in errors))

    def test_documented_accepted_nonzero_exit(self):
        with tempfile.TemporaryDirectory() as raw:
            run = Path(raw) / "run1"
            meta = valid_basalt_meta()
            meta["process"] = {
                "exit_code": 139,
                "accepted_nonzero_exit": True,
                "failure_reason": "known post-save shutdown fault",
            }
            self.write_meta(run, meta)
            self.assertEqual(validate_provenance(run, required_schema=2), [])

    def test_private_path_is_rejected(self):
        with tempfile.TemporaryDirectory() as raw:
            run = Path(raw) / "run1"
            meta = valid_basalt_meta()
            meta["sandbox"] = "/home/private-user/work"
            self.write_meta(run, meta)
            errors = validate_provenance(run, required_schema=2)
            self.assertTrue(any("private absolute path" in error for error in errors))

    def test_every_contract_is_wired_into_its_runner(self):
        for algorithm, requirement in REQUIREMENTS.items():
            runner = RUN_SCRIPTS / f"run_{algorithm}.sh"
            self.assertTrue(runner.is_file(), algorithm)
            text = runner.read_text()
            for role in requirement.artifacts:
                self.assertIn(f"{role}=", text, f"{algorithm}: artifact {role}")
            for role in requirement.sources:
                self.assertIn(f"{role}=", text, f"{algorithm}: source {role}")
            for role in requirement.binaries:
                self.assertIn(f"{role}=", text, f"{algorithm}: binary {role}")
            for key in requirement.parameters:
                needle = "--seed" if key == "seed" else f"{key}="
                self.assertIn(needle, text, f"{algorithm}: parameter {key}")
            if requirement.environment:
                self.assertIn("--conda-env", text, algorithm)
            if requirement.container:
                self.assertRegex(text, r"--container(?:-image)?\b", algorithm)
            self.assertIn("--measurement-mode", text, algorithm)
            self.assertRegex(text, r"(?s)_resource_monitor\.py.*--(?:pid|container)", algorithm)
            self.assertIn("mark_resource_start", text, algorithm)
            self.assertIn("finish_resource_window", text, algorithm)
            self.assertLess(text.index("_resource_monitor.py"), text.index("mark_resource_start"), algorithm)
            self.assertLess(text.index("mark_resource_start"), text.index("finish_resource_window"), algorithm)
            self.assertLess(text.index("finish_resource_window"), text.rindex("enrich_run_meta"), algorithm)
            if "--measurement-mode transport" in text:
                self.assertIn("--transport-stats", text, algorithm)


class MeasurementValidationTests(unittest.TestCase):
    def write_run(self, root: Path, measurements: dict) -> Path:
        run = root / "run1"
        run.mkdir()
        trajectory = "".join(
            f"{i}.0 {i}.0 0 0 0 0 0 1\n" for i in range(3)
        )
        (run / "trajectory.txt").write_text(trajectory)
        (run / "run_meta.json").write_text(json.dumps({
            "measurement_schema": 1,
            "measurements": measurements,
        }))
        (run / "resources.csv").write_text(
            "t_s,scope,label,target_available,process_count,cpu_pct,cpu_time_s,ram_mib,vram_mib,gpu_util_pct\n"
            "0.0,process_tree,test,true,1,,0.1,10,,\n"
            "0.1,process_tree,test,true,1,50,0.2,11,,\n"
        )
        return run

    def test_valid_max_throughput_measurements(self):
        values = {
            "mode": "max_throughput", "input_frames": 3, "processed_frames": 3,
            "published_frames": None, "dropped_frames": None,
            "publisher_dropped_frames": None, "output_poses": 3,
            "input_duration_s": 2.0, "trajectory_duration_s": 2.0,
            "processing_time_s": 1.0, "end_to_end_time_s": 1.0,
            "processing_fps": 3.0, "end_to_end_fps": 3.0,
            "trajectory_pose_rate": 1.5, "realtime_factor": 2.0,
            "processing_time_scope": "estimator_command_including_initialization_and_finalization",
            "resource_scope": "process_tree", "transport": None,
        }
        with tempfile.TemporaryDirectory() as raw:
            run = self.write_run(Path(raw), values)
            self.assertEqual(validate_measurements(run, required_schema=1), [])

    def test_transport_does_not_invent_downstream_drops(self):
        values = {
            "mode": "transport", "input_frames": 3, "processed_frames": None,
            "published_frames": 3, "dropped_frames": None,
            "publisher_dropped_frames": 0, "output_poses": 3,
            "input_duration_s": 2.0, "trajectory_duration_s": 2.0,
            "processing_time_s": None, "end_to_end_time_s": 3.0,
            "processing_fps": None, "end_to_end_fps": 1.0,
            "trajectory_pose_rate": 1.5, "realtime_factor": 2 / 3,
            "processing_time_scope": "unavailable", "resource_scope": "process_tree",
            "transport": {"camera_frames_expected": 3, "camera_frames_published": 3},
        }
        with tempfile.TemporaryDirectory() as raw:
            run = self.write_run(Path(raw), values)
            self.assertEqual(validate_measurements(run, required_schema=1), [])
            values["dropped_frames"] = 0
            (run / "run_meta.json").write_text(json.dumps({
                "measurement_schema": 1, "measurements": values,
            }))
            self.assertTrue(any(
                "invents estimator" in error
                for error in validate_measurements(run, required_schema=1)
            ))

    def test_paced_run_has_no_processing_fps_and_rejects_system_scope(self):
        values = {
            "mode": "paced", "input_frames": 3, "processed_frames": 3,
            "published_frames": None, "dropped_frames": None,
            "publisher_dropped_frames": None, "output_poses": 3,
            "input_duration_s": 2.0, "trajectory_duration_s": 2.0,
            "processing_time_s": None, "end_to_end_time_s": 2.2,
            "processing_fps": None, "end_to_end_fps": 3 / 2.2,
            "trajectory_pose_rate": 1.5, "realtime_factor": 2 / 2.2,
            "processing_time_scope": "unavailable", "resource_scope": "process_tree",
            "transport": None,
        }
        with tempfile.TemporaryDirectory() as raw:
            run = self.write_run(Path(raw), values)
            self.assertEqual(validate_measurements(run, required_schema=1), [])
            values["resource_scope"] = "system"
            (run / "run_meta.json").write_text(json.dumps({
                "measurement_schema": 1, "measurements": values,
            }))
            self.assertTrue(any(
                "explicit scoped target" in error
                for error in validate_measurements(run, required_schema=1)
            ))


class EnricherTests(unittest.TestCase):
    def setUp(self):
        self.module = load_enricher()

    def test_execution_stage_preserves_forced_shutdown_evidence(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            stages = root / "processes"
            stages.mkdir()
            (stages / "node.json").write_text(json.dumps({
                "status": "exited", "exit_code": -9, "token": "private-token",
            }))
            (stages / "node.stops.jsonl").write_text(json.dumps({
                "signals": [{"signal": 9, "pids": [123]}], "remaining": [],
            }) + "\n")
            result = self.module.execution_stages(root)
            self.assertEqual(result[0]["exit_code"], -9)
            self.assertTrue(result[0]["forced_kill_recorded"])
            self.assertEqual(len(result[0]["stop_log_sha256"]), 64)
            self.assertNotIn("token", result[0])

    def test_artifact_hash_and_normalized_snapshot(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.module.RESULTS = root / "cache-root"
            run = root / "run1"
            source = root / "config.yaml"
            source.write_text(f"repo: {self.module.REPO}\nhome: {Path.home()}\n")
            entry = self.module.artifact_entry("estimator_config", str(source), run, snapshot=True)
            self.assertEqual(len(entry["sha256"]), 64)
            self.assertEqual(entry["path"], "config.yaml")
            snapshot = (run / entry["snapshot"]).read_text()
            self.assertEqual(len(entry["snapshot_sha256"]), 64)
            self.assertIn("<repo>", snapshot)
            self.assertIn("<home>", snapshot)
            self.assertNotIn(str(Path.home()), snapshot)

    def test_git_source_identity_and_dirty_diff(self):
        with tempfile.TemporaryDirectory() as raw:
            repo = Path(raw) / "source"
            repo.mkdir()
            subprocess.run(["git", "init", "-q", str(repo)], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.email", "test@example.invalid"], check=True)
            subprocess.run(["git", "-C", str(repo), "config", "user.name", "Test"], check=True)
            tracked = repo / "tracked.txt"
            tracked.write_text("one\n")
            subprocess.run(["git", "-C", str(repo), "add", "tracked.txt"], check=True)
            subprocess.run(["git", "-C", str(repo), "commit", "-qm", "initial"], check=True)
            clean = self.module.source_entry("algorithm", str(repo))
            self.assertFalse(clean["dirty"])
            self.assertIsNone(clean["diff_sha256"])
            tracked.write_text("two\n")
            dirty = self.module.source_entry("algorithm", str(repo))
            self.assertTrue(dirty["dirty"])
            self.assertEqual(len(dirty["diff_sha256"]), 64)

    def test_end_to_end_enrichment(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            self.module.RESULTS = root / "cache-root"
            run = root / "run1"
            run.mkdir()
            meta_path = run / "run_meta.json"
            meta_path.write_text(json.dumps({
                "algo": "basalt", "dataset": "test", "seq": "seq",
                "run_id": 1, "run_type": "vio", "duration_s": 1.0,
            }))
            (run / "trajectory.txt").write_text(
                "0 0 0 0 0 0 0 1\n1 1 0 0 0 0 0 1\n2 2 0 0 0 0 0 1\n"
            )
            (run / "resources.csv").write_text(
                "t_s,scope,label,target_available,process_count,cpu_pct,cpu_time_s,ram_mib,vram_mib,gpu_util_pct\n"
                "0,process_tree,test,true,1,,0.1,10,,\n"
            )
            self.module.sequence_measurements = lambda *_: (3, 2.0)
            calibration = root / "calib.json"
            config = root / "estimator.json"
            binary = root / "basalt_vio"
            calibration.write_text("{}\n")
            config.write_text("{}\n")
            binary.write_bytes(b"binary")
            old_argv = sys.argv
            try:
                sys.argv = [
                    "_enrich_run_meta.py", str(meta_path),
                    "--artifact", f"camera_calibration={calibration}",
                    "--artifact", f"estimator_config={config}",
                    "--binary", f"estimator={binary}",
                    "--param", "use_imu=true", "--param", "num_threads=0",
                    "--param", "playback_rate=offline",
                    "--measurement-mode", "max_throughput",
                ]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", ResourceWarning)
                    self.assertEqual(self.module.main(), 0)
            finally:
                sys.argv = old_argv
            self.assertEqual(validate_provenance(run, required_schema=2), [])
            self.assertEqual(validate_measurements(run, required_schema=1), [])
            enriched = json.loads(meta_path.read_text())
            self.assertRegex(enriched["machine_id"], r"^machine-[0-9a-f]{12}$")
            self.assertNotIn(str(Path.home()), meta_path.read_text())


class SeededPythonTests(unittest.TestCase):
    def test_script_directory_shadows_environment_packages(self):
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            package = root / "shadowpkg"
            package.mkdir()
            (package / "__init__.py").write_text("VALUE = 'source-tree'\n")
            script = root / "demo.py"
            script.write_text("import shadowpkg; print(shadowpkg.VALUE)\n")
            result = subprocess.run(
                [sys.executable, str(RUN_SCRIPTS / "_seeded_python.py"), "7", str(script)],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), "source-tree")


class MeasurementHelperTests(unittest.TestCase):
    def test_proc_accounting_needs_no_optional_python_package(self):
        module = load_run_script("_resource_monitor")
        pids = module.process_tree_pids([os.getpid()])
        self.assertIn(os.getpid(), pids)
        cpu, rss, count = module.process_stats(pids, set())
        self.assertGreaterEqual(cpu, 0)
        self.assertGreater(rss, 0)
        self.assertGreaterEqual(count, 1)

    def test_transport_stats_are_atomic_and_typed(self):
        module = load_run_script("_transport_stats")
        with tempfile.TemporaryDirectory() as raw:
            path = Path(raw) / "transport.json"
            module.write_transport_stats(
                path, camera_frames_expected=10, camera_frames_published=9,
                imu_messages_published=20,
            )
            value = json.loads(path.read_text())
            self.assertEqual(value["schema"], 1)
            self.assertEqual(value["camera_frames_published"], 9)
            self.assertFalse(path.with_suffix(".json.tmp").exists())


class ManifestAndSiteTests(unittest.TestCase):
    def test_browser_refuses_changed_current_evaluation(self):
        import hashlib
        module=load_script('build_site')
        with tempfile.TemporaryDirectory() as raw:
            module.REPO=Path(raw);module.RESULTS=Path(raw)/'results'
            source=module.RESULTS/'stage/run_eval.json';source.parent.mkdir(parents=True)
            source.write_text('{"eval_schema": 3}')
            run={'evaluation_path':'results/stage/run_eval.json',
                 'evaluation_sha256':hashlib.sha256(source.read_bytes()).hexdigest()}
            artifact={'path':'repaired_run_eval.json','source_path':run['evaluation_path']}
            output=Path(raw)/'export/repaired_run_eval.json'
            module.artifact_copy(run,artifact,output)
            saved=output.read_bytes();source.write_text('{"eval_schema": 2}')
            with self.assertRaisesRegex(ValueError,'changed'):
                module.artifact_copy(run,artifact,output)
            self.assertEqual(output.read_bytes(),saved)

    def test_reconciled_browser_keeps_qualification_and_historical_scope_explicit(self):
        module = load_script('build_site')
        run = dict(path='vo/dataset/sequence/algorithm/run1',run_type='vo',dataset='dataset',
                   sequence='sequence',algorithm='algorithm',repeat=1,status='ok',
                   scientific_status='rerun_required',scientific_blockers=['bad calibration'],
                   process_exit_code=139,execution_status='exited_nonzero',
                   campaign_membership='historical_excluded',input_variant='default',
                   metrics={'primary_ate_rmse_m':.1,'primary_alignment':'sim3','coverage_gap_pct':None},
                   artifacts=[{'path':'old.png','interpretation':'historical_derived'}])
        module.artifact_copy=lambda *args: Path('fake')
        index=module.index_page({'runs':[run]}, {run['path']:'run.html'})
        detail=module.run_page(run,'run.html','files')
        self.assertIn('data-headline="no"', index)
        self.assertIn('rerun_required', index)
        self.assertIn('historical_excluded', detail)
        self.assertIn('bad calibration', detail)
        self.assertIn('exited_nonzero; exit 139', detail)
        self.assertIn('0.1000 (sim3)', detail)
        self.assertIn('Dense coverage [%]</dt><dd>unknown', detail)
        self.assertIn('historical_derived', detail)
        self.assertNotIn('<img', detail)

    def test_manifest_labels_legacy_and_invalid_provenance(self):
        module = load_script("build_manifest")
        with tempfile.TemporaryDirectory() as raw:
            module.RESULTS = Path(raw) / "results"
            run = module.RESULTS / "vo" / "dataset" / "sequence" / "algorithm" / "run1"
            run.mkdir(parents=True)
            (run / "COMPLETE").touch()
            (run / "run_meta.json").write_text(json.dumps({"run_id": 1}))
            module.validate_location = lambda _: []
            module.validate = lambda _: []
            module.validate_provenance = lambda *_args, **_kwargs: []
            legacy = module.run_entry("vo", run)
            self.assertEqual(legacy["status"], "unreconciled")
            self.assertEqual(legacy["provenance_status"], "legacy")

            (run / "run_meta.json").write_text(json.dumps({"run_id": 1, "provenance_schema": 2}))
            module.validate_provenance = lambda *_args, **_kwargs: ["broken provenance"]
            invalid = module.run_entry("vo", run)
            self.assertEqual(invalid["status"], "invalid")
            self.assertEqual(invalid["provenance_status"], "invalid")

    def test_site_renders_provenance_column_and_detail(self):
        module = load_script("build_site")
        run = {
            "path": "vo/dataset/sequence/algorithm/run1",
            "run_type": "vo", "dataset": "dataset", "sequence": "sequence",
            "algorithm": "algorithm", "repeat": 1, "status": "complete",
            "provenance_status": "complete", "metrics": {}, "artifacts": [],
        }
        index = module.index_page({"runs": [run]}, {run["path"]: "run.html"})
        detail = module.run_page(run, "run.html", "files")
        self.assertIn("<th>Provenance</th>", index)
        self.assertIn("<th>Measurements</th>", index)
        self.assertIn("provenance-complete", index)
        self.assertIn("<dt>Provenance</dt>", detail)


if __name__ == "__main__":
    unittest.main()
