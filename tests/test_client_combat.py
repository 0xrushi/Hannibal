"""
Tests for combat-related RPC commands in HannibalClient.

Tests: attack, attack_walk, patrol, set_stance, set_formation, guard, stop
"""

import pytest
from hannibal_api.client import HannibalClient
from hannibal_api.transport import FileTransport


class MockTransport:
    """Mock transport for testing without actual file I/O."""

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


class TestAttackCommand:
    """Tests for the attack command."""

    def test_attack_basic(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "attacker_ids": [100, 101, 102],
                "target_id": 500,
                "queued": False,
            },
        }

        result = client.attack(target_id=500)

        assert mock_transport.last_request["action"] == "attack"
        assert mock_transport.last_request["target_id"] == 500
        assert mock_transport.last_request["queued"] is False
        assert result["attacker_ids"] == [100, 101, 102]

    def test_attack_queued(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {"attacker_ids": [100], "target_id": 500, "queued": True},
        }

        result = client.attack(target_id=500, queued=True)

        assert mock_transport.last_request["queued"] is True
        assert result["queued"] is True


class TestAttackWalkCommand:
    """Tests for the attack_walk command."""

    def test_attack_walk_basic(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101],
                "position": {"x": 200, "z": 250},
                "target_classes": "Unit",
            },
        }

        result = client.attack_walk(x=200, z=250)

        assert mock_transport.last_request["action"] == "attack_walk"
        assert mock_transport.last_request["x"] == 200
        assert mock_transport.last_request["z"] == 250
        assert mock_transport.last_request["target_classes"] == "Unit"

    def test_attack_walk_custom_target(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}

        client.attack_walk(x=300, z=300, target_classes="Structure")

        assert mock_transport.last_request["target_classes"] == "Structure"

    def test_attack_walk_queued(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}

        client.attack_walk(x=100, z=150, queued=True)

        assert mock_transport.last_request["queued"] is True


class TestPatrolCommand:
    """Tests for the patrol command."""

    def test_patrol_basic(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100, 101], "position": {"x": 150, "z": 200}},
        }

        result = client.patrol(x=150, z=200)

        assert mock_transport.last_request["action"] == "patrol"
        assert mock_transport.last_request["x"] == 150
        assert mock_transport.last_request["z"] == 200
        assert result["position"] == {"x": 150, "z": 200}

    def test_patrol_queued(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}

        client.patrol(x=200, z=250, queued=True)

        assert mock_transport.last_request["queued"] is True


class TestSetStanceCommand:
    """Tests for the set_stance command."""

    def test_stance_violent(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100, 101], "stance": "violent"},
        }

        result = client.set_stance("violent")

        assert mock_transport.last_request["action"] == "set_stance"
        assert mock_transport.last_request["stance"] == "violent"
        assert result["stance"] == "violent"

    def test_stance_aggressive(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_stance("aggressive")
        assert mock_transport.last_request["stance"] == "aggressive"

    def test_stance_defensive(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_stance("defensive")
        assert mock_transport.last_request["stance"] == "defensive"

    def test_stance_passive(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_stance("passive")
        assert mock_transport.last_request["stance"] == "passive"

    def test_stance_standground(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_stance("standground")
        assert mock_transport.last_request["stance"] == "standground"

    def test_stance_invalid(self, client, mock_transport):
        with pytest.raises(ValueError, match="Invalid stance"):
            client.set_stance("invalid_stance")


class TestSetFormationCommand:
    """Tests for the set_formation command."""

    def test_formation_box(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100, 101, 102], "formation": "Box"},
        }

        result = client.set_formation("Box")

        assert mock_transport.last_request["action"] == "set_formation"
        assert mock_transport.last_request["formation"] == "Box"
        assert result["formation"] == "Box"

    def test_formation_line(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_formation("LineClosed")
        assert mock_transport.last_request["formation"] == "LineClosed"

    def test_formation_phalanx(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_formation("Phalanx")
        assert mock_transport.last_request["formation"] == "Phalanx"

    def test_formation_wedge(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_formation("Wedge")
        assert mock_transport.last_request["formation"] == "Wedge"

    def test_formation_invalid(self, client, mock_transport):
        with pytest.raises(ValueError, match="Invalid formation"):
            client.set_formation("InvalidFormation")


class TestGuardCommand:
    """Tests for the guard command."""

    def test_guard_basic(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {"guard_ids": [100, 101], "target_id": 200},
        }

        result = client.guard(target_id=200)

        assert mock_transport.last_request["action"] == "guard"
        assert mock_transport.last_request["target_id"] == 200
        assert mock_transport.last_request["queued"] is False
        assert result["target_id"] == 200

    def test_guard_queued(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}

        client.guard(target_id=300, queued=True)

        assert mock_transport.last_request["queued"] is True


class TestStopCommand:
    """Tests for the stop command."""

    def test_stop_basic(self, client, mock_transport):
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100, 101, 102]},
        }

        result = client.stop()

        assert mock_transport.last_request["action"] == "stop"
        assert mock_transport.last_request["queued"] is False
        assert result["entity_ids"] == [100, 101, 102]

    def test_stop_queued(self, client, mock_transport):
        mock_transport.next_response = {"ok": True, "result": {}}

        client.stop(queued=True)

        assert mock_transport.last_request["queued"] is True


class TestCombatWorkflow:
    """Integration tests for typical combat workflows."""

    def test_select_and_attack_workflow(self, client, mock_transport):
        # Select units
        mock_transport.next_response = {
            "ok": True,
            "result": {"selected_ids": [100, 101, 102]},
        }
        client.select([100, 101, 102])
        assert mock_transport.last_request["action"] == "select"

        # Set stance to aggressive
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_stance("aggressive")
        assert mock_transport.last_request["action"] == "set_stance"

        # Set formation
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_formation("LineClosed")
        assert mock_transport.last_request["action"] == "set_formation"

        # Attack-walk to position
        mock_transport.next_response = {"ok": True, "result": {}}
        client.attack_walk(x=300, z=300)
        assert mock_transport.last_request["action"] == "attack_walk"

    def test_patrol_workflow(self, client, mock_transport):
        # Select guards
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select([100, 101])

        # Set to defensive stance
        mock_transport.next_response = {"ok": True, "result": {}}
        client.set_stance("defensive")

        # Patrol between points
        mock_transport.next_response = {"ok": True, "result": {}}
        client.patrol(x=150, z=150)
        assert mock_transport.last_request["x"] == 150
