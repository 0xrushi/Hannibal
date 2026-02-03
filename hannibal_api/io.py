from __future__ import annotations

import json
from pathlib import Path
from typing import Union

from .models import PlanFile


def load_plan_file(path: Union[str, Path]) -> PlanFile:
    p = Path(path)
    data = json.loads(p.read_text(encoding="utf-8"))
    return PlanFile.model_validate(data)


def write_plan_file(path: Union[str, Path], plan: PlanFile) -> None:
    p = Path(path)
    payload = plan.model_dump(mode="json")
    text = json.dumps(payload, indent=2, sort_keys=True)
    if not text.endswith("\n"):
        text += "\n"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
