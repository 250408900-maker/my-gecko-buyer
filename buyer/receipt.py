"""The one receipt that says what moved, read from the ledger, never from a tool's answer.

Two reads of the same things, one before signing and one after the submit confirmed:
the store's `total_purchases`, the buyer's token balance, and the store's token balance.
The receipt is the difference, compared with what was pinned.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from .chain import explorer
from .intent import IntentRecord
from .ledger import Chain
from .prepared import Prepared


@dataclass(frozen=True)
class Snapshot:
    total_purchases: int
    last_receipt_id: int | None
    buyer_raw: int
    store_raw: int
    read_at: str


def read_snapshot(chain: Chain, intent: IntentRecord, prepared: Prepared) -> Snapshot:
    store = chain.store(intent.store)
    if store is None:
        raise LookupError(f"store {intent.store} has no account on {chain.cluster}")
    return Snapshot(
        total_purchases=store.total_purchases,
        last_receipt_id=store.sales[-1].receipt_id if store.sales else None,
        buyer_raw=chain.token_balance(prepared.buyer, prepared.mint),
        store_raw=chain.token_balance(prepared.authority, prepared.mint),
        read_at=datetime.now(UTC).isoformat(),
    )


@dataclass
class Receipt:
    ask: str
    network: str
    store: str
    product: str
    signature: str
    explorer: str
    slot: int | None
    price_raw: int | None
    mint: str
    buyer: str
    buyer_delta_raw: int
    store_delta_raw: int
    total_purchases_before: int
    total_purchases_after: int
    intent_pinned_at: str
    source: str
    reconciled: bool = False
    findings: list[str] = field(default_factory=list)


def reconcile(
    intent: IntentRecord,
    prepared: Prepared,
    before: Snapshot,
    after: Snapshot,
    submitted: dict[str, Any],
    source: str,
) -> Receipt:
    signature = str(submitted.get("signature", ""))
    receipt = Receipt(
        ask=intent.ask,
        network=intent.network,
        store=intent.store,
        product=prepared.product,
        signature=signature,
        explorer=explorer(signature, intent.network),
        slot=submitted.get("slot"),
        price_raw=prepared.price_raw,
        mint=prepared.mint,
        buyer=prepared.buyer,
        buyer_delta_raw=after.buyer_raw - before.buyer_raw,
        store_delta_raw=after.store_raw - before.store_raw,
        total_purchases_before=before.total_purchases,
        total_purchases_after=after.total_purchases,
        intent_pinned_at=intent.pinned_at,
        source=source,
    )
    price = prepared.price_raw
    if price is None:
        receipt.findings.append("the simulation reported no amount, so there is nothing to match")
    else:
        if receipt.buyer_delta_raw != -price:
            receipt.findings.append(f"buyer moved {receipt.buyer_delta_raw}, expected -{price}")
        if receipt.store_delta_raw != price:
            receipt.findings.append(f"store moved {receipt.store_delta_raw}, expected +{price}")
    step = after.total_purchases - before.total_purchases
    if step != 1:
        # A busy class store can take another sale in between: said, never hidden.
        receipt.findings.append(
            f"total_purchases went {before.total_purchases} to {after.total_purchases}, "
            "not n to n+1"
        )
    receipt.reconciled = not receipt.findings
    return receipt


def write(receipt: Receipt, directory: Path) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    stem = receipt.signature[:8] or "unsigned"
    path = directory / f"{stem}.json"
    path.write_text(json.dumps(asdict(receipt), indent=2) + "\n", encoding="utf-8")
    (directory / f"{stem}.md").write_text(render(receipt), encoding="utf-8")
    return path


def render(receipt: Receipt) -> str:
    verdict = "reconciled with the ledger" if receipt.reconciled else "NOT reconciled"
    lines = [
        f"# Receipt {receipt.signature[:8]}",
        "",
        f"**{receipt.ask}**, from `{receipt.store}` on {receipt.network}: {verdict}.",
        "",
        f"- signature: `{receipt.signature}`",
        f"- explorer: {receipt.explorer}",
        f"- slot: {receipt.slot}",
        f"- product: {receipt.product}",
        f"- price_raw: {receipt.price_raw} of mint `{receipt.mint}`",
        f"- buyer delta: {receipt.buyer_delta_raw}",
        f"- store delta: {receipt.store_delta_raw:+d}",
        f"- total_purchases: {receipt.total_purchases_before} to {receipt.total_purchases_after}",
        f"- intent pinned at: {receipt.intent_pinned_at}",
        f"- source: {receipt.source}",
    ]
    lines += [f"- finding: {f}" for f in receipt.findings]
    return "\n".join(lines) + "\n"
