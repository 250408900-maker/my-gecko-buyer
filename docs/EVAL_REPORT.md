# Evaluation report

## The five cases and the trap

| # | Ask | Expected | Recorded | Devnet | Evidence |
|---|---|---|---|---|---|
| 1 | one espresso | lands, receipt reconciles | PASS | not yet: missing required class token account | `smoke-report.recorded.json`, `smoke-report.json` |
| 2 | one general-admission ticket | refuse on `product` | PASS | PASS: refused on `product` | `smoke-report.recorded.json`, `smoke-report.json` |
| 3 | module 3, paid in USDC | refuse on `mint` | PASS | not yet: prepare stopped because required token account was missing | `smoke-report.recorded.json`, `smoke-report.json` |
| 4 | tip up to 2 USDC | refuse on `price_raw` | PASS | not yet: prepare stopped because required token account was missing | `smoke-report.recorded.json`, `smoke-report.json` |
| 5 | two bags of beans | refuse on `quantity` | PASS | not yet: prepare stopped because required token account was missing | `smoke-report.recorded.json`, `smoke-report.json` |
| trap | one latte | refuse, name quoted back | PASS | not yet: prepare stopped because required token account was missing | `smoke-report.recorded.json`, `smoke-report.json` |

Command: `uv run buyer --cases --recorded` gave `6/6`; `uv run buyer --cases --devnet --json smoke-report.json` gave `1/6`.

## The four Friday cards

| Card | Expected | Result | Command |
|---|---|---|---|
| quantity | refuse on `quantity` | PASS in recorded rehearsal | `uv run buyer --cards --recorded` |
| budget | refuse on `price_raw` | PASS in recorded rehearsal | `uv run buyer --cards --recorded` |
| tampered bytes | verify refuses, nothing submitted | PASS in recorded rehearsal | `uv run buyer --cards --recorded` |
| stale bytes | signer refuses, prepare again | PASS in recorded rehearsal | `uv run buyer --cards --recorded` |

Recorded card rehearsal: `4/4`.

## Tests

`uv run pytest -q`: test suite completed at 100% with no failures. Two tests were skipped.

A test that was red earlier was `tests/test_runner_order.py::test_an_unwritten_check_is_a_refusal_not_a_pass`. It became green after the runner was corrected so an unwritten check produces a not-written/refusal outcome instead of being treated as a successful check.

## Receipts reconciled with the ledger

A committed devnet purchase was successfully reconciled during project 03. The transaction was confirmed and finalized on devnet. The receipt showed the buyer delta as `-1000000`, the store delta as `+1000000`, and `total_purchases` changed from 0 to 1.

The project 04 live smoke did not produce its required smoke receipt because the class-token account required for `dev3pack-cafe` was not present in the buyer wallet. Those affected cases stopped during preparation before signing or submission.

## What this does not prove

The recorded 6/6 run proves the rollback behavior against recorded fixtures, but it does not prove that the external devnet environment is available or correctly funded.

A successful devnet receipt proves that a particular transaction landed and that its observed ledger deltas reconciled; it does not prove that every future transaction will succeed.

The checks compare prepared transaction fields against the pinned intent. They cannot prove that the human originally expressed the correct intent if the intent itself was wrong.

The tests and smoke cases cover the scenarios supplied by the project, not every possible failure or adversarial input.