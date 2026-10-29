import unittest

from mower.application.transformation import (
    simulate_measurements,
    solve_rigid_transformation,
)
from mower.domain import Point3D, WagonPose


class TransformationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.local_points = (
            Point3D(100.0, 100.0, 170.0),
            Point3D(400.0, 100.0, 170.0),
            Point3D(400.0, 300.0, 170.0),
            Point3D(100.0, 300.0, 170.0),
            Point3D(250.0, 200.0, 170.0),
        )
        self.true_pose = WagonPose(Point3D(40000.0, -11000.0, -160.0), 12.0)

    def test_exact_measurements_recover_pose(self) -> None:
        measurements = simulate_measurements(
            self.local_points,
            self.true_pose,
            noise_mm=0.0,
            seed=1,
        )
        result = solve_rigid_transformation(measurements)
        self.assertAlmostEqual(result.pose.origin_project.x, 40000.0)
        self.assertAlmostEqual(result.pose.origin_project.y, -11000.0)
        self.assertAlmostEqual(result.pose.origin_project.z, -160.0)
        self.assertAlmostEqual(result.pose.yaw_deg, 12.0)
        self.assertAlmostEqual(result.rms_mm, 0.0, places=8)

    def test_noisy_measurements_remain_within_acceptance(self) -> None:
        measurements = simulate_measurements(
            self.local_points,
            self.true_pose,
            noise_mm=0.02,
            seed=1,
        )
        result = solve_rigid_transformation(measurements)
        self.assertLess(result.rms_mm, 0.05)
        self.assertLess(result.max_residual_mm, 0.10)
