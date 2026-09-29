"""Founder only, for Friday: make N mainnet wallets capped at 3 espressos, and say how to fund them.

    uv run python scripts/friday_wallets.py --count 6
    uv run python scripts/friday_wallets.py --count 6 --out ~/dev3pack-friday

THIS SCRIPT NEVER SENDS ANYTHING AND NEVER SIGNS. It makes no network call at all. It
generates keypairs locally, into a folder OUTSIDE any git repository (mode 600), writes a
manifest of ADDRESSES (no keys), and prints exactly how much USDC and SOL each wallet
needs. You fund them yourself, with your own tools; the commands are printed for you to
read and run, not run by this script.

The cap is the balance. A wallet that holds 3 espressos' worth of USDC cannot spend a
fourth, whatever the software does. The buyer's `--mainnet-budget-raw` is a second fence
on top: it refuses to sign any single purchase above one espresso.

The espresso price defaults to geckocoffee's as read on 2026-09-26 (100000 raw USDC,
6 decimals). Confirm it with `list_stores {"store": "geckocoffee"}` before you fund.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
from pathlib import Path

from solders.keypair import Keypair

from buyer.signer import inside_git_repo

MAINNET_USDC = "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
USDC_DECIMALS = 6
LAMPORTS_PER_SOL = 1_000_000_000
#: A system account must keep this much to exist at all (rent-exempt minimum, 0 bytes).
RENT_EXEMPT_WALLET = 890_880
#: Measured on devnet, 2026-09-28, same program: the first purchase from a store cost the
#: buyer 1493440 lamports (an account the purchase creates, plus the fee); the second cost
#: 5000, the fee alone. Budgeting every purchase at the first one's cost is the safe side.
PER_PURCHASE_LAMPORTS = 1_493_440


def funding(espressos: int, price_raw: int, sol_margin: float) -> tuple[int, int]:
    """(USDC raw, lamports) one wallet needs for `espressos` purchases and no more."""
    usdc_raw = espressos * price_raw
    lamports = RENT_EXEMPT_WALLET + espressos * PER_PURCHASE_LAMPORTS
    return usdc_raw, lamports + int(sol_margin * LAMPORTS_PER_SOL)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--count", type=int, required=True, help="how many wallets")
    parser.add_argument("--out", default=str(Path.home() / "dev3pack-friday-wallets"))
    parser.add_argument("--espressos", type=int, default=3)
    parser.add_argument("--espresso-price-raw", type=int, default=100_000)
    parser.add_argument("--sol-margin", type=float, default=0.004, help="SOL on top, per wallet")
    args = parser.parse_args()

    if not 1 <= args.count <= 100:
        print("refusing: --count between 1 and 100")
        return 1
    out = Path(args.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True, mode=0o700)
    if inside_git_repo(out / "x"):
        print(f"refusing: {out} is inside a git repository. Mainnet keys never live in a repo.")
        return 1
    existing = sorted(out.glob("friday-*.json"))
    if existing:
        print(f"refusing: {out} already holds {len(existing)} wallets. Use another --out.")
        return 1

    usdc_raw, lamports = funding(args.espressos, args.espresso_price_raw, args.sol_margin)
    sol_text = f"{lamports / LAMPORTS_PER_SOL:.6f}"
    usdc_text = f"{usdc_raw / 10**USDC_DECIMALS:.6f}"

    rows = []
    for index in range(1, args.count + 1):
        key = Keypair()
        path = out / f"friday-{index:02d}.json"
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(list(bytes(key)), handle)
        rows.append(
            {
                "wallet": index,
                "address": str(key.pubkey()),
                "keypair": str(path),
                "usdc_raw": usdc_raw,
                "lamports": lamports,
            }
        )
        del key

    with (out / "manifest.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)

    print(f"{args.count} wallets in {out} (keys mode 600, manifest.csv has addresses only)\n")
    print(
        f"Each wallet: {usdc_raw} raw USDC ({usdc_text}) = {args.espressos} x "
        f"{args.espresso_price_raw}, and {lamports} lamports ({sol_text} SOL)."
    )
    print(
        f"  SOL = {RENT_EXEMPT_WALLET} rent-exempt minimum + {args.espressos} x "
        f"{PER_PURCHASE_LAMPORTS} per purchase + {args.sol_margin} SOL margin"
    )
    print(
        f"Total: {usdc_raw * args.count} raw USDC, "
        f"{lamports * args.count / LAMPORTS_PER_SOL:.6f} SOL\n"
    )
    for row in rows:
        print(f"  {row['wallet']:>2}  {row['address']}")
    print("\nThis script sent nothing. To fund, run these yourself, from your own wallet:\n")
    for row in rows:
        print(
            f"  solana transfer --url mainnet-beta --allow-unfunded-recipient "
            f"{row['address']} {sol_text}"
        )
        print(
            f"  spl-token transfer --url mainnet-beta --fund-recipient "
            f"{MAINNET_USDC} {usdc_text} {row['address']}"
        )
    print("\nHand each participant ONE keypair file on Friday, outside their repo, and the cap:")
    print(
        f'  GECKO_MAINNET_KEYPAIR=<file> uv run buyer "one espresso" --mainnet '
        f"--store geckocoffee --mainnet-budget-raw {args.espresso_price_raw}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
