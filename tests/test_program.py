"""The program, from its IDL: addresses, instruction bytes, and what the prepared bytes say."""

from __future__ import annotations

import dataclasses

import pytest
from conftest import fixture

from buyer import letmebuy
from buyer.prepared import GeckoRefused, Prepared

CAFE = "AzJW94Hpu8wnNpQ9DyCvyann24tmdDKhfdKn9GxFYX5f"
CLASS_MINT = "Eoqdd43nFQ9HzGq8HjBRVLCV6aTqCFRiwHy1ZVQheYSi"


def test_the_store_address_is_derived_from_its_name() -> None:
    assert str(letmebuy.store_address("dev3pack-cafe")) == CAFE
    assert str(letmebuy.store_address("dev3pack-caf")) != CAFE


def test_initialize_is_encoded_from_the_idl() -> None:
    owner = letmebuy.program_id()  # any address will do for the encoding
    ix = letmebuy.build_instruction(
        "initialize",
        {"receipts": letmebuy.store_address("dev3x"), "authority": owner},
        {"store_name": "dev3x"},
    )
    spec = letmebuy.instruction_spec("initialize")
    assert bytes(ix.data) == bytes(spec["discriminator"]) + (5).to_bytes(4, "little") + b"dev3x"
    assert ix.accounts[1].is_signer and ix.accounts[1].is_writable
    assert str(ix.accounts[2].pubkey) == "11111111111111111111111111111111"


def test_a_float_price_is_refused() -> None:
    owner = letmebuy.program_id()
    with pytest.raises(letmebuy.ProgramError, match="whole number"):
        letmebuy.build_instruction(
            "add_product",
            {"receipts": owner, "authority": owner, "mint": owner},
            {"store_name": "dev3x", "name": "Espresso", "price": 1.5},
        )


def test_the_prepared_purchase_is_read_from_the_bytes() -> None:
    prepared = Prepared.from_answer(fixture("cases/1-espresso")["calls"]["prepare_purchase"])
    assert prepared.program == str(letmebuy.program_id())
    assert prepared.programs == (str(letmebuy.program_id()),)
    assert prepared.store == CAFE
    assert prepared.product == "Espresso"
    assert prepared.quantity == 1
    assert prepared.price_raw == 1_000_000
    assert prepared.mint == CLASS_MINT
    assert prepared.network == "devnet"


def test_the_lookalike_mint_is_visible_in_the_bytes() -> None:
    prepared = Prepared.from_answer(fixture("cases/3-module")["calls"]["prepare_purchase"])
    assert prepared.mint != CLASS_MINT


def test_a_gecko_refusal_is_raised_with_its_code() -> None:
    with pytest.raises(GeckoRefused) as caught:
        Prepared.from_answer(fixture("refusals/product-unknown")["answer"])
    assert caught.value.code == "product-unknown"


def test_prepared_is_immutable() -> None:
    prepared = Prepared.from_answer(fixture("cases/1-espresso")["calls"]["prepare_purchase"])
    with pytest.raises(dataclasses.FrozenInstanceError):
        prepared.quantity = 2  # type: ignore[misc]
