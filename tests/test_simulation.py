import unittest

from mower.application import MowerSystem
from mower.domain import Point3D
from mower.hardware.simulation import (
    SimGyro,
    SimRotationMotor,
    SimTracker,
    SimXYZRobot,
    SimulationError,
)


class SimulationTests(unittest.TestCase):
    @staticmethod
    def make_system() -> MowerSystem:
        return MowerSystem(SimXYZRobot(), SimTracker(noise_mm=0.0), SimGyro(), SimRotationMotor())

    def test_complete_simulation_probe(self) -> None:
        system = self.make_system()
        system.initialize()
        result = system.simulation_probe(Point3D(100.0, -50.0, -20.0))
        self.assertEqual(result["xyz"], Point3D(100.0, -50.0, -20.0))
        self.assertEqual(result["tracker"], Point3D(0.0, 0.0, 0.0))

    def test_motion_requires_homing(self) -> None:
        xyz = SimXYZRobot()
        xyz.connect()
        with self.assertRaisesRegex(SimulationError, "nicht referenziert"):
            xyz.move_to(Point3D(1.0, 2.0, 3.0))

    def test_workspace_limit_is_enforced(self) -> None:
        system = self.make_system()
        system.initialize()
        with self.assertRaisesRegex(SimulationError, "Arbeitsraums"):
            system.simulation_probe(Point3D(501.0, 0.0, 0.0))

