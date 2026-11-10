"""Shared Nexova incident rules.

The CSV checks come from the incidents-file-analyzer briefing. The model
checks and the CSV-to-model maps come from the centralized-incident-manager
briefing. ``scripts/analyze.py``, ``scripts/seed_incidents.py`` and the API
import this package; they do not keep a second copy of the rules.
"""

from nexova_incidents.csv_rules import AnalysisError, csv_rows, row_flags
from nexova_incidents.model import (
    BRANCHES,
    CATEGORIES,
    ORIGINS,
    STATUSES,
    validate_create,
    validate_filters,
    validate_transition,
)
from nexova_incidents.transform import prepare_csv

__all__ = [
    "BRANCHES",
    "CATEGORIES",
    "ORIGINS",
    "STATUSES",
    "AnalysisError",
    "csv_rows",
    "prepare_csv",
    "row_flags",
    "validate_create",
    "validate_filters",
    "validate_transition",
]
