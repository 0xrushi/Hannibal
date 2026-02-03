#!/usr/bin/env python3
"""
Demo script showing how to issue realtime commands to Hannibal.

This demonstrates the Python API for controlling Hannibal in a running game.

SETUP REQUIRED:
1. The RPC executor must be loaded in Hannibal (rpc-executor.js)
2. Add to bot.js update loop: if (this.rpc) this.rpc.update();
3. Enable file I/O in launcher.py: set "fil": 1 for the bot

For now, this is a demonstration of the API structure.
"""

import json
from pathlib import Path
from uuid import uuid4


def create_move_command(entity_ids, x, z):
    """Create a move command."""
    return {
        "correlation_id": str(uuid4()),
        "action": "move",
        "entity_ids": entity_ids,
        "position": {"x": float(x), "z": float(z)}
    }


def create_select_command(entity_ids):
    """Create a select command."""
    return {
        "correlation_id": str(uuid4()),
        "action": "select",
        "entity_ids": entity_ids
    }


def create_gather_command(resource, targets=None, near="selection"):
    """Create a gather command."""
    cmd = {
        "correlation_id": str(uuid4()),
        "action": "gather",
        "resource": resource,
        "near": near
    }
    if targets:
        cmd["targets"] = targets
    return cmd


def create_build_command(what, amount=1, mode="selected"):
    """Create a build command."""
    return {
        "correlation_id": str(uuid4()),
        "action": "build",
        "what": what,
        "amount": amount,
        "mode": mode
    }


def demo_scenario():
    """
    Demo scenario:
    1. Select 2 villagers
    2. Send them to gather wood
    3. Build a house with selected builders
    4. Train more villagers
    """

    commands = []

    print("Creating demo command sequence...")
    print()

    # 1. Select villagers (you'd get these IDs from game state)
    print("1. Select entities 186, 188")
    commands.append(create_select_command([186, 188]))

    # 2. Order them to gather wood
    print("2. Gather wood")
    commands.append(create_gather_command("wood.tree", targets=3))

    # 3. Build a house using selected builders
    print("3. Build house")
    commands.append(create_build_command("house", amount=1))

    # 4. Move a spearman to position (150, 200)
    print("4. Move spearman (ID 250) to position (150, 200)")
    commands.append(create_move_command([250], 150.0, 200.0))

    print()
    print("Generated commands:")
    print(json.dumps(commands, indent=2))

    # Write to file
    export_dir = Path("/home/doraemon/Documents/Hannibal/exports")
    export_dir.mkdir(parents=True, exist_ok=True)
    command_file = export_dir / "realtime_commands.json"

    with open(command_file, 'w') as f:
        json.dump(commands, f, indent=2)

    print()
    print(f"✓ Commands written to: {command_file}")
    print()
    print("To execute these commands:")
    print("1. Make sure Hannibal bot has RPC executor loaded")
    print("2. Make sure 'fil' debug option is enabled")
    print("3. The bot will poll this file and execute commands")
    print()
    print("Check responses in:")
    print(f"  {export_dir / 'realtime_responses.json'}")


if __name__ == "__main__":
    demo_scenario()
