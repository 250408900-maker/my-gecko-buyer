# Issues

## 2026-10-01: Live smoke could not prepare purchases because the buyer lacked the class token accounts

- **What I saw:** Running `uv run buyer --cases --devnet --json smoke-report.json` produced `Gecko refused, receipt-failed` during `prepare`. The output reported that the `sender_token_account` did not exist on devnet and that the buyer held no token account for the store.
- **What was actually wrong:** The buyer wallet had not been funded with the class tokens required to run the live smoke against `dev3pack-cafe`. Case 3 also requires the class lookalike token.
- **How I found it:** The `prepare_purchase` error explicitly identified the missing `sender_token_account`. The recorded rollback then ran the same six cases successfully with `6/6`, showing that the buyer's check logic itself was working.
- **What I changed:** I did not change the buyer code because this was an environment/funding problem, not a logic bug. I used `uv run buyer --cases --json smoke-report.recorded.json` with `GECKO_SOURCE=recorded` to verify the rollback path while waiting for the required devnet tokens.
- **What it cost:** Time only. The failing cases stopped during prepare, before signing or submitting a transaction.
- **Would the checks have caught it?** No. The transaction could not be prepared because the required token account did not exist, so execution stopped before the seven purchase checks. Once preparation succeeds, those checks validate the prepared purchase against the pinned intent.