import unittest

from mower.domain import Point3D
from mower.ui.project_view import ProjectView


class ProjectViewTests(unittest.TestCase):
    def test_fit_uses_equal_xy_scale(self) -> None:
        view = ProjectView()
        view.fit(
            [Point3D(0.0, 0.0, 0.0), Point3D(2000.0, 1000.0, 0.0)],
            width=1000.0,
            height=700.0,
        )
        origin = view.world_to_screen(Point3D(0.0, 0.0, 0.0), 1000.0, 700.0)
        x_step = view.world_to_screen(Point3D(100.0, 0.0, 0.0), 1000.0, 700.0)
        y_step = view.world_to_screen(Point3D(0.0, 100.0, 0.0), 1000.0, 700.0)
        self.assertAlmostEqual(x_step[0] - origin[0], origin[1] - y_step[1])

    def test_zoom_keeps_mouse_anchor_in_place(self) -> None:
        view = ProjectView(center_x=100.0, center_y=200.0, scale=2.0)
        before = view.screen_to_world(300.0, 250.0, 800.0, 600.0)
        view.zoom_at(1.25, 300.0, 250.0, 800.0, 600.0)
        after = view.screen_to_world(300.0, 250.0, 800.0, 600.0)
        self.assertAlmostEqual(before.x, after.x)
        self.assertAlmostEqual(before.y, after.y)
