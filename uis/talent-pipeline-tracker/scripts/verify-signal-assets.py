#!/usr/bin/env python3
"""Comprueba que los assets SIGNAL copiados no han cambiado de bytes."""

import hashlib
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
EXPECTED = {
    "styles/tokens.css": "9b1f68b4a44d79f0990778953c208af96c08e5bd8bd4f70b16697fbb24f51e52",
    "styles/tokens.json": "aee1644faad9743f1fd6278453f7dc5fc7ddd31572a790ad068ec23afad202fa",
    "styles/motion.css": "36b2f4d56439871d1ae46d4e2ad3e3d0d0b5da7a2700c503d4382247784b2f5c",
    "styles/motion.json": "c13a8241b6a7c8d638fee1d5a4457b37da5141d2b563e58541297637a63aa5c5",
    "public/brand/lockups/signal-horizontal.svg": "85459232bf51e7bf7c94225fd4f2cd6b71a681b6d701cb4ffd6d2a142cf57a81",
    "public/brand/lockups/signal-stacked.svg": "11314b300284db342bc15a7c7695c23199f65f68178af45586b62d01e9ea133a",
}

failed = False
for relative, digest in EXPECTED.items():
    path = ROOT / relative
    if not path.is_file():
        print("FAIL", relative, "missing")
        failed = True
        continue
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual != digest:
        print("FAIL", relative, actual)
        failed = True
    else:
        print("PASS", relative, actual)

sys.exit(1 if failed else 0)
