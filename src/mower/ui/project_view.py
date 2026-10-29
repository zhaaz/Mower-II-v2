from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from mower.domain import Point3D


@dataclass(slots=True)
class ProjectView:
    center_x: float = 0.0
    center_y: float = 0.0
    scale: float = 1.0

    def fit(
        self,
        positions: Iterable[Point3D],
        width: float,
        height: float,
        padding: float = 45.0,
    ) -> None:
        points = list(positions)
        if not points:
            return
        x_min = min(point.x for point in points)
        x_max = max(point.x for point in points)
        y_min = min(point.y for point in points)
        y_max = max(point.y for point in points)
        x_span = max(x_max - x_min, 100.0)
        y_span = max(y_max - y_min, 100.0)
        usable_width = max(width - 2.0 * padding, 1.0)
        usable_height = max(height - 2.0 * padding, 1.0)
        self.center_x = (x_min + x_max) / 2.0
        self.center_y = (y_min + y_max) / 2.0
        self.scale = max(min(usable_width / x_span, usable_height / y_span), 1.0e-6)

    def world_to_screen(
        self,
        point: Point3D,
        width: float,
        height: float,
    ) -> tuple[float, float]:
        return (
            width / 2.0 + (point.x - self.center_x) * self.scale,
            height / 2.0 - (point.y - self.center_y) * self.scale,
        )

    def screen_to_world(
        self,
        screen_x: float,
        screen_y: float,
        width: float,
        height: float,
    ) -> Point3D:
        return Point3D(
            self.center_x + (screen_x - width / 2.0) / self.scale,
            self.center_y - (screen_y - height / 2.0) / self.scale,
            0.0,
        )

    def zoom_at(
        self,
        factor: float,
        screen_x: float,
        screen_y: float,
        width: float,
        height: float,
    ) -> None:
        if factor <= 0.0:
            raise ValueError("Zoomfaktor muss positiv sein")
        anchor_before = self.screen_to_world(screen_x, screen_y, width, height)
        self.scale = min(max(self.scale * factor, 1.0e-6), 1.0e3)
        anchor_after = self.screen_to_world(screen_x, screen_y, width, height)
        self.center_x += anchor_before.x - anchor_after.x
        self.center_y += anchor_before.y - anchor_after.y
