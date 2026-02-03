#!/usr/bin/env python3
"""
Combat Commands Demonstration Script

Demonstrates the new combat RPC commands for Hannibal AI:
- attack: Attack specific target
- attack_walk: Move and attack enemies
- patrol: Patrol between points
- set_stance: Set unit combat stance
- set_formation: Set unit formation
- guard: Guard another unit
- stop: Stop current action

Usage:
    1. Start 0 A.D. with Hannibal AI
    2. Run this script: python tools/combat_demo.py
    3. Follow the prompts to test each command
"""

from hannibal_api.client import HannibalClient
import time


def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_result(result):
    """Pretty print a result dictionary."""
    for key, value in result.items():
        print(f"  {key}: {value}")


def demo_basic_attack():
    """Demonstrate basic attack command."""
    print_section("Demo 1: Basic Attack Command")

    client = HannibalClient(player_id=1)

    print("\n1. Getting current state...")
    state = client.get_state()
    print_result(state)

    print("\n2. Listing military units...")
    entities = client.list_entities(filter={"class": "Soldier"})
    soldiers = entities["entities"][:5]
    print(f"  Found {len(soldiers)} soldiers")
    for s in soldiers:
        print(f"    ID {s['id']}: {s['template']}")

    if not soldiers:
        print("  ⚠ No soldiers found. Train some units first!")
        return

    soldier_ids = [s["id"] for s in soldiers]

    print(f"\n3. Selecting {len(soldier_ids)} soldiers...")
    result = client.select(soldier_ids)
    print_result(result)

    print("\n4. Setting stance to 'aggressive'...")
    result = client.set_stance("aggressive")
    print_result(result)

    print("\n5. Setting formation to 'Box'...")
    result = client.set_formation("Box")
    print_result(result)

    # Note: You would need to find an enemy entity ID to actually attack
    print("\n6. Ready to attack (target_id needed)...")
    print("  Usage: client.attack(target_id=<enemy_id>)")
    print("  ℹ Use list_entities to find enemy units")


def demo_attack_walk():
    """Demonstrate attack-walk command."""
    print_section("Demo 2: Attack-Walk Command")

    client = HannibalClient(player_id=1)

    print("\n1. Listing soldiers...")
    entities = client.list_entities(filter={"class": "Soldier"})
    soldiers = entities["entities"][:3]

    if not soldiers:
        print("  ⚠ No soldiers found. Train some units first!")
        return

    soldier_ids = [s["id"] for s in soldiers]
    print(f"  Selected {len(soldier_ids)} soldiers")

    print("\n2. Selecting soldiers...")
    client.select(soldier_ids)

    print("\n3. Attack-walk to position (300, 300)...")
    print("  Units will move to this position and attack any enemies encountered")
    result = client.attack_walk(x=300, z=300, target_classes="Unit")
    print_result(result)

    print("\n4. Attack-walk can target specific classes:")
    print("  - 'Unit' (default): Attack any enemy units")
    print("  - 'Structure': Attack buildings")
    print("  - 'Infantry': Attack infantry only")


def demo_patrol():
    """Demonstrate patrol command."""
    print_section("Demo 3: Patrol Command")

    client = HannibalClient(player_id=1)

    print("\n1. Listing soldiers for patrol duty...")
    entities = client.list_entities(filter={"class": "Soldier"})
    soldiers = entities["entities"][:4]

    if not soldiers:
        print("  ⚠ No soldiers found. Train some units first!")
        return

    soldier_ids = [s["id"] for s in soldiers]

    print("\n2. Selecting patrol group...")
    client.select(soldier_ids)

    print("\n3. Setting defensive stance (good for patrols)...")
    client.set_stance("defensive")

    print("\n4. Setting up patrol route...")
    print("  Patrolling to position (200, 200) and back")
    result = client.patrol(x=200, z=200)
    print_result(result)

    print("\n  ℹ Units will patrol between current position and target")
    print("  ℹ They will engage enemies encountered during patrol")


def demo_stances():
    """Demonstrate different combat stances."""
    print_section("Demo 4: Combat Stances")

    client = HannibalClient(player_id=1)

    stances = [
        ("violent", "Attack anything in range, chase far"),
        ("aggressive", "Attack anything in range, chase nearby"),
        ("defensive", "Attack when attacked, chase briefly"),
        ("passive", "Never attack"),
        ("standground", "Attack in range, never move"),
    ]

    print("\nAvailable Combat Stances:\n")
    for stance, description in stances:
        print(f"  • {stance:12s}: {description}")

    print("\n1. Listing soldiers...")
    entities = client.list_entities(filter={"class": "Soldier"})
    if entities["entities"]:
        soldier_ids = [e["id"] for e in entities["entities"][:3]]

        print("\n2. Selecting soldiers...")
        client.select(soldier_ids)

        print("\n3. Testing 'aggressive' stance (recommended for offense)...")
        result = client.set_stance("aggressive")
        print_result(result)

        time.sleep(1)

        print("\n4. Testing 'defensive' stance (recommended for guards)...")
        result = client.set_stance("defensive")
        print_result(result)
    else:
        print("  ⚠ No soldiers found. Train some units first!")


