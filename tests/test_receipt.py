"""The receipt is two ledger reads and their difference, never the submit response."""

from __future__ import annotations

import dataclasses

from conftest import fixture

from buyer.intent import IntentRecord
from buyer.ledger import RecordedChain
from buyer.prepared import Prepared
from buyer.receipt import read_snapshot, reconcile, render


def setup() -> tuple[IntentRecord, Prepared, dict]:
    case = fixture("cases/1-espresso")
    ctx = case["context"]
    intent = IntentRecord(
        ask=case["ask"],
        store=ctx["store"],
        product="Espresso",
        quantity=1,
        budget_raw=ctx["budget_raw"],
        mint=ctx["pay_mint"],
        buyer=ctx["buyer"],
        network="devnet",
        store_authority="Dt8quRFWgTMrrDgVa4GGFRJWksncskbs1tpYAQHkEPwJ",
        menu_price_raw=1_000_000,
    )
    return intent, Prepared.from_answer(case["calls"]["prepare_purchase"]), case


def test_the_recorded_landing_reconciles() -> None:
    intent, prepared, case = setup()
    chain = RecordedChain(case["ledger"])
    before = read_snapshot(chain, intent, prepared)
    after = read_snapshot(chain, intent, prepared)
    receipt = reconcile(
        intent, prepared, before, after, case["calls"]["submit_transaction"], "recorded"
    )
    assert receipt.reconciled, receipt.findings
    assert receipt.buyer_delta_raw == -1_000_000 and receipt.store_delta_raw == 1_000_000
    assert receipt.total_purchases_after == receipt.total_purchases_before + 1
    assert "cluster=devnet" in receipt.explorer
    assert receipt.signature in render(receipt)


def test_a_delta_that_does_not_match_the_price_is_a_finding() -> None:
    intent, prepared, case = setup()
    chain = RecordedChain(case["ledger"])
    before = read_snapshot(chain, intent, prepared)
    after = dataclasses.replace(
        read_snapshot(chain, intent, prepared), buyer_raw=before.buyer_raw - 2_000_000
    )
    receipt = reconcile(
        intent, prepared, before, after, case["calls"]["submit_transaction"], "recorded"
    )
    assert not receipt.reconciled
    assert any("buyer moved -2000000" in f for f in receipt.findings)
