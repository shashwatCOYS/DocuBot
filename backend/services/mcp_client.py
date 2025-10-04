"""Lightweight MCP Gateway client wrapper.

This module provides a minimal HTTP/WebSocket-agnostic wrapper to call tools
exposed via the Docker MCP Gateway. The exact gateway deployment and tool names
are configured via environment variables in `config.Settings`.

If the gateway is not enabled/configured, this client should not be used.
"""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

import httpx


class MCPClientError(Exception):
    pass


class MCPClient:
    """Minimal client for invoking MCP tools via an HTTP endpoint.

    Notes:
        - This assumes the Docker MCP Gateway exposes an HTTP endpoint for tool
          invocation. If your gateway is WS-only, front it with an HTTP bridge
          or adapt this client accordingly.
        - Safe fallback behavior: on any error, callers can catch and fallback.
    """

    def __init__(self, base_url: str, api_key: Optional[str] = None, timeout_s: float = 30.0):
        if not base_url:
            raise MCPClientError("MCP base_url is required")
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Invoke a tool by name with the given arguments.

        Expected generic contract (may vary by gateway):
            POST {base_url}/tools/call
            {
              "tool": "exa.search",  # or your configured tool name
              "arguments": { ... }
            }

        Returns the parsed JSON response.
        """
        if not tool_name:
            raise MCPClientError("tool_name is required")

        headers: Dict[str, str] = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        payload = {"tool": tool_name, "arguments": arguments}

        async with httpx.AsyncClient(timeout=self.timeout_s, follow_redirects=True) as client:
            resp = await client.post(
                f"{self.base_url}/tools/call",
                headers=headers,
                content=json.dumps(payload),
            )
            resp.raise_for_status()
            return resp.json()


