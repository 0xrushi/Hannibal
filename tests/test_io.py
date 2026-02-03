import json
import tempfile
import unittest
from pathlib import Path

from hannibal_api.io import load_plan_file, write_plan_file
from hannibal_api.models import PlanFile


class TestPlanIO(unittest.TestCase):
    def test_round_trip(self):
        plan = PlanFile.model_validate(
            {
                "api_version": 1,
                "plans": {
                    1: {
                        0: [
                            {
                                "id": "a1",
                                "op": "select",
                                "args": {"selector": {"by": "ids", "ids": [186]}},
                            },
                        ],
                        1: [
                            {
                                "id": "a2",
                                "op": "gather",
                                "args": {"resource": "wood.tree"},
                            },
                        ],
                        2: [],
                    }
                },
            }
        )

        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "plan.json"
            write_plan_file(path, plan)
            loaded = load_plan_file(path)
            self.assertEqual(loaded.model_dump(), plan.model_dump())

    def test_write_is_stable_json(self):
        plan = PlanFile.model_validate(
            {
                "api_version": 1,
                "plans": {
                    1: {
                        0: [
                            {
                                "id": "a1",
                                "op": "gather",
                                "args": {"resource": "wood.tree"},
                            }
                        ]
                    }
                },
            }
        )
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "plan.json"
            write_plan_file(path, plan)
            text = path.read_text(encoding="utf-8")
            self.assertTrue(text.endswith("\n"))
            parsed = json.loads(text)
            self.assertEqual(parsed["api_version"], 1)


if __name__ == "__main__":
    unittest.main()
