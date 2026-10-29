import unittest

from mower.domain import Point3D
from mower.ui.xyz_top_view import Viewport, robot_to_screen


class XYZTopViewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.minimum = Point3D(-500.0, -500.0, -250.0)
        self.maximum = Point3D(500.0, 500.0, 50.0)
        self.viewport = Viewport(300.0, 300.0, 25.0)

    def test_x_positive_points_up(self) -> None:
        origin = robot_to_screen(Point3D(0.0, 0.0, 0.0), self.minimum, self.maximum, self.viewport)
        positive_x = robot_to_screen(Point3D(100.0, 0.0, 0.0), self.minimum, self.maximum, self.viewport)
        self.assertLess(positive_x[1], origin[1])

    def test_y_positive_points_left(self) -> None:
        origin = robot_to_screen(Point3D(0.0, 0.0, 0.0), self.minimum, self.maximum, self.viewport)
        positive_y = robot_to_screen(Point3D(0.0, 100.0, 0.0), self.minimum, self.maximum, self.viewport)
        self.assertLess(positive_y[0], origin[0])

    def test_x_and_y_use_identical_scale(self) -> None:
        origin = robot_to_screen(Point3D(0.0, 0.0, 0.0), self.minimum, self.maximum, self.viewport)
        x_step = robot_to_screen(Point3D(100.0, 0.0, 0.0), self.minimum, self.maximum, self.viewport)
        y_step = robot_to_screen(Point3D(0.0, 100.0, 0.0), self.minimum, self.maximum, self.viewport)
        x_pixels = abs(x_step[1] - origin[1])
        y_pixels = abs(y_step[0] - origin[0])
        self.assertAlmostEqual(x_pixels, y_pixels)

    def test_non_square_workspace_keeps_equal_scale(self) -> None:
        wide_y_maximum = Point3D(500.0, 1500.0, 50.0)
        origin = robot_to_screen(Point3D(0.0, 0.0, 0.0), self.minimum, wide_y_maximum, self.viewport)
        x_step = robot_to_screen(Point3D(100.0, 0.0, 0.0), self.minimum, wide_y_maximum, self.viewport)
        y_step = robot_to_screen(Point3D(0.0, 100.0, 0.0), self.minimum, wide_y_maximum, self.viewport)
        self.assertAlmostEqual(
            abs(x_step[1] - origin[1]),
            abs(y_step[0] - origin[0]),
        )
