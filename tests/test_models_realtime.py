"""Unit tests for hannibal_api.models_realtime."""

import pytest
from pydantic import ValidationError

from hannibal_api.models_realtime import (
    ApiResponse,
    BuildRequest,
    BuildResponse,
    EntityInfo,
    GameState,
    GatherRequest,
    GatherResponse,
    GetStateRequest,
    GetStateResponse,
    ListEntitiesRequest,
    ListEntitiesResponse,
    Position,
    ResearchRequest,
    ResearchResponse,
    SelectRequest,
    SelectResponse,
    TrainRequest,
    TrainResponse,
)


# ============================================================================
# Basic Types Tests
# ============================================================================


def test_position_2d():
    """Test Position with x and z only."""
    pos = Position(x=100.5, z=200.7)
    assert pos.x == 100.5
    assert pos.z == 200.7
    assert pos.y is None


def test_position_3d():
    """Test Position with x, y, z."""
    pos = Position(x=100.5, z=200.7, y=50.0)
    assert pos.x == 100.5
    assert pos.z == 200.7
    assert pos.y == 50.0


def test_position_extra_fields_forbidden():
    """Test that Position rejects extra fields."""
    with pytest.raises(ValidationError):
        Position(x=1.0, z=2.0, invalid=3.0)


# ============================================================================
# Request Models Tests
# ============================================================================


def test_select_request_valid():
    """Test valid SelectRequest."""
    req = SelectRequest(entity_ids=[186, 188, 190])
    assert req.action == "select"
    assert req.entity_ids == [186, 188, 190]
    assert isinstance(req.correlation_id, str)
    assert len(req.correlation_id) > 0


def test_select_request_custom_correlation_id():
    """Test SelectRequest with custom correlation_id."""
    req = SelectRequest(entity_ids=[1, 2], correlation_id="custom-123")
    assert req.correlation_id == "custom-123"


def test_select_request_empty_ids():
    """Test SelectRequest rejects empty entity_ids."""
    with pytest.raises(ValidationError):
        SelectRequest(entity_ids=[])


def test_select_request_extra_fields_forbidden():
    """Test SelectRequest rejects extra fields."""
    with pytest.raises(ValidationError):
        SelectRequest(entity_ids=[1, 2], extra_field="invalid")


def test_gather_request_valid():
    """Test valid GatherRequest."""
    req = GatherRequest(resource="wood.tree")
    assert req.action == "gather"
    assert req.resource == "wood.tree"
    assert req.targets is None
    assert req.near == "selection"


def test_gather_request_with_targets():
    """Test GatherRequest with targets parameter."""
    req = GatherRequest(resource="food.fruit", targets=3, near="cc")
    assert req.resource == "food.fruit"
    assert req.targets == 3
    assert req.near == "cc"


def test_gather_request_invalid_targets():
    """Test GatherRequest rejects invalid targets."""
    with pytest.raises(ValidationError):
        GatherRequest(resource="wood.tree", targets=0)
    with pytest.raises(ValidationError):
        GatherRequest(resource="wood.tree", targets=-1)


def test_gather_request_invalid_resource_type():
    """Test GatherRequest rejects invalid resource types."""
    with pytest.raises(ValidationError):
        GatherRequest(resource="invalid.resource")


def test_build_request_valid():
    """Test valid BuildRequest."""
    req = BuildRequest(what="house")
    assert req.action == "build"
    assert req.what == "house"
    assert req.amount == 1
    assert req.mode == "selected"
    assert req.on_empty_selection == "error_then_fallback"


def test_build_request_with_amount():
    """Test BuildRequest with custom amount."""
    req = BuildRequest(what="house", amount=3, mode="economy")
    assert req.amount == 3
    assert req.mode == "economy"


def test_build_request_invalid_amount():
    """Test BuildRequest rejects invalid amount."""
    with pytest.raises(ValidationError):
        BuildRequest(what="house", amount=0)
    with pytest.raises(ValidationError):
        BuildRequest(what="house", amount=-1)


def test_train_request_valid():
    """Test valid TrainRequest."""
    req = TrainRequest(unit="female.citizen")
    assert req.action == "train"
    assert req.unit == "female.citizen"
    assert req.amount == 1


def test_train_request_with_amount():
    """Test TrainRequest with custom amount."""
    req = TrainRequest(unit="infantry.spearman", amount=5)
    assert req.amount == 5


def test_train_request_invalid_amount():
    """Test TrainRequest rejects invalid amount."""
    with pytest.raises(ValidationError):
        TrainRequest(unit="soldier", amount=0)


def test_research_request_valid():
    """Test valid ResearchRequest."""
    req = ResearchRequest(tech="phase_village")
    assert req.action == "research"
    assert req.tech == "phase_village"


def test_get_state_request_valid():
    """Test valid GetStateRequest."""
    req = GetStateRequest()
    assert req.action == "get_state"
    assert isinstance(req.correlation_id, str)


def test_list_entities_request_valid():
    """Test valid ListEntitiesRequest."""
    req = ListEntitiesRequest()
    assert req.action == "list_entities"
    assert req.filter == {}


def test_list_entities_request_with_filter():
    """Test ListEntitiesRequest with custom filter."""
    filter_dict = {"type": "worker", "idle": True}
    req = ListEntitiesRequest(filter=filter_dict)
    assert req.filter == filter_dict


