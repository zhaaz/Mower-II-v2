from __future__ import annotations

import math
from dataclasses import dataclass

from .models import Point3D


@dataclass(frozen=True, slots=True)
class RobotWorkspace:
    minimum: Point3D = Point3D(0.0, 0.0, 150.0)
    maximum: Point3D = Point3D(500.0, 400.0, 200.0)

    def contains(self, point: Point3D) -> bool:
        return (
            self.minimum.x <= point.x <= self.maximum.x
            and self.minimum.y <= point.y <= self.maximum.y
            and self.minimum.z <= point.z <= self.maximum.z
        )


@dataclass(frozen=True, slots=True)
class WagonGeometry:
    """Geometrie im lokalen Robotersystem, XYZ-Ursprung an einer Ecke."""

    footprint_min_x: float = -50.0
    footprint_max_x: float = 550.0
    footprint_min_y: float = -50.0
    footprint_max_y: float = 450.0
    workspace: RobotWorkspace = RobotWorkspace()
    marking_z_mm: float = 165.9

    @property
    def center_local(self) -> Point3D:
        return Point3D(
            (self.footprint_min_x + self.footprint_max_x) / 2.0,
            (self.footprint_min_y + self.footprint_max_y) / 2.0,
            self.marking_z_mm,
        )


@dataclass(frozen=True, slots=True)
class WagonPose:
    """Projektkoordinate des XYZ-Ursprungs und Drehung der lokalen Achsen."""

    origin_project: Point3D
    yaw_deg: float = 0.0

    def local_to_project(self, point: Point3D) -> Point3D:
        angle = math.radians(self.yaw_deg)
        cosine = math.cos(angle)
        sine = math.sin(angle)
        return Point3D(
            self.origin_project.x + cosine * point.x - sine * point.y,
            self.origin_project.y + sine * point.x + cosine * point.y,
            self.origin_project.z + point.z,
        )

    def project_to_local(self, point: Point3D, local_z: float | None = None) -> Point3D:
        angle = math.radians(self.yaw_deg)
        cosine = math.cos(angle)
        sine = math.sin(angle)
        dx = point.x - self.origin_project.x
        dy = point.y - self.origin_project.y
        return Point3D(
            cosine * dx + sine * dy,
            -sine * dx + cosine * dy,
            point.z - self.origin_project.z if local_z is None else local_z,
        )

    def polygon_to_project(self, local_points: list[Point3D]) -> list[Point3D]:
        return [self.local_to_project(point) for point in local_points]
