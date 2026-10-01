#!/usr/bin/env python3

import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from canonicalize_orb_trajectory import TrajectoryError, canonicalize  # noqa: E402


POSE_A = "1 2 3 0 0 0 1"
POSE_B = "2 3 4 0 0 0 1"


class CanonicalizeOrbTrajectoryTests(unittest.TestCase):
    def run_case(self, contents: str):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "raw.txt"
            destination = Path(tmp) / "trajectory.txt"
            source.write_text(contents)
            stats = canonicalize(source, destination)
            return stats, destination.read_text()

    def test_removes_only_exact_duplicate_timestamp_pose(self):
        stats, output = self.run_case(
            f"1000000000 {POSE_A}\n1000000000 {POSE_A}\n2000000000 {POSE_B}\n"
        )
        self.assertEqual(stats["raw_rows"], 3)
        self.assertEqual(stats["output_rows"], 2)
        self.assertEqual(stats["exact_duplicates_removed"], 1)
        self.assertEqual(output.splitlines()[0], f"1.000000000 {POSE_A}")

    def test_rejects_conflicting_duplicate_timestamp(self):
        with self.assertRaisesRegex(TrajectoryError, "conflicting pose"):
            self.run_case(
                f"1000000000 {POSE_A}\n1000000000 {POSE_B}\n2000000000 {POSE_B}\n"
            )

    def test_rejects_time_reversal(self):
        with self.assertRaisesRegex(TrajectoryError, "timestamp decreased"):
            self.run_case(f"2000000000 {POSE_A}\n1000000000 {POSE_B}\n")


if __name__ == "__main__":
    unittest.main()
