# -*- coding: utf-8 -*-
"""麦当劳 MCP 客户端（零第三方依赖，仅用 Python 标准库）

协议：MCP over Streamable HTTP（https://mcp.mcd.cn）
- 每个请求独立 POST，无需维护会话（服务端为无状态设计，实测无 session id）
- 响应可能是纯 JSON，也可能是 SSE（text/event-stream），两种都兼容
- 工具返回值优先取 structuredContent.data，取不到再解析 content 里的文本 JSON
"""

import json
import os
import urllib.error
import urllib.request

MCP_URL = "https://mcp.mcd.cn"
PROTOCOL_VERSION = "2025-03-26"


def _parse_response(body):
    """解析 MCP 响应体：纯 JSON 或 SSE 两种格式。"""
    text = body.strip()
    if text.startswith("{"):
        return json.loads(text)
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[len("data:"):].strip())
    raise RuntimeError("无法解析 MCP 响应：" + text[:200])


class McpKeHu(object):
    """麦当劳 MCP 客户端。

    token 可直接传入，或读环境变量 MCD_MCP_TOKEN（也可由本地 .env 提供）。
    """

    def __init__(self, token=None, url=MCP_URL):
        self.url = url
        self.token = token or os.environ.get("MCD_MCP_TOKEN", "")
        self._seq = 0

    @property
    def available(self):
        """是否配置了 Token。"""
        return bool(self.token)

    # ---------- 底层 RPC ----------
    def _rpc(self, method, params=None, notification=False):
        if not self.available:
            raise RuntimeError("未配置 MCP Token：请设置环境变量 MCD_MCP_TOKEN")
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        if not notification:
            self._seq += 1
            payload["id"] = self._seq
        request = urllib.request.Request(
            self.url,
            data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self.token,
                "Content-Type": "application/json",
                "Accept": "application/json, text/event-stream",
            },
            method="POST",
        )
        try:
            with urllib.request.urlopen(request, timeout=30) as resp:
                body = resp.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "ignore")[:200]
            raise RuntimeError("MCP HTTP %s：%s" % (exc.code, detail))
        except urllib.error.URLError as exc:
            raise RuntimeError("MCP 网络错误：%s" % exc.reason)
        if notification:
            return None
        return _parse_response(body)

    # ---------- 高层封装 ----------
    def handshake(self):
        """initialize 握手，返回服务端信息（如 {'name': 'mcd-mcp', 'version': '1.0.0'}）。"""
        resp = self._rpc("initialize", {
            "protocolVersion": PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "mcd-almanac", "version": "1.0.0"},
        })
        self._rpc("notifications/initialized", {}, notification=True)
        return resp.get("result", {}).get("serverInfo", {})

    def list_tools(self):
        """拉取工具清单。"""
        resp = self._rpc("tools/list", {})
        return resp.get("result", {}).get("tools", [])

    def call_tool(self, name, arguments=None):
        """调用工具，返回结构化数据（dict 或 list）。

        优先取 structuredContent.data；退化到解析 content 文本块里的 JSON。
        """
        resp = self._rpc("tools/call", {"name": name, "arguments": arguments or {}})
        result = resp.get("result", {})
        if result.get("isError"):
            raise RuntimeError("MCP 工具调用失败：" + name)
        structured = result.get("structuredContent")
        if isinstance(structured, dict) and "data" in structured:
            return structured["data"]
        if structured is not None:
            return structured
        for block in result.get("content", []):
            if isinstance(block, dict) and block.get("type") == "text":
                try:
                    return json.loads(block["text"])
                except ValueError:
                    continue
        return result
