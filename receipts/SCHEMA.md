# receipts/

One pair per landed purchase, named by the first 8 characters of the signature:
`<sig8>.json` (the data) and `<sig8>.md` (the same, for a person). Written by the runner
from `buyer/receipt.py`, from two ledger reads, never from the submit answer.

| Field | What it is |
|---|---|
| `ask` | what the person asked, word for word |
| `network` | `devnet` (Friday participants: `mainnet`) |
| `store`, `product` | the store name as pinned, and the product in the signed bytes |
| `signature`, `explorer`, `slot` | the transaction, a link anyone can open, and where it landed |
| `price_raw`, `mint` | the simulated amount leaving the buyer, and the mint as an address |
| `buyer_delta_raw` | buyer's token balance after minus before. Should be `-price_raw` |
| `store_delta_raw` | store's token balance after minus before. Should be `+price_raw` |
| `total_purchases_before`, `_after` | the store's counter, read twice. Should go n to n+1 |
| `intent_pinned_at` | when the pin was written; earlier than the prepare |
| `source` | `devnet`, `mainnet` or `recorded` |
| `reconciled`, `findings` | true only when every delta matched; otherwise each mismatch, in words |

Keep at least one devnet receipt committed before Friday: it covers a network failure on
stage, said out loud if you use it.
