"""
Pydantic models for the Hannibal Realtime API Contract.

This module defines the request/response schemas for real-time game-intent
operations against a running 0 A.D. match where Hannibal controls a player slot.
"""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional, Union
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


# ============================================================================
# Basic Types
# ============================================================================

EntityId = int
Pid = int


class Position(BaseModel):
    """2D or 3D position in game world."""

    model_config = ConfigDict(extra="forbid")

    x: float
    z: float
    y: Optional[float] = None  # elevation (optional)


ResourceType = Literal[
    "wood.tree",
    "food.fruit",
    "food.fish",
    "food.meat",
    "food.grain",
    "stone.rock",
    "metal.ore",
]


# ============================================================================
# Request Models
# ============================================================================


class SelectRequest(BaseModel):
    """
    Set current selection by literal entity ids.
    Hannibal side will filter to owned + existing entities.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["select"] = "select"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    entity_ids: List[EntityId] = Field(min_length=1)


class GatherRequest(BaseModel):
    """
    Order selected entities to gather a resource type.
    Uses current Hannibal-side selection.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["gather"] = "gather"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    resource: ResourceType
    targets: Optional[int] = Field(default=None, ge=1)
    near: Literal["selection", "cc"] = "selection"


class BuildRequest(BaseModel):
    """
    Build a structure.
    Default uses selected builders; if selection empty: error then fall back to economy.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["build"] = "build"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    what: str  # class-like name (e.g. "house") or full template
    amount: int = Field(default=1, ge=1)
    mode: Literal["selected", "economy"] = "selected"
    on_empty_selection: Literal["error_then_fallback"] = "error_then_fallback"


class TrainRequest(BaseModel):
    """
    Train units.
    Hannibal economy selects producers/queues.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["train"] = "train"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    unit: str  # class-like (e.g. "female.citizen") or full template
    amount: int = Field(default=1, ge=1)


class ResearchRequest(BaseModel):
    """
    Research a technology.
    Hannibal economy selects a producer.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["research"] = "research"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    tech: str  # technology template id


class GetStateRequest(BaseModel):
    """
    Read current player state (resources, pop, phase, etc.).
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["get_state"] = "get_state"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))


class ListEntitiesRequest(BaseModel):
    """
    List entities for planning/debugging.
    Filter rules defined by connector implementation.
    """

    model_config = ConfigDict(extra="forbid")

    action: Literal["list_entities"] = "list_entities"
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    filter: Dict[str, Any] = Field(default_factory=dict)


# Union of all request types
Request = Union[
    SelectRequest,
    GatherRequest,
    BuildRequest,
    TrainRequest,
    ResearchRequest,
    GetStateRequest,
    ListEntitiesRequest,
]


# ============================================================================
# Response Models
# ============================================================================


class GameState(BaseModel):
    """Current player state snapshot."""

    model_config = ConfigDict(extra="forbid")

    pid: Pid
    resources: Dict[str, float]  # e.g. {"food": 300, "wood": 200, ...}
    population: int
    population_cap: int
    phase: int
    current_selection: List[EntityId]


class EntityInfo(BaseModel):
    """Information about a single entity."""

    model_config = ConfigDict(extra="forbid")

    id: EntityId
    template: str
    position: Optional[Position] = None
    owner: Optional[Pid] = None
    health: Optional[float] = None
    max_health: Optional[float] = None


class ApiResponse(BaseModel):
    """
    Standard response envelope for all API calls.
    Contains correlation_id for request matching and ok/error status.
    """

    model_config = ConfigDict(extra="forbid")

    correlation_id: str
    ok: bool
    result: Optional[Any] = None  # success payload
    error: Optional[str] = None  # error message if ok=False

    @classmethod
    def success(cls, correlation_id: str, result: Any = None) -> ApiResponse:
        """Create a successful response."""
        return cls(correlation_id=correlation_id, ok=True, result=result)

    @classmethod
    def failure(cls, correlation_id: str, error: str) -> ApiResponse:
        """Create an error response."""
        return cls(correlation_id=correlation_id, ok=False, error=error)


class SelectResponse(BaseModel):
    """Response for select action."""

    model_config = ConfigDict(extra="forbid")

    selected_ids: List[EntityId]  # filtered to owned + existing


class GatherResponse(BaseModel):
    """Response for gather action."""

    model_config = ConfigDict(extra="forbid")

    entity_ids: List[EntityId]  # entities that received gather orders
    target_count: int  # number of resource targets found


class BuildResponse(BaseModel):
    """Response for build action."""

    model_config = ConfigDict(extra="forbid")

    builder_ids: List[EntityId]  # builders assigned
    template: str  # resolved civ-correct template
    used_mode: Literal["selected", "economy"]  # which mode was actually used
    fallback_triggered: bool = False  # true if empty selection triggered fallback


class TrainResponse(BaseModel):
    """Response for train action."""

    model_config = ConfigDict(extra="forbid")

    template: str  # resolved civ-correct unit template
    queued: int  # number of units queued


class ResearchResponse(BaseModel):
    """Response for research action."""

    model_config = ConfigDict(extra="forbid")

    tech: str  # technology id
    queued: bool  # whether research was queued


class GetStateResponse(BaseModel):
    """Response for get_state action."""

    model_config = ConfigDict(extra="forbid")

    state: GameState


class ListEntitiesResponse(BaseModel):
    """Response for list_entities action."""

    model_config = ConfigDict(extra="forbid")

    entities: List[EntityInfo]
    count: int
