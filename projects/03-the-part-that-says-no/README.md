# Project 03: the part that says no, as a server, and your first landed purchase

**Wednesday 30 September, session 13 (build and secure an MCP server).** The last 15
minutes of class, then homework. Today money moves, on devnet, with your own key.

Two things. First, your check becomes a small MCP server of its own, so any agent (not
only your buyer) can ask it "should I sign this?". Second, your buyer finishes the loop:
sign, verify, submit, and a receipt read from the ledger.

## What you ship

| File | What is in it |
|---|---|
| `server/guard.py` | `is_public_url(url) -> bool`, standard library only |
| `server/check_server.py` | an MCP server with one tool, `check_purchase` |
| `buyer/agent.py` | the `sign`, `verify`, `submit` and `write_the_receipt` steps written |
| `receipts/<sig8>.json` and `.md` | your first landed devnet purchase, committed |

Then `uv run python projects/03-the-part-that-says-no/check.py` prints a local score out
of 10 (add `--online` to also confirm your receipts' signatures on devnet).

## Steps

### 1. The guard (in class)

Session 13's rule: a server that fetches a URL it was handed can be pointed at things only
it can reach. Your server will accept an optional `rpc_url` (so it can re-read the store
itself), which makes it exactly that kind of server.

Write `server/guard.py` with `is_public_url(url: str) -> bool`. Standard library only
(`urllib.parse`, `ipaddress`, `socket`). It returns `False` for anything that is not
`https`, and for any host that is, or resolves to, a private, loopback, link-local,
reserved or multicast address. Decide what happens when the name does not resolve, and
write the decision in a comment.

The check script tries it against `http://127.0.0.1:8899`, `https://169.254.169.254/`,
`https://10.0.0.8/`, `file:///etc/passwd` and `https://localhost/`, and expects `False`
for every one.

### 2. The server

`server/check_server.py`, with `MCPServer` from `mcp.server.mcpserver` (the `mcp` 2.x package, already a dependency, the same one the course uses):

- one tool, `check_purchase(intent: dict, prepared_answer: dict, rpc_url: str | None = None)`;
- it rebuilds an `IntentRecord` and `Prepared.from_answer(...)`, runs `check_all`, and
  returns the verdict: `passed`, the `field` that refused, `asked` and `found`;
- if `rpc_url` is given and `is_public_url` says no, it refuses before fetching anything;
- it runs keyless: it never loads a signer, and it works on recorded answers
  (feed it `fixtures/cases/5-beans.json`'s pin and prepared answer and it must refuse on
  `quantity`).

Serve it with `uv run python server/check_server.py` (stdio) and call it from your
assistant, or from a ten-line client. Tomorrow you deploy it.

### 3. Finish the loop

Write the four remaining steps in `buyer/agent.py`: `sign`, `verify`, `submit`,
`write_the_receipt`. Each docstring names the call and its arguments. Offline first:

```bash
uv run buyer --cases --recorded     # 6/6: case 1 now lands, on the recorded answers
uv run buyer --cards --recorded     # 4/4: the Friday cards
```

### 4. Land it on devnet

You need Monday's setup (`scripts/devnet_setup.py`) and your store
(`scripts/create_store.py`). Then:

```bash
uv run buyer "one espresso" --devnet
```

The runner prints each step and ends with an explorer link. Open it. Then read the receipt
it wrote in `receipts/`: the buyer's delta, the store's delta and `total_purchases` came
from two ledger reads, not from what `submit_transaction` said. Commit the receipt.

If your store is not up yet, buy from the class store instead. You need class tokens for
that (ask the instructor to send your buyer some):

```bash
uv run buyer "one espresso" --devnet --store dev3pack-cafe --mint Eoqdd43nFQ9HzGq8HjBRVLCV6aTqCFRiwHy1ZVQheYSi
```

## What can go wrong, and what it means

| You see | It means | Do |
|---|---|---|
| `REFUSED on blockhash` | more than ~60 s passed between prepare and sign | run it again; never re-sign old bytes |
| `Gecko refused, receipt-failed` | the simulation failed: usually no SOL, or none of the token | check the buyer's balances, then run again |
| `REFUSED on cluster` | your RPC is not devnet | fix `GECKO_DEVNET_RPC`; the signer is right to refuse |
| `submit ... unconfirmed` | sent, not yet confirmed | look the signature up before doing anything else |

## Done looks like

- [ ] `is_public_url` refuses all five URLs above, and accepts a public https address (`https://8.8.8.8/`)
- [ ] your server refuses case 5 on `quantity`, keyless
- [ ] `--cases --recorded` is 6/6 and `--cards --recorded` is 4/4
- [ ] a devnet receipt is committed, and its explorer link opens
- [ ] `verify_signed_transaction` ran before every `submit_transaction` (it is the runner's order; say why on Friday)
