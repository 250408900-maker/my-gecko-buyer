"""Every test here is offline. The network is blocked, so a test that reaches for it fails."""

from __future__ import annotations

import json
import socket
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
FIXTURES = ROOT / "fixtures"


@pytest.fixture(autouse=True)
def no_network(monkeypatch: pytest.MonkeyPatch) -> None:
    def blocked(*_: Any, **__: Any) -> None:
        raise OSError("tests are offline: the network is blocked")

    monkeypatch.setattr(socket.socket, "connect", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)


def fixture(name: str) -> dict[str, Any]:
    """A recorded fixture by its path under fixtures/, without .json: "cases/1-espresso"."""
    return json.loads((FIXTURES / f"{name}.json").read_text())


def case_names(group: str) -> list[str]:
    return [f"{group}/{p.stem}" for p in sorted((FIXTURES / group).glob("*.json"))]
