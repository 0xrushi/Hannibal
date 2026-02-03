#!/usr/bin/env python3
"""
Find entities from the game log and generate move commands.

This script parses the Hannibal log file to find living entities
and helps you generate console commands to move them.

Usage:
    python tools/find_entities.py [entity_type]

Examples:
    python tools/find_entities.py spearman
    python tools/find_entities.py female
    python tools/find_entities.py all
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def parse_log_file(log_path):
    """
    Parse the log file to track entities.

    Returns:
        dict: {entity_id: entity_name} for living entities
    """
    entities = {}  # entity_id -> name
    destroyed = set()  # entity_ids that were destroyed

    log_file = Path(log_path)
    if not log_file.exists():
        print(f"Error: Log file not found: {log_path}")
        return {}

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Look for entity destruction events
            # Pattern: "PDC: removed id: 188, name: units.athen.infantry.spearman.b"
            destroy_match = re.search(r'PDC: removed id: (\d+), name: (.+)', line)
            if destroy_match:
                entity_id = int(destroy_match.group(1))
                destroyed.add(entity_id)
                continue

            # Look for destroy events (alternative pattern)
            # Pattern: "EVT: Destroy fired: ({player:1, name:"Destroy", id:188,"
            destroy_evt_match = re.search(r'Destroy.*id:(\d+)', line)
            if destroy_evt_match:
                entity_id = int(destroy_evt_match.group(1))
                destroyed.add(entity_id)
                continue

            # Look for entity mentions (various patterns)
            # You might need to add more patterns based on your logs
            # For now, we'll collect from destruction events

    # Get entities by checking initial state or exports
    # Since we only see destroyed entities in the log above,
    # let's recommend checking the exports or using the console

    return entities, destroyed


def get_entity_list_from_exports(export_dir):
    """Try to get entity list from export files if available."""
    export_path = Path(export_dir)
    if not export_path.exists():
        return {}

    # Look for any JSON export files
    entity_files = list(export_path.glob("*.export"))

    # This would need to be implemented based on export format
    return {}


def suggest_console_commands(entity_type="all"):
    """Suggest console commands to list and move entities."""

    print("=" * 70)
    print("CONSOLE COMMANDS TO FIND AND MOVE ENTITIES")
    print("=" * 70)
    print()
    print("Step 1: Find entities - Press F9 in game and paste this:")
    print("-" * 70)

    if entity_type == "spearman" or entity_type == "spear":
        print("""
// Find all spearmen owned by player 1
var bot = AIs.AIs[0].bot;
var units = bot.state.getOwnUnits().filter(API3.Filters.byClass("Spear"));
units.forEach(function(u) {
    print("Spearman ID: " + u.id() + " at position " + uneval(u.position()));
});
""")
    elif entity_type == "female" or entity_type == "citizen":
        print("""
// Find all female citizens owned by player 1
var bot = AIs.AIs[0].bot;
var units = bot.state.getOwnUnits().filter(API3.Filters.byClass("FemaleCitizen"));
units.forEach(function(u) {
    print("Female Citizen ID: " + u.id() + " at position " + uneval(u.position()));
});
""")
    else:  # all
        print("""
// Find all units owned by player 1
var bot = AIs.AIs[0].bot;
var units = bot.state.getOwnUnits().toEntityArray();
print("Total units: " + units.length);
units.slice(0, 20).forEach(function(u) {
    print("Entity " + u.id() + ": " + u.templateName() + " at " + uneval(u.position()));
});
""")

    print("-" * 70)
    print()
    print("Step 2: Move an entity - Once you have an ID, use:")
    print("-" * 70)
    print("""
// Replace 186 with your entity ID, and [150, 200] with target position
AIs.AIs[0].bot.effector.move([186], [150, 200]);
""")
    print("-" * 70)
    print()
    print("Step 3: Alternative - Use the helper script:")
    print("-" * 70)
    print("  ./tools/console_commands.py move <entity_id> <x> <z>")
    print()
    print("  Example:")
    print("  ./tools/console_commands.py move 186 150 200")
    print("-" * 70)
    print()


def main():
    entity_type = "all"
    if len(sys.argv) > 1:
        entity_type = sys.argv[1].lower()

    log_path = "/home/doraemon/Documents/Hannibal/logs/last.log"

    print()
    print("Searching for entities in game logs...")
    print(f"Log file: {log_path}")
    print()

    entities, destroyed = parse_log_file(log_path)

    if destroyed:
        print(f"Found {len(destroyed)} destroyed entities in the log:")
        for eid in sorted(destroyed):
            print(f"  - Entity {eid} (destroyed)")
        print()
        print("Note: These entities are no longer alive and cannot be moved.")
        print()

    if not entities:
        print("No living entities found in log (this is normal).")
        print()
        print("To find living entities, you need to query the running game.")
        print()

    suggest_console_commands(entity_type)


if __name__ == "__main__":
    main()
