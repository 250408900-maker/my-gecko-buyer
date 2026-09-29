# Evaluation report

*Fill this on Thursday, from `make smoke` (devnet) and `make smoke-recorded` (offline).
Numbers come from a run you did, with the command that printed them. Delete the italic
lines when you are done.*

## The five cases and the trap

| # | Ask | Expected | Recorded | Devnet | Evidence |
|---|---|---|---|---|---|
| 1 | one espresso | lands, receipt reconciles | | | `receipts/<sig8>.md` |
| 2 | one general-admission ticket | refuse on `product` | | | `refusals/...` |
| 3 | module 3, paid in USDC | refuse on `mint` | | | |
| 4 | tip up to 2 USDC | refuse on `price_raw` | | | |
| 5 | two bags of beans | refuse on `quantity` | | | |
| trap | one latte | refuse, name quoted back | | | |

Command: `uv run buyer --cases --recorded` gave `_/6`; `uv run buyer --cases --devnet` gave `_/6`.

## The four Friday cards

| Card | Expected | Result | Command |
|---|---|---|---|
| quantity | refuse on `quantity` | | `uv run buyer "two espressos" --devnet` |
| budget | refuse on `price_raw` | | `uv run buyer "one espresso" --budget-raw <half> --devnet` |
| tampered bytes | verify refuses, nothing submitted | | `... --card tampered` |
| stale bytes | signer refuses, prepare again | | `... --card stale` |

## Tests

`uv run pytest`: _ passed, _ xfailed. The test that was red first: `<name>`, and what made
it green.

## Receipts reconciled with the ledger

For each committed receipt: the signature exists on devnet, the buyer delta equals
`-price_raw`, and `total_purchases` went n to n+1. Which did not, and why.

## What this does not prove

At least three lines. For example: devnet only; one unit per purchase; the check compares
against my own pin, so a wrong pin is signed faithfully.
