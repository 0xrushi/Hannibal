"""
Tests for Phase 1 improvements to existing commands.

Tests: Enhanced gather, build, list_entities, and new gather_near_position
"""

import pytest
from hannibal_api.client import HannibalClient


class MockTransport:
    """Mock transport for testing."""

    def __init__(self):
        self.last_request = None
        self.next_response = {"ok": True, "result": {}}

    def send_and_recv(self, request, timeout=5.0):
        self.last_request = request
        return self.next_response

    def clear_stale_files(self):
        pass


@pytest.fixture
def mock_transport():
    return MockTransport()


@pytest.fixture
def client(mock_transport):
    return HannibalClient(player_id=1, transport=mock_transport)


class TestEnhancedGather:
    """Tests for improved gather command."""

    def test_gather_basic(self, client, mock_transport):
        """Test basic gather still works."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101],
                "resource": "wood.tree",
                "targets": [500],
                "nearest_distance": 25.3,
            },
        }

        result = client.gather("wood.tree")

        assert mock_transport.last_request["action"] == "gather"
        assert mock_transport.last_request["resource"] == "wood.tree"
        assert result["resource"] == "wood.tree"
        assert "nearest_distance" in result

    def test_gather_with_targets(self, client, mock_transport):
        """Test gather with multiple targets."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101, 102],
                "resource": "food.fruit",
                "targets": [500, 501, 502],
            },
        }

        result = client.gather("food.fruit", targets=3)

        assert mock_transport.last_request["targets"] == 3
        assert len(result["targets"]) == 3

    def test_gather_near_cc(self, client, mock_transport):
        """Test gather near civic center."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.gather("stone.rock", near="cc")

        assert mock_transport.last_request["near"] == "cc"

    def test_gather_near_selection(self, client, mock_transport):
        """Test gather near selection (default)."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.gather("metal.ore")

        assert mock_transport.last_request["near"] == "selection"


