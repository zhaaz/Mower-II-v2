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
