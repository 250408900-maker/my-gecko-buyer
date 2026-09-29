"""Project 04 self-check: the smoke, the rollback, the deploy, one incident, the rehearsal.

    uv run python projects/04-smoke-and-rollback/check.py

Standard library only, offline: it reads files you already produced. The score is
LOCAL: it is not sent anywhere and nothing is marked.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
CASES = ["1-espresso", "2-ticket", "3-module", "4-tip", "5-beans", "6-latte"]


def report(name: str) -> dict[str, dict]:
    path = ROOT / name
    if not path.is_file():
        return {}
    return {row["case"]: row for row in json.loads(path.read_text())}


def field(row: dict) -> str:
    outcome = row.get("outcome") or {}
    refusal = outcome.get("refusal") or {}
    return f"{outcome.get('kind')}:{refusal.get('field', '')}"


def main() -> int:
    lines: list[tuple[bool, str, str]] = []

    live = report("smoke-report.json")
    from_devnet = bool(live) and all(r.get("source") == "devnet" for r in live.values())
    landed = live.get("1-espresso", {})
    receipt = (landed.get("outcome") or {}).get("receipt") or {}
    lines.append(
        (from_devnet and len(live) == 6, "smoke ran on devnet", "smoke-report.json, six cases")
    )
    lines.append(
        (
            bool(landed.get("match")) and bool(receipt.get("reconciled")),
            "case 1 landed",
            "and its receipt reconciled with the ledger",
        )
    )
    refused = [c for c in CASES[1:] if live.get(c, {}).get("match")]
    lines.append((len(refused) == 5, "five refusals", f"{len(refused)}/5 refused on their field"))

    rolled = report("smoke-report.recorded.json")
    lines.append(
        (
            len(rolled) == 6
            and all(r["match"] for r in rolled.values())
            and all(r.get("source") == "recorded" for r in rolled.values()),
            "rollback 6/6",
            "smoke-report.recorded.json",
        )
    )
    same = [
        c for c in CASES if live.get(c) and rolled.get(c) and field(live[c]) == field(rolled[c])
    ]
    lines.append(
        (
            len(same) == 6,
            "one code path",
            f"live and recorded end the same way in {len(same)}/6 cases",
        )
    )

    sig = str(receipt.get("signature", ""))
    committed = bool(sig) and (ROOT / "receipts" / f"{sig[:8]}.json").is_file()
    lines.append((committed, "smoke receipt kept", f"receipts/{sig[:8] or '<sig8>'}.json"))

    deploy = HERE / "deploy.md"
    text = deploy.read_text(encoding="utf-8") if deploy.is_file() else ""
    lines.append(
        (
            bool(re.search(r"https://\S+", text)) and "check_purchase" in text,
            "deploy.md",
            "a public https URL and one check_purchase call",
        )
    )

    issues = (ROOT / "docs" / "ISSUES.md").read_text(encoding="utf-8")
    real = re.findall(r"^## 20\d\d-\d\d-\d\d", issues, flags=re.M)
    lines.append((bool(real), "ISSUES.md", f"{len(real)} dated incident(s)"))

    evaluation = (ROOT / "docs" / "EVAL_REPORT.md").read_text(encoding="utf-8")
    lines.append(("_/6" not in evaluation, "EVAL_REPORT.md", "the smoke numbers are filled in"))

    defence = (ROOT / "docs" / "DEFENCE.md").read_text(encoding="utf-8")
    rows = [ln for ln in defence.splitlines() if re.match(r"^\| \d:\d\d \|", ln)]
    said = [ln for ln in rows if ln.rstrip().rstrip("|").rsplit("|", 1)[-1].strip()]
    lines.append(
        (len(rows) == 7 and len(said) == 7, "DEFENCE.md", f"{len(said)}/7 minutes scripted")
    )

    width = max(len(name) for _, name, _ in lines)
    for ok, name, detail in lines:
        print(f"  {'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    passed = sum(ok for ok, _, _ in lines)
    print(f"\nlocal score: {passed}/{len(lines)}")
    print("This score is local. It is not sent anywhere, and project 04 is not marked.")
    return 0 if passed == len(lines) else 1


if __name__ == "__main__":
    sys.exit(main())
