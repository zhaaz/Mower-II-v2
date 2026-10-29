import tempfile
import unittest
from pathlib import Path

from mower.domain.flexible_point_file import (
    PointImportSettings,
    load_points_with_settings,
    preview_rows,
)


class FlexiblePointFileTests(unittest.TestCase):
    def _write(self, text: str) -> Path:
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        path = Path(directory.name) / "points.txt"
        path.write_text(text, encoding="utf-8")
        return path

    def test_reordered_semicolon_columns_and_header(self) -> None:
        path = self._write(
            "Export aus Fremdprogramm\n"
            "Rechts;Punkt;Hoehe;Hoch;Code;Text\n"
            "41007.5;P1;9.25;-10619.5;2;Achse A\n"
        )
        settings = PointImportSettings(
            delimiter=";",
            skip_rows=2,
            id_column=1,
            x_column=0,
            y_column=3,
            z_column=2,
            marker_column=4,
            remark_column=5,
        )
        points = load_points_with_settings(path, settings)
        self.assertEqual(points[0].name, "P1")
        self.assertEqual(points[0].target.x, 41007.5)
        self.assertEqual(points[0].target.y, -10619.5)
        self.assertEqual(points[0].marker_code, 2)
        self.assertEqual(points[0].remark, "Achse A")

    def test_whitespace_and_decimal_comma(self) -> None:
        path = self._write('P1 41007,5 -10619,5 9,25 1 "Randpunkt"\n')
        settings = PointImportSettings(decimal_separator=",")
        points = load_points_with_settings(path, settings)
        self.assertEqual(points[0].target.z, 9.25)
        self.assertEqual(points[0].remark, "Randpunkt")

    def test_minimum_four_columns(self) -> None:
        path = self._write("P1;1.0;2.0;3.0\n")
        settings = PointImportSettings(
            delimiter=";",
            marker_column=None,
            remark_column=None,
        )
        points = load_points_with_settings(path, settings)
        self.assertEqual(points[0].marker_code, 1)
        self.assertEqual(points[0].remark, "")

    def test_duplicate_required_mapping_is_rejected(self) -> None:
        path = self._write("P1;1.0;2.0;3.0\n")
        settings = PointImportSettings(
            delimiter=";",
            x_column=1,
            y_column=1,
            marker_column=None,
            remark_column=None,
        )
        with self.assertRaisesRegex(ValueError, "unterschiedliche"):
            load_points_with_settings(path, settings)

    def test_preview_ignores_comments(self) -> None:
        path = self._write("// Kommentar\nP1;1;2;3\n")
        rows = preview_rows(path, ";", skip_rows=0)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0].columns, ("P1", "1", "2", "3"))