def demo_formations():
    """Demonstrate different unit formations."""
    print_section("Demo 5: Unit Formations")

    formations = [
        ("Scatter", "Loose, spread out formation"),
        ("Box", "Defensive square formation"),
        ("LineClosed", "Tight line formation (good for melee)"),
        ("ColumnClosed", "Tight column for marching"),
        ("Wedge", "Wedge/triangle formation (breakthrough)"),
        ("Phalanx", "Greek phalanx formation (spears)"),
        ("Testudo", "Roman turtle formation (defense)"),
        ("BattleLine", "Standard battle line"),
    ]

    print("\nAvailable Formations:\n")
    for formation, description in formations:
        print(f"  • {formation:15s}: {description}")

    client = HannibalClient(player_id=1)

    print("\n1. Listing soldiers...")
    entities = client.list_entities(filter={"class": "Soldier"})
    if entities["entities"]:
        soldier_ids = [e["id"] for e in entities["entities"][:8]]

        print(f"\n2. Selecting {len(soldier_ids)} soldiers...")
        client.select(soldier_ids)

        print("\n3. Testing 'Phalanx' formation...")
        result = client.set_formation("Phalanx")
        print_result(result)

        time.sleep(1)

        print("\n4. Testing 'Wedge' formation...")
        result = client.set_formation("Wedge")
        print_result(result)
    else:
        print("  ⚠ No soldiers found. Train some units first!")


def demo_guard():
    """Demonstrate guard command."""
    print_section("Demo 6: Guard Command")

    client = HannibalClient(player_id=1)

    print("\n1. Listing all entities...")
    entities = client.list_entities()

    # Find soldiers and a building
    soldiers = [e for e in entities["entities"] if "infantry" in e["template"].lower()]
    buildings = [
        e for e in entities["entities"] if "civil_centre" in e["template"].lower()
    ]

    if not soldiers or not buildings:
        print("  ⚠ Need both soldiers and a civic center for this demo")
        return

    soldier_ids = [s["id"] for s in soldiers[:2]]
    building_id = buildings[0]["id"]

    print(f"\n2. Selected {len(soldier_ids)} guards")
    print(f"  Civic Center ID: {building_id}")

    client.select(soldier_ids)

    print("\n3. Setting guards to defensive stance...")
    client.set_stance("defensive")

    print("\n4. Ordering guards to protect civic center...")
    result = client.guard(target_id=building_id)
    print_result(result)

    print("\n  ℹ Guards will follow and protect the target")
    print("  ℹ They will attack enemies that threaten the target")


def demo_stop():
    """Demonstrate stop command."""
    print_section("Demo 7: Stop Command")

    client = HannibalClient(player_id=1)

    print("\n1. Listing soldiers...")
    entities = client.list_entities(filter={"class": "Soldier"})
    if not entities["entities"]:
        print("  ⚠ No soldiers found")
        return

    soldier_ids = [e["id"] for e in entities["entities"][:3]]

    print("\n2. Selecting soldiers...")
    client.select(soldier_ids)

    print("\n3. Issuing move command...")
    client.move(soldier_ids, x=400, z=400)

    print("\n4. Stopping all current actions...")
    result = client.stop()
    print_result(result)

    print("\n  ℹ Stop cancels current orders immediately")
    print("  ℹ Use queued=True to add stop to the end of the queue")


def main():
    """Run all demonstrations."""
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║         Hannibal AI - Combat Commands Demonstration         ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝

This script demonstrates the new combat RPC commands available
in the Hannibal AI system.

Prerequisites:
  • 0 A.D. must be running
  • Hannibal AI must be active (player 1)
  • You should have some military units trained

Commands demonstrated:
  1. Basic Attack - Attack specific targets
  2. Attack-Walk - Move and attack enemies
  3. Patrol - Patrol between points
  4. Combat Stances - Set unit behavior
  5. Unit Formations - Organize troops
  6. Guard - Protect a unit/building
  7. Stop - Cancel current orders
""")

    demos = [
        ("1", "Basic Attack", demo_basic_attack),
        ("2", "Attack-Walk", demo_attack_walk),
        ("3", "Patrol", demo_patrol),
        ("4", "Combat Stances", demo_stances),
        ("5", "Unit Formations", demo_formations),
        ("6", "Guard Command", demo_guard),
        ("7", "Stop Command", demo_stop),
        ("A", "Run All Demos", None),
        ("Q", "Quit", None),
    ]

    while True:
        print("\n" + "─" * 60)
        print("Select a demo to run:")
        print()
        for key, name, _ in demos:
            print(f"  [{key}] {name}")
        print()

        choice = input("Enter choice: ").strip().upper()

        if choice == "Q":
            print("\nExiting...")
            break
        elif choice == "A":
            for key, name, func in demos:
                if func:
                    try:
                        func()
                        time.sleep(2)
                    except Exception as e:
                        print(f"\n⚠ Error in {name}: {e}")
            print("\n✓ All demos completed!")
        else:
            for key, name, func in demos:
                if key == choice and func:
                    try:
                        func()
                    except Exception as e:
                        print(f"\n⚠ Error: {e}")
                    break


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInterrupted by user. Exiting...")
    except Exception as e:
        print(f"\n⚠ Fatal error: {e}")
        import traceback

        traceback.print_exc()
