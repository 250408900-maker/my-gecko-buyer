"""Store-owner and instructor transactions for `scripts/`, on devnet only.

The buyer never uses this module: it signs through `buyer/signer.py`. These are the
transactions that set a store up (fund, mint, initialize, add a product), and every send
asserts the devnet genesis hash first. There is no parameter that points them anywhere else.

The SPL Token and associated-token instructions are encoded by hand from their published
layouts, to keep the dependencies to `solders`.
"""

from __future__ import annotations

from solders.hash import Hash
from solders.instruction import AccountMeta, Instruction
from solders.keypair import Keypair
from solders.message import Message
from solders.pubkey import Pubkey
from solders.system_program import CreateAccountParams, TransferParams, create_account, transfer
from solders.transaction import Transaction

from . import chain
from .letmebuy import ATA_PROGRAM, SYSTEM_PROGRAM, TOKEN_PROGRAM, token_account

MINT_SIZE = 82
LAMPORTS_PER_SOL = 1_000_000_000


def send(
    rpc_url: str, instructions: list[Instruction], payer: Keypair, signers: list[Keypair]
) -> str:
    """Sign with `signers` and send to DEVNET. Refuses before signing if the RPC is not devnet."""
    chain.assert_cluster(rpc_url, "devnet")
    blockhash = Hash.from_string(chain.latest_blockhash(rpc_url))
    message = Message.new_with_blockhash(instructions, payer.pubkey(), blockhash)
    tx = Transaction(signers, message, blockhash)
    return chain.send_and_confirm(rpc_url, bytes(tx), "devnet")


def sol_transfer(source: Pubkey, destination: Pubkey, lamports: int) -> Instruction:
    return transfer(TransferParams(from_pubkey=source, to_pubkey=destination, lamports=lamports))


def create_mint(
    rpc_url: str, payer: Pubkey, mint: Pubkey, authority: Pubkey, decimals: int
) -> list[Instruction]:
    rent = int(chain.rpc(rpc_url, "getMinimumBalanceForRentExemption", [MINT_SIZE]))
    create = create_account(
        CreateAccountParams(
            from_pubkey=payer, to_pubkey=mint, lamports=rent, space=MINT_SIZE, owner=TOKEN_PROGRAM
        )
    )
    # InitializeMint2 (tag 20): decimals, mint authority, no freeze authority.
    data = bytes([20, decimals]) + bytes(authority) + b"\x00"
    init = Instruction(TOKEN_PROGRAM, data, [AccountMeta(mint, False, True)])
    return [create, init]


def create_token_account(payer: Pubkey, owner: Pubkey, mint: Pubkey) -> Instruction:
    """CreateIdempotent (tag 1): a no-op when the account already exists."""
    return Instruction(
        ATA_PROGRAM,
        bytes([1]),
        [
            AccountMeta(payer, True, True),
            AccountMeta(token_account(owner, mint), False, True),
            AccountMeta(owner, False, False),
            AccountMeta(mint, False, False),
            AccountMeta(SYSTEM_PROGRAM, False, False),
            AccountMeta(TOKEN_PROGRAM, False, False),
        ],
    )


def mint_to(mint: Pubkey, owner: Pubkey, authority: Pubkey, amount_raw: int) -> Instruction:
    """MintTo (tag 7) into `owner`'s associated token account."""
    return Instruction(
        TOKEN_PROGRAM,
        bytes([7]) + amount_raw.to_bytes(8, "little"),
        [
            AccountMeta(mint, False, True),
            AccountMeta(token_account(owner, mint), False, True),
            AccountMeta(authority, True, False),
        ],
    )


def sol(lamports: int) -> str:
    return f"{lamports / LAMPORTS_PER_SOL:.6f} SOL"
