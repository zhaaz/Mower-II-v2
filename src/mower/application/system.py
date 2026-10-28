from __future__ import annotations

from dataclasses import dataclass

from mower.domain import Point3D
from mower.hardware import Gyro, RotationMotor, Tracker, XYZRobot


@dataclass(slots=True)
class MowerSystem:
    xyz: XYZRobot
    tracker: Tracker
    gyro: Gyro
    rotation_motor: RotationMotor
    initialized: bool = False

    def initialize(self) -> None:
        self.xyz.connect()
        self.tracker.connect()
        self.gyro.connect()
        self.rotation_motor.connect()
        self.xyz.home()
        self.initialized = True

    def simulation_probe(self, target: Point3D) -> dict[str, object]:
        if not self.initialized:
            raise RuntimeError("System ist nicht initialisiert")
        self.xyz.move_to(target)
        return {
            "xyz": self.xyz.position,
            "tracker": self.tracker.measure(),
            "yaw_deg": self.gyro.yaw_deg(),
        }

