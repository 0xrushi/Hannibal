import json
import tempfile
import unittest
from pathlib import Path

from hannibal_api.command_file import write_command_file


class TestCommandFile(unittest.TestCase):
    def test_write_command_file_creates_parent(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "nested" / "hannibal_rpc_command.json"
            cmd = {
                "id": "x",
                "action": "move",
                "entity_ids": [1],
                "x": 1,
                "z": 2,
                "player_id": 1,
            }
            out = write_command_file(cmd, path=p)
            self.assertEqual(out, p)
            data = json.loads(p.read_text(encoding="utf-8"))
            self.assertEqual(data["action"], "move")


if __name__ == "__main__":
    unittest.main()
