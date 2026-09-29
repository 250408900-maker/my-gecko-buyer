"""Project 03 self-check: the guard, the server, the loop, and a landed devnet receipt.

    uv run python projects/03-the-part-that-says-no/check.py
    uv run python projects/03-the-part-that-says-no/check.py --online   # also ask devnet

Standard library only. Offline unless you pass --online, which only READS devnet
(getSignatureStatuses). The score is LOCAL: not sent anywhere, and nothing is marked.
"""

from __future__ import annotations

import argparse
import ast
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEVNET = "https://api.devnet.solana.com"
SIGNATURE = re.compile(r"^[1-9A-HJ-NP-Za-km-z]{80,90}$")
PUBLIC = "https://8.8.8.8/"
MUST_REFUSE = [
    "http://127.0.0.1:8899",
    "https://169.254.169.254/",
    "https://10.0.0.8/",
    "file:///etc/passwd",
    "https://localhost/",
]


def still_todo(path: Path, function: str) -> bool:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    defs = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == function]
    if not defs:
        return True
    return any(
        isinstance(inner, ast.Raise) and "NotYetWritten" in ast.unparse(inner)
        for inner in ast.walk(defs[-1])
    )


def guard_refuses() -> tuple[bool, str]:
    path = ROOT / "server" / "guard.py"
    if not path.is_file():
        return False, "server/guard.py does not exist yet"
    spec = importlib.util.spec_from_file_location("guard", path)
    if not spec or not spec.loader:
        return False, "server/guard.py could not be loaded"
    guard = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(guard)
        let_through = [u for u in MUST_REFUSE if guard.is_public_url(u)]
    except Exception as exc:  # noqa: BLE001 - a self-check reports, it does not crash
        return False, f"is_public_url raised {type(exc).__name__}: {exc}"
    if let_through:
        return False, f"let through: {', '.join(let_through)}"
    return True, f"refuses all {len(MUST_REFUSE)} private or non-https URLs"


def guard_accepts() -> bool:
    """A guard that refuses everything is not a guard. A literal public IP needs no DNS."""
    spec = importlib.util.spec_from_file_location("guard", ROOT / "server" / "guard.py")
    if not spec or not spec.loader:
        return False
    guard = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(guard)
        return bool(guard.is_public_url(PUBLIC))
    except Exception:  # noqa: BLE001
        return False


def run_group(group: str) -> list[dict]:
    with tempfile.TemporaryDirectory() as tmp:
        report = Path(tmp) / "out.json"
        subprocess.run(
            [
                sys.executable,
                "-m",
                "buyer",
                f"--{group}",
                "--recorded",
                "--out",
                tmp,
                "--json",
                str(report),
            ],
            cwd=ROOT,
            env={**os.environ, "GECKO_SOURCE": "recorded"},
            capture_output=True,
            text=True,
            timeout=120,
        )
        return json.loads(report.read_text()) if report.is_file() else []


def devnet_receipts() -> list[dict]:
    out = []
    for path in sorted((ROOT / "receipts").glob("*.json")):
        data = json.loads(path.read_text())
        if data.get("source") == "devnet" and SIGNATURE.match(str(data.get("signature", ""))):
            out.append(data)
    return out


def on_devnet(signature: str) -> bool:
    body = json.dumps(
        {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSignatureStatuses",
            "params": [[signature], {"searchTransactionHistory": True}],
        }
    ).encode()
    request = urllib.request.Request(DEVNET, body, {"content-type": "application/json"})
    with urllib.request.urlopen(request, timeout=30) as response:
        status = json.loads(response.read())["result"]["value"][0]
    return bool(status and not status.get("err"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--online", action="store_true", help="confirm receipts on devnet")
    args = parser.parse_args()
    lines: list[tuple[bool, str, str]] = []

    ok, detail = guard_refuses()
    lines.append((ok, "guard refuses", detail))
    lines.append((ok and guard_accepts(), "guard accepts", f"a public https address ({PUBLIC})"))
    server = ROOT / "server" / "check_server.py"
    text = server.read_text(encoding="utf-8") if server.is_file() else ""
    lines.append(
        (
            "check_purchase" in text and "is_public_url" in text,
            "check server",
            "server/check_server.py defines check_purchase and uses the guard",
        )
    )

    for step in ("sign", "verify", "submit", "write_the_receipt"):
        lines.append(
            (not still_todo(ROOT / "buyer/agent.py", step), f"step {step}", "buyer/agent.py")
        )

    cases = {row["case"]: row for row in run_group("cases")}
    landed = cases.get("1-espresso", {})
    lines.append((bool(landed.get("match")), "case 1 lands", "recorded, receipt reconciled"))
    cards = run_group("cards")
    lines.append((len(cards) == 4 and all(c["match"] for c in cards), "cards 4/4", "recorded"))

    receipts = [r for r in devnet_receipts() if r.get("reconciled")]
    detail = f"{len(receipts)} reconciled devnet receipt(s) in receipts/"
    ok = bool(receipts)
    if ok and args.online:
        ok = all(on_devnet(r["signature"]) for r in receipts)
        detail += ", confirmed on devnet" if ok else ", NOT all found on devnet"
    lines.append((ok, "devnet receipt", detail))

    width = max(len(name) for _, name, _ in lines)
    for ok, name, detail in lines:
        print(f"  {'PASS' if ok else 'FAIL'}  {name.ljust(width)}  {detail}")
    passed = sum(ok for ok, _, _ in lines)
    print(f"\nlocal score: {passed}/{len(lines)}")
    print("This score is local. It is not sent anywhere, and project 03 is not marked.")
    return 0 if passed == len(lines) else 1


if __name__ == "__main__":
    sys.exit(main())
