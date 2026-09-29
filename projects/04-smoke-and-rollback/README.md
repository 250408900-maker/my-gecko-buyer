# Project 04: smoke, rollback, deploy

**Thursday 1 October, session 14 (deploy and operate).** The last 15 minutes of class,
then homework, then one timed rehearsal of Friday.

Operating a thing means knowing, in one command, whether it still works, and having a
second command for when it does not. Today you get both, you deploy your check server,
and you write down one thing that really went wrong this week.

## What you ship

| File | What is in it |
|---|---|
| `smoke-report.json` | `make smoke` on devnet: the five cases and the trap, one lands, five refuse |
| `smoke-report.recorded.json` | `make smoke-recorded`: the same, on recorded answers (the rollback) |
| `projects/04-smoke-and-rollback/deploy.md` | your check server's public URL, one call to it and its answer, and how you would roll it back |
| `docs/ISSUES.md` | at least one real incident from this week |
| `docs/EVAL_REPORT.md` | filled from the two smoke reports and your tests |
| `docs/DEFENCE.md` | your six minutes, rehearsed once against the clock |

Then `uv run python projects/04-smoke-and-rollback/check.py` prints a local score out of 10.

## Steps

### 1. The smoke (in class)

Your buyer needs class tokens to buy from `dev3pack-cafe` (the instructor sends them,
together with the lookalike token use case 3 needs). Then:

```bash
make smoke
```

It runs all six fixtures' asks LIVE on devnet against `dev3pack-cafe`, each with its own
budget and pay mint, and writes `smoke-report.json`. Case 1 lands and writes a receipt;
the other five refuse on their field, and nothing is signed for them. A case that does
not end as expected is the most useful line in the report: find out why before anything
else.

### 2. Reconcile

For every receipt the smoke wrote, the runner already read the ledger twice. Confirm it
from outside your own code:

```bash
uv run python projects/03-the-part-that-says-no/check.py --online
```

It asks devnet directly whether each committed signature exists and succeeded.

### 3. The rollback

When the hosted MCP or devnet misbehaves on Friday, you do not debug on stage. You switch:

```bash
make smoke-recorded           # GECKO_SOURCE=recorded: fixtures, no network, no key
```

Same code path, same checks, same refusals; only the transport differs. If this does not
print 6/6, your rollback is broken, and that is worth knowing today rather than tomorrow.

### 4. Deploy the check server

Session 14 deploys an MCP server. Deploy yours from project 03: any host that serves
HTTPS will do, run with the streamable HTTP transport. It holds no key, so there is
nothing secret to configure. It must still refuse a private `rpc_url` once it is public:
try it.

Write `deploy.md`: the URL, one `check_purchase` call and what it answered, the command
that redeploys, and what you would do if it went down during the defence (hint: step 3).

### 5. One real incident

Something went wrong this week: an expired blockhash, a 429, a store name somebody else
had taken, a test that passed for the wrong reason. Write it in `docs/ISSUES.md` in the
shape the file asks for. A real incident with a boring cause is worth more than an
invented one with a dramatic cause.

### 6. Rehearse

Fill `docs/DEFENCE.md`, then run the six minutes once with a timer and somebody drawing a
card. `uv run buyer --cards --recorded` first, so you know each card refuses.

## Done looks like

- [ ] `smoke-report.json`: case 1 landed, five refused on their fields, from devnet
- [ ] `smoke-report.recorded.json`: 6/6, from recorded answers
- [ ] a receipt from the smoke is committed and confirmed on devnet
- [ ] your check server answers at a public URL and refuses a private `rpc_url`
- [ ] `docs/ISSUES.md` holds one real incident
- [ ] you ran the six minutes once and know which minute runs long
