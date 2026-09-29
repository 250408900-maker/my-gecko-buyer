"""Publish store/store.json to devnet: your store, read back from its own account.

    uv run python scripts/create_store.py                 # store/store.json
    uv run python scripts/create_store.py --dry-run       # check the rules, send nothing

It checks the store rules first (the same ones as challenge 2), then on devnet:
`initialize` the store if its account does not exist, `add_product` for every product it
does not have yet, and `update_telegram_channel` if you set one. Safe to run again: a
product already there is left alone (the program cannot edit a product, only delete it).

Instructions are built locally from the program's IDL (buyer/letmebuy.py) and signed by
your OWNER key from ~/.config/dev3pack/. Gecko's hosted `prepare_instruction` will do this
once it takes a `network`; today it builds for mainnet only.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

from solders.pubkey import Pubkey

from buyer import chain
from buyer.devnet_tx import send, sol
from buyer.letmebuy import SYSTEM_PROGRAM, build_instruction, decode_store, store_address
from buyer.mcp_client import GeckoUnavailable, HostedGecko
from buyer.signer import CONFIG_DIR, load_keypair

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_NAME = "dev3octocat"


class StoreRuleBroken(ValueError):
    pass


def validate(spec: dict, own_mint: str | None) -> list[dict]:
    """The store rules. Each one is a real failure somebody has already had."""
    name = spec.get("store", "")
    if not re.fullmatch(r"[a-z0-9][a-z0-9-]{2,31}", name):
        raise StoreRuleBroken(
            f"store name {name!r}: lowercase letters, digits and dashes, 3 to 32 characters. "
            "The program refuses underscores."
        )
    if name == EXAMPLE_NAME:
        raise StoreRuleBroken(
            f"{EXAMPLE_NAME} is the example. Store names are ONE global namespace on devnet "
            "(the account is PDA(['receipts', name])): use dev3<your handle>."
        )
    channel = spec.get("telegram_channel", "")
    if channel and not channel.startswith("@"):
        raise StoreRuleBroken(
            f"telegram_channel {channel!r} must start with @, or orders reach nobody"
        )
    products = spec.get("products", [])
    if len(products) < 3:
        raise StoreRuleBroken("at least 3 products: a buyer needs a choice to get right")
    seen = set()
    resolved = []
    for product in products:
        pname, price, mint = product.get("name", ""), product.get("price_raw"), product.get("mint")
        if not pname or pname in seen:
            raise StoreRuleBroken(f"product name {pname!r} is empty or appears twice")
        seen.add(pname)
        if not isinstance(price, int) or isinstance(price, bool) or price <= 0:
            raise StoreRuleBroken(
                f"{pname}: price_raw must be a whole number above 0, got {price!r}"
            )
        if mint == "own":
            if not own_mint:
                raise StoreRuleBroken(f"{pname}: mint 'own' needs scripts/devnet_setup.py first")
            mint = own_mint
        try:
            Pubkey.from_string(mint)
        except (ValueError, TypeError) as exc:
            raise StoreRuleBroken(f"{pname}: mint {mint!r} is not a 32-byte address") from exc
        resolved.append({"name": pname, "price_raw": price, "mint": mint})
    return resolved


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--store-file", default=str(ROOT / "store" / "store.json"))
    parser.add_argument("--home", default=str(CONFIG_DIR))
    parser.add_argument("--owner", help="owner keypair path (default: <home>/devnet-owner.json)")
    parser.add_argument("--rpc", default=os.environ.get("GECKO_DEVNET_RPC", chain.DEVNET_RPC))
    parser.add_argument("--dry-run", action="store_true", help="check the rules, send nothing")
    parser.add_argument("--no-gecko", action="store_true", help="skip the read-back through Gecko")
    args = parser.parse_args()

    home = Path(args.home).expanduser()
    config_path = home / "devnet.json"
    config = json.loads(config_path.read_text()) if config_path.is_file() else {}
    store_file = Path(args.store_file)
    spec = json.loads(store_file.read_text())
    try:
        products = validate(spec, config.get("mint"))
    except StoreRuleBroken as exc:
        print(f"refusing: {exc}")
        return 1
    name = spec["store"]
    address = store_address(name)
    print(f"store {name}  ->  {address}")
    for p in products:
        print(f"  {p['name']:<28} {p['price_raw']:>12} raw  {p['mint']}")
    if args.dry_run:
        print("dry run: the rules pass; nothing was sent")
        return 0

    chain.assert_cluster(args.rpc, "devnet")
    owner = load_keypair(Path(args.owner or home / "devnet-owner.json"))
    start = chain.lamports(args.rpc, owner.pubkey())
    raw = chain.account_data(args.rpc, address)
    if raw is None:
        ix = build_instruction(
            "initialize",
            {"receipts": address, "authority": owner.pubkey(), "system_program": SYSTEM_PROGRAM},
            {"store_name": name},
        )
        print(f"  initialize        {send(args.rpc, [ix], owner, [owner])}")
        raw = chain.account_data(args.rpc, address)
    store = decode_store(raw or b"")
    if store.authority != str(owner.pubkey()):
        print(
            f"refusing: {name} already exists and belongs to {store.authority}. Pick another name."
        )
        return 1

    have = {p.name: p for p in store.products}
    for p in products:
        if p["name"] in have:
            old = have[p["name"]]
            if (old.price_raw, old.mint) != (p["price_raw"], p["mint"]):
                print(
                    f"  {p['name']}: already listed at {old.price_raw} of {old.mint}; "
                    "the program cannot edit a product (delete it and run again)"
                )
            continue
        ix = build_instruction(
            "add_product",
            {
                "receipts": address,
                "authority": owner.pubkey(),
                "mint": Pubkey.from_string(p["mint"]),
            },
            {"store_name": name, "name": p["name"], "price": p["price_raw"]},
        )
        print(f"  add_product {p['name'][:20]:<20} {send(args.rpc, [ix], owner, [owner])}")

    channel = spec.get("telegram_channel", "")
    if channel and channel != store.telegram_channel:
        ix = build_instruction(
            "update_telegram_channel",
            {"receipts": address, "authority": owner.pubkey()},
            {"store_name": name, "telegram_channel_id": channel},
        )
        print(f"  telegram channel  {send(args.rpc, [ix], owner, [owner])}")

    final = decode_store(chain.account_data(args.rpc, address) or b"")
    spent = start - chain.lamports(args.rpc, owner.pubkey())
    print(
        f"\n{final.name} on devnet: {len(final.products)} products, "
        f"total_purchases {final.total_purchases}, owner spent {sol(spent)}"
    )
    print(f"  {chain.explorer(str(address), 'devnet', 'address')}")

    if not args.no_gecko:
        try:
            answer = HostedGecko().call("list_stores", {"store": name, "network": "devnet"})
            found = [s for s in answer.get("stores", []) if s.get("store") == name]
            menu = (
                ", ".join(f"{p['name']} {p['price_raw']}" for p in found[0]["products"])
                if found
                else "not found"
            )
            print(f"  read back by Gecko: {menu}")
        except GeckoUnavailable as exc:
            print(f"  Gecko did not answer ({exc}); the store is on devnet regardless")

    spec["address"] = str(address)
    store_file.write_text(json.dumps(spec, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
