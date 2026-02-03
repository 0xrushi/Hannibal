# Hannibal RPC Usage Guide

Control Hannibal AI using Python client APIs with file-based command transport.

## Quick Start

### 1. Python Client API

Use the Python client to send commands:

```python
from hannibal_api.client import HannibalClient

# Create client
client = HannibalClient(player_id=1, timeout=5.0)

# Send a command (writes to file)
client.select([186, 188])
```

### 2. Execute in Game

In the game console (F9), execute:

```javascript
AIs.AIs[0].bot.rpc.executeFromFile()
```

This reads the command file, executes it, and writes the response.

### 3. Read Response

The Python client automatically reads the response:

```python
# The select() call above already returned the response
result = client.select([186, 188])
print(result)  # {'selected_ids': [186, 188]}
```

## Workflow

```
Python Client
    ↓ writes command.json
~/.config/0ad/config/hannibal_rpc_command.json
    ↓ manually trigger in console
Game: AIs.AIs[0].bot.rpc.executeFromFile()
    ↓ reads, executes, writes
~/.config/0ad/config/hannibal_rpc_response.json
    ↓ Python reads response
Python Client returns result
```

## Available Commands

### Select Entities

```python
result = client.select([186, 188, 190])
# Returns: {'selected_ids': [186, 188]}
```

### Move Entities

```python
result = client.move([186, 188], x=150, z=200)
# Returns: {'moved_ids': [186, 188], 'position': {'x': 150, 'z': 200}}
```

### Gather Resources

```python
# Select workers first
client.select([186, 188])

# Then gather
result = client.gather("wood.tree")
# Returns: {'entity_ids': [186, 188], 'resource': 'wood.tree', 'targets': [...]}
```

Resource types: `wood.tree`, `food.fruit`, `food.grain`, `stone.rock`, `metal.ore`

### Build Structures

```python
# Using selected builders
client.select([186, 188])
result = client.build("house", mode="selected")

# Or let economy manage it
result = client.build("barracks", amount=2, mode="economy")
```

### Train Units

```python
result = client.train("female.citizen", amount=3)
# Returns: {'unit': 'female.citizen', 'queued': 3}
```

### Research Technology

```python
result = client.research("phase_town")
# Returns: {'tech': 'phase_town', 'queued': True}
```

### Get Player State

```python
state = client.get_state()
print(state)
# {
#   'player_id': 1,
#   'resources': {'food': 300, 'wood': 200, 'stone': 100, 'metal': 50},
#   'population': 25,
#   'population_cap': 50,
#   'phase': 'village',
#   'current_selection': [186, 188]
# }
```

### List Entities

```python
# List all entities
entities = client.list_entities()
print(f"Found {entities['count']} entities")

# Filter by class
workers = client.list_entities(filter={"class": "Worker"})
```

## Direct Console Usage

You can also call RPC methods directly in the console without Python:

```javascript
var rpc = AIs.AIs[0].bot.rpc;

// Move entities
rpc.move([186, 188], 150, 200);

// Select
rpc.select([186, 188]);

// Gather
rpc.gather("wood.tree");

// Build
rpc.build("house", 1, "selected");

// Train
rpc.train("female.citizen", 3);

// Get state
rpc.getState();
```

## TypeScript Version

The RPC module is also available in TypeScript with full type definitions:

- Location: `ts/source/simulation/ai/hannibal/rpc.ts`
- Includes type definitions for all commands, results, and game entities
- Compile with: `npx tsc -p tsconfig.ai.json`

## Error Handling

Commands return `{ok: true, result: {...}}` on success or `{ok: false, error: "..."}` on failure.

Python client raises `RuntimeError` on command failure:

```python
try:
    client.gather("wood.tree")
except RuntimeError as e:
    print(f"Command failed: {e}")
```

## File Locations

- Command file: `~/.config/0ad/config/hannibal_rpc_command.json`
- Response file: `~/.config/0ad/config/hannibal_rpc_response.json`

## Automation

To automate command execution without manual console input, you could:

1. Create a mod that polls for commands periodically
2. Use game events to trigger command checks
3. Hook into Hannibal's tick loop (add polling back if needed)

For now, manual execution via `executeFromFile()` keeps the system simple and transparent.
