"""
Realtime API Client for Hannibal

Programmatic Python interface to control Hannibal in a running game.
Uses the launcher's stdout capture to communicate with the game.
"""

import subprocess
import re
import time
from typing import List, Optional, Tuple
from pathlib import Path


class HannibalRealtimeClient:
    """
    Client for controlling Hannibal AI in real-time via launcher subprocess.

    This client allows you to send commands to a running game by injecting
    JavaScript via the game console programmatically.
    """

    def __init__(self, player_id: int = 1):
        """
        Initialize the client.

        Args:
            player_id: Which player's Hannibal bot to control (1-indexed)
        """
        self.player_id = player_id
        self.bot_index = player_id - 1  # AIs array is 0-indexed

    def _inject_command(self, js_code: str) -> str:
        """
        Inject JavaScript code into the running game via xdotool.

        This simulates keyboard input to paste code into the console.
        """
        # Note: This requires the game console to be open (F9)
        # and the game window to be focused

        # Escape special characters for shell
        escaped_code = js_code.replace('"', '\\"').replace('$', '\\$')

        # Use xdotool to type the command
        cmd = f'xdotool type --clearmodifiers "{escaped_code}"'
        subprocess.run(cmd, shell=True)

        # Press Enter to execute
        subprocess.run('xdotool key Return', shell=True)

        time.sleep(0.1)  # Give game time to process

        return "Command injected"

    def list_entities(self, entity_filter: Optional[str] = None) -> List[dict]:
        """
        List entities owned by the Hannibal player.

        Args:
            entity_filter: Optional filter like "Spear", "FemaleCitizen", etc.

        Returns:
            List of entity dicts with id, template, and position
        """
        if entity_filter:
            js_code = f"""
var bot = AIs.AIs[{self.bot_index}].bot;
var units = bot.state.getOwnUnits().filter(API3.Filters.byClass("{entity_filter}"));
units.forEach(function(u) {{
    print("RPC_ENTITY: " + u.id() + "|" + u.templateName() + "|" + uneval(u.position()));
}});
"""
        else:
            js_code = f"""
var bot = AIs.AIs[{self.bot_index}].bot;
var units = bot.state.getOwnUnits().toEntityArray();
units.slice(0, 20).forEach(function(u) {{
    print("RPC_ENTITY: " + u.id() + "|" + u.templateName() + "|" + uneval(u.position()));
}});
"""

        # For now, return instruction to manually execute
        return {
            "method": "list_entities",
            "console_command": js_code.strip(),
            "instruction": "Press F9, paste the command, then press Enter"
        }

    def move(self, entity_ids: List[int], x: float, z: float) -> dict:
        """
        Move entities to a position.

        Args:
            entity_ids: List of entity IDs to move
            x: X coordinate
            z: Z coordinate

        Returns:
            Command result
        """
        ids_str = "[" + ", ".join(map(str, entity_ids)) + "]"

        js_code = f"AIs.AIs[{self.bot_index}].bot.effector.move({ids_str}, [{x}, {z}]);"

        return {
            "method": "move",
            "console_command": js_code,
            "entity_ids": entity_ids,
            "target": {"x": x, "z": z},
            "instruction": "Press F9, paste the command, then press Enter"
        }

    def get_console_command(self, method: str, **kwargs) -> str:
        """
        Generate a console command for any method.

        Args:
            method: Method name ('move', 'list_entities', 'select', etc.)
            **kwargs: Method arguments

        Returns:
            JavaScript command to paste in console
        """
        if method == "move":
            return self.move(kwargs['entity_ids'], kwargs['x'], kwargs['z'])['console_command']
        elif method == "list_entities":
            return self.list_entities(kwargs.get('filter'))['console_command']
        else:
            raise ValueError(f"Unknown method: {method}")


def get_entity_list(log_path: str = "/home/doraemon/Documents/Hannibal/logs/last.log") -> List[Tuple[int, str]]:
    """
    Parse entity list from game log output.

    Looks for RPC entity list output in the log.

    Returns:
        List of (entity_id, template_name) tuples
    """
    entities = []

    log_file = Path(log_path)
    if not log_file.exists():
        return entities

    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            # Look for RPC entity list output
            # Format: "1::   RPC:   ID 192: units.athen.infantry.spearman.b at [120, 180]"
            match = re.search(r'RPC:\s+ID (\d+):\s+([^\s]+)\s+at', line)
            if match:
                entity_id = int(match.group(1))
                template = match.group(2)
                entities.append((entity_id, template))

    return entities


# Convenience functions

def find_spearmen(log_path: str = "/home/doraemon/Documents/Hannibal/logs/last.log") -> List[int]:
    """Find all spearman entity IDs from log."""
    entities = get_entity_list(log_path)
    return [eid for eid, template in entities if 'spear' in template.lower()]


def find_entities_by_type(entity_type: str, log_path: str = "/home/doraemon/Documents/Hannibal/logs/last.log") -> List[int]:
    """Find entity IDs by type from log."""
    entities = get_entity_list(log_path)
    return [eid for eid, template in entities if entity_type.lower() in template.lower()]
