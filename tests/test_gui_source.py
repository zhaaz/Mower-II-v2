import ast
import unittest
from pathlib import Path


class GuiSourceTests(unittest.TestCase):
    def test_app_has_no_stale_body_name(self) -> None:
        source_path = Path(__file__).parents[1] / "src" / "mower" / "ui" / "app.py"
        tree = ast.parse(source_path.read_text(encoding="utf-8"))
        stale_loads = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.Name)
            and isinstance(node.ctx, ast.Load)
            and node.id == "body"
        ]
        self.assertEqual(stale_loads, [])
