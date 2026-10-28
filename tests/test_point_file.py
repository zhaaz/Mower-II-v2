import unittest

from mower.domain.point_file import parse_point_line


class PointFileTests(unittest.TestCase):
    def test_current_point_format_is_supported(self) -> None:
        point = parse_point_line('1 41007.732913 -10619.040819 9.942616 1 "Labor"', 1)
        self.assertIsNotNone(point)
        assert point is not None
        self.assertEqual(point.name, "1")
        self.assertEqual(point.target.x, 41007.732913)
        self.assertEqual(point.marker_shape, "plus")
        self.assertEqual(point.remark, "Labor")

    def test_comment_and_decimal_comma_are_supported(self) -> None:
        point = parse_point_line('P2 1,25 2,50 3,75 4 "Rand" // Kommentar', 2)
        self.assertIsNotNone(point)
        assert point is not None
        self.assertEqual(point.target.z, 3.75)
        self.assertEqual(point.marker_shape, "plus_circle")

