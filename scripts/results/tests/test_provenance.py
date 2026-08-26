#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
import warnings
from pathlib import Path


RESULTS_SCRIPTS = Path(__file__).resolve().parents[1]
RUN_SCRIPTS = RESULTS_SCRIPTS.parent / "run"
sys.path.insert(0, str(RESULTS_SCRIPTS))
from validate_run import validate_provenance  # noqa: E402
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


class EnricherTests(unittest.TestCase):
    def setUp(self):
        self.module = load_enricher()

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
                "run_id": 1, "run_type": "vio",
            }))
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
                ]
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", ResourceWarning)
                    self.assertEqual(self.module.main(), 0)
            finally:
                sys.argv = old_argv
            self.assertEqual(validate_provenance(run, required_schema=2), [])
            enriched = json.loads(meta_path.read_text())
            self.assertRegex(enriched["machine_id"], r"^machine-[0-9a-f]{12}$")
            self.assertNotIn(str(Path.home()), meta_path.read_text())


class ManifestAndSiteTests(unittest.TestCase):
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
            self.assertEqual(legacy["status"], "complete")
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
        self.assertIn("provenance-complete", index)
        self.assertIn("<dt>Provenance</dt>", detail)


if __name__ == "__main__":
    unittest.main()
