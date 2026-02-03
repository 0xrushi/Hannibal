"""
Tests for Phase 3 unit management commands.

Tests: garrison, unload, unload_all, repair, heal, return_resources
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


class TestGarrisonCommand:
    """Tests for garrison command."""

    def test_garrison_basic(self, client, mock_transport):
        """Test basic garrison."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101],
                "target_id": 200,
                "queued": False,
            },
        }

        result = client.garrison(target_id=200)

        assert mock_transport.last_request["action"] == "garrison"
        assert mock_transport.last_request["target_id"] == 200
        assert mock_transport.last_request["queued"] is False
        assert result["entity_ids"] == [100, 101]

    def test_garrison_queued(self, client, mock_transport):
        """Test garrison with queued command."""
        mock_transport.next_response = {"ok": True, "result": {"queued": True}}

        result = client.garrison(target_id=300, queued=True)

        assert mock_transport.last_request["queued"] is True
        assert result["queued"] is True

    def test_garrison_building(self, client, mock_transport):
        """Test garrisoning in building."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100], "target_id": 250},
        }

        client.garrison(target_id=250)  # Civic center

        assert mock_transport.last_request["target_id"] == 250

    def test_garrison_ship(self, client, mock_transport):
        """Test garrisoning on transport ship."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.garrison(target_id=400)  # Transport ship

        assert mock_transport.last_request["action"] == "garrison"


class TestUnloadCommand:
    """Tests for unload command."""

    def test_unload_default(self, client, mock_transport):
        """Test unload without specifying entities (unloads first)."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"garrison_holder_id": 200, "unloaded_ids": [100]},
        }

        result = client.unload(garrison_holder_id=200)

        assert mock_transport.last_request["action"] == "unload"
        assert mock_transport.last_request["garrison_holder_id"] == 200
        assert result["unloaded_ids"] == [100]

    def test_unload_specific_entities(self, client, mock_transport):
        """Test unloading specific entities."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "garrison_holder_id": 200,
                "unloaded_ids": [100, 101, 102],
            },
        }

        result = client.unload(garrison_holder_id=200, entity_ids=[100, 101, 102])

        assert mock_transport.last_request["entity_ids"] == [100, 101, 102]
        assert result["unloaded_ids"] == [100, 101, 102]

    def test_unload_single_entity(self, client, mock_transport):
        """Test unloading single entity."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"garrison_holder_id": 250, "unloaded_ids": [105]},
        }

        result = client.unload(garrison_holder_id=250, entity_ids=[105])

        assert mock_transport.last_request["entity_ids"] == [105]


class TestUnloadAllCommand:
    """Tests for unload_all command."""

    def test_unload_all_basic(self, client, mock_transport):
        """Test unloading all units."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"garrison_holder_id": 200},
        }

        result = client.unload_all(garrison_holder_id=200)

        assert mock_transport.last_request["action"] == "unload_all"
        assert mock_transport.last_request["garrison_holder_id"] == 200
        assert result["garrison_holder_id"] == 200

    def test_unload_all_from_building(self, client, mock_transport):
        """Test unloading all from building."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.unload_all(garrison_holder_id=300)

        assert mock_transport.last_request["garrison_holder_id"] == 300

    def test_unload_all_from_ship(self, client, mock_transport):
        """Test unloading all from transport ship."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.unload_all(garrison_holder_id=450)

        assert mock_transport.last_request["action"] == "unload_all"


class TestRepairCommand:
    """Tests for repair command."""

    def test_repair_basic(self, client, mock_transport):
        """Test basic repair."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "repairer_ids": [100, 101],
                "target_id": 300,
                "autocontinue": True,
                "queued": False,
            },
        }

        result = client.repair(target_id=300)

        assert mock_transport.last_request["action"] == "repair"
        assert mock_transport.last_request["target_id"] == 300
        assert mock_transport.last_request["autocontinue"] is True
        assert result["repairer_ids"] == [100, 101]

    def test_repair_no_autocontinue(self, client, mock_transport):
        """Test repair without autocontinue."""
        mock_transport.next_response = {"ok": True, "result": {"autocontinue": False}}

        result = client.repair(target_id=400, autocontinue=False)

        assert mock_transport.last_request["autocontinue"] is False
        assert result["autocontinue"] is False

    def test_repair_queued(self, client, mock_transport):
        """Test repair with queued command."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.repair(target_id=500, queued=True)

        assert mock_transport.last_request["queued"] is True

    def test_repair_building(self, client, mock_transport):
        """Test repairing damaged building."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"target_id": 350, "autocontinue": True},
        }

        result = client.repair(target_id=350)

        assert result["target_id"] == 350

    def test_repair_siege(self, client, mock_transport):
        """Test repairing siege weapon."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.repair(target_id=600, autocontinue=False)

        assert mock_transport.last_request["target_id"] == 600


class TestHealCommand:
    """Tests for heal command."""

    def test_heal_basic(self, client, mock_transport):
        """Test basic heal."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "healer_ids": [100, 101],
                "target_id": 200,
                "queued": False,
                "note": "Healers will automatically heal target when in range",
            },
        }

        result = client.heal(target_id=200)

        assert mock_transport.last_request["action"] == "heal"
        assert mock_transport.last_request["target_id"] == 200
        assert result["healer_ids"] == [100, 101]
        assert "note" in result

    def test_heal_queued(self, client, mock_transport):
        """Test heal with queued command."""
        mock_transport.next_response = {"ok": True, "result": {"queued": True}}

        result = client.heal(target_id=300, queued=True)

        assert mock_transport.last_request["queued"] is True
        assert result["queued"] is True

    def test_heal_wounded_soldier(self, client, mock_transport):
        """Test healing wounded soldier."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"healer_ids": [150], "target_id": 250},
        }

        client.heal(target_id=250)

        assert mock_transport.last_request["target_id"] == 250


