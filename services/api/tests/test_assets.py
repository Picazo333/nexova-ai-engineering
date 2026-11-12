"""SIGNAL assets copied into the backoffice keep their original bytes."""

from __future__ import annotations

import gzip
import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BACKOFFICE = ROOT / "uis" / "backoffice"

EXPECTED = {
    "tokens/tokens.css": "9b1f68b4a44d79f0990778953c208af96c08e5bd8bd4f70b16697fbb24f51e52",
    "tokens/tokens.json": "aee1644faad9743f1fd6278453f7dc5fc7ddd31572a790ad068ec23afad202fa",
    "tokens/motion.css": "36b2f4d56439871d1ae46d4e2ad3e3d0d0b5da7a2700c503d4382247784b2f5c",
    "tokens/motion.json": "c13a8241b6a7c8d638fee1d5a4457b37da5141d2b563e58541297637a63aa5c5",
    "brand/lockups/signal-horizontal.svg": "85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81",
    "brand/lockups/signal-stacked.svg": "11314b300284db342bc15a7c7695c23199f65f68178af45586b62d01e9ea133a",
    "brand/README.md": "8eab7f78a2b35a5d5f439869f7e93c98f14917398cf2e877296316e57b41451a",
}


def test_signal_asset_hashes() -> None:
    for relative, expected in EXPECTED.items():
        digest = hashlib.sha256((BACKOFFICE / relative).read_bytes()).hexdigest()
        assert digest == expected, relative


def test_front_end_transfer_budgets() -> None:
    css = b"".join(
        (BACKOFFICE / name).read_bytes()
        for name in ("tokens/tokens.css", "tokens/motion.css", "css/app.css")
    )
    js = b"".join(
        (BACKOFFICE / "js" / name).read_bytes()
        for name in ("motion-pref.js", "app.js", "auth.js", "suppliers.js", "incidents-manager.js")
    )
    assert len(gzip.compress(css)) <= 40 * 1024
    assert len(gzip.compress(js)) <= 170 * 1024
