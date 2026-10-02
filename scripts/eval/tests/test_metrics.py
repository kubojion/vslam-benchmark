import sys
from pathlib import Path
import unittest

import numpy as np
from scipy.spatial.transform import Rotation

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from _metrics import (right_transform, validate_poses, interpolate_reference,
                      camera_association, fit_alignment, apply_alignment,
                      relative_errors, distance_pairs, translation_origin_errors)


def poses(t, xyz=None, yaw=None):
    n = len(t)
    a = np.zeros((n, 8)); a[:, 0] = t; a[:, 7] = 1
    if xyz is not None: a[:, 1:4] = xyz
    if yaw is not None: a[:, 4:] = Rotation.from_euler('z', yaw).as_quat()
    return a


class MetricsTests(unittest.TestCase):
    def test_rotating_lever_arm_requires_right_transform(self):
        a = poses([0, 1, 2], yaw=[0, np.pi/2, np.pi])
        extrinsic = np.eye(4); extrinsic[0, 3] = 2
        actual = right_transform(a, extrinsic)
        np.testing.assert_allclose(actual[:, 1:4], [[2, 0, 0], [0, 2, 0], [-2, 0, 0]], atol=1e-14)
        np.testing.assert_allclose(right_transform(actual, np.linalg.inv(extrinsic)), a, atol=1e-14)

    def test_interpolation_never_bridges_reference_holes_or_extrapolates(self):
        a = poses([1, 1.1, 2, 2.1], [[0, 0, 0], [1, 0, 0], [2, 0, 0], [3, 0, 0]])
        out, keep = interpolate_reference(a, [0, 1, 1.05, 1.5, 2, 2.1, 3], .2)
        self.assertEqual(keep.tolist(), [False, True, True, False, True, True, False])
        np.testing.assert_allclose(out[1, 1], .5)

    def test_sparse_export_is_not_filled(self):
        a = poses([0, 1, 5])
        out, ids, dt = camera_association(a, np.arange(6), .01)
        self.assertEqual(ids.tolist(), [0, 1, 5]); self.assertEqual(len(out), 3)

    def test_explicit_exclusion_is_not_filled_when_shorter_than_gap_threshold(self):
        a = poses([0, .2, .6, .8], [[0, 0, 0], [1, 0, 0], [3, 0, 0], [4, 0, 0]])
        intervals = [[0, .2], [.6, .8]]
        query = [0, .1, .2, .3, .4, .5, .6, .7, .8]
        out, keep = interpolate_reference(a, query, .5, intervals)
        self.assertEqual(keep.tolist(), [True, True, True, False, False, False, True, True, True])
        np.testing.assert_allclose(out[:, 1], [0, .5, 1, 3, 3.5, 4])
        # An apparently short distance/time window must also respect the mask.
        self.assertEqual(distance_pairs(a, 2, .5, valid_intervals=intervals).tolist(), [])

    def test_reference_exclusion_applies_even_if_raw_samples_remain(self):
        a = poses([0, .2, .4, .6, .8])
        _, keep = interpolate_reference(a, [.2, .3, .4, .5, .6], .5, [[0, .2], [.6, .8]])
        self.assertEqual(keep.tolist(), [True, False, False, False, True])

    def test_invalid_support_intervals_are_rejected(self):
        a = poses([0, 1, 2])
        for intervals in ([], [[1, 0]], [[0, 1], [1, 2]], [[0, float('nan')]]):
            with self.subTest(intervals=intervals), self.assertRaises(ValueError):
                interpolate_reference(a, [0, 1], valid_intervals=intervals)

    def test_high_rate_export_uses_one_pose_per_camera(self):
        a = poses(np.arange(100)/100)
        out, ids, dt = camera_association(a, np.arange(10)/10)
        self.assertEqual(len(out), 10); self.assertEqual(len(np.unique(out[:, 0])), 10)

    def test_reused_estimate_is_not_counted_twice(self):
        a = poses([1, 2])
        out, ids, dt = camera_association(a, [0.999, 1.001, 2.0], .01)
        self.assertEqual(len(out), 2)

    def test_invalid_timestamps_and_quaternions_rejected(self):
        a = poses([1, 1, 2])
        with self.assertRaises(ValueError): validate_poses(a)
        a = poses([1, 2]); a[0, 7] = 0
        with self.assertRaises(ValueError): validate_poses(a)
        a = poses([1e18, 1e18 + 1e9])
        with self.assertRaises(ValueError): validate_poses(a)

    def test_se3_does_not_absorb_scale(self):
        xyz = np.array([[0, 0, 0], [1, 0, 0], [1, 2, 0], [0, 2, 1.]])
        g = poses([0, 1, 2, 3], xyz)
        e = poses([0, 1, 2, 3], 2*xyz + 8)
        sim = fit_alignment(e[:, 1:4], g[:, 1:4], True)
        self.assertAlmostEqual(sim[2], .5)
        np.testing.assert_allclose(apply_alignment(e, sim)[:, 1:4], xyz, atol=1e-14)
        se = fit_alignment(e[:, 1:4], g[:, 1:4], False)
        self.assertGreater(np.linalg.norm(apply_alignment(e, se)[:, 1:4]-xyz), .5)

    def test_stationary_and_collinear_fits_fail_explicitly(self):
        for xyz in [np.zeros((4, 3)), np.c_[np.arange(4), np.zeros((4, 2))]]:
            with self.assertRaises(ValueError): fit_alignment(xyz, xyz)

    def test_direction_error_is_not_displacement_magnitude_error(self):
        g = poses([0, 1], [[0, 0, 0], [1, 0, 0]])
        e = poses([0, 1], [[0, 0, 0], [0, 1, 0]])
        t, r, d = relative_errors(g, e, [[0, 1]])
        self.assertAlmostEqual(t[0], np.sqrt(2)); self.assertEqual(d[0], 0)

    def test_common_world_rotation_does_not_change_relative_error(self):
        g = poses([0, 1, 2], [[0, 0, 0], [1, 0, 0], [1, 2, 0]], [0, .2, .5])
        r = Rotation.from_euler('xyz', [.4, -.3, .9]).as_matrix()
        e = apply_alignment(g, (r, [3, 5, 8], 1))
        t, angle, d = relative_errors(g, e, [[0, 1], [1, 2]])
        np.testing.assert_allclose(t, 0, atol=1e-14)
        np.testing.assert_allclose(angle, 0, atol=1e-12)

    def test_windows_do_not_bridge_sampling_holes(self):
        g = poses([0, .1, .2, 3, 3.1], [[i, 0, 0] for i in range(5)])
        self.assertEqual(distance_pairs(g, 1, .2).tolist(), [[0, 1], [1, 2], [3, 4]])

    def test_translation_origin_keeps_heading_error(self):
        g = poses([0, 1], [[0, 0, 0], [1, 0, 0]])
        e = poses([0, 1], [[3, 4, 0], [3, 5, 0]])
        self.assertAlmostEqual(translation_origin_errors(g, e)['rmse'], 1)


if __name__ == '__main__': unittest.main()
