#!/usr/bin/env python3
"""
Simple script to move a spearman unit in a running Hannibal game.

This is a proof-of-concept for the realtime API using file-based transport.
The game must be running with Hannibal AI enabled.

Usage:
    python tools/move_spearman.py <entity_id> <x> <z>

Example:
    python tools/move_spearman.py 186 150.5 200.0
"""

import json
import sys
import time
from pathlib import Path
from uuid import uuid4


def get_command_file():
    """Get the path to the command file that Hannibal will read."""
    # Using the export folder configured in launcher.py
    export_dir = Path("/home/doraemon/Documents/Hannibal/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir / "realtime_commands.json"


def get_response_file():
    """Get the path to the response file that Hannibal will write."""
    export_dir = Path("/home/doraemon/Documents/Hannibal/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir / "realtime_responses.json"


def send_move_command(entity_id, x, z):
    """
    Send a move command to the running game.

    Args:
        entity_id: The ID of the entity to move (e.g., 186)
        x: X coordinate on the map
        z: Z coordinate on the map
    """
    correlation_id = str(uuid4())

    command = {
        "correlation_id": correlation_id,
        "action": "move",
        "entity_ids": [entity_id],
        "position": {"x": float(x), "z": float(z)}
    }

    command_file = get_command_file()

    # Read existing commands if any
    commands = []
    if command_file.exists():
        try:
            with open(command_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    commands = data
        except (json.JSONDecodeError, IOError):
            pass

    # Append new command
    commands.append(command)

    # Write commands
    with open(command_file, 'w') as f:
        json.dump(commands, f, indent=2)

    print(f"✓ Sent move command:")
    print(f"  Entity ID: {entity_id}")
    print(f"  Position: ({x}, {z})")
    print(f"  Correlation ID: {correlation_id}")
    print(f"  Command file: {command_file}")
    print()
    print("Waiting for response...")

    # Wait for response (with timeout)
    response_file = get_response_file()
    timeout = 10  # seconds
    start_time = time.time()

    while time.time() - start_time < timeout:
        if response_file.exists():
            try:
                with open(response_file, 'r') as f:
                    responses = json.load(f)

                # Look for our response
                for resp in responses:
                    if resp.get("correlation_id") == correlation_id:
                        print(f"✓ Received response:")
                        print(f"  OK: {resp.get('ok')}")
                        if resp.get('ok'):
                            print(f"  Result: {resp.get('result')}")
                        else:
                            print(f"  Error: {resp.get('error')}")
                        return
            except (json.JSONDecodeError, IOError):
                pass

        time.sleep(0.5)

    print("⚠ Timeout waiting for response")
    print()
    print("NOTE: Make sure the Hannibal RPC executor is loaded in the game!")
    print("You need to add the executor module to Hannibal's update loop.")


def list_entities():
    """List entities - helpful for finding spearman IDs."""
    correlation_id = str(uuid4())

    command = {
        "correlation_id": correlation_id,
        "action": "list_entities",
        "filter": {"class": "Infantry"}  # Filter for infantry units
    }

    command_file = get_command_file()

    commands = []
    if command_file.exists():
        try:
            with open(command_file, 'r') as f:
                data = json.load(f)
                if isinstance(data, list):
                    commands = data
        except (json.JSONDecodeError, IOError):
            pass

    commands.append(command)

    with open(command_file, 'w') as f:
        json.dump(commands, f, indent=2)

    print(f"✓ Sent list_entities command")
    print(f"  Filter: Infantry units")
    print(f"  Correlation ID: {correlation_id}")
    print()
    print("Check the response file for entity IDs:")
    print(f"  {get_response_file()}")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        print("\nTip: First find entity IDs by checking game logs or exports.")
        print("     Look for lines like '1::INFO  : entity 186 is a spearman'")
        sys.exit(1)

    if sys.argv[1] == "list":
        list_entities()
        return

    if len(sys.argv) != 4:
        print("Error: Expected 3 arguments: <entity_id> <x> <z>")
        print()
        print(__doc__)
        sys.exit(1)

    try:
        entity_id = int(sys.argv[1])
        x = float(sys.argv[2])
        z = float(sys.argv[3])
    except ValueError:
        print("Error: Arguments must be numbers")
        print("  entity_id: integer")
        print("  x, z: floats")
        sys.exit(1)

    send_move_command(entity_id, x, z)


if __name__ == "__main__":
    main()
