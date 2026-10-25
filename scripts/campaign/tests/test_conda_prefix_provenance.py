import importlib.util
import json
from pathlib import Path
from unittest.mock import patch

import pytest

HELPER = Path(__file__).resolve().parents[2] / "run/_enrich_run_meta.py"
spec = importlib.util.spec_from_file_location("enrich_prefix_test", HELPER)
enrich = importlib.util.module_from_spec(spec)
spec.loader.exec_module(enrich)


@pytest.mark.parametrize("environment,selector", [("cuvslam", "-n"), ("/private/envs/cuvslam", "-p")])
def test_snapshot_selector_and_safe_filename(tmp_path, environment, selector):
    packages = [{"name": "numpy", "version": "1", "build_string": "x", "channel": "defaults"}]
    with patch.object(enrich, "command", return_value=json.dumps(packages)) as command:
        result = enrich.conda_snapshot(environment, tmp_path)
    command.assert_called_once_with(["conda", "list", selector, environment, "--json"], timeout=60)
    assert result["name"] == "cuvslam"
    assert result["snapshot"] == "provenance/conda-cuvslam.json"
    assert result["package_count"] == 1
    assert (tmp_path / result["snapshot"]).is_file()
    assert "/private/" not in json.dumps(result)


def test_name_and_prefix_preserve_identical_package_identity(tmp_path):
    with patch.object(enrich, "command", return_value='[{"name":"numpy","version":"1"}]'):
        named = enrich.conda_snapshot("cuvslam", tmp_path / "named")
        prefix = enrich.conda_snapshot("/private/envs/cuvslam", tmp_path / "prefix")
    assert named == prefix


def test_failed_lookup_remains_failure(tmp_path):
    with patch.object(enrich, "command", return_value=None):
        with pytest.raises(ValueError, match="cannot inspect"):
            enrich.conda_snapshot("/private/envs/cuvslam", tmp_path)
    assert not (tmp_path / "provenance").exists()


@pytest.mark.parametrize("name", ["", "/", "..", "../escape", "relative/env"])
def test_invalid_names_do_not_write(tmp_path, name):
    with patch.object(enrich, "command") as command:
        with pytest.raises(ValueError):
            enrich.conda_snapshot(name, tmp_path)
    command.assert_not_called()
