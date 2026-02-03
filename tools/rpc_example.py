#!/usr/bin/env python3
"""
Simple example of using Hannibal RPC with file-based transport.

Usage:
    1. Run this script to generate commands
    2. In game console (F9), execute: AIs.AIs[0].bot.rpc.executeFromFile()
    3. Script will wait for response and display result
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hannibal_api.client import HannibalClient


def main():
    print("=" * 70)
    print("Hannibal RPC Example")
    print("=" * 70)
    print()

    # Create client
    client = HannibalClient(player_id=1, timeout=10.0)

    # Clear any old files
    print("Clearing old files...")
    client.clear_stale_files()
    print()

    # Example 1: Get state
    print("Example 1: Get Player State")
    print("-" * 70)
    print("Command sent to file. Now execute in game console (F9):")
    print("  AIs.AIs[0].bot.rpc.executeFromFile()")
    print()

    try:
        state = client.get_state()
        print("✓ Success!")
        print(f"  Player ID: {state['player_id']}")
        print(f"  Resources: {state['resources']}")
        print(f"  Population: {state['population']}/{state['population_cap']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()
        return 1

    # Example 2: List entities
    print("Example 2: List Entities")
    print("-" * 70)
    print("Command sent. Execute in console:")
    print("  AIs.AIs[0].bot.rpc.executeFromFile()")
    print()

    try:
        entities = client.list_entities()
        print("✓ Success!")
        print(f"  Found {entities['count']} entities:")
        for ent in entities['entities'][:5]:
            print(f"    - ID {ent['id']}: {ent['template']}")
        print()
    except Exception as e:
        print(f"✗ Error: {e}")
        print()

    # Example 3: Select entities
    if entities['count'] > 0:
        entity_ids = [e['id'] for e in entities['entities'][:2]]

        print(f"Example 3: Select Entities {entity_ids}")
        print("-" * 70)
        print("Command sent. Execute in console:")
        print("  AIs.AIs[0].bot.rpc.executeFromFile()")
        print()

        try:
            result = client.select(entity_ids)
            print("✓ Success!")
            print(f"  Selected: {result['selected_ids']}")
            print()
        except Exception as e:
            print(f"✗ Error: {e}")
            print()

    print("=" * 70)
    print("Examples complete!")
    print()
    print("You can continue using the client to send more commands.")
    print("Just remember to execute executeFromFile() in the console after each one.")
    print("=" * 70)

    return 0


if __name__ == "__main__":
    sys.exit(main())
