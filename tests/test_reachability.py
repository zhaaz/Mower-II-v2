import unittest

from mower.domain import Point3D, RobotWorkspace, WagonGeometry, WagonPose


class ReachabilityTests(unittest.TestCase):
    def test_confirmed_workspace_dimensions(self) -> None:
        workspace = RobotWorkspace()
        self.assertEqual(workspace.maximum.x - workspace.minimum.x, 500.0)
        self.assertEqual(workspace.maximum.y - workspace.minimum.y, 400.0)
        self.assertEqual(workspace.maximum.z - workspace.minimum.z, 50.0)

    def test_confirmed_wagon_dimensions(self) -> None:
        wagon = WagonGeometry()
        self.assertEqual(wagon.footprint_max_x - wagon.footprint_min_x, 600.0)
        self.assertEqual(wagon.footprint_max_y - wagon.footprint_min_y, 500.0)

    def test_reachability_in_local_workspace(self) -> None:
        workspace = RobotWorkspace()
        self.assertTrue(workspace.contains(Point3D(250.0, 200.0, 165.9)))
        self.assertFalse(workspace.contains(Point3D(-0.1, 200.0, 165.9)))
        self.assertFalse(workspace.contains(Point3D(250.0, 400.1, 165.9)))

    def test_rotated_pose_round_trip(self) -> None:
        pose = WagonPose(Point3D(10000.0, -5000.0, 0.0), 37.0)
        local = Point3D(125.0, 275.0, 165.9)
        project = pose.local_to_project(local)
        restored = pose.project_to_local(project)
        self.assertAlmostEqual(restored.x, local.x)
        self.assertAlmostEqual(restored.y, local.y)
        self.assertAlmostEqual(restored.z, local.z)
