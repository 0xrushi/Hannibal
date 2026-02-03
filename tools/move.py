#!/usr/bin/env python3
"""
Simple command-line tool to generate move commands.

Usage:
    python tools/move.py 192 150 200
    python tools/move.py 192,195,198 150 200
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from hannibal_api.realtime_client import HannibalRealtimeClient


def main():
    if len(sys.argv) < 4:
        print("Usage: python tools/move.py <entity_ids> <x> <z>")
        print()
        print("Examples:")
        print("  python tools/move.py 192 150 200")
        print("  python tools/move.py 192,195,198 150 200")
        print()
        print("This generates the JavaScript command to paste in game (F9)")
        sys.exit(1)

    # Parse entity IDs (can be comma-separated)
    entity_ids_str = sys.argv[1]
    if ',' in entity_ids_str:
        entity_ids = [int(x.strip()) for x in entity_ids_str.split(',')]
    else:
        entity_ids = [int(entity_ids_str)]

    x = float(sys.argv[2])
    z = float(sys.argv[3])

    # Create client
    client = HannibalRealtimeClient(player_id=1)

    # Generate move command
    move_cmd = client.move(entity_ids, x, z)

    print()
    print("=" * 70)
    print(f"Moving units {entity_ids} to position ({x}, {z})")
    print("=" * 70)
    print()
    print("Press F9 in game, then paste this command:")
    print()
    print(move_cmd['console_command'])
    print()
    print("=" * 70)


if __name__ == "__main__":
    main()
