#!/usr/bin/env python3
"""
Generate JavaScript console commands for direct execution in 0 A.D.

This is the quickest way to test commands without setting up the full RPC layer.

Usage:
    python tools/console_commands.py move 186 150 200
    python tools/console_commands.py select 186 188 190

Then:
1. Launch 0 A.D. with Hannibal
2. Press F9 to open console
3. Paste the generated command
"""

import sys


def generate_move_command(entity_ids, x, z):
    """Generate console command to move entities."""
    ids_str = "[" + ", ".join(map(str, entity_ids)) + "]"
    return f"AIs.AIs[0].bot.effector.move({ids_str}, [{x}, {z}]);"


def generate_select_command(entity_ids):
    """Generate console command to set selection."""
    ids_str = "[" + ", ".join(map(str, entity_ids)) + "]"
    # This would set Hannibal's internal selection
    return f"AIs.AIs[0].bot.selection = {ids_str}; print('Selected: ' + uneval({ids_str}));"


def generate_gather_command(resource):
    """Generate console command for gathering (requires selection)."""
    return f"// Gather {resource} - requires implementing gather in RPC executor first"


def generate_chat_command(message):
    """Generate console command to send chat message."""
    return f'AIs.AIs[0].bot.effector.chat("{message}");'


def print_usage():
    print(__doc__)
    print("\nCommands:")
    print("  move <id1> [id2...] <x> <z>  - Move entities to position")
    print("  select <id1> [id2...]        - Set selection")
    print("  chat <message>               - Send chat message")
    print()
    print("Examples:")
    print("  python console_commands.py move 186 150 200")
    print("  python console_commands.py move 186 188 190 150 200")
    print("  python console_commands.py select 186 188")
    print("  python console_commands.py chat 'Hello from Python!'")


def main():
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    command = sys.argv[1]

    if command == "move":
        if len(sys.argv) < 5:
            print("Error: move requires at least entity_id, x, z")
            print("Usage: move <id1> [id2...] <x> <z>")
            sys.exit(1)

        # Last two args are x, z
        x = float(sys.argv[-2])
        z = float(sys.argv[-1])
        entity_ids = [int(arg) for arg in sys.argv[2:-2]]

        if not entity_ids:
            print("Error: need at least one entity ID")
            sys.exit(1)

        js_command = generate_move_command(entity_ids, x, z)

        print()
        print("=" * 60)
        print("CONSOLE COMMAND (Press F9 in game, then paste this):")
        print("=" * 60)
        print()
        print(js_command)
        print()
        print("=" * 60)
        print(f"This will move entities {entity_ids} to position ({x}, {z})")
        print("=" * 60)
        print()

    elif command == "select":
        if len(sys.argv) < 3:
            print("Error: select requires at least one entity ID")
            print("Usage: select <id1> [id2...]")
            sys.exit(1)

        entity_ids = [int(arg) for arg in sys.argv[2:]]

        js_command = generate_select_command(entity_ids)

        print()
        print("=" * 60)
        print("CONSOLE COMMAND (Press F9 in game, then paste this):")
        print("=" * 60)
        print()
        print(js_command)
        print()
        print("=" * 60)
        print(f"This will set selection to: {entity_ids}")
        print("=" * 60)
        print()

    elif command == "chat":
        if len(sys.argv) < 3:
            print("Error: chat requires a message")
            print("Usage: chat <message>")
            sys.exit(1)

        message = " ".join(sys.argv[2:])
        js_command = generate_chat_command(message)

        print()
        print("=" * 60)
        print("CONSOLE COMMAND (Press F9 in game, then paste this):")
        print("=" * 60)
        print()
        print(js_command)
        print()
        print("=" * 60)
        print(f"This will send chat message: {message}")
        print("=" * 60)
        print()

    else:
        print(f"Error: Unknown command '{command}'")
        print()
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
