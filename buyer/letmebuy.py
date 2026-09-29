"""The `let_me_buy` program, read from its IDL: addresses, instructions, and the store account.

Everything here comes from `buyer/idl/let_me_buy.idl.json`, the program's published Anchor
IDL. It was vendored from Gecko's repository (`capabilities/let_me_buy.idl.json` in
`surfcall`), which is where the hosted MCP reads it too. The encoder is a small subset of
what Gecko's `gecko/instruction_build.py` does: only the argument types this program uses.

Nothing in this file touches a key or the network.
"""

from __future__ import annotations

import json
import struct
from dataclasses import dataclass, field
from functools import cache
from pathlib import Path
from typing import Any

from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey

IDL_PATH = Path(__file__).parent / "idl" / "let_me_buy.idl.json"

TOKEN_PROGRAM = Pubkey.from_string("TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA")
ATA_PROGRAM = Pubkey.from_string("ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL")
SYSTEM_PROGRAM = Pubkey.from_string("11111111111111111111111111111111")


class ProgramError(ValueError):
    """The IDL cannot express what was asked: an unknown instruction, account or type."""


@cache
def idl() -> dict[str, Any]:
    return json.loads(IDL_PATH.read_text(encoding="utf-8"))


def program_id() -> Pubkey:
    return Pubkey.from_string(idl()["address"])


def instruction_spec(name: str) -> dict[str, Any]:
    for spec in idl()["instructions"]:
        if spec["name"] == name:
            return spec
    raise ProgramError(f"the IDL has no instruction called {name!r}")


def store_address(store_name: str) -> Pubkey:
    """The store's one account: PDA(['receipts', name]). One global namespace per name."""
    return Pubkey.find_program_address([b"receipts", store_name.encode()], program_id())[0]


def token_account(owner: Pubkey, mint: Pubkey) -> Pubkey:
    """The associated token account of `owner` for `mint` (classic SPL Token)."""
    return Pubkey.find_program_address(
        [bytes(owner), bytes(TOKEN_PROGRAM), bytes(mint)], ATA_PROGRAM
    )[0]


# --- encoding -------------------------------------------------------------------------

_UINT = {"u8": 1, "u16": 2, "u32": 4, "u64": 8}


def _encode(declared: Any, value: Any, name: str) -> bytes:
    if declared == "string":
        if not isinstance(value, str):
            raise ProgramError(f"`{name}` must be a string")
        raw = value.encode("utf-8")
        return len(raw).to_bytes(4, "little") + raw
    if declared in _UINT:
        # bool is an int in Python; refusing it keeps True from being encoded as 1.
        if not isinstance(value, int) or isinstance(value, bool):
            raise ProgramError(f"`{name}` must be a whole number, got {type(value).__name__}")
        width = _UINT[declared]
        if not 0 <= value < 1 << (8 * width):
            raise ProgramError(f"`{name}` = {value} does not fit a {declared}")
        return value.to_bytes(width, "little")
    raise ProgramError(f"`{name}` is declared {declared!r}, which this encoder refuses")


def build_instruction(name: str, accounts: dict[str, Pubkey], args: dict[str, Any]) -> Instruction:
    """One program instruction from the IDL: discriminator, Borsh args, account flags.

    Accounts the IDL pins (the system program) are filled from the IDL, never asked for.
    """
    spec = instruction_spec(name)
    data = bytes(spec["discriminator"])
    for arg in spec["args"]:
        if arg["name"] not in args:
            raise ProgramError(f"{name}: argument `{arg['name']}` is missing")
        data += _encode(arg["type"], args[arg["name"]], arg["name"])
    metas = []
    for slot in spec["accounts"]:
        if "address" in slot:
            address = Pubkey.from_string(slot["address"])
        elif slot["name"] in accounts:
            address = accounts[slot["name"]]
        else:
            raise ProgramError(f"{name}: account `{slot['name']}` is missing")
        metas.append(AccountMeta(address, bool(slot.get("signer")), bool(slot.get("writable"))))
    return Instruction(program_id(), data, metas)


def purchase_account_names() -> list[str]:
    """make_purchase's accounts, in the order they sit in the instruction."""
    return [slot["name"] for slot in instruction_spec("make_purchase")["accounts"]]


def decode_purchase_args(data: bytes) -> dict[str, Any]:
    """make_purchase's args from instruction data: store_name, product_name, table_number."""
    spec = instruction_spec("make_purchase")
    if data[:8] != bytes(spec["discriminator"]):
        raise ProgramError("this instruction is not make_purchase")
    reader = _Reader(data, 8)
    return {
        "store_name": reader.string(),
        "product_name": reader.string(),
        "table_number": reader.u8(),
    }


# --- the store account ----------------------------------------------------------------


@dataclass(frozen=True)
class Product:
    name: str
    price_raw: int
    decimals: int
    mint: str


@dataclass(frozen=True)
class Sale:
    receipt_id: int
    buyer: str
    was_delivered: bool
    price_raw: int
    timestamp: int
    table_number: int
    product: str


@dataclass(frozen=True)
class Store:
    """The `Receipts` account, decoded field by field in the IDL's order."""

    name: str
    authority: str
    total_purchases: int
    products: list[Product] = field(default_factory=list)
    sales: list[Sale] = field(default_factory=list)
    telegram_channel: str = ""
    details: str = ""


class _Reader:
    def __init__(self, raw: bytes, at: int = 0) -> None:
        self.raw, self.at = raw, at

    def take(self, n: int) -> bytes:
        if self.at + n > len(self.raw):
            raise ProgramError("the account ends before its layout does")
        out = self.raw[self.at : self.at + n]
        self.at += n
        return out

    def u8(self) -> int:
        return self.take(1)[0]

    def u32(self) -> int:
        return struct.unpack("<I", self.take(4))[0]

    def u64(self) -> int:
        return struct.unpack("<Q", self.take(8))[0]

    def i64(self) -> int:
        return struct.unpack("<q", self.take(8))[0]

    def pubkey(self) -> str:
        return str(Pubkey.from_bytes(self.take(32)))

    def string(self) -> str:
        return self.take(self.u32()).decode("utf-8")


def decode_store(raw: bytes) -> Store:
    expected = bytes(next(a for a in idl()["accounts"] if a["name"] == "Receipts")["discriminator"])
    if raw[:8] != expected:
        raise ProgramError("this account is not a let_me_buy store")
    reader = _Reader(raw, 8)
    sales = [
        Sale(
            receipt_id=reader.u64(),
            buyer=reader.pubkey(),
            was_delivered=bool(reader.u8()),
            price_raw=reader.u64(),
            timestamp=reader.i64(),
            table_number=reader.u8(),
            product=reader.string(),
        )
        for _ in range(reader.u32())
    ]
    total = reader.u64()
    name = reader.string()
    authority = reader.pubkey()
    products = []
    for _ in range(reader.u32()):
        price = reader.u64()
        decimals = reader.u8()
        mint = reader.pubkey()
        products.append(
            Product(name=reader.string(), price_raw=price, decimals=decimals, mint=mint)
        )
    channel = reader.string()
    reader.u8()  # bump
    details = reader.string()
    return Store(name, authority, total, products, sales, channel, details)
