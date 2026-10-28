import unittest

from mower.application import MowerSystem
from mower.application.system import WorkflowState
from mower.hardware.simulation import SimGyro, SimRotationMotor, SimTracker, SimXYZRobot


class WorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.system = MowerSystem(SimXYZRobot(), SimTracker(), SimGyro(), SimRotationMotor())

    def test_complete_workflow_reaches_ready(self) -> None:
        self.assertEqual(self.system.workflow_state, WorkflowState.OFFLINE)
        self.system.initialize()
        self.assertEqual(self.system.workflow_state, WorkflowState.INITIALIZED)
        self.system.perform_transformation()
        self.system.calibrate_offset()
        self.system.calibrate_marker_height()
        self.assertEqual(self.system.workflow_state, WorkflowState.READY)

    def test_order_is_enforced(self) -> None:
        self.system.initialize()
        with self.assertRaisesRegex(RuntimeError, "Transformation"):
            self.system.calibrate_offset()

