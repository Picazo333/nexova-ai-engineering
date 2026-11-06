#!/usr/bin/env python3
"""Analyse a Nexova support-ticket CSV.

The validation rules live in ``packages/incident_analysis`` and are the same
ones the API uses. Customer emails are never printed or written to
``results.csv``.

Example, from this directory:

    python analyze.py incidents-nexova.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

PACKAGES = Path(__file__).resolve().parents[1] / "packages"
if str(PACKAGES) not in sys.path:
    sys.path.insert(0, str(PACKAGES))

from incident_analysis.engine import AnalysisError, analyze_bytes  # noqa: E402

YES = {"y", "yes", "s", "si", "sí"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Analyse a Nexova support-ticket CSV. Emails are never printed."
    )
    parser.add_argument("csv_path", help="Path to the UTF-8 CSV")
    choice = parser.add_mutually_exclusive_group()
    choice.add_argument("--export", action="store_true", help="Write results.csv without asking")
    choice.add_argument("--no-export", action="store_true", help="Do not write results.csv")
    args = parser.parse_args(argv)

    path = Path(args.csv_path)
    if not path.is_file():
        print(f"error: file not found: {path}", file=sys.stderr)
        return 1
    try:
        report = analyze_bytes(path.read_bytes(), path.name)
    except AnalysisError as exc:
        print(f"error: {exc.message_en}", file=sys.stderr)
        return 1
    except OSError:
        print("error: the file could not be read.", file=sys.stderr)
        return 1

    sys.stdout.write(report.console())
    if _wants_export(args):
        destination = Path.cwd() / "results.csv"
        destination.write_text(report.csv_text(), encoding="utf-8", newline="\n")
        print(f"Results saved to {destination.name}")
    else:
        print("Results were not exported.")
    return 0


def _wants_export(args: argparse.Namespace) -> bool:
    if args.export:
        print("Export results to CSV? [y / n]: y")
        return True
    if args.no_export:
        print("Export results to CSV? [y / n]: n")
        return False
    prompt = "Export results to CSV? [y / n]: "
    if sys.stdin.isatty():
        answer = input(prompt)
    else:
        print(prompt, end="", flush=True)
        answer = sys.stdin.readline()
        if answer == "":
            print("n")
            answer = "n"
    return answer.strip().lower() in YES


if __name__ == "__main__":
    raise SystemExit(main())