class TestReturnResourcesCommand:
    """Tests for return_resources command."""

    def test_return_resources_auto(self, client, mock_transport):
        """Test return resources to nearest dropsite."""
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entity_ids": [100, 101],
                "dropsite_id": 200,
                "queued": False,
            },
        }

        result = client.return_resources()

        assert mock_transport.last_request["action"] == "return_resources"
        assert result["dropsite_id"] == 200

    def test_return_resources_specific(self, client, mock_transport):
        """Test return resources to specific dropsite."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100], "dropsite_id": 300},
        }

        result = client.return_resources(dropsite_id=300)

        assert mock_transport.last_request["dropsite_id"] == 300
        assert result["dropsite_id"] == 300

    def test_return_resources_queued(self, client, mock_transport):
        """Test return resources with queued command."""
        mock_transport.next_response = {"ok": True, "result": {"queued": True}}

        result = client.return_resources(queued=True)

        assert mock_transport.last_request["queued"] is True

    def test_return_to_storehouse(self, client, mock_transport):
        """Test returning to storehouse."""
        mock_transport.next_response = {
            "ok": True,
            "result": {"dropsite_id": 400},
        }

        client.return_resources(dropsite_id=400)

        assert mock_transport.last_request["dropsite_id"] == 400

    def test_return_to_civic_center(self, client, mock_transport):
        """Test returning to civic center."""
        mock_transport.next_response = {"ok": True, "result": {}}

        client.return_resources(dropsite_id=250)

        assert mock_transport.last_request["action"] == "return_resources"


class TestPhase3Integration:
    """Integration tests for Phase 3 unit management."""

    def test_garrison_and_unload_workflow(self, client, mock_transport):
        """Test garrison and unload workflow."""
        # Select units
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select([100, 101, 102])

        # Garrison in building
        mock_transport.next_response = {
            "ok": True,
            "result": {"entity_ids": [100, 101, 102], "target_id": 200},
        }
        result = client.garrison(target_id=200)
        assert result["target_id"] == 200

        # Unload specific units
        mock_transport.next_response = {
            "ok": True,
            "result": {"unloaded_ids": [100, 101]},
        }
        result = client.unload(garrison_holder_id=200, entity_ids=[100, 101])
        assert len(result["unloaded_ids"]) == 2

        # Unload all remaining
        mock_transport.next_response = {"ok": True, "result": {}}
        client.unload_all(garrison_holder_id=200)

    def test_repair_workflow(self, client, mock_transport):
        """Test repair workflow."""
        # List damaged buildings
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entities": [
                    {
                        "id": 300,
                        "template": "structures/athen_house",
                        "health": {"current": 50, "max": 100, "percent": 50},
                    }
                ],
                "count": 1,
            },
        }
        buildings = client.list_entities(filter={"class": "Structure"})
        damaged = [b for b in buildings["entities"] if b.get("health", {}).get("percent", 100) < 100]

        if damaged:
            # Select workers
            mock_transport.next_response = {"ok": True, "result": {}}
            client.select([100, 101])

            # Repair damaged building
            mock_transport.next_response = {"ok": True, "result": {}}
            client.repair(target_id=damaged[0]["id"])

    def test_heal_workflow(self, client, mock_transport):
        """Test heal workflow."""
        # Find wounded soldiers
        mock_transport.next_response = {
            "ok": True,
            "result": {
                "entities": [
                    {
                        "id": 400,
                        "health": {"current": 30, "max": 100, "percent": 30},
                    }
                ],
                "count": 1,
            },
        }
        soldiers = client.list_entities(filter={"class": "Soldier"})

        # Find healers
        mock_transport.next_response = {
            "ok": True,
            "result": {"entities": [{"id": 150}], "count": 1},
        }
        healers = client.list_entities(filter={"class": "Healer"})

        if healers["entities"]:
            # Select healers
            mock_transport.next_response = {"ok": True, "result": {}}
            client.select([healers["entities"][0]["id"]])

            # Heal wounded soldier
            mock_transport.next_response = {"ok": True, "result": {}}
            client.heal(target_id=400)

    def test_gather_and_return_workflow(self, client, mock_transport):
        """Test gather and return resources workflow."""
        # Select gatherers
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select([100, 101, 102])

        # Gather resources
        mock_transport.next_response = {
            "ok": True,
            "result": {"resource": "wood.tree", "targets": [500]},
        }
        client.gather("wood.tree")

        # Return resources when full
        mock_transport.next_response = {
            "ok": True,
            "result": {"dropsite_id": 200},
        }
        client.return_resources()

        assert mock_transport.last_request["action"] == "return_resources"

    def test_defensive_garrison_workflow(self, client, mock_transport):
        """Test defensive garrison workflow."""
        # Under attack - garrison units for protection
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select([100, 101, 102, 103])  # Wounded soldiers

        # Garrison in civic center
        mock_transport.next_response = {"ok": True, "result": {}}
        client.garrison(target_id=250)  # Civic center heals garrisoned units

        # After healing, unload all
        mock_transport.next_response = {"ok": True, "result": {}}
        client.unload_all(garrison_holder_id=250)

    def test_transport_workflow(self, client, mock_transport):
        """Test transport ship workflow."""
        # Load units on ship
        mock_transport.next_response = {"ok": True, "result": {}}
        client.select([100, 101, 102])
        client.garrison(target_id=600)  # Transport ship

        # Move ship (would be done separately)
        # ...

        # Unload at destination
        mock_transport.next_response = {"ok": True, "result": {}}
        client.unload_all(garrison_holder_id=600)
