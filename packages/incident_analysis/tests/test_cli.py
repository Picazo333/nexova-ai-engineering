"""The command-line script accepts a path and can write results.csv."""

from __future__ import annotations

import csv
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "analyze.py"
OFFICIAL = ROOT / "scripts" / "incidents-nexova.csv"


def _run(*args: str, stdin: str | None = None, cwd: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        cwd=cwd,
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def test_script_prints_briefing_figures_and_prompts(tmp_path: Path) -> None:
    completed = _run(str(OFFICIAL), stdin="n\n", cwd=tmp_path)
    assert completed.returncode == 0, completed.stderr
    assert "TOTAL RECORDS IN FILE .......... 100" in completed.stdout
    assert "Average score: 3.84 / 5.00" in completed.stdout
    assert "Export results to CSV? [y / n]:" in completed.stdout
    assert "Results were not exported." in completed.stdout
    assert not (tmp_path / "results.csv").exists()
    assert "@" not in completed.stdout
    assert "@" not in completed.stderr


def test_script_exports_one_row_per_metric(tmp_path: Path) -> None:
    completed = _run(str(OFFICIAL), stdin="y\n", cwd=tmp_path)
    assert completed.returncode == 0, completed.stderr
    exported = (tmp_path / "results.csv").read_text(encoding="utf-8")
    rows = list(csv.DictReader(exported.splitlines()))
    assert rows
    assert {row["metric"] for row in rows} >= {"total_records", "satisfaction_average"}
    assert "@" not in exported


def test_export_flag_does_not_need_stdin(tmp_path: Path) -> None:
    completed = _run(str(OFFICIAL), "--export", cwd=tmp_path)
    assert completed.returncode == 0, completed.stderr
    assert (tmp_path / "results.csv").is_file()
    assert "Export results to CSV? [y / n]: y" in completed.stdout


def test_missing_file_and_usage(tmp_path: Path) -> None:
    missing = _run(str(tmp_path / "absent.csv"), cwd=tmp_path)
    assert missing.returncode == 1
    assert "file not found" in missing.stderr
    usage = _run(cwd=tmp_path)
    assert usage.returncode == 2
