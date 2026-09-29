"""What `prepare_purchase` actually prepared, read from the unsigned bytes.

Gecko's answer carries labels (`accounts`, `args`, `effects`). The bytes are what gets
signed. So every field the check compares is read from the transaction itself: the
program each instruction calls, the accounts in the order the IDL declares them, the
product name inside the instruction data, and how many purchases the bytes contain.
The one number the bytes cannot carry is the price (the program reads it from the store
account), so `price_raw` comes from the simulation's `effects` for the buyer.
"""

from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any

from solders.transaction import Transaction, VersionedTransaction

from . import letmebuy


class GeckoRefused(Exception):
    """Gecko itself refused to prepare: a refusal is an answer, read `code` and `reason`."""

    def __init__(self, answer: dict[str, Any]) -> None:
        self.answer = answer
        self.code = str(answer.get("code") or "error")
        self.reason = str(answer.get("reason") or answer.get("error") or "no reason given")
        super().__init__(f"{self.code}: {self.reason}")


@dataclass(frozen=True)
class Prepared:
    program: str
    #: every program the bytes call besides compute budget and the token plumbing
    programs: tuple[str, ...]
    store: str
    buyer: str
    authority: str
    mint: str
    source: str
    destination: str
    store_name: str
    product: str
    quantity: int
    price_raw: int | None
    network: str
    status: str
    binding: str
    binding_strength: str
    last_valid_block_height: int
    blocks_remaining: int | None
    unsigned_transaction: str

    @classmethod
    def from_answer(cls, answer: dict[str, Any]) -> Prepared:
        if answer.get("refused") or "transaction" not in answer:
            raise GeckoRefused(answer)
        unsigned = answer["transaction"]["unsigned_transaction"]
        message = _message(base64.b64decode(unsigned))
        keys = [str(k) for k in message.account_keys]
        purchases = []
        called = []
        for ix in message.instructions:
            program = keys[ix.program_id_index]
            called.append(program)
            try:
                # Matched by discriminator, whatever program it is sent to: a purchase
                # aimed at a lookalike program must still be read, so the check can say so.
                args = letmebuy.decode_purchase_args(bytes(ix.data))
            except letmebuy.ProgramError:
                continue
            names = letmebuy.purchase_account_names()
            accounts = dict(zip(names, (keys[i] for i in ix.accounts), strict=False))
            purchases.append((program, args, accounts))
        if not purchases:
            listed = ", ".join(sorted(set(called))) or "nothing"
            raise ValueError(f"the prepared bytes contain no make_purchase; they call {listed}")
        program, args, accounts = purchases[0]
        expires = answer.get("expires", {})
        return cls(
            program=program,
            programs=tuple(sorted(set(called) - _PLUMBING)),
            store=accounts["receipts"],
            buyer=accounts["signer"],
            authority=accounts["authority"],
            mint=accounts["mint"],
            source=accounts["sender_token_account"],
            destination=accounts["recipient_token_account"],
            store_name=args["store_name"],
            product=args["product_name"],
            quantity=len(purchases),
            price_raw=_price_paid(answer, accounts["signer"]),
            network=str(answer.get("network", "")),
            status=str(answer.get("status", "")),
            binding=str(answer.get("binding", "")),
            binding_strength=str(answer.get("binding_strength", "exact")),
            last_valid_block_height=int(expires.get("last_valid_block_height", 0)),
            blocks_remaining=expires.get("blocks_remaining"),
            unsigned_transaction=unsigned,
        )


#: Programs a purchase may call besides the store's own: compute budget and the token
#: programs. The `program` field reports anything else, so a smuggled call is visible.
_PLUMBING = {
    "ComputeBudget111111111111111111111111111111",
    str(letmebuy.TOKEN_PROGRAM),
    str(letmebuy.ATA_PROGRAM),
    str(letmebuy.SYSTEM_PROGRAM),
}


def _message(raw: bytes) -> Any:
    try:
        return VersionedTransaction.from_bytes(raw).message
    except Exception:  # noqa: BLE001 - solders raises its own error types
        return Transaction.from_bytes(raw).message


def _price_paid(answer: dict[str, Any], buyer: str) -> int | None:
    """The simulated amount leaving the buyer, in the smallest unit; None if not reported."""
    outs = [o for o in answer.get("effects", {}).get("tokens_out", []) if o.get("owner") == buyer]
    if not outs:
        return None
    return sum(int(o["amount_raw"]) for o in outs)
