"""The two checks that ship written. Read these before you write the other five."""

from __future__ import annotations

import dataclasses

from conftest import fixture

from buyer.check import check_program, check_store
from buyer.intent import IntentRecord
from buyer.prepared import Prepared


def espresso() -> tuple[IntentRecord, Prepared]:
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
        network=ctx["network"],
        store_authority="Dt8quRFWgTMrrDgVa4GGFRJWksncskbs1tpYAQHkEPwJ",
        menu_price_raw=1_000_000,
    )
    return intent, Prepared.from_answer(case["calls"]["prepare_purchase"])


def test_program_agrees_on_the_real_purchase() -> None:
    intent, prepared = espresso()
    assert check_program(intent, prepared).ok


def test_program_refuses_a_lookalike_program() -> None:
    intent, prepared = espresso()
    swapped = dataclasses.replace(prepared, program="Lookalike1111111111111111111111111111111111")
    result = check_program(intent, swapped)
    assert not result.ok and result.field == "program"
    assert result.found == "Lookalike1111111111111111111111111111111111"


def test_program_refuses_an_extra_program_riding_along() -> None:
    intent, prepared = espresso()
    extra = dataclasses.replace(
        prepared, programs=(*prepared.programs, "Extra111111111111111111111111111111111111111")
    )
    assert not check_program(intent, extra).ok


def test_store_agrees_when_the_account_is_derived_from_the_pinned_name() -> None:
    intent, prepared = espresso()
    assert check_store(intent, prepared).ok


def test_store_refuses_when_the_pin_names_another_store() -> None:
    """Use case 1's refusal: the account is not the one derived from the pinned name."""
    intent, prepared = espresso()
    other = dataclasses.replace(intent, store="dev3pack-cafe2")
    result = check_store(other, prepared)
    assert not result.ok and result.field == "store"
    assert "dev3pack-cafe2" in str(result.asked) and result.found == prepared.store
