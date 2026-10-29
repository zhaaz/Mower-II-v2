from __future__ import annotations

import random
from dataclasses import dataclass, field

from mower.domain import Point3D


class SimulationError(RuntimeError):
    pass


@dataclass(slots=True)
class SimXYZRobot:
    workspace_min: Point3D = Point3D(0.0, 0.0, 150.0)
    workspace_max: Point3D = Point3D(500.0, 400.0, 200.0)
    _position: Point3D = Point3D(0.0, 0.0, 0.0)
    connected: bool = False
    homed: bool = False
    stopped: bool = False

    @property
    def position(self) -> Point3D:
        return self._position

    def connect(self) -> None:
        self.connected = True
        self.stopped = False

    def home(self) -> None:
        self._require_connected()
        self._position = Point3D(
            self.workspace_min.x,
            self.workspace_min.y,
            self.workspace_max.z,
        )
        self.homed = True

    def move_to(self, target: Point3D) -> None:
        self._require_connected()
        if not self.homed:
            raise SimulationError("XYZ ist nicht referenziert")
        if not all((
            self.workspace_min.x <= target.x <= self.workspace_max.x,
            self.workspace_min.y <= target.y <= self.workspace_max.y,
            self.workspace_min.z <= target.z <= self.workspace_max.z,
        )):
            raise SimulationError(f"Ziel außerhalb des Arbeitsraums: {target}")
        self._position = target

    def emergency_stop(self) -> None:
        self.stopped = True

    def _require_connected(self) -> None:
        if not self.connected or self.stopped:
            raise SimulationError("XYZ ist nicht betriebsbereit")


@dataclass(slots=True)
class SimTracker:
    true_position: Point3D = Point3D(0.0, 0.0, 0.0)
    noise_mm: float = 0.02
    seed: int = 1
    connected: bool = False
    _random: random.Random = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self._random = random.Random(self.seed)

    def connect(self) -> None:
        self.connected = True

    def measure(self) -> Point3D:
        if not self.connected:
            raise SimulationError("Tracker ist nicht verbunden")
        noise = lambda: self._random.gauss(0.0, self.noise_mm)
        return Point3D(
            self.true_position.x + noise(),
            self.true_position.y + noise(),
            self.true_position.z + noise(),
        )


@dataclass(slots=True)
class SimGyro:
    angle_deg: float = 0.0
    connected: bool = False

    def connect(self) -> None:
        self.connected = True

    def yaw_deg(self) -> float:
        if not self.connected:
            raise SimulationError("Murata ist nicht verbunden")
        return self.angle_deg


@dataclass(slots=True)
class SimRotationMotor:
    angle_deg: float = 0.0
    connected: bool = False

    def connect(self) -> None:
        self.connected = True

    def move_to(self, angle_deg: float) -> None:
        if not self.connected:
            raise SimulationError("GYEMS ist nicht verbunden")
        self.angle_deg = angle_deg

    def stop(self) -> None:
        pass

