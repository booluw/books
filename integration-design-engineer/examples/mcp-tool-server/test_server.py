import json
import threading
import unittest
import urllib.error
import urllib.request

import server


class ToolServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.httpd = server.make_server(port=0)
        cls.port = cls.httpd.server_address[1]
        threading.Thread(target=cls.httpd.serve_forever, daemon=True).start()

    @classmethod
    def tearDownClass(cls):
        cls.httpd.shutdown()

    def setUp(self):
        server.RETURNS.clear()
        server.AUDIT_LOG.clear()
        server._calls.clear()

    def rpc(self, method, params=None, token="token-alice", rpc_id=1):
        body = json.dumps({"jsonrpc": "2.0", "id": rpc_id, "method": method, "params": params or {}}).encode()
        request = urllib.request.Request(f"http://127.0.0.1:{self.port}/mcp", data=body, method="POST",
                                         headers={"Authorization": f"Bearer {token}",
                                                  "Content-Type": "application/json"})
        with urllib.request.urlopen(request) as response:
            return json.loads(response.read())

    def call(self, name, arguments, token="token-alice"):
        return self.rpc("tools/call", {"name": name, "arguments": arguments}, token)["result"]

    def test_unauthenticated_request_is_rejected(self):
        with self.assertRaises(urllib.error.HTTPError) as ctx:
            self.rpc("tools/list", token="nope")
        self.assertEqual(ctx.exception.code, 401)

    def test_tools_list_has_schemas_and_descriptions(self):
        tools = self.rpc("tools/list")["result"]["tools"]
        self.assertEqual({t["name"] for t in tools}, {"get_order_status", "list_recent_orders", "start_return"})
        for tool in tools:
            self.assertGreater(len(tool["description"]), 40)
            self.assertEqual(tool["inputSchema"]["type"], "object")

    def test_status_of_own_order(self):
        result = self.call("get_order_status", {"order_id": "ORD-10001"})
        self.assertFalse(result["isError"])
        self.assertEqual(result["structuredContent"]["tracking_number"], "JD014600006281234567")

    def test_cannot_read_another_customers_order(self):
        # Even if a prompt-injected agent asks for Bob's order, Alice's token cannot read it.
        result = self.call("get_order_status", {"order_id": "ORD-20001"})
        self.assertTrue(result["isError"])
        self.assertIn("No order ORD-20001 found", result["structuredContent"]["error"])

    def test_instructive_error_for_bad_id(self):
        result = self.call("get_order_status", {"order_id": "10001"})
        self.assertTrue(result["isError"])
        self.assertIn("ORD-10001", result["structuredContent"]["error"])

    def test_list_is_scoped_and_ordered(self):
        orders = self.call("list_recent_orders", {})["structuredContent"]["orders"]
        self.assertEqual([o["order_id"] for o in orders], ["ORD-10002", "ORD-10001"])

    def test_start_return_is_idempotent(self):
        args = {"order_id": "ORD-10001", "sku": "TSHIRT-M", "reason": "wrong_size"}
        first = self.call("start_return", args)["structuredContent"]
        retry = self.call("start_return", args)["structuredContent"]
        self.assertEqual(first["return_id"], retry["return_id"])
        self.assertTrue(first["newly_created"])
        self.assertFalse(retry["newly_created"])
        self.assertEqual(len(server.RETURNS), 1)

    def test_business_rule_enforced(self):
        result = self.call("start_return", {"order_id": "ORD-10002", "sku": "CAP-01", "reason": "other"})
        self.assertTrue(result["isError"])
        self.assertIn("once it has shipped", result["structuredContent"]["error"])

    def test_every_call_is_audited_without_free_text(self):
        self.call("start_return", {"order_id": "ORD-10001", "sku": "TSHIRT-M", "reason": "damaged"})
        entry = server.AUDIT_LOG[-1]
        self.assertEqual((entry["user"], entry["tool"]), ("cus_alice", "start_return"))
        self.assertNotIn("reason", entry["args"])

    def test_rate_limit(self):
        for _ in range(server.RATE_LIMIT_PER_MINUTE):
            self.assertFalse(self.call("list_recent_orders", {})["isError"])
        self.assertTrue(self.call("list_recent_orders", {})["isError"])

    def test_unknown_method(self):
        self.assertEqual(self.rpc("resources/list")["error"]["code"], -32601)


if __name__ == "__main__":
    unittest.main()
