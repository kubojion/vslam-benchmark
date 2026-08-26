from __future__ import annotations

import importlib.util
from pathlib import Path
import unittest


REPO = Path(__file__).resolve().parents[3]
MODULE_PATH = REPO / "scripts/campaign/run_quality_campaign.py"
SPEC = importlib.util.spec_from_file_location("run_quality_campaign", MODULE_PATH)
assert SPEC and SPEC.loader
campaign = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(campaign)


class CampaignDefinitionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.doc, _ = campaign.load_manifest(campaign.DEFAULT_MANIFEST)
        cls.cells = campaign.expand_cells(cls.doc)

    def test_committed_size_and_uniqueness(self) -> None:
        keys = [campaign.cell_key(cell) for cell in self.cells]
        self.assertEqual(220, len(keys))
        self.assertEqual(220, len(set(keys)))
        self.assertEqual(1100, len(keys) * self.doc["repeats"])
        self.assertEqual([], campaign.validate_manifest(self.doc, self.cells))

    def test_out_of_scope_algorithms_are_absent(self) -> None:
        algorithms = {cell["algorithm"] for cell in self.cells}
        self.assertTrue(algorithms.isdisjoint(campaign.EXCLUDED))

    def test_missing_zed_duplicate_profiles_have_safe_fallbacks(self) -> None:
        cases = (
            ("vio-lc", "orbslam3"),
            ("vio-lc", "okvis2"),
            ("vio-lc", "airslam"),
        )
        for run_type, algorithm in cases:
            cell = {
                "run_type": run_type,
                "dataset": "zed2i",
                "sequence": "field1_110426_full_10fps_q90",
                "algorithm": algorithm,
            }
            with self.subTest(algorithm=algorithm):
                for _, candidates in campaign.config_groups(cell):
                    self.assertTrue(any(path.is_file() for path in candidates), candidates)


if __name__ == "__main__":
    unittest.main()
