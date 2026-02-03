"""Hannibal start-plan API connector (Python).

This package focuses on:
- Defining a deterministic start-time plan schema (tick 0/1/2)
- Validating it with Pydantic v2
- Reading/writing the plan as JSON

It does not control 0 A.D. directly (transport is separate).
"""

from .models import (
    PlanFile,
    Action,
    SelectAction,
    GatherAction,
    BuildAction,
    TrainAction,
    ResearchAction,
    LaunchGroupAction,
)
from .io import load_plan_file, write_plan_file

__all__ = [
    "PlanFile",
    "Action",
    "SelectAction",
    "GatherAction",
    "BuildAction",
    "TrainAction",
    "ResearchAction",
    "LaunchGroupAction",
    "load_plan_file",
    "write_plan_file",
]
