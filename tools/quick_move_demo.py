#!/usr/bin/env python3
"""
Quick demonstration of using the Python API to move units.

This shows how to use the programmatic API without manual console typing.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hannibal_api.realtime_client import HannibalRealtimeClient

print("=" * 70)
print("Hannibal Realtime Python API - Move Spearman Demo")
print("=" * 70)
print()

# Create API client for player 1
client = HannibalRealtimeClient(player_id=1)

print("The API lets you generate commands programmatically in Python:")
print()

# Example: Find spearmen
print("1. List spearmen:")
list_cmd = client.list_entities("Spear")
print(f"   Python: client.list_entities('Spear')")
print()
print(f"   Generated JS:")
print(f"   {list_cmd['console_command']}")
print()

# Example: Move a spearman
entity_id = 192  # You'll get this from the entity list
x, z = 150.0, 200.0

print(f"2. Move spearman ID {entity_id} to ({x}, {z}):")
print(f"   Python: client.move([{entity_id}], {x}, {z})")
print()

move_cmd = client.move([entity_id], x, z)
print(f"   Generated JS:")
print(f"   {move_cmd['console_command']}")
print()

# Example: Move multiple units
print("3. Move multiple units:")
entity_ids = [192, 195, 198]
print(f"   Python: client.move({entity_ids}, {x}, {z})")
print()

move_cmd_multi = client.move(entity_ids, x, z)
print(f"   Generated JS:")
print(f"   {move_cmd_multi['console_command']}")
print()

print("=" * 70)
print("How to Use")
print("=" * 70)
print()
print("STEP 1: Run launcher.py and wait for game to start")
print("STEP 2: Entity IDs will appear in output at tick 5 like:")
print("        1::   RPC:   ID 192: units.cart.infantry.spearman.b at [120, 180]")
print()
print("STEP 3: Use Python API to generate console commands:")
print("        client = HannibalRealtimeClient(player_id=1)")
print("        cmd = client.move([192], 150.0, 200.0)")
print("        print(cmd['console_command'])")
print()
print("STEP 4: Press F9 in game, paste the generated command, press Enter")
print()
print("=" * 70)
print("You write PYTHON, not JavaScript!")
print("=" * 70)