# ============================================================================
# Response Models Tests
# ============================================================================


def test_game_state_valid():
    """Test valid GameState."""
    state = GameState(
        pid=1,
        resources={"food": 300, "wood": 200, "stone": 100, "metal": 100},
        population=10,
        population_cap=50,
        phase=1,
        current_selection=[186, 188],
    )
    assert state.pid == 1
    assert state.resources["food"] == 300
    assert state.population == 10
    assert len(state.current_selection) == 2


def test_entity_info_minimal():
    """Test EntityInfo with minimal fields."""
    entity = EntityInfo(id=186, template="units.iber.support.female.citizen")
    assert entity.id == 186
    assert entity.template == "units.iber.support.female.citizen"
    assert entity.position is None
    assert entity.owner is None


def test_entity_info_complete():
    """Test EntityInfo with all fields."""
    entity = EntityInfo(
        id=186,
        template="units.iber.support.female.citizen",
        position=Position(x=100.0, z=200.0),
        owner=1,
        health=75.0,
        max_health=100.0,
    )
    assert entity.position.x == 100.0
    assert entity.owner == 1
    assert entity.health == 75.0


def test_api_response_success_factory():
    """Test ApiResponse.success factory method."""
    resp = ApiResponse.success(correlation_id="test-123", result={"data": "value"})
    assert resp.correlation_id == "test-123"
    assert resp.ok is True
    assert resp.result == {"data": "value"}
    assert resp.error is None


def test_api_response_failure_factory():
    """Test ApiResponse.failure factory method."""
    resp = ApiResponse.failure(correlation_id="test-456", error="Something went wrong")
    assert resp.correlation_id == "test-456"
    assert resp.ok is False
    assert resp.result is None
    assert resp.error == "Something went wrong"


def test_api_response_direct_construction():
    """Test ApiResponse direct construction."""
    resp = ApiResponse(correlation_id="test-789", ok=True, result="OK")
    assert resp.correlation_id == "test-789"
    assert resp.ok is True
    assert resp.result == "OK"


def test_select_response_valid():
    """Test valid SelectResponse."""
    resp = SelectResponse(selected_ids=[186, 188])
    assert resp.selected_ids == [186, 188]


def test_gather_response_valid():
    """Test valid GatherResponse."""
    resp = GatherResponse(entity_ids=[186, 188, 190], target_count=5)
    assert len(resp.entity_ids) == 3
    assert resp.target_count == 5


def test_build_response_valid():
    """Test valid BuildResponse."""
    resp = BuildResponse(
        builder_ids=[186, 188],
        template="structures.iber.house",
        used_mode="selected",
    )
    assert len(resp.builder_ids) == 2
    assert resp.template == "structures.iber.house"
    assert resp.used_mode == "selected"
    assert resp.fallback_triggered is False


def test_build_response_with_fallback():
    """Test BuildResponse with fallback triggered."""
    resp = BuildResponse(
        builder_ids=[100, 101],
        template="structures.iber.house",
        used_mode="economy",
        fallback_triggered=True,
    )
    assert resp.used_mode == "economy"
    assert resp.fallback_triggered is True


def test_train_response_valid():
    """Test valid TrainResponse."""
    resp = TrainResponse(template="units.iber.support.female.citizen", queued=3)
    assert resp.template == "units.iber.support.female.citizen"
    assert resp.queued == 3


def test_research_response_valid():
    """Test valid ResearchResponse."""
    resp = ResearchResponse(tech="phase_village", queued=True)
    assert resp.tech == "phase_village"
    assert resp.queued is True


def test_get_state_response_valid():
    """Test valid GetStateResponse."""
    state = GameState(
        pid=1,
        resources={"food": 300},
        population=10,
        population_cap=50,
        phase=1,
        current_selection=[],
    )
    resp = GetStateResponse(state=state)
    assert resp.state.pid == 1
    assert resp.state.population == 10


def test_list_entities_response_valid():
    """Test valid ListEntitiesResponse."""
    entities = [
        EntityInfo(id=186, template="units.iber.support.female.citizen"),
        EntityInfo(id=188, template="units.iber.support.female.citizen"),
    ]
    resp = ListEntitiesResponse(entities=entities, count=2)
    assert len(resp.entities) == 2
    assert resp.count == 2


# ============================================================================
# Integration Tests
# ============================================================================


def test_request_response_round_trip():
    """Test serialization round-trip for request/response."""
    # Create a request
    req = SelectRequest(entity_ids=[1, 2, 3], correlation_id="test-round-trip")

    # Serialize to JSON
    req_json = req.model_dump_json()

    # Deserialize back
    req_restored = SelectRequest.model_validate_json(req_json)

    assert req_restored.correlation_id == "test-round-trip"
    assert req_restored.entity_ids == [1, 2, 3]


def test_api_response_with_typed_result():
    """Test ApiResponse wrapping a typed response."""
    select_result = SelectResponse(selected_ids=[186, 188])
    api_resp = ApiResponse.success(correlation_id="test-123", result=select_result)

    assert api_resp.ok is True
    assert isinstance(api_resp.result, SelectResponse)
    assert api_resp.result.selected_ids == [186, 188]
