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
    """Bildet X+ nach oben und Y+ nach links mit gleichem Maßstab ab."""
    x_span = workspace_max.x - workspace_min.x
    y_span = workspace_max.y - workspace_min.y
    if x_span <= 0.0 or y_span <= 0.0:
        raise ValueError("Ungültige Arbeitsraumgrenzen")

    usable_width = max(1.0, viewport.width - 2.0 * viewport.padding)
    usable_height = max(1.0, viewport.height - 2.0 * viewport.padding)
    scale = min(usable_width / y_span, usable_height / x_span)

    drawn_width = y_span * scale
    drawn_height = x_span * scale
    left = (viewport.width - drawn_width) / 2.0
    bottom = (viewport.height + drawn_height) / 2.0

    screen_x = left + (workspace_max.y - point.y) * scale
    screen_y = bottom - (point.x - workspace_min.x) * scale
    return screen_x, screen_y


def workspace_screen_bounds(
    workspace_min: Point3D,
    workspace_max: Point3D,
    viewport: Viewport,
) -> tuple[float, float, float, float]:
    """Liefert den proportional eingepassten Arbeitsraum als left/top/right/bottom."""
    top_right = robot_to_screen(
        Point3D(workspace_max.x, workspace_min.y, 0.0),
        workspace_min,
        workspace_max,
        viewport,
    )
    bottom_left = robot_to_screen(
        Point3D(workspace_min.x, workspace_max.y, 0.0),
        workspace_min,
        workspace_max,
        viewport,
    )
    return bottom_left[0], top_right[1], top_right[0], bottom_left[1]

