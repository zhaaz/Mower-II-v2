import unittest

from mower.domain import Point3D
from mower.ui.project_view import ProjectView, format_scale_length, nice_scale_length


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

    def test_pan_moves_map_with_mouse(self) -> None:
        view = ProjectView(center_x=0.0, center_y=0.0, scale=2.0)
        point_before = view.world_to_screen(Point3D(0.0, 0.0, 0.0), 800.0, 600.0)
        view.pan_pixels(40.0, -20.0)
        point_after = view.world_to_screen(Point3D(0.0, 0.0, 0.0), 800.0, 600.0)
        self.assertAlmostEqual(point_after[0] - point_before[0], 40.0)
        self.assertAlmostEqual(point_after[1] - point_before[1], -20.0)

    def test_scale_bar_uses_readable_units(self) -> None:
        self.assertEqual(nice_scale_length(1.0, 110.0), 100.0)
        self.assertEqual(format_scale_length(100.0), "10 cm")
        self.assertEqual(format_scale_length(1000.0), "1 m")
        self.assertEqual(format_scale_length(5000.0), "5 m")
