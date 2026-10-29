import json
import tempfile
import unittest
from pathlib import Path

from mower.config import load_config


class ConfigTests(unittest.TestCase):
    def test_project_config_is_loaded_and_validated(self) -> None:
        config = load_config()
        self.assertEqual(config.workspace.minimum.x, 0.0)
        self.assertEqual(config.workspace.maximum.x, 500.0)
        self.assertEqual(config.wagon.marking_z_mm, 165.9)
        self.assertEqual(config.front_direction, "+X")
        self.assertEqual(len(config.transformation.calibration_points), 5)

    def test_calibration_point_outside_workspace_is_rejected(self) -> None:
        source = Path("config/mower_config.json")
        data = json.loads(source.read_text(encoding="utf-8"))
        data["transformation"]["calibration_points_mm"][0] = [-1.0, 100.0, 170.0]
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "invalid.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "außerhalb"):
                load_config(path)