class TestGatherNearPosition:
    """Tests for new gather_near_position command."""

    def test_gather_near_position_basic(self, client, mock_transport):
        """Test gather near specific position."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101],
                "resource": "wood.tree",
                "targets": [500],
                "search_position": {"x": 250, "z": 300},
                "search_radius": 100,
                "resources_found": 5,
                "nearest_distance": 35.2,
            },
        }

        result = client.gather_near_position(x=250, z=300, resource="wood.tree")

        assert mock_transport.last_request["action"] == "gather_near_position"
        assert mock_transport.last_request["x"] == 250
        assert mock_transport.last_request["z"] == 300
        assert mock_transport.last_request["resource"] == "wood.tree"
        assert mock_transport.last_request["radius"] == 100  # Default

    def test_gather_near_position_custom_radius(self, client, mock_transport):
        """Test gather with custom search radius."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.gather_near_position(x=100, z=150, resource="food.fruit", radius=50)

        assert mock_transport.last_request["radius"] == 50

    def test_gather_near_position_response_details(self, client, mock_transport):
        """Test detailed response from gather_near_position."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100],
                "resource": "stone.rock",
                "targets": [600],
                "search_position": {"x": 200, "z": 200},
                "search_radius": 75,
                "resources_found": 3,
                "nearest_distance": 42.5,
            },
        }

        result = client.gather_near_position(x=200, z=200, resource="stone.rock", radius=75)

        assert result["search_position"]["x"] == 200
        assert result["search_position"]["z"] == 200
        assert result["search_radius"] == 75
        assert result["resources_found"] == 3
        assert result["nearest_distance"] == 42.5


class TestEnhancedBuild:
    """Tests for improved build command."""

    def test_build_basic(self, client, mock_transport):
        """Test basic build still works."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"template": "house", "mode": "selected"},
        }

        result = client.build("house")

        assert mock_transport.last_request["action"] == "build"
        assert mock_transport.last_request["what"] == "house"

    def test_build_with_position(self, client, mock_transport):
        """Test build with custom position."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "template": "barracks",
                "position": {"x": 300, "z": 350, "angle": 0},
                "custom_position": True,
            },
        }

        result = client.build("barracks", x=300, z=350)

        assert mock_transport.last_request["x"] == 300
        assert mock_transport.last_request["z"] == 350
        assert result["custom_position"] is True

    def test_build_with_angle(self, client, mock_transport):
        """Test build with rotation angle."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.build("house", x=100, z=100, angle=1.57)

        assert mock_transport.last_request["angle"] == 1.57

    def test_build_economy_mode(self, client, mock_transport):
        """Test build in economy mode."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"mode": "economy", "template": "storehouse"},
        }

        result = client.build("storehouse", mode="economy")

        assert mock_transport.last_request["mode"] == "economy"
        assert result["mode"] == "economy"


class TestEnhancedListEntities:
    """Tests for improved list_entities command."""

    def test_list_entities_basic(self, client, mock_transport):
        """Test basic list_entities still works."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entities": [
                    {"id": 100, "template": "units/athen_infantry_spearman_b"}
                ],
                "count": 1,
                "total": 1,
            },
        }

        result = client.list_entities()

        assert mock_transport.last_request["action"] == "list_entities"
        assert result["count"] == 1

    def test_list_entities_with_class_filter(self, client, mock_transport):
        """Test filtering by class."""
        mock_transport.next_response = {"ok": True, "result": {"entities": [], "count": 0, "total": 0}}

        client.list_entities(filter={"class": "Worker"})

        assert mock_transport.last_request["filter"]["class"] == "Worker"

    def test_list_entities_pagination(self, client, mock_transport):
        """Test pagination."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entities": [],
                "count": 10,
                "total": 100,
                "offset": 20,
                "limit": 10,
                "has_more": True,
            },
        }

        result = client.list_entities(offset=20, limit=10)

        assert mock_transport.last_request["filter"]["offset"] == 20
        assert mock_transport.last_request["filter"]["limit"] == 10
        assert result["has_more"] is True

    def test_list_entities_position_filter(self, client, mock_transport):
        """Test filtering by position."""
        mock_transport.next_response = {"ok": True, "result": {"entities": [], "count": 0, "total": 0}}

        client.list_entities(filter={"position": {"x": 200, "z": 250, "radius": 50}})

        assert mock_transport.last_request["filter"]["position"]["x"] == 200
        assert mock_transport.last_request["filter"]["position"]["z"] == 250
        assert mock_transport.last_request["filter"]["position"]["radius"] == 50

    def test_list_entities_health_filter(self, client, mock_transport):
        """Test filtering by health."""
        mock_transport.next_response = {"ok": True, "result": {"entities": [], "count": 0, "total": 0}}

        client.list_entities(filter={"min_health": 75})

        assert mock_transport.last_request["filter"]["min_health"] == 75

    def test_list_entities_owner_filter(self, client, mock_transport):
        """Test filtering by owner."""
        mock_transport.next_response = {"ok": True, "result": {"entities": [], "count": 0, "total": 0}}

        client.list_entities(filter={"owner": 2})

        assert mock_transport.last_request["filter"]["owner"] == 2

    def test_list_entities_exclude_structures(self, client, mock_transport):
        """Test excluding structures."""
        mock_transport.next_response = {"ok": True, "result": {"entities": [], "count": 0, "total": 0}}

        client.list_entities(include_structures=False)

        assert mock_transport.last_request["filter"]["include_structures"] is False

    def test_list_entities_enhanced_info(self, client, mock_transport):
        """Test enhanced entity information in response."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entities": [
                    {
                        "id": 100,
                        "template": "units/athen_infantry_spearman_b",
                        "position": {"x": 150, "z": 200},
                        "owner": 1,
                        "health": {"current": 75, "max": 100, "percent": 75},
                        "stance": "aggressive",
                        "classes": ["Infantry", "Melee", "Soldier"],
                    }
                ],
                "count": 1,
                "total": 1,
            },
        }

        result = client.list_entities()

        entity = result["entities"][0]
        assert "health" in entity
        assert entity["health"]["percent"] == 75
        assert "stance" in entity
        assert "classes" in entity

    def test_list_entities_combined_filters(self, client, mock_transport):
        """Test multiple filters combined."""
        mock_transport.next_response = {"ok": True, "result": {"entities": [], "count": 0, "total": 0}}

        client.list_entities(
            filter={
                "class": "Soldier",
                "min_health": 50,
                "position": {"x": 300, "z": 300, "radius": 100},
            },
            offset=10,
            limit=20,
        )

        request_filter = mock_transport.last_request["filter"]
        assert request_filter["class"] == "Soldier"
        assert request_filter["min_health"] == 50
        assert request_filter["position"]["radius"] == 100
        assert request_filter["offset"] == 10
        assert request_filter["limit"] == 20


class TestPhase1Integration:
    """Integration tests for Phase 1 improvements."""

    def test_gather_workflow(self, client, mock_transport):
        """Test improved gather workflow."""
        # Select workers
        mock_transport.next_response = {"ok": True, "result": {"selected_ids": [100, 101]}}
        client.select([100, 101])

        # Gather wood near their position
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101],
                "resource": "wood.tree",
                "targets": [500],
                "nearest_distance": 20.5,
            },
        }
        result = client.gather("wood.tree", near="selection")

        assert result["nearest_distance"] == 20.5
        assert mock_transport.last_request["action"] == "gather"

    def test_build_workflow(self, client, mock_transport):
        """Test improved build workflow."""
        # Select builders
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select([100, 101])

        # Build at specific location
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "template": "house",
                "position": {"x": 200, "z": 250, "angle": 0},
                "custom_position": True,
            },
        }
        result = client.build("house", x=200, z=250)

        assert result["custom_position"] is True
        assert result["position"]["x"] == 200

    def test_list_and_gather_workflow(self, client, mock_transport):
        """Test finding resources and gathering."""
        # List entities near a position
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entities": [
                    {"id": 100, "position": {"x": 150, "z": 150}},
                    {"id": 101, "position": {"x": 155, "z": 155}},
                ],
                "count": 2,
                "total": 2,
            },
        }
        entities = client.list_entities(
            filter={"class": "Worker", "position": {"x": 150, "z": 150, "radius": 50}}
        )

        # Select those workers
        worker_ids = [e["id"] for e in entities["entities"]]
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select(worker_ids)

        # Gather near that position
        mock_transport.next_response = {
            "ok": True,
            "result": {"resource": "wood.tree", "targets": [500]}
        }
        client.gather_near_position(x=150, z=150, resource="wood.tree", radius=100)

        assert mock_transport.last_request["action"] == "gather_near_position"
