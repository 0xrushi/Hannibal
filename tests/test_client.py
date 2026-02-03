"""
Unit tests for HannibalClient.
"""

import pytest

from hannibal_api.client import HannibalClient


class MockTransport:
    """Mock transport for testing."""

    def __init__(self):
        self.last_request = None
        self.next_response = None

    def send_and_recv(self, request, timeout=None):
        """Store request and return mock response."""
        self.last_request = request
        return self.next_response or {"ok": True, "result": {}}

    def clear_stale_files(self):
        """Mock clear."""
        pass


@pytest.fixture
def mock_transport():
    """Create a mock transport."""
    return MockTransport()


@pytest.fixture
def client(mock_transport):
    """Create a client with mock transport."""
    return HannibalClient(player_id=2, transport=mock_transport)


def test_client_select(client, mock_transport):
    """Test select command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {"selected_ids": [100, 101]},
    }

    result = client.select([100, 101, 999])

    # Check request
    assert mock_transport.last_request["action"] == "select"
    assert mock_transport.last_request["player_id"] == 2
    assert mock_transport.last_request["entity_ids"] == [100, 101, 999]

    # Check result
    assert result["selected_ids"] == [100, 101]


def test_client_move(client, mock_transport):
    """Test move command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {"moved_ids": [200], "position": {"x": 150, "z": 250}},
    }

    result = client.move([200], x=150, z=250)

    assert mock_transport.last_request["action"] == "move"
    assert mock_transport.last_request["x"] == 150
    assert mock_transport.last_request["z"] == 250


def test_client_gather(client, mock_transport):
    """Test gather command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {"entity_ids": [100, 101], "resource": "wood.tree"},
    }

    result = client.gather("wood.tree", targets=5, near="cc")

    assert mock_transport.last_request["action"] == "gather"
    assert mock_transport.last_request["resource"] == "wood.tree"
    assert mock_transport.last_request["targets"] == 5
    assert mock_transport.last_request["near"] == "cc"


def test_client_build(client, mock_transport):
    """Test build command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {"template": "house", "mode": "selected"},
    }

    result = client.build("house", amount=2, mode="selected")

    assert mock_transport.last_request["action"] == "build"
    assert mock_transport.last_request["what"] == "house"
    assert mock_transport.last_request["amount"] == 2
    assert mock_transport.last_request["mode"] == "selected"


def test_client_train(client, mock_transport):
    """Test train command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {"unit": "infantry.spearman", "queued": 5},
    }

    result = client.train("infantry.spearman", amount=5)

    assert mock_transport.last_request["action"] == "train"
    assert mock_transport.last_request["unit"] == "infantry.spearman"
    assert mock_transport.last_request["amount"] == 5


def test_client_research(client, mock_transport):
    """Test research command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {"tech": "phase_town", "queued": True},
    }

    result = client.research("phase_town")

    assert mock_transport.last_request["action"] == "research"
    assert mock_transport.last_request["tech"] == "phase_town"


def test_client_get_state(client, mock_transport):
    """Test get_state command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {
            "player_id": 2,
            "resources": {"food": 400, "wood": 300},
            "population": 25,
            "phase": "town",
        },
    }

    result = client.get_state()

    assert mock_transport.last_request["action"] == "get_state"
    assert result["player_id"] == 2
    assert result["resources"]["food"] == 400


def test_client_list_entities(client, mock_transport):
    """Test list_entities command."""
    mock_transport.next_response = {
        "ok": True,
        "result": {
            "entities": [{"id": 123, "template": "units.athen.female_citizen"}],
            "count": 1,
        },
    }

    result = client.list_entities(filter={"class": "Worker"})

    assert mock_transport.last_request["action"] == "list_entities"
    assert mock_transport.last_request["filter"]["class"] == "Worker"
    assert result["count"] == 1


def test_client_error_handling(client, mock_transport):
    """Test that client raises RuntimeError on command failure."""
    mock_transport.next_response = {
        "ok": False,
        "error": "No entities selected",
    }

    with pytest.raises(RuntimeError, match="No entities selected"):
        client.gather("wood.tree")
