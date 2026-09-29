"""Instructor only: top student devnet addresses up to about 0.05 SOL each. DEVNET ONLY.

    uv run python scripts/class_funder.py --file students.txt            # dry run: prints the plan
    uv run python scripts/class_funder.py --file students.txt --send     # sends it

`students.txt` holds what `devnet_setup.py` told each student to send you, one line each:

    <owner address> [<buyer address>]     # anything after a # is ignored

The FIRST address on a line is topped up to `--sol` (default 0.05; the measured need for
a store and a week of purchases is about 0.023). With `--class-mint` and
`--mint-authority`, the LAST address on the line also gets `--tokens` of each class token.
For dev3pack-cafe pass both mints: the class "USDC" (Eoqdd43n...) so the student can buy,
and the lookalike (BRPT4Sr7...) so use case 3 reaches the student's own mint check, the
way a scam token reaches a real wallet: unasked.

The funder defaults to the Solana CLI key (~/.config/solana/id.json). That key is used on
devnet only: the RPC's genesis hash is checked before the plan is even printed, and again
before every send. The default is a dry run.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from solders.pubkey import Pubkey

from buyer import chain
from buyer.devnet_tx import LAMPORTS_PER_SOL, create_token_account, mint_to, send, sol, sol_transfer
from buyer.letmebuy import token_account
from buyer.signer import load_keypair

BATCH = 8  # transfers per transaction, well inside the packet limit


def read_lines(path: str | None, extra: list[str]) -> list[list[Pubkey]]:
    raw = list(extra)
    if path:
        raw += Path(path).read_text().splitlines()
    rows = []
    for line in raw:
        words = line.split("#", 1)[0].split()
        if not words:
            continue
        try:
            rows.append([Pubkey.from_string(w) for w in words])
        except ValueError:
            print(f"skipping a line that is not addresses: {line.strip()!r}")
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("addresses", nargs="*", help="addresses, if not using --file")
    parser.add_argument("--file", help="one student per line: <owner> [<buyer>]")
    parser.add_argument("--funder", default=str(Path.home() / ".config" / "solana" / "id.json"))
    parser.add_argument("--sol", type=float, default=0.05, help="top each first address up to this")
    parser.add_argument(
        "--class-mint",
        action="append",
        default=[],
        help="a class token to hand out; repeat it for the lookalike token of use case 3",
    )
    parser.add_argument("--mint-authority", help="keypair that may mint the class token")
    parser.add_argument("--tokens", type=int, default=20, help="class tokens per student")
    parser.add_argument("--decimals", type=int, default=6)
    parser.add_argument("--rpc", default=os.environ.get("GECKO_DEVNET_RPC", chain.DEVNET_RPC))
    parser.add_argument("--send", action="store_true", help="actually send (default: dry run)")
    args = parser.parse_args()

    genesis = chain.assert_cluster(args.rpc, "devnet")
    print(f"devnet {args.rpc} genesis {genesis}")
    funder = load_keypair(Path(args.funder))
    rows = read_lines(args.file, args.addresses)
    target = int(args.sol * LAMPORTS_PER_SOL)

    plan: list[tuple[Pubkey, int]] = []
    for row in rows:
        have = chain.lamports(args.rpc, row[0])
        need = max(0, target - have)
        print(f"  {row[0]}  holds {sol(have)}  ->  {'ok' if not need else '+' + sol(need)}")
        if need:
            plan.append((row[0], need))
    total = sum(n for _, n in plan)
    balance = chain.lamports(args.rpc, funder.pubkey())
    print(
        f"\n{len(plan)} of {len(rows)} to top up, {sol(total)} in all. "
        f"Funder {funder.pubkey()} holds {sol(balance)}."
    )
    if total > balance:
        print("refusing: the funder cannot cover the plan")
        return 1

    token_rows: list[tuple[Pubkey, Pubkey]] = []
    if args.class_mint and not args.mint_authority:
        print("refusing: --class-mint needs --mint-authority")
        return 1
    for mint_text in args.class_mint:
        mint = Pubkey.from_string(mint_text)
        waiting = [
            row[-1]
            for row in rows
            if chain.token_balance_raw(args.rpc, token_account(row[-1], mint)) == 0
        ]
        token_rows += [(owner, mint) for owner in waiting]
        print(f"{len(waiting)} to receive {args.tokens} of {mint} each")

    if not args.send:
        print("dry run: nothing was sent. Add --send to send it.")
        return 0

    for start in range(0, len(plan), BATCH):
        batch = plan[start : start + BATCH]
        ixs = [sol_transfer(funder.pubkey(), who, lamports) for who, lamports in batch]
        print(f"  sent SOL to {len(batch)}: {send(args.rpc, ixs, funder, [funder])}")
    if token_rows:
        authority = load_keypair(Path(args.mint_authority))
        amount = args.tokens * 10**args.decimals
        for owner, mint in token_rows:
            ixs = [
                create_token_account(funder.pubkey(), owner, mint),
                mint_to(mint, owner, authority.pubkey(), amount),
            ]
            signature = send(args.rpc, ixs, funder, [funder, authority])
            print(f"  {args.tokens} of {str(mint)[:8]}.. to {owner}: {signature}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
