"""Gecko's hosted MCP, spoken over plain HTTP, and its recorded twin.

The MCP session is the same four moves as project 01's curl block: `initialize`, keep the
`mcp-session-id` header, send `notifications/initialized`, then `tools/call`. The server
answers as server-sent events (`event: message` / `data: {...}`), so the reply is read
line by line.

`RecordedGecko` answers from a fixture file instead of the network. The buyer cannot tell
the two apart, which is the point: one code path, and only the transport differs.
"""

from __future__ import annotations

import copy
import json
import os
import urllib.request
from pathlib import Path
from typing import Any, Protocol

DEFAULT_URL = "https://mcp.geckovision.tech/orquestra/mcp"
PROTOCOL_VERSION = "2025-06-18"


class GeckoUnavailable(RuntimeError):
    """The MCP did not answer, or answered something that is not MCP. Not a refusal."""


class Gecko(Protocol):
    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]: ...


class HostedGecko:
    """One MCP session to the hosted Gecko, opened on the first call and reused."""

    def __init__(self, url: str | None = None, timeout: float = 60) -> None:
        self.url = url or os.environ.get("GECKO_MCP_URL", DEFAULT_URL)
        self.timeout = timeout
        self.session_id: str | None = None
        self._next_id = 1

    def _post(self, message: dict[str, Any]) -> tuple[dict[str, str], bytes]:
        headers = {
            "content-type": "application/json",
            "accept": "application/json, text/event-stream",
            "user-agent": "dev3pack-gecko-buyer",
        }
        if self.session_id:
            headers["mcp-session-id"] = self.session_id
        request = urllib.request.Request(self.url, json.dumps(message).encode(), headers)
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                return {k.lower(): v for k, v in response.headers.items()}, response.read()
        except OSError as exc:
            raise GeckoUnavailable(f"{self.url} did not answer: {exc}") from exc

    def _request(self, method: str, params: dict[str, Any]) -> dict[str, Any]:
        self._next_id += 1
        headers, body = self._post(
            {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params}
        )
        if "mcp-session-id" in headers:
            self.session_id = headers["mcp-session-id"]
        message = _read_reply(body)
        if message.get("error"):
            raise GeckoUnavailable(f"{method}: {message['error']}")
        return message["result"]

    def _handshake(self) -> None:
        self._request(
            "initialize",
            {
                "protocolVersion": PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "dev3pack-gecko-buyer", "version": "0.1.0"},
            },
        )
        if not self.session_id:
            raise GeckoUnavailable("initialize returned no mcp-session-id header")
        self._post({"jsonrpc": "2.0", "method": "notifications/initialized"})

    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        if self.session_id is None:
            self._handshake()
        result = self._request("tools/call", {"name": tool, "arguments": arguments})
        text = "".join(
            c.get("text", "") for c in result.get("content", []) if c.get("type") == "text"
        )
        try:
            answer = json.loads(text)
        except json.JSONDecodeError:
            answer = {"error": text}
        if result.get("isError") and isinstance(answer, dict):
            answer.setdefault("error", text)
        return answer


def _read_reply(body: bytes) -> dict[str, Any]:
    """A JSON-RPC reply, whether it came as plain JSON or as server-sent events."""
    text = body.decode("utf-8", errors="replace").strip()
    if text.startswith("{"):
        return json.loads(text)
    for line in text.splitlines():
        if line.startswith("data:"):
            return json.loads(line[5:].strip())
    raise GeckoUnavailable(f"the reply was neither JSON nor an event stream: {text[:200]!r}")


# --- recorded ---------------------------------------------------------------------------


class RecordedMiss(KeyError):
    """The fixture holds no recorded answer for this tool."""


class RecordedGecko:
    """Answers from a fixture: `{"calls": {"<tool>": <answer>, ...}}`.

    `verify_signed_transaction` has two recorded answers: the one for the signed bytes the
    fixture holds, and `verify_signed_transaction:other`, which is what Gecko answered when
    it was handed any other bytes (the tampered-bytes card).
    """

    def __init__(self, fixture: dict[str, Any]) -> None:
        self.fixture = fixture
        self.asked: list[tuple[str, dict[str, Any]]] = []

    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        self.asked.append((tool, copy.deepcopy(arguments)))
        calls = self.fixture.get("calls", {})
        key = tool
        if tool == "verify_signed_transaction":
            if arguments.get("transaction") != self.fixture.get("signed_transaction"):
                key = "verify_signed_transaction:other"
        if key not in calls:
            raise RecordedMiss(
                f"this fixture has no recorded answer for {key}; "
                f"it has {', '.join(sorted(calls)) or 'none'}"
            )
        return copy.deepcopy(calls[key])


class RecordingGecko:
    """Wraps a live Gecko and keeps every answer, so a real run can become a fixture."""

    def __init__(self, inner: Gecko) -> None:
        self.inner = inner
        self.calls: dict[str, Any] = {}

    def call(self, tool: str, arguments: dict[str, Any]) -> dict[str, Any]:
        answer = self.inner.call(tool, arguments)
        key = tool
        if tool == "verify_signed_transaction" and tool in self.calls:
            key = "verify_signed_transaction:other"
        self.calls[key] = copy.deepcopy(answer)
        return answer


def load_fixture(path: Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))
