from __future__ import annotations

from typing import Annotated, Any, Dict, List, Literal, Optional, Tuple, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


Pid = int
EntityId = int
Tick = Literal[0, 1, 2]


class SelectorByIds(BaseModel):
    model_config = ConfigDict(extra="forbid")

    by: Literal["ids"]
    ids: List[EntityId] = Field(min_length=1)

    @field_validator("ids")
    @classmethod
    def _ids_must_be_positive(cls, v: List[int]) -> List[int]:
        if any((not isinstance(i, int) or i < 1) for i in v):
            raise ValueError("selector.ids must be positive integers")
        return v


Selector = Annotated[SelectorByIds, Field(discriminator="by")]


class SelectArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    set: Literal["current", "name"] = "current"
    name: Optional[str] = None
    selector: Selector

    def model_post_init(self, __context: Any) -> None:
        if self.set == "name" and not self.name:
            raise ValueError("select.args.name is required when set='name'")


class GatherArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # e.g. "wood.tree", "food.fruit", "stone.rock", "metal.ore"
    resource: str
    # If omitted, uses current selection (Hannibal-side semantics).
    who: Literal["selection"] = "selection"
    # Optional hint for target selection.
    near: Literal["selection", "cc"] = "selection"
    # Optional cap for how many resource entities to target.
    targets: Optional[int] = Field(default=None, ge=1)


class BuildArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # class-like ("house") or full template ("structures.iber.house")
    what: str
    amount: int = Field(default=1, ge=1)
    sid: Union[Literal["main"], int] = "main"
    near: Union[Literal["cc"], Tuple[float, float]] = "cc"

    # How to choose builders.
    mode: Literal["selected", "economy"] = "selected"
    # If mode == selected and selection is empty, Hannibal should error then fall back.
    on_empty_selection: Literal["error_then_fallback"] = "error_then_fallback"


class TrainArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    # class-like ("female.citizen") or full template ("units.iber.support.female.citizen")
    unit: str
    amount: int = Field(default=1, ge=1)
    sid: Union[Literal["main"], int] = "main"


class ResearchArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tech: str
    sid: Union[Literal["main"], int] = "main"


class LaunchGroupArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    groupname: str
    sid: Union[Literal["main"], int] = "main"
    params: Dict[str, Any] = Field(default_factory=dict)


class BaseAction(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(min_length=1)


class SelectAction(BaseAction):
    op: Literal["select"]
    args: SelectArgs


class GatherAction(BaseAction):
    op: Literal["gather"]
    args: GatherArgs


class BuildAction(BaseAction):
    op: Literal["build"]
    args: BuildArgs


class TrainAction(BaseAction):
    op: Literal["train"]
    args: TrainArgs


class ResearchAction(BaseAction):
    op: Literal["research"]
    args: ResearchArgs


class LaunchGroupAction(BaseAction):
    op: Literal["launch_group"]
    args: LaunchGroupArgs


Action = Annotated[
    Union[
        SelectAction,
        GatherAction,
        BuildAction,
        TrainAction,
        ResearchAction,
        LaunchGroupAction,
    ],
    Field(discriminator="op"),
]


class PlanFile(BaseModel):
    model_config = ConfigDict(extra="forbid")

    api_version: int = Field(default=1, ge=1)

    # plans[pid][tick] = list[Action]
    plans: Dict[int, Dict[int, List[Action]]]

    def validate_unique_action_ids(self) -> None:
        seen: set[str] = set()
        for pid, ticks in self.plans.items():
            for tick, actions in ticks.items():
                for action in actions:
                    if action.id in seen:
                        raise ValueError(f"duplicate action id: {action.id}")
                    seen.add(action.id)

    def model_post_init(self, __context: Any) -> None:
        for pid in self.plans.keys():
            if not isinstance(pid, int) or pid < 1 or pid > 8:
                raise ValueError(f"pid must be an int in [1, 8], got: {pid!r}")
        for pid, ticks in self.plans.items():
            for tick in ticks.keys():
                if tick not in (0, 1, 2):
                    raise ValueError(
                        f"tick must be 0, 1, or 2 (pid={pid}), got: {tick!r}"
                    )
        # Validate sid ints (when not 'main')
        for pid, ticks in self.plans.items():
            for tick, actions in ticks.items():
                for action in actions:
                    if hasattr(action, "args") and hasattr(action.args, "sid"):
                        sid = getattr(action.args, "sid")
                        if isinstance(sid, int) and sid < 1:
                            raise ValueError(
                                f"sid must be >= 1 when int (pid={pid}, tick={tick}), got: {sid}"
                            )
        self.validate_unique_action_ids()
