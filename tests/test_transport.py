"""
Unit tests for transport adapter.
"""

import json
import tempfile
import time
from pathlib import Path

import pytest

from hannibal_api.transport import FileTransport


@pytest.fixture
def temp_paths(tmp_path):
    """Create temporary paths for command and response files."""
    return {
        "command": tmp_path / "command.json",
        "response": tmp_path / "response.json",
    }


def test_send_creates_command_file(temp_paths):
    """Test that send creates a command file with correlation_id."""
    transport = FileTransport(
        command_path=temp_paths["command"],
        response_path=temp_paths["response"],
    )

    request = {"action": "move", "entity_ids": [123], "x": 100, "z": 200}
    correlation_id = transport.send(request)

    # Check that correlation_id was added
    assert correlation_id is not None
    assert "correlation_id" in request

    # Check that file was created
    assert temp_paths["command"].exists()

    # Check file contents
    written = json.loads(temp_paths["command"].read_text())
    assert written["action"] == "move"
    assert written["correlation_id"] == correlation_id


def test_send_preserves_correlation_id(temp_paths):
    """Test that send preserves provided correlation_id."""
    transport = FileTransport(
        command_path=temp_paths["command"],
        response_path=temp_paths["response"],
    )

    my_id = "test-123"
    request = {"action": "select", "entity_ids": [1, 2], "correlation_id": my_id}
    correlation_id = transport.send(request)

    assert correlation_id == my_id

    written = json.loads(temp_paths["command"].read_text())
    assert written["correlation_id"] == my_id


def test_recv_reads_matching_response(temp_paths):
    """Test that recv reads response with matching correlation_id."""
    transport = FileTransport(
        command_path=temp_paths["command"],
        response_path=temp_paths["response"],
        default_timeout=1.0,
    )

    correlation_id = "test-456"

    # Write a response file
    response = {
        "correlation_id": correlation_id,
        "ok": True,
        "result": {"selected_ids": [1, 2, 3]},
    }
    temp_paths["response"].write_text(json.dumps(response))

    # Receive it
    received = transport.recv(correlation_id)

    assert received["correlation_id"] == correlation_id
    assert received["ok"] is True
    assert received["result"]["selected_ids"] == [1, 2, 3]

    # Response file should be deleted
    assert not temp_paths["response"].exists()


def test_recv_timeout(temp_paths):
    """Test that recv raises TimeoutError if no response received."""
    transport = FileTransport(
        command_path=temp_paths["command"],
        response_path=temp_paths["response"],
        default_timeout=0.2,
    )

    with pytest.raises(TimeoutError):
        transport.recv("nonexistent-id")


def test_send_and_recv(temp_paths):
    """Test send_and_recv in a simulated scenario."""
    transport = FileTransport(
        command_path=temp_paths["command"],
        response_path=temp_paths["response"],
        default_timeout=1.0,
    )

    request = {"action": "get_state"}

    # Send in background, then simulate response
    def simulate_game_response():
        """Simulate the game writing a response."""
        time.sleep(0.1)  # Simulate processing delay

        # Read the command
        command = json.loads(temp_paths["command"].read_text())
        correlation_id = command["correlation_id"]

        # Write a response
        response = {
            "correlation_id": correlation_id,
            "ok": True,
            "result": {"player_id": 1, "resources": {"food": 300}},
        }
        temp_paths["response"].write_text(json.dumps(response))

    # Start simulation in background
    import threading

    thread = threading.Thread(target=simulate_game_response)
    thread.start()

    # Send and receive
    response = transport.send_and_recv(request)

    thread.join()

    assert response["ok"] is True
    assert response["result"]["player_id"] == 1


def test_clear_stale_files(temp_paths):
    """Test clearing stale files."""
    transport = FileTransport(
        command_path=temp_paths["command"],
        response_path=temp_paths["response"],
    )

    # Create some stale files
    temp_paths["command"].write_text('{"action": "old"}')
    temp_paths["response"].write_text('{"ok": false}')

    assert temp_paths["command"].exists()
    assert temp_paths["response"].exists()

    # Clear them
    transport.clear_stale_files()

    assert not temp_paths["command"].exists()
    assert not temp_paths["response"].exists()
