from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from mower.domain import Point3D
from mower.hardware import Gyro, RotationMotor, Tracker, XYZRobot


class WorkflowState(StrEnum):
    OFFLINE = "offline"
    INITIALIZED = "initialized"
    TRANSFORMED = "transformed"
    OFFSET_CALIBRATED = "offset_calibrated"
    READY = "ready"


@dataclass(slots=True)
class MowerSystem:
    xyz: XYZRobot
    tracker: Tracker
    gyro: Gyro
    rotation_motor: RotationMotor
    initialized: bool = False
    transformation_valid: bool = False
    offset_calibrated: bool = False
    marker_height_calibrated: bool = False

    def initialize(self) -> None:
        self.xyz.connect()
        self.tracker.connect()
        self.gyro.connect()
        self.rotation_motor.connect()
        self.xyz.home()
        self.initialized = True

    @property
    def workflow_state(self) -> WorkflowState:
        if not self.initialized:
            return WorkflowState.OFFLINE
        if not self.transformation_valid:
            return WorkflowState.INITIALIZED
        if not self.offset_calibrated:
            return WorkflowState.TRANSFORMED
        if not self.marker_height_calibrated:
            return WorkflowState.OFFSET_CALIBRATED
        return WorkflowState.READY

    def perform_transformation(self) -> None:
        self._require_initialized()
        self.transformation_valid = True

    def calibrate_offset(self) -> None:
        self._require_initialized()
        if not self.transformation_valid:
            raise RuntimeError("Vor der Offsetkalibrierung ist eine Transformation erforderlich")
        self.offset_calibrated = True

    def calibrate_marker_height(self) -> None:
        self._require_initialized()
        if not self.offset_calibrated:
            raise RuntimeError("Vor der Markierhöhe ist die Offsetkalibrierung erforderlich")
        self.marker_height_calibrated = True

    def move_robot(self, target: Point3D) -> None:
        self._require_initialized()
        self.xyz.move_to(target)

    def simulation_probe(self, target: Point3D) -> dict[str, object]:
        if not self.initialized:
            raise RuntimeError("System ist nicht initialisiert")
        self.xyz.move_to(target)
        return {
            "xyz": self.xyz.position,
            "tracker": self.tracker.measure(),
            "yaw_deg": self.gyro.yaw_deg(),
        }

    def _require_initialized(self) -> None:
        if not self.initialized:
            raise RuntimeError("System ist nicht initialisiert")

