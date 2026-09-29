# The defence: Friday 2 October, six minutes

*Your script. Keep the minutes, fill the right-hand column with what YOU will show and
say, and rehearse it once on Thursday against the clock. Delete the italic lines.*

One design rule: everything you show ends in a **receipt** (it landed, and this is what
moved) or a **refusal** (it did not sign, and this is the field that disagreed).

## The six minutes

| Min | On screen | Backed by | What I say |
|---|---|---|---|
| 0:00 | your README's first lines: the sentence and the explorer link | `README.md` | |
| 0:45 | your assistant with Gecko connected: `list_stores` shows *your* store | `docs/connect.md`, `store/store.json` | |
| 1:30 | the live buy: pin, prepare, 7 ticks, sign, verify, submit | `uv run buyer "one espresso" --devnet` | |
| 2:30 | the landing: the explorer, then the receipt with ledger deltas | `receipts/<sig8>.md` | |
| 3:15 | **the injected failure**: the judge draws a card; your buyer refuses and signs nothing | `buyer/check.py`, `refusals/` | |
| 4:30 | tests and the five-case table; one test that was red first | `uv run pytest`, `docs/EVAL_REPORT.md` | |
| 5:15 | the ADR: the decision, and what would reverse it | `docs/adr/0001-refusals-before-signing.md` | |

Friday participants with a capped mainnet wallet from the founder may do minute 1:30 on
mainnet against geckocoffee instead (see "Friday on mainnet" below). Everyone else stays
on devnet, and that is the whole defence.

## The four cards

The judge draws one, face down. You do not know which, so you cannot stage it; your
buyer has to refuse it on its own.

| Card | What the judge does | The command | The expected refusal |
|---|---|---|---|
| **Quantity** | asks for two espressos | `uv run buyer "two espressos" --devnet` | `quantity`: asked 2, prepared 1 |
| **Budget** | sets the budget to half the price | `uv run buyer "one espresso" --budget-raw <half> --devnet` | `price_raw`: both numbers |
| **Tampered bytes** | changes one byte of the signed transaction before verify | `uv run buyer "one espresso" --devnet --card tampered` | `signed bytes`: `verify_signed_transaction` refuses, so there is no submit |
| **Stale bytes** | waits past `expires`, then asks you to sign | `uv run buyer "one espresso" --devnet --card stale` | `blockhash`: the bytes expired; prepare again, never re-sign |

Rehearse all four offline first, with no network and no key:

```bash
uv run buyer --cards --recorded      # 4/4 once your steps and checks are written
```

## Before you go on stage

- [ ] One devnet receipt is **committed** (`receipts/<sig8>.md`). If the network fails at
      2:30, show it and say out loud that it is the committed one. Same code path, honest.
- [ ] `uv run buyer --cases --recorded` prints 6/6 and `--cards` prints 4/4.
- [ ] `uv run pytest` is green and `python3 scripts/scan_secrets.py` finds nothing.
- [ ] Your devnet buyer holds SOL and your token (`solana balance -u devnet <buyer>`).
- [ ] Your assistant's connector is live; you tried `list_stores` today, not yesterday.

## Friday on mainnet (only with a founder-issued wallet)

If you are given a capped wallet: it is a keypair file handed to you on Friday, holding
three espressos' worth of USDC and a little SOL, and nothing else. It never enters your
repository, and you give it back after.

```bash
GECKO_MAINNET_KEYPAIR=<the file you were handed> \
  uv run buyer "one espresso" --mainnet --store geckocoffee --mainnet-budget-raw 100000
```

The signer refuses to sign on mainnet without `--mainnet-budget-raw`, refuses any
purchase above it, and checks mainnet's genesis hash before the signature. The wallet's
balance is the hard cap: a fourth espresso cannot be paid for.

## Questions you should be ready for

- Why does Gecko never hold your key, and what would change if it did?
- Which of your seven checks would you drop first, and what risk would you accept?
- Your buyer refused. How does the person at the chat know it was right to?
- What does your receipt NOT prove?
