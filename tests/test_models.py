import unittest

from pydantic import ValidationError

from hannibal_api.models import PlanFile


class TestPlanModels(unittest.TestCase):
    def test_valid_minimal_plan(self):
        plan = PlanFile.model_validate(
            {
                "api_version": 1,
                "plans": {
                    1: {
                        0: [
                            {
                                "id": "a1",
                                "op": "select",
                                "args": {
                                    "set": "current",
                                    "selector": {"by": "ids", "ids": [186, 188]},
                                },
                            },
                            {
                                "id": "a2",
                                "op": "gather",
                                "args": {"resource": "wood.tree"},
                            },
                        ],
                        1: [
                            {
                                "id": "a3",
                                "op": "build",
                                "args": {
                                    "what": "house",
                                    "amount": 1,
                                    "sid": "main",
                                    "mode": "selected",
                                },
                            }
                        ],
                        2: [
                            {
                                "id": "a4",
                                "op": "train",
                                "args": {
                                    "unit": "female.citizen",
                                    "amount": 3,
                                    "sid": "main",
                                },
                            }
                        ],
                    }
                },
            }
        )

        self.assertEqual(plan.api_version, 1)
        self.assertIn(1, plan.plans)
        self.assertIn(0, plan.plans[1])

    def test_duplicate_action_id_rejected(self):
        with self.assertRaises(ValueError):
            PlanFile.model_validate(
                {
                    "api_version": 1,
                    "plans": {
                        1: {
                            0: [
                                {
                                    "id": "dup",
                                    "op": "train",
                                    "args": {"unit": "female.citizen", "amount": 1},
                                },
                            ],
                            1: [
                                {
                                    "id": "dup",
                                    "op": "research",
                                    "args": {"tech": "phase.town"},
                                },
                            ],
                        }
                    },
                }
            )

    def test_select_name_requires_name(self):
        with self.assertRaises(ValidationError):
            PlanFile.model_validate(
                {
                    "api_version": 1,
                    "plans": {
                        1: {
                            0: [
                                {
                                    "id": "a1",
                                    "op": "select",
                                    "args": {
                                        "set": "name",
                                        "selector": {"by": "ids", "ids": [1]},
                                    },
                                }
                            ]
                        }
                    },
                }
            )


if __name__ == "__main__":
    unittest.main()
