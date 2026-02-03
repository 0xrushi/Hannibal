import json
import tempfile
import unittest
from pathlib import Path

from hannibal_api.cli import normalize_plan_file


class TestCliNormalize(unittest.TestCase):
    def test_normalize_rewrites_sorted(self):
        raw = {
            "plans": {
                1: {
                    0: [
                        {"id": "a1", "op": "gather", "args": {"resource": "wood.tree"}},
                    ]
                }
            },
            "api_version": 1,
        }

        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "plan.json"
            p.write_text(json.dumps(raw), encoding="utf-8")

            normalize_plan_file(p)
            text = p.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))


if __name__ == "__main__":
    unittest.main()
