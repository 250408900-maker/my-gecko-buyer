# The projects

One per day of week 3, each sized for the last 10 to 15 minutes of a one-hour class plus
homework. Together they build the capstone you present on Friday 2 October.

| Day | Project | What you build | Local check |
|---|---|---|---|
| before | [00: your store, and a buyer that refuses well](00-your-store-and-buyer/README.md) | weekly challenge 2, in the course folder | the course notebook |
| Mon 28 | [01: read the menu, prepare, refuse](01-read-the-menu/README.md) | a real menu over MCP, one prepared purchase, one refusal; then your store on devnet | `python3 projects/01-read-the-menu/check.py` |
| Tue 29 | [02: pin, prepare, check](02-pin-prepare-check/README.md) | `parse_intent`, the pin and prepare steps, five field checks, on recorded answers | `uv run python projects/02-pin-prepare-check/check.py` |
| Wed 30 | [03: the part that says no](03-the-part-that-says-no/README.md) | your check as an MCP server with an SSRF guard; sign, verify, submit, receipt; your first devnet landing | `uv run python projects/03-the-part-that-says-no/check.py` |
| Thu 1 | [04: smoke, rollback, deploy](04-smoke-and-rollback/README.md) | `make smoke` on devnet, the recorded rollback, the server deployed, one real incident | `uv run python projects/04-smoke-and-rollback/check.py` |
| Fri 2 | the presentation | six minutes, one injected failure: [docs/DEFENCE.md](../docs/DEFENCE.md) | |

Every `check.py` prints a local score. It is not sent anywhere and nothing is marked by it.

They build on each other, so doing them in order is easier. Skipping one does not lock you
out of the next: every project runs on recorded answers (`GECKO_SOURCE=recorded`), and the
class store `dev3pack-cafe` stands in for yours until it is up.

Pull each one with `git pull upstream main`.
