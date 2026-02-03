#!/usr/bin/env python3
"""
Integration test for Hannibal Realtime API.

This script demonstrates the complete file-based transport workflow:
1. List entities to find workers
2. Select specific workers
3. Order them to gather wood
4. Build a house using selected workers
5. Train a new villager

Prerequisites:
- 0 A.D. must be running with Hannibal as an AI player
- The game must be in progress (not paused)

Usage:
    python tools/integration_realtime_api.py
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from hannibal_api.client import HannibalClient


def main():
    """Run the integration test."""
    print("=" * 70)
    print("Hannibal Realtime API - Integration Test")
    print("=" * 70)
    print()

    # Initialize client
    client = HannibalClient(player_id=1, timeout=10.0)

    # Clear any stale files from previous runs
    print("1. Clearing stale files...")
    client.clear_stale_files()
    time.sleep(0.5)

    # Step 1: Get current state
    print("\n2. Getting player state...")
    try:
        state = client.get_state()
        print(f"   Player ID: {state['player_id']}")
        print(f"   Resources: {state['resources']}")
        print(f"   Population: {state['population']}/{state['population_cap']}")
        print(f"   Phase: {state['phase']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        print("\n   Make sure:")
        print("   - 0 A.D. is running with Hannibal as player 1")
        print("   - The game is in progress (not paused)")
        print("   - Hannibal RPC polling is enabled (check logs)")
        return 1

    # Step 2: List entities to find workers
    print("\n3. Listing all entities...")
    try:
        entities_result = client.list_entities()
        entities = entities_result["entities"]
        print(f"   Found {len(entities)} entities")

        # Find workers (female citizens)
        workers = [
            e for e in entities
            if "female" in e["template"].lower() or "citizen" in e["template"].lower()
        ]

        if not workers:
            print("   WARNING: No workers found, using first 2 entities")
            workers = entities[:2]

        if len(workers) < 2:
            print("   ERROR: Need at least 2 entities to test")
            return 1

        print(f"   Found {len(workers)} workers:")
        for w in workers[:5]:
            print(f"     - ID {w['id']}: {w['template']} at {w['position']}")

    except Exception as e:
        print(f"   ERROR: {e}")
        return 1

    # Step 3: Select 2 workers
    print("\n4. Selecting 2 workers...")
    worker_ids = [w["id"] for w in workers[:2]]
    try:
        select_result = client.select(worker_ids)
        print(f"   Selected: {select_result['selected_ids']}")
    except Exception as e:
        print(f"   ERROR: {e}")
        return 1

    # Step 4: Order them to gather wood
    print("\n5. Ordering workers to gather wood...")
    try:
        gather_result = client.gather("wood.tree")
        print(f"   Gathering: {gather_result}")
    except Exception as e:
        print(f"   WARNING: {e}")
        print("   (This might fail if no wood is nearby)")

    # Step 5: Build a house (selected mode)
    print("\n6. Building a house with selected workers...")
    try:
        build_result = client.build("house", amount=1, mode="selected")
        print(f"   Build result: {build_result}")
        if build_result.get("fallback_triggered"):
            print("   (Used economy mode fallback)")
    except Exception as e:
        print(f"   WARNING: {e}")

    # Step 6: Train a villager (economy mode)
    print("\n7. Training a villager...")
    try:
        train_result = client.train("female.citizen", amount=1)
        print(f"   Train result: {train_result}")
    except Exception as e:
        print(f"   WARNING: {e}")

    # Final state check
    print("\n8. Checking final state...")
    try:
        final_state = client.get_state()
        print(f"   Resources: {final_state['resources']}")
        print(f"   Population: {final_state['population']}/{final_state['population_cap']}")
    except Exception as e:
        print(f"   ERROR: {e}")

    print("\n" + "=" * 70)
    print("Integration test completed!")
    print("=" * 70)
    print("\nCheck the game to verify:")
    print("  - Workers moved to gather wood")
    print("  - A house is being built")
    print("  - A villager is being trained")

    return 0


if __name__ == "__main__":
    sys.exit(main())
