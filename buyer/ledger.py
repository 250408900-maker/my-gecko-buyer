"""What the buyer reads from the chain itself: the cluster, the block height, a store, a balance.

The receipt is built from these reads and never from what a tool said happened. Live reads
go to an RPC node. Recorded reads come from the fixture, in the order they were made.
"""

from __future__ import annotations

import time
from dataclasses import asdict
from typing import Any, Protocol

from solders.pubkey import Pubkey

from . import chain
from .letmebuy import Product, Sale, Store, decode_store, store_address, token_account


class Chain(Protocol):
    cluster: str
    rpc_url: str

    def genesis(self) -> str: ...
    def block_height(self) -> int: ...
    def store(self, name: str) -> Store | None: ...
    def token_balance(self, owner: str, mint: str) -> int: ...
    def wait_past(self, height: int) -> None: ...


class LiveChain:
    def __init__(self, cluster: str, rpc_url: str) -> None:
        self.cluster, self.rpc_url = cluster, rpc_url

    def genesis(self) -> str:
        return str(chain.rpc(self.rpc_url, "getGenesisHash"))

    def block_height(self) -> int:
        return chain.block_height(self.rpc_url)

    def store(self, name: str) -> Store | None:
        raw = chain.account_data(self.rpc_url, store_address(name))
        return None if raw is None else decode_store(raw)

    def token_balance(self, owner: str, mint: str) -> int:
        ata = token_account(Pubkey.from_string(owner), Pubkey.from_string(mint))
        return chain.token_balance_raw(self.rpc_url, ata)

    def wait_past(self, height: int) -> None:
        while self.block_height() <= height:
            time.sleep(2)


def store_to_json(store: Store) -> dict[str, Any]:
    return asdict(store)


def store_from_json(data: dict[str, Any]) -> Store:
    return Store(
        name=data["name"],
        authority=data["authority"],
        total_purchases=data["total_purchases"],
        products=[Product(**p) for p in data.get("products", [])],
        sales=[Sale(**s) for s in data.get("sales", [])],
        telegram_channel=data.get("telegram_channel", ""),
        details=data.get("details", ""),
    )


class RecordedChain:
    """Serves `ledger.reads` from a fixture: each `store()` call moves to the next read."""

    def __init__(self, ledger: dict[str, Any]) -> None:
        self.cluster = ledger.get("cluster", "devnet")
        self.rpc_url = ledger.get("rpc_url", chain.DEVNET_RPC)
        self._genesis = ledger.get("genesis", chain.DEVNET_GENESIS)
        self._height = int(ledger.get("block_height", 0))
        self._reads = ledger.get("reads", [])
        self._cursor = -1

    def genesis(self) -> str:
        return self._genesis

    def block_height(self) -> int:
        return self._height

    def store(self, name: str) -> Store | None:
        self._cursor += 1
        if self._cursor >= len(self._reads):
            raise LookupError("this fixture recorded no further ledger read")
        data = self._reads[self._cursor].get("store")
        return None if data is None else store_from_json(data)

    def token_balance(self, owner: str, mint: str) -> int:
        read = self._reads[max(self._cursor, 0)]
        return int(read.get("balances", {}).get(f"{owner}:{mint}", 0))

    def wait_past(self, height: int) -> None:
        # Recorded time does not pass by itself; the stale card moves it on.
        self._height = height + 1


class RecordingChain:
    """Wraps a live chain and keeps every read, so a real run can become a fixture."""

    def __init__(self, inner: LiveChain) -> None:
        self.inner = inner
        self.cluster, self.rpc_url = inner.cluster, inner.rpc_url
        self.reads: list[dict[str, Any]] = []
        self.first_height: int | None = None

    def genesis(self) -> str:
        return self.inner.genesis()

    def block_height(self) -> int:
        height = self.inner.block_height()
        if self.first_height is None:
            self.first_height = height
        return height

    def store(self, name: str) -> Store | None:
        found = self.inner.store(name)
        self.reads.append(
            {"store": None if found is None else store_to_json(found), "balances": {}}
        )
        return found

    def token_balance(self, owner: str, mint: str) -> int:
        value = self.inner.token_balance(owner, mint)
        if self.reads:
            self.reads[-1]["balances"][f"{owner}:{mint}"] = value
        return value

    def wait_past(self, height: int) -> None:
        self.inner.wait_past(height)

    def to_fixture(self) -> dict[str, Any]:
        return {
            "cluster": self.cluster,
            "rpc_url": self.rpc_url,
            "genesis": self.genesis(),
            "block_height": self.first_height or 0,
            "reads": self.reads,
        }
