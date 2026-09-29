"""Monday, once: your devnet keys, funded, and your own 6-decimal token.

    uv run python scripts/devnet_setup.py                  # uses the class funder's SOL
    uv run python scripts/devnet_setup.py --funder <path>  # or your own devnet keypair

What it does, and it is safe to run again (every step checks before it acts):

1. checks the RPC is devnet by its genesis hash, and refuses otherwise;
2. makes three keypairs in ~/.config/dev3pack/ (outside this repo, mode 600):
   `devnet-owner.json` (your store), `devnet-buyer.json` (your buyer), `devnet-mint.json`;
3. waits for SOL: the class funder tops your OWNER address up to about 0.05 SOL. Without
   it, `--funder <keypair>` pays from a devnet wallet you control, and the public faucet
   is tried once (it usually answers 429);
4. moves a little SOL from owner to buyer for fees;
5. creates your own token (6 decimals, you are the mint authority) and mints 100 of it
   to your buyer;
6. writes ~/.config/dev3pack/devnet.json: addresses and key PATHS, never key bytes.

It prints addresses only. It never prints a key.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

from solders.keypair import Keypair
from solders.pubkey import Pubkey

from buyer import chain
from buyer.devnet_tx import (
    LAMPORTS_PER_SOL,
    create_mint,
    create_token_account,
    mint_to,
    send,
    sol,
    sol_transfer,
)
from buyer.letmebuy import token_account
from buyer.signer import CONFIG_DIR, KeyLocationError, inside_git_repo, load_keypair

OWNER_NEEDS = int(0.035 * LAMPORTS_PER_SOL)  # store rent (~0.021 measured) + mint + fees
BUYER_GETS = int(0.012 * LAMPORTS_PER_SOL)  # ~0.0015 per purchase measured, plus fees
DECIMALS = 6
MINT_AMOUNT_RAW = 100 * 10**DECIMALS


def keyfile(home: Path, role: str) -> Path:
    path = home / f"devnet-{role}.json"
    if not path.exists():
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w") as handle:
            json.dump(list(bytes(Keypair())), handle)
        print(f"  made   {role:<6} key  {path}")
    return path


def fund_owner(rpc: str, owner: Pubkey, funder_path: str | None) -> int:
    balance = chain.lamports(rpc, owner)
    if balance >= OWNER_NEEDS:
        return balance
    if funder_path:
        funder = load_keypair(Path(funder_path))
        need = OWNER_NEEDS + BUYER_GETS // 2 - balance
        print(f"  fund   owner from --funder {funder.pubkey()}: {sol(need)}")
        send(rpc, [sol_transfer(funder.pubkey(), owner, need)], funder, [funder])
        return chain.lamports(rpc, owner)
    try:
        signature = chain.rpc(rpc, "requestAirdrop", [str(owner), LAMPORTS_PER_SOL // 10])
        print("  asked  the public faucet for 0.1 SOL")
        chain.confirm(rpc, signature, 45)
    except (chain.ChainError, OSError) as exc:
        print(f"  faucet refused ({str(exc)[:80]})")
    return chain.lamports(rpc, owner)


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--home", default=str(CONFIG_DIR), help="where the keys live (outside any repo)"
    )
    parser.add_argument("--funder", help="a devnet keypair file that pays for your setup")
    parser.add_argument("--rpc", default=os.environ.get("GECKO_DEVNET_RPC", chain.DEVNET_RPC))
    args = parser.parse_args()

    home = Path(args.home).expanduser().resolve()
    home.mkdir(parents=True, exist_ok=True, mode=0o700)
    if inside_git_repo(home / "x"):
        print(f"refusing: {home} is inside a git repository. Keys never live in a repo.")
        return 1
    genesis = chain.assert_cluster(args.rpc, "devnet")
    print(f"devnet  {args.rpc}  genesis {genesis}")

    try:
        owner = load_keypair(keyfile(home, "owner"))
        buyer = load_keypair(keyfile(home, "buyer"))
        mint_key = load_keypair(keyfile(home, "mint"))
    except KeyLocationError as exc:
        print(f"refusing: {exc}")
        return 1
    mint = mint_key.pubkey()
    print(f"  owner  {owner.pubkey()}")
    print(f"  buyer  {buyer.pubkey()}")
    print(f"  mint   {mint}")

    balance = fund_owner(args.rpc, owner.pubkey(), args.funder)
    if balance < OWNER_NEEDS:
        print(
            f"\nNot funded yet: the owner holds {sol(balance)} and needs {sol(OWNER_NEEDS)}.\n"
            "Send this line to your instructor, then run this again:\n\n"
            f"    {owner.pubkey()} {buyer.pubkey()}\n"
        )
        return 2
    print(f"  owner  holds {sol(balance)}")

    if chain.lamports(args.rpc, buyer.pubkey()) < BUYER_GETS // 2:
        print(f"  fund   buyer from owner: {sol(BUYER_GETS)}")
        send(args.rpc, [sol_transfer(owner.pubkey(), buyer.pubkey(), BUYER_GETS)], owner, [owner])

    if chain.account_data(args.rpc, mint) is None:
        print(f"  create your token: {DECIMALS} decimals, mint authority = owner")
        instructions = create_mint(args.rpc, owner.pubkey(), mint, owner.pubkey(), DECIMALS)
        send(args.rpc, instructions, owner, [owner, mint_key])

    buyer_ata = token_account(buyer.pubkey(), mint)
    if chain.token_balance_raw(args.rpc, buyer_ata) == 0:
        print(f"  mint   100 of your token to the buyer ({MINT_AMOUNT_RAW} raw)")
        send(
            args.rpc,
            [
                create_token_account(owner.pubkey(), buyer.pubkey(), mint),
                mint_to(mint, buyer.pubkey(), owner.pubkey(), MINT_AMOUNT_RAW),
            ],
            owner,
            [owner],
        )
    time.sleep(1)

    config = {
        "cluster": "devnet",
        "rpc": args.rpc,
        "genesis": genesis,
        "owner": {"address": str(owner.pubkey()), "keypair": str(home / "devnet-owner.json")},
        "buyer": {"address": str(buyer.pubkey()), "keypair": str(home / "devnet-buyer.json")},
        "mint": str(mint),
        "decimals": DECIMALS,
    }
    (home / "devnet.json").write_text(json.dumps(config, indent=2) + "\n")
    print(f"\nready. {home / 'devnet.json'}")
    print(f"  owner  {sol(chain.lamports(args.rpc, owner.pubkey()))}")
    print(
        f"  buyer  {sol(chain.lamports(args.rpc, buyer.pubkey()))}, "
        f"{chain.token_balance_raw(args.rpc, buyer_ata)} raw of {mint}"
    )
    print(f"  explorer {chain.explorer(str(mint), 'devnet', 'address')}")
    print('\nNext: put your mint into store/store.json (or leave "mint": "own"), then')
    print("    uv run python scripts/create_store.py")
    print(
        f"The buyer signs with {home / 'devnet-buyer.json'} (devnet.json says so; "
        "GECKO_DEVNET_KEYPAIR overrides it)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
