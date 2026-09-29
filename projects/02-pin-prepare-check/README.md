# Project 02: pin, prepare, check

**Tuesday 29 September, session 12 (MCP architecture).** About the last 15 minutes of
class, then homework. Offline: everything today runs on recorded devnet answers, with no
key and no network.

Today your buyer learns to say no. It pins what was asked **before** any bytes exist, asks
Gecko to prepare the purchase, and compares seven fields of the prepared bytes with the
pin. When one disagrees, it refuses and names the field and both values.

## What you ship

| File | What is in it |
|---|---|
| `projects/02-pin-prepare-check/tools.md` | every orquestra tool you used, labelled `reads`, `builds unsigned bytes` or `changes state` |
| `buyer/intent.py` | `parse_intent` written |
| `buyer/agent.py` | the `pin_intent`, `prepare` and `check` steps written |
| `buyer/check.py` | the five checks written: `check_product`, `check_price`, `check_mint`, `check_quantity`, `check_destination` |

Then `uv run python projects/02-pin-prepare-check/check.py` prints a local score out of 12.

## Steps

### 1. Label the tools (in class, 10 minutes)

In session 12 you saw that an MCP server is a list of tools, and that a tool's description
is text somebody else wrote. List the tools your buyer calls, and for each one say what it
does to the world. Use these three labels exactly:

| Label | Means |
|---|---|
| `reads` | answers from state; nothing is created, nothing expires |
| `builds unsigned bytes` | creates something to sign, which expires; nothing is on chain yet |
| `changes state` | after this, something happened on chain |

Write the table in `tools.md`, one row per tool: `list_stores`, `prepare_purchase`,
`verify_signed_transaction`, `submit_transaction`. Then add two lines: which tool you would
never let an agent call without a check first, and one sentence from a tool description or
a product name that tries to give your agent an order (look at `dev3pack-cafe`'s menu).

### 2. Pin (homework)

Read `buyer/intent.py`. `IntentRecord` is frozen: once pinned, it cannot change. Write
`parse_intent(ask, menu, context)`. Its docstring lists the decisions. Then write the
`pin_intent` step in `buyer/agent.py`: parse, then `pin(...)` to `run.out / "intents"`.

Run it on the recorded answers:

```bash
uv run buyer "one espresso" --recorded
```

The runner now gets past `pin` and stops at `prepare`, which is not written yet.

### 3. Prepare

Write the `prepare` step: one `prepare_purchase` call with the fields **from the pin**,
never from the ask. `Prepared.from_answer` reads the fields out of the unsigned bytes. Read
`buyer/prepared.py` to see why the bytes, and not Gecko's labels, are what you check.

### 4. Check

Write the `check` step (one line), then the five checks in `buyer/check.py`. The two worked
examples, `check_program` and `check_store`, show the shape: return `agree(...)` or
`refuse(field, asked, found)`. Each TODO's docstring says which use case must refuse.

The tests tell you when each one is right. They are expected failures (`x`) until you
write the check, and real tests after:

```bash
uv run pytest tests/test_your_work.py -v
```

### 5. Run the five cases

```bash
uv run buyer --cases --recorded
```

Cases 2 to 6 should now refuse on the field their fixture expects, with both values.
Case 1 passes every check and stops at `sign`: that is Wednesday.

## Done looks like

- [ ] `tools.md` labels the four tools, and `submit_transaction` is the only one that changes state
- [ ] `uv run buyer --cases --recorded` shows 5 refusals, each naming its field and both values
- [ ] case 1 passes all seven checks and stops at `sign`
- [ ] `uv run pytest` is green, with fewer `x` than this morning
- [ ] at least one test was red before it was green, and you can say which

## If you fall behind

Everything today is offline. The minimum for Friday is projects 01 and 02 on recorded
answers, plus one refusal you can explain.
