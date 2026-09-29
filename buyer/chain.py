"""Solana JSON-RPC over stdlib, and the one question asked before any signature: which chain?

A cluster is identified by its genesis hash, never by its URL. A URL can say "devnet" and
point anywhere; the genesis hash is what the node itself answers.
"""

from __future__ import annotations

import base64
import json
import time
import urllib.request
from typing import Any

from solders.pubkey import Pubkey

DEVNET_RPC = "https://api.devnet.solana.com"
DEVNET_GENESIS = "EtWTRABZaYq6iMfeYKouRu166VU2xqa1wcaWoxPkrZBG"
MAINNET_GENESIS = "5eykt4UsFv8P8NJdTREpY1vzqKqZKvdpKuc147dw2N9d"
GENESIS = {"devnet": DEVNET_GENESIS, "mainnet": MAINNET_GENESIS}


class ChainError(RuntimeError):
    """The node answered with an error, or did not answer in time."""


class WrongCluster(RuntimeError):
    """The RPC's genesis hash is not the cluster this step is allowed to touch."""


def rpc(url: str, method: str, params: list[Any] | None = None, timeout: float = 30) -> Any:
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or []})
    request = urllib.request.Request(
        url,
        body.encode(),
        {"content-type": "application/json", "user-agent": "dev3pack-gecko-buyer"},
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        out = json.loads(response.read())
    if out.get("error"):
        raise ChainError(f"{method}: {out['error']}")
    return out["result"]


def assert_cluster(url: str, cluster: str) -> str:
    """Refuse unless the node at `url` answers with `cluster`'s genesis hash."""
    expected = GENESIS[cluster]
    actual = rpc(url, "getGenesisHash")
    if actual != expected:
        raise WrongCluster(
            f"refusing: the RPC at {url} has genesis {actual}, and {cluster} is {expected}"
        )
    return actual


def block_height(url: str) -> int:
    return int(rpc(url, "getBlockHeight", [{"commitment": "confirmed"}]))


def latest_blockhash(url: str) -> str:
    return rpc(url, "getLatestBlockhash", [{"commitment": "confirmed"}])["value"]["blockhash"]


def lamports(url: str, address: Pubkey | str) -> int:
    return int(rpc(url, "getBalance", [str(address), {"commitment": "confirmed"}])["value"])


def account_data(url: str, address: Pubkey | str) -> bytes | None:
    value = rpc(
        url, "getAccountInfo", [str(address), {"encoding": "base64", "commitment": "confirmed"}]
    )["value"]
    return None if value is None else base64.b64decode(value["data"][0])


def token_balance_raw(url: str, token_account: Pubkey | str) -> int:
    """A token account's balance in the smallest unit; 0 when the account does not exist."""
    try:
        value = rpc(
            url, "getTokenAccountBalance", [str(token_account), {"commitment": "confirmed"}]
        )
    except ChainError as exc:
        if "could not find account" in str(exc).lower() or "invalid param" in str(exc).lower():
            return 0
        raise
    return int(value["value"]["amount"])


def send_and_confirm(url: str, signed: bytes, cluster: str, wait_s: float = 60) -> str:
    """Send signed bytes to `cluster` and wait for `confirmed`. Asserts the cluster first."""
    assert_cluster(url, cluster)
    signature = rpc(
        url,
        "sendTransaction",
        [
            base64.b64encode(signed).decode(),
            {"encoding": "base64", "preflightCommitment": "confirmed"},
        ],
    )
    return confirm(url, signature, wait_s)


def confirm(url: str, signature: str, wait_s: float = 60) -> str:
    deadline = time.monotonic() + wait_s
    while time.monotonic() < deadline:
        status = rpc(url, "getSignatureStatuses", [[signature], {"searchTransactionHistory": True}])
        entry = status["value"][0]
        if entry and entry.get("confirmationStatus") in ("confirmed", "finalized"):
            if entry.get("err"):
                raise ChainError(f"landed with an error {entry['err']}: {signature}")
            return signature
        time.sleep(1)
    raise ChainError(f"not confirmed after {wait_s:.0f}s: {signature}")


def explorer(signature_or_address: str, cluster: str = "devnet", kind: str = "tx") -> str:
    suffix = "" if cluster == "mainnet" else f"?cluster={cluster}"
    return f"https://explorer.solana.com/{kind}/{signature_or_address}{suffix}"
