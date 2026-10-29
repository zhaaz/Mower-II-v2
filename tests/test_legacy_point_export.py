import tempfile
import unittest
from pathlib import Path

from mower.domain import Point3D, StakeoutPoint
from mower.domain.legacy_point_export import (
    legacy_point_text,
    save_legacy_point_file,
)
from mower.domain.point_file import load_points


class LegacyPointExportTests(unittest.TestCase):
    def test_export_can_be_read_by_legacy_parser(self) -> None:
        points = [
            StakeoutPoint(
                "P1",
                Point3D(41007.732913, -10619.040819, 9.942616),
                marker_code=2,
                remark="Achse A",
            ),
            StakeoutPoint(
                "P2",
                Point3D(41050.025045, -10756.263154, 11.514529),
                marker_code=1,
                remark="",
            ),
        ]
        with tempfile.TemporaryDirectory() as temp_dir:
            target = Path(temp_dir) / "converted.txt"
            save_legacy_point_file(target, points)
            restored = load_points(target)
        self.assertEqual(len(restored), 2)
        self.assertEqual(restored[0].name, "P1")
        self.assertEqual(restored[0].target.x, 41007.732913)
        self.assertEqual(restored[0].marker_code, 2)
        self.assertEqual(restored[0].remark, "Achse A")

    def test_export_has_fixed_six_decimal_places(self) -> None:
        point = StakeoutPoint("1", Point3D(1.0, 2.5, 3.25))
        text = legacy_point_text([point])
        self.assertIn('1  1.000000  2.500000  3.250000  1  ""', text)

    def test_quotes_and_line_breaks_in_remark_are_sanitized(self) -> None:
        point = StakeoutPoint(
            "1",
            Point3D(1.0, 2.0, 3.0),
            remark='Text mit "Zitat"\nund Umbruch',
        )
        text = legacy_point_text([point])
        self.assertIn('"Text mit \'Zitat\' und Umbruch"', text)
