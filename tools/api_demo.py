#!/usr/bin/env python3
"""
Demonstration of the Hannibal Realtime API (Programmatic Usage)

This script shows how to use the Python API to control units in a running game.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hannibal_api.realtime_client import HannibalRealtimeClient, find_spearmen, get_entity_list


def main():
    print("=" * 70)
    print("Hannibal Realtime API Demo")
    print("=" * 70)
    print()

    # Create client for player 1
    client = HannibalRealtimeClient(player_id=1)

    print("Step 1: Launch the game")
    print("-" * 70)
    print("Run: python launcher.py")
    print("Wait for the game to start...")
    print()

    print("Step 2: Get entity IDs from the game")
    print("-" * 70)
    print("The RPC executor will output entity lists on tick 5.")
    print("Check the launcher output for lines like:")
    print("  1::   RPC:   ID 192: units.cart.infantry.spearman.b at [120, 180]")
    print()
    print("Or, use the API to generate a list command:")
    list_cmd = client.list_entities("Spear")
    print(f"Console command: {list_cmd['console_command']}")
    print()

    print("Step 3: Move a spearman")
    print("-" * 70)
    print("Once you have an entity ID (e.g., 192), use the API:")
    print()
    print("Python code:")
    print("  client = HannibalRealtimeClient(player_id=1)")
    print("  move_cmd = client.move([192], 150.0, 200.0)")
    print("  print(move_cmd['console_command'])")
    print()

    # Demo: Generate move command for a hypothetical spearman
    entity_id = 192  # Example ID
    move_cmd = client.move([entity_id], 150.0, 200.0)

    print("Generated console command:")
    print(f"  {move_cmd['console_command']}")
    print()

    print("Step 4: Execute in game")
    print("-" * 70)
    print("Method 1 - Manual:")
    print("  1. Press F9 in the game")
    print("  2. Paste the console command")
    print("  3. Press Enter")
    print()
    print("Method 2 - Parse from logs:")
    print("  After game runs for a few ticks:")
    entities = get_entity_list()
    if entities:
        print(f"  Found {len(entities)} entities in log")
        spearmen_ids = find_spearmen()
        if spearmen_ids:
            print(f"  Spearmen IDs: {spearmen_ids}")
            print()
            print("  Now you can move them:")
            for sid in spearmen_ids[:1]:  # Move first spearman
                cmd = client.move([sid], 150.0, 200.0)
                print(f"    {cmd['console_command']}")
    else:
        print("  No entities found in log yet - game needs to run first")
    print()

    print("=" * 70)
    print("Full Example")
    print("=" * 70)
    print("""
from hannibal_api.realtime_client import HannibalRealtimeClient

# Create client
client = HannibalRealtimeClient(player_id=1)

# Generate command to move spearman ID 192 to position (150, 200)
move_cmd = client.move([192], 150.0, 200.0)

# Print the console command
print(move_cmd['console_command'])

# Output:
# AIs.AIs[0].bot.effector.move([192], [150, 200]);

# Then press F9 in game and paste this command!
""")


if __name__ == "__main__":
    main()
