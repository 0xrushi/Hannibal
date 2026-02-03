from __future__ import annotations

import json
import os
import threading
import time
import uuid
from typing import Any, Dict, Optional

from pydantic import TypeAdapter

from hannibal_api.rl_interface_client import RLInterfaceClient

from .models import (
    EvaluateAction,
    PushCommandAction,
    ZeroADAction,
    ZeroADObservation,
    ZeroADState,
)


_ACTION_ADAPTER = TypeAdapter(ZeroADAction)


def _normalize_eval_result(value: Any) -> Any:
    """Best-effort normalization for RL /evaluate return values.

    The 0 A.D. RL interface JSON-encodes the evaluation result. Some helper
    snippets in this repo return JSON-stringified objects, which then decode
    to a Python `str`. If the returned value is a JSON string, parse it.
    """

    if isinstance(value, str):
        s = value.strip()
        if not s:
            return value
        if (s.startswith("{") and s.endswith("}")) or (
            s.startswith("[") and s.endswith("]")
        ):
            try:
                return json.loads(s)
            except Exception:
                return value
    return value


class ZeroADSession:
    """Stateful proxy session for one running 0 A.D. instance."""

    def __init__(self, rl_url: Optional[str] = None):
        self.rl_url = (
            rl_url
            or os.environ.get("ZEROAD_RL_URL")
            or os.environ.get("HANNIBAL_RL_URL")
            or "http://127.0.0.1:6000"
        ).rstrip("/")
        self.rl = RLInterfaceClient(self.rl_url)

        self._lock = threading.Lock()
        self._state = ZeroADState(rl_url=self.rl_url)

    @property
    def state(self) -> ZeroADState:
        return self._state

    def _get_sim_time(self) -> Optional[float]:
        code = (
            "(function(){"
            "var cmpTimer=Engine.QueryInterface(SYSTEM_ENTITY,IID_Timer);"
            "if(!cmpTimer) return {error:'no IID_Timer'};"
            "var t=typeof cmpTimer.GetTime==='function'?cmpTimer.GetTime():-1;"
            "return {time:t};"
            "})()"
        )
        out = _normalize_eval_result(self.rl.evaluate(code))
        if isinstance(out, dict) and isinstance(out.get("time"), (int, float)):
            return float(out["time"])
        return None

    def reset(
        self,
        seed: Optional[int] = None,
        episode_id: Optional[str] = None,
        **_kwargs: Any,
    ) -> Dict[str, Any]:
        """Reset local session state (does not reset the 0 A.D. match)."""

        with self._lock:
            self._state.episode_id = episode_id or str(uuid.uuid4())
            self._state.step_count = 0

            # Ping RL interface.
            try:
                ping = self.rl.evaluate("1+1")
                ping = _normalize_eval_result(ping)
            except Exception as e:
                obs = ZeroADObservation(
                    ok=False,
                    error=f"rl_interface_unreachable: {e}",
                    episode_id=self._state.episode_id,
                    step_count=self._state.step_count,
                )
                return obs.model_dump(mode="json")

            # Best-effort stepper detection (requires sim time to advance).
            t1 = self._get_sim_time()
            time.sleep(0.05)
            t2 = self._get_sim_time()
            stepper_detected: Optional[bool]
            if t1 is None or t2 is None:
                stepper_detected = None
            else:
                stepper_detected = t2 > t1

            self._state.last_sim_time = t2 if t2 is not None else t1
            self._state.stepper_detected = stepper_detected

            obs = ZeroADObservation(
                ok=True,
                result={"ping": ping, "seed": seed},
                episode_id=self._state.episode_id,
                step_count=self._state.step_count,
                stepper_detected=stepper_detected,
                sim_time=self._state.last_sim_time,
            )
            return obs.model_dump(mode="json")

    def step(
        self,
        action_dict: Dict[str, Any],
        timeout_s: Optional[float] = None,
        **_kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute one OpenEnv step (proxying to RL /evaluate)."""

        with self._lock:
            action = _ACTION_ADAPTER.validate_python(action_dict)
            result: Any
            try:
                if isinstance(action, PushCommandAction):
                    result = self.rl.push_command(action.player_id, action.cmd)
                elif isinstance(action, EvaluateAction):
                    # RLInterfaceClient.evaluate uses a fixed 10s timeout internally.
                    # Keep timeout_s for API compatibility; ignore for now.
                    _ = timeout_s
                    result = self.rl.evaluate(action.code)
                else:
                    raise ValueError(f"unsupported action type: {type(action)}")
            except Exception as e:
                obs = ZeroADObservation(
                    ok=False,
                    error=str(e),
                    episode_id=self._state.episode_id,
                    step_count=self._state.step_count,
                    stepper_detected=self._state.stepper_detected,
                    sim_time=self._state.last_sim_time,
                )
                return obs.model_dump(mode="json")

            result = _normalize_eval_result(result)

            self._state.step_count += 1
            t = self._get_sim_time()
            if t is not None:
                self._state.last_sim_time = t

            obs = ZeroADObservation(
                ok=True,
                result=result,
                episode_id=self._state.episode_id,
                step_count=self._state.step_count,
                stepper_detected=self._state.stepper_detected,
                sim_time=self._state.last_sim_time,
            )
            return obs.model_dump(mode="json")
