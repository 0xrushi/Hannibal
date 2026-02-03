import unittest
from unittest.mock import Mock

from hannibal_api.console_inject import (
    build_set_rpc_command_js,
    inject_into_0ad_console,
)
from hannibal_api.parsing import parse_entity_ids


class TestConsoleInject(unittest.TestCase):
    def test_parse_entity_ids_single(self):
        self.assertEqual(parse_entity_ids("186"), [186])

    def test_parse_entity_ids_csv(self):
        self.assertEqual(parse_entity_ids("186, 187,188"), [186, 187, 188])

    def test_parse_entity_ids_rejects_empty(self):
        with self.assertRaises(ValueError):
            parse_entity_ids("")

    def test_parse_entity_ids_rejects_non_numeric(self):
        with self.assertRaises(ValueError):
            parse_entity_ids("186,abc")

    def test_build_set_rpc_command_js_is_single_line(self):
        js = build_set_rpc_command_js(
            {"action": "move", "entity_ids": [1], "x": 10, "z": 20}
        )
        self.assertNotIn("\n", js)
        self.assertTrue(js.startswith("HANNIBAL_DEBUG.rpc_command ="))
        self.assertTrue(js.endswith(";"))

    def test_inject_into_0ad_console_calls_xdotool(self):
        runner = Mock()
        inject_into_0ad_console("HANNIBAL_DEBUG.rpc_command = {};", runner=runner)
        calls = [c.args[0] for c in runner.call_args_list]
        self.assertGreaterEqual(len(calls), 4)
        self.assertEqual(calls[0][0], "xdotool")
        self.assertEqual(calls[-1][0], "xdotool")


if __name__ == "__main__":
    unittest.main()
