from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional


def default_command_path() -> Path:
    """Default command file path.

    Hannibal-side JS reads this via:
      Engine.ReadFile("config/hannibal_rpc_command.json")
    which maps to the user's config directory.
    """

    return Path.home() / ".config" / "0ad" / "config" / "hannibal_rpc_command.json"


def write_command_file(command: Dict[str, Any], path: Optional[Path] = None) -> Path:
    """Write a single command JSON file for Hannibal to consume."""

    p = path or default_command_path()
    p.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(command, indent=2, sort_keys=True)
    if not text.endswith("\n"):
        text += "\n"
    p.write_text(text, encoding="utf-8")
    return p
