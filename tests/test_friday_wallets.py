"""Friday's arithmetic only. The script's key generation is founder-run and is not run here."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("friday", ROOT / "scripts" / "friday_wallets.py")
assert spec and spec.loader
friday = importlib.util.module_from_spec(spec)
spec.loader.exec_module(friday)


def test_three_espressos_is_the_whole_usdc_balance() -> None:
    usdc_raw, _ = friday.funding(3, 100_000, 0.004)
    assert usdc_raw == 300_000  # a fourth espresso cannot be paid for, whatever the software does


def test_the_sol_covers_rent_three_purchases_and_the_margin() -> None:
    _, lamports = friday.funding(3, 100_000, 0.004)
    assert lamports == 890_880 + 3 * 1_493_440 + 4_000_000


def test_the_script_never_sends_or_signs() -> None:
    source = (ROOT / "scripts" / "friday_wallets.py").read_text()
    for forbidden in ("sendTransaction", "urlopen", "sign_message", "Transaction(", "buyer.chain"):
        assert forbidden not in source
