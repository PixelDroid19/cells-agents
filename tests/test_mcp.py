import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from cells_agent.mcp import serve
from memory_stub import make_backend


class MCPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="cells mcp ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "project"
        self.root.mkdir()
        self.store = Path(self.tmp.name) / "store"
        backend = make_backend(Path(self.tmp.name))
        env = patch.dict("os.environ", {"CELLS_MEMORY_COMMAND": str(backend)})
        env.start()
        self.addCleanup(env.stop)

    def exchange(self, calls, write=False):
        requests = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25", "capabilities": {}, "clientInfo": {"name": "test", "version": "1"}}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"}] + calls
        output = io.StringIO()
        serve(str(self.root), None, self.store, memory_write=write, stdin=io.StringIO("\n".join(map(json.dumps, requests)) + "\n"), stdout=output)
        return [json.loads(line) for line in output.getvalue().splitlines()]

    def call(self, name, args=None, id=2):
        return {"jsonrpc": "2.0", "id": id, "method": "tools/call", "params": {"name": name, "arguments": args or {}}}

    def test_readonly_tool_list_and_project_do_not_create_store(self):
        result = self.exchange([{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}, self.call("cells_project", id=3)])
        names = [tool["name"] for tool in result[1]["result"]["tools"]]
        self.assertNotIn("cells_memory_save", names)
        self.assertEqual(result[0]["result"]["protocolVersion"], "2025-11-25")
        self.assertFalse(self.store.exists())

    def test_memory_save_and_get_roundtrip(self):
        saved = self.exchange([self.call("cells_memory_save", {"title": "Scope", "content": "Project scoped memory"})], write=True)
        record = json.loads(saved[1]["result"]["content"][0]["text"])
        found = self.exchange([self.call("cells_memory_get", {"id": record["id"]})])
        self.assertFalse(found[1]["result"]["isError"])
        self.assertEqual(json.loads(found[1]["result"]["content"][0]["text"])["content"], "Project scoped memory")

    def test_write_tool_disabled_and_unknown_arguments_rejected(self):
        values = self.exchange([self.call("cells_memory_save", {"title": "x", "content": "x"}), self.call("cells_project", {"root": "/"}, id=3)])
        self.assertEqual(values[1]["error"]["code"], -32602)
        self.assertEqual(values[2]["error"]["code"], -32602)
        self.assertFalse(self.store.exists())

    def test_invalid_typed_arguments_do_not_execute(self):
        for args in ({"catalog": "docs", "query": "x", "detail": "false"}, {"catalog": "docs", "query": "x", "limit": True}):
            self.assertEqual(self.exchange([self.call("cells_search", args)])[1]["error"]["code"], -32602)

    def test_bad_json_does_not_kill_server(self):
        output = io.StringIO()
        serve(str(self.root), None, self.store, stdin=io.StringIO('!\n{"jsonrpc":"2.0","method":"ping","id":7}\n'), stdout=output)
        values = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertEqual(values[0]["error"]["code"], -32700)
        self.assertEqual(values[1]["id"], 7)

    def test_nonfinite_json_id_does_not_escape_to_protocol(self):
        for invalid in ("NaN", "Infinity", "1e999"):
            output = io.StringIO()
            serve(str(self.root), None, self.store, stdin=io.StringIO('{"jsonrpc":"2.0","method":"ping","id":' + invalid + '}\n'), stdout=output)
            value = json.loads(output.getvalue())
            self.assertIsNone(value["id"])
            self.assertIn("error", value)

    def test_notifications_cannot_write_memory(self):
        call = self.call("cells_memory_save", {"title": "x", "content": "x"})
        del call["id"]
        self.exchange([call], write=True)
        self.assertFalse(self.store.exists())

    def test_deep_json_does_not_close_the_mcp_session(self):
        nested = "[" * 1600 + "0" + "]" * 1600
        attack = '{"jsonrpc":"2.0","id":2,"method":"ping","params":{"source":' + nested + '}}\n'
        ping = '{"jsonrpc":"2.0","id":3,"method":"ping"}\n'
        output = io.StringIO()
        serve(str(self.root), None, self.store, stdin=io.StringIO(attack + ping), stdout=output)
        replies = [json.loads(line) for line in output.getvalue().splitlines()]
        self.assertIn("error", replies[0])
        self.assertEqual(replies[-1], {"jsonrpc": "2.0", "id": 3, "result": {}})
