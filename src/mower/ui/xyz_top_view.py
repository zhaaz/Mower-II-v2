from __future__ import annotations

from dataclasses import dataclass

from mower.domain import Point3D


@dataclass(frozen=True, slots=True)
class Viewport:
    width: float
    height: float
    padding: float = 28.0


def robot_to_screen(
    point: Point3D,
    workspace_min: Point3D,
    workspace_max: Point3D,
    viewport: Viewport,
) -> tuple[float, float]:
    """Bildet X+ nach oben und Y+ nach links ab."""
    x_span = workspace_max.x - workspace_min.x
    y_span = workspace_max.y - workspace_min.y
    if x_span <= 0.0 or y_span <= 0.0:
        raise ValueError("Ungültige Arbeitsraumgrenzen")

    usable_width = max(1.0, viewport.width - 2.0 * viewport.padding)
    usable_height = max(1.0, viewport.height - 2.0 * viewport.padding)
    x_fraction = (point.x - workspace_min.x) / x_span
    y_fraction = (point.y - workspace_min.y) / y_span

    screen_x = viewport.width - viewport.padding - y_fraction * usable_width
    screen_y = viewport.height - viewport.padding - x_fraction * usable_height
    return screen_x, screen_y

