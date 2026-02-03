from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from typing import Iterable, List, Optional, Sequence

from .parsing import parse_entity_ids


@dataclass(frozen=True)
class XdotoolConfig:
    window_name: str = "0 A.D."
    open_console_key: str = "F9"
    activate_timeout_sec: float = 2.0


def build_set_rpc_command_js(command: dict) -> str:
    """Build a single-line JS statement to set HANNIBAL_DEBUG.rpc_command."""

    payload = json.dumps(command, separators=(",", ":"))
    return f"HANNIBAL_DEBUG.rpc_command = {payload};"


def _xdotool(args: Sequence[str], runner=subprocess.run) -> None:
    runner(["xdotool", *args], check=True)


def inject_into_0ad_console(
    js_code: str,
    *,
    cfg: Optional[XdotoolConfig] = None,
    runner=subprocess.run,
) -> None:
    """Inject JS into the 0 A.D. dev console using xdotool.

    This is best-effort automation:
    - activates the 0 A.D. window
    - opens the console (F9 by default)
    - types a single-line JS command and presses Return
    """

    cfg = cfg or XdotoolConfig()
    code = " ".join(js_code.splitlines()).strip()
    if not code:
        raise ValueError("js_code is empty")

    # Activate the game window.
    _xdotool(
        ["search", "--name", cfg.window_name, "windowactivate", "--sync"], runner=runner
    )

    # Open console.
    if cfg.open_console_key:
        _xdotool(["key", cfg.open_console_key], runner=runner)

    # Type and execute.
    _xdotool(["type", "--clearmodifiers", code], runner=runner)
    _xdotool(["key", "Return"], runner=runner)
