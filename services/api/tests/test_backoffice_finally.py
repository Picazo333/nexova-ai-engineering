"""Backoffice fetch chains clear their loading state in a `finally` block.

Rubric 017 (ai-eng-error-handling): "Los bloques `finally` se usan correctamente
para limpiar el estado de carga." Each chain that sets a busy/loading flag must
end in `.finally(...)`, so the flag is cleared whatever the outcome.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

JS = Path(__file__).resolve().parents[3] / "uis" / "backoffice" / "js"

# file -> minimum number of fetch chains with a loading/busy flag
EXPECTED_FINALLY = {
    "app.js": 1,  # analyze form (setBusy)
    "auth.js": 2,  # login and register (setBusy)
    "suppliers.js": 4,  # list, create, rate, status
    "incidents-manager.js": 3,  # submit, summary, list
}


@pytest.mark.parametrize(("name", "minimum"), sorted(EXPECTED_FINALLY.items()))
def test_loading_chains_end_in_finally(name: str, minimum: int) -> None:
    source = (JS / name).read_text(encoding="utf-8")
    assert len(re.findall(r"\}\)\.finally\(function \(\)", source)) >= minimum


def test_no_then_after_catch_is_used_as_a_fake_finally() -> None:
    # `.catch(...).then(function () {` was the old pattern in app.js; it skips
    # the cleanup if the catch handler itself throws.
    source = (JS / "app.js").read_text(encoding="utf-8")
    assert "}).then(function () {\n      if (seq === requestSeq) {\n        setBusy(false);" not in source


def test_finally_does_not_wipe_the_incident_confirmation() -> None:
    # setBusy(false) empties the status text; the finally block must only reset
    # the button so the confirmation and error banners stay visible.
    source = (JS / "incidents-manager.js").read_text(encoding="utf-8")
    block = source.split("}).finally(function () {", 1)[1].split("});", 1)[0]
    assert "setBusy(" not in block
    assert "submit.disabled = false" in block
