# The defence: Friday 2 October, six minutes

One design rule: everything I show ends in a **receipt** (it landed, and this is what
moved) or a **refusal** (it did not sign, and this is the field that disagreed).

## The six minutes

| Min | On screen | Backed by | What I say |
|---|---|---|---|
| 0:00 | README first lines and explorer link | `README.md` | My buyer turns a natural-language purchase request into a pinned intent. It either completes the purchase and produces a reconciled receipt, or refuses before signing when something does not match. |
| 0:45 | Gecko `list_stores` showing my store | `docs/connect.md`, `store/store.json` | This is my store and its products. Gecko provides the transaction data, but it never holds my private signing key. |
| 1:30 | Live buy: pin, prepare, seven checks, sign, verify, submit | `uv run buyer "one espresso" --devnet` | The request is pinned before transaction bytes exist. The prepared purchase is checked field by field. Only after all seven checks pass do I sign locally, verify the signed transaction, and submit it. |
| 2:30 | Explorer and receipt | `receipts/<sig8>.md` | This shows the purchase landed on devnet. The receipt is reconciled using ledger reads: the buyer balance decreased, the store balance increased, and total purchases increased. |
| 3:15 | Injected failure/card | `buyer/check.py`, `refusals/` | Now I inject a failure. If a checked field disagrees with the pinned intent, the buyer refuses. Nothing is submitted, and the refusal records the field plus the asked and found values. |
| 4:30 | Tests and evaluation report | `uv run pytest`, `docs/EVAL_REPORT.md` | I also have recorded cases that use the same buyer code path without depending on the network. This gives me a rollback demonstration if devnet or the hosted MCP is unavailable. |
| 5:15 | ADR | `docs/adr/0001-refusals-before-signing.md` | My design decision is to refuse before signing whenever a safety check fails. I would only change this if another mechanism could provide the same guarantee that the transaction matches the pinned intent before authorization. |

## The four cards

The judge draws one, face down. I do not know which card will be selected, so the buyer
must detect and refuse the problem itself.

| Card | What the judge does | The command | The expected refusal |
|---|---|---|---|
| **Quantity** | asks for two espressos | `uv run buyer "two espressos" --devnet` | `quantity`: asked 2, prepared 1 |
| **Budget** | sets the budget to half the price | `uv run buyer "one espresso" --budget-raw <half> --devnet` | `price_raw`: both numbers |
| **Tampered bytes** | changes one byte of the signed transaction before verify | `uv run buyer "one espresso" --devnet --card tampered` | `signed bytes`: `verify_signed_transaction` refuses, so there is no submit |
| **Stale bytes** | waits past `expires`, then asks you to sign | `uv run buyer "one espresso" --devnet --card stale` | `blockhash`: the bytes expired; prepare again, never re-sign |

Rehearse all four offline first:

```bash
uv run buyer --cards --recorded