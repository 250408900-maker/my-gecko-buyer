# The buyer signs only when <N> fields match the pinned intent

*Your first decision record. Fill every section, keep the headings. The table's rows are
the seven fields `buyer/check.py` compares, plus the signed-bytes step; say in your own
words how and why for each one. Delete these italic lines when you are done.*

## Status and date

proposed | accepted, YYYY-MM-DD

## Context

My buyer holds a key that can pay. Gecko prepares the bytes; I sign them. What would a
wrong transaction cost, and which past incident shows it? (one number)

## Decision

Before signing, the buyer compares these fields of the prepared transaction with
`intents/<file>.json` and refuses on the first mismatch, naming the field and both values:

| Field | Compared how | Why this one |
|---|---|---|
| program | address equality, and no other program riding along | |
| store | address, derived from `['receipts', name]`, never a constant | |
| product | | |
| price_raw | integer, at or under the pinned budget | |
| mint | address, never the symbol | |
| quantity | integer | |
| destination | the store authority's token account for the pinned mint | |
| signed bytes | `verify_signed_transaction` before `submit_transaction` | |

## What this forbids

Signing on a partial match. Retrying a refusal unchanged. Signing without a passed
simulation. (Add what YOUR design forbids.)

## What I left out, and why

The field I chose not to check, and the risk I accept by not checking it.

## What would reverse this

The observation that would make me drop or add a field. Example: "if Gecko's verify
already binds price and mint, my own price check is duplicate work, and I drop it."

## What this does not prove

That my pin was right. The buyer faithfully signs a wrong request.
