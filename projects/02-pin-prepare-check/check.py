"""Project 02 self-check: are your pin, your prepare and your five checks written, and do
the recorded cases refuse on the right field?

    uv run python projects/02-pin-prepare-check/check.py

Standard library only, offline. It reads your source files, and runs the buyer on the
recorded answers (`--cases --recorded`, no network, no key). The score is LOCAL: it is
not sent anywhere and nothing is marked.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
LABELS = {"reads", "builds unsigned bytes", "changes state"}
TOOLS = ["list_stores", "prepare_purchase", "verify_signed_transaction", "submit_transaction"]


def still_todo(path: Path, function: str) -> bool:
    """True while the function's body still raises NotYetWritten."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    # The LAST definition is the one Python uses.
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function]
    if not defs:
        return True
    return any(
        isinstance(inner, ast.Raise) and "NotYetWritten" in ast.unparse(inner)
        for inner in ast.walk(defs[-1])
    )


def run_cases() -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "cases.json"
        env = {**os.environ, "GECKO_SOURCE": "recorded"}
        subprocess.run(
            [
                sys.executable,
                "-m",
                "buyer",
                "--cases",
                "--recorded",
                "--out",
                tmp,
                "--json",
                str(report),
            ],
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            timeout=120,
        )
        return json.loads(report.read_text()) if report.is_file() else []


def main() -> int:
    lines: list[tuple[bool, str, str]] = []

    tools = HERE / "tools.md"
    text = tools.read_text(encoding="utf-8").lower() if tools.is_file() else ""
    rows = {t: next((ln for ln in text.splitlines() if t in ln), "") for t in TOOLS}
    labelled = all(any(label in row for label in LABELS) for row in rows.values())
    only_submit = "changes state" in rows["submit_transaction"] and not any(
        "changes state" in rows[t] for t in TOOLS if t != "submit_transaction"
    )
    lines.append(
        (labelled and only_submit, "tools.md", "four tools labelled; only submit changes state")
    )

    lines.append(
        (
            not still_todo(ROOT / "buyer/intent.py", "parse_intent"),
            "parse_intent",
            "buyer/intent.py",
        )
    )
    for name in (
        "check_product",
        "check_price",
        "check_mint",
        "check_quantity",
        "check_destination",
    ):
        lines.append((not still_todo(ROOT / "buyer/check.py", name), name, "buyer/check.py"))

    results = {row["case"]: row for row in run_cases()}
    for case in ("2-ticket", "3-module", "4-tip", "5-beans", "6-latte"):
        row = results.get(case)
        refusal = (row or {}).get("outcome", {}).get("refusal") or {}
        both = refusal.get("asked") is not None and refusal.get("found") is not None
        ok = bool(row and row["match"] and both)
        want = (row or {}).get("expected", {}).get("field", "?")
        lines.append((ok, f"case {case}", f"refuses on {want}, naming both values"))

    width = max(len(name) for _, name, _ in lines)
    for ok, name, detail in lines:
        print(f"  {'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    passed = sum(ok for ok, _, _ in lines)
    print(f"\nlocal score: {passed}/{len(lines)}")
    print("This score is local. It is not sent anywhere, and project 02 is not marked.")
    return 0 if passed == len(lines) else 1


if __name__ == "__main__":
    sys.exit(main())
