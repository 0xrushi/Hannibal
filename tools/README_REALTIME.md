# Realtime API - Programmatic Control

Control Hannibal AI in a running 0 A.D. game using **Python code**, not manual console commands.

## What This Is

A **Python API** for controlling game units programmatically:

```python
from hannibal_api.realtime_client import HannibalRealtimeClient

client = HannibalRealtimeClient(player_id=1)

# Move spearman ID 192 to position (150, 200)
client.move([192], 150.0, 200.0)

# List all spearmen
client.list_entities("Spear")
```

The API generates JavaScript commands that execute in the game. You write Python, not JavaScript.

---

## Quick Start - Move a Spearman via API

### 1. Setup (One-time)

The RPC executor is now integrated into Hannibal. Files updated:
- `source/simulation/ai/hannibal/bot.js` - Added RPC import
- `source/simulation/ai/hannibal/rpc.js` - RPC executor
- `mods/hannibal/simulation/ai/hannibal/` - Deployed files

### 2. Launch Game

```bash
python launcher.py
```

Wait for the game to start. On tick 5, the RPC executor will print entity lists:

```
1::   RPC:   ID 192: units.cart.infantry.spearman.b at [120, 180]
1::   RPC:   ID 195: units.cart.support.female.citizen at [125, 175]
```

### 3. Use Python API

```python
from hannibal_api.realtime_client import HannibalRealtimeClient

# Create API client
client = HannibalRealtimeClient(player_id=1)

# Generate move command for spearman ID 192
move_cmd = client.move([192], 150.0, 200.0)

# Get the console command
print(move_cmd['console_command'])
# Output: AIs.AIs[0].bot.effector.move([192], [150, 200]);
```

### 4. Execute Command

The API generates JavaScript. To execute it:

**Current approach:**
- Press F9 in game
- Paste the generated command
- Press Enter

**Future:** Automated injection via launcher integration (in progress).

---

## Python API Reference

### `HannibalRealtimeClient(player_id)`

Create a client for controlling a specific player's Hannibal bot.

```python
client = HannibalRealtimeClient(player_id=1)
```

### `client.move(entity_ids, x, z)`

Generate command to move entities.

```python
# Move single unit
client.move([192], 150.0, 200.0)

# Move multiple units
client.move([192, 195, 198], 150.0, 200.0)
```

Returns:
```python
{
    'method': 'move',
    'console_command': 'AIs.AIs[0].bot.effector.move([192], [150, 200]);',
    'entity_ids': [192],
    'target': {'x': 150.0, 'z': 200.0},
    'instruction': 'Press F9, paste the command, then press Enter'
}
```

### `client.list_entities(filter=None)`

Generate command to list entities.

```python
# List all units
client.list_entities()

# List spearmen only
client.list_entities("Spear")

# List female citizens
client.list_entities("FemaleCitizen")
```

### Helper Functions

```python
from hannibal_api.realtime_client import find_spearmen, get_entity_list

# Get all entities from log
entities = get_entity_list()  # [(id, template), ...]

# Find spearman IDs
spearman_ids = find_spearmen()  # [192, 195, ...]
```

---

## Complete Example

```python
#!/usr/bin/env python3
from hannibal_api.realtime_client import HannibalRealtimeClient, find_spearmen

def move_all_spearmen():
    # Create client
    client = HannibalRealtimeClient(player_id=1)

    # Find spearmen from game log
    spearmen = find_spearmen()

    if not spearmen:
        print("No spearmen found. Run game first and check logs.")
        return

    print(f"Found {len(spearmen)} spearmen: {spearmen}")

    # Generate move commands
    for spear_id in spearmen:
        cmd = client.move([spear_id], 150.0, 200.0)
        print(f"To move spearman {spear_id}:")
        print(f"  {cmd['console_command']}")
        print()

if __name__ == "__main__":
    move_all_spearmen()
```

Run it:
```bash
python tools/api_demo.py
```

---

## Files

**Python API:**
- `hannibal_api/realtime_client.py` - Main API client
- `hannibal_api/models_realtime.py` - Pydantic models
- `tools/api_demo.py` - Full working example
- `tools/move_spearman.py` - Simple move script
- `tools/find_entities.py` - Entity discovery helper

**JavaScript (Game Side):**
- `source/simulation/ai/hannibal/rpc.js` - RPC executor
- `source/simulation/ai/hannibal/bot.js` - Bot integration
- `mods/hannibal/simulation/ai/hannibal/` - Deployed files

---

## How It Works

```
┌─────────────┐
│ Python API  │  You write Python code
└──────┬──────┘
       │
       │ generates
       ▼
┌─────────────────────┐
│ JavaScript Commands │  AIs.AIs[0].bot.effector.move([192], [150, 200]);
└──────┬──────────────┘
       │
       │ execute in
       ▼
┌─────────────┐
│ 0 A.D. Game │  Units move on screen
└─────────────┘
```

You use **Python** to generate **JavaScript** that controls the **game**.

No manual typing in console - the API does it for you.

---

## Next Steps

**Current Implementation:**
1. ✅ Python API generates JavaScript commands
2. ✅ RPC executor integrated into Hannibal
3. ✅ Entity listing on game start (tick 5)
4. ⚠️  Manual execution (copy-paste to console)

**Future Improvements:**
1. Automatic command injection (no manual paste)
2. Two-way communication (read responses back to Python)
3. WebSocket transport for real-time control
4. Full HuggingFace Agents integration

---

## Troubleshooting

**"No entities found in log"**
- Game needs to run for at least 5 ticks
- Check `logs/last.log` for RPC output
- Enable chat debug: set `"cht": 1` in launcher.py

**"Bot not found at AIs.AIs[0]"**
- You might be player 2: use `player_id=2`
- Check game setup in launcher.py

**"RPC executor not initialized"**
- Make sure you copied the updated files to mods/
- Restart the game after file changes

---

## Difference from Manual Console

**Manual (old way):**
1. Press F9
2. Type: `AIs.AIs[0].bot.effector.move([192], [150, 200]);`
3. Press Enter

**API (new way):**
```python
client = HannibalRealtimeClient(player_id=1)
client.move([192], 150.0, 200.0)
```

The API **generates** the JavaScript for you. You write Python, not JavaScript.

(Execution still requires F9 + paste, but this will be automated next)
