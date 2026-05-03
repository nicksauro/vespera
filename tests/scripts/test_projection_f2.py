"""AC4 — F2 documented divergence: buy_agent/sell_agent preserved as int64.

Tests:
  (i)  dtypes after projection are int64 (NOT cast to string)
  (ii) values byte-equal pre/post (NOT zero-padded)
  (iii) module docstring contains F2 ACCEPTED DIVERGENCE marker
  (iv) D-02 register reference present in docstring
"""
from __future__ import annotations

from pathlib import Path

import pyarrow as pa

import scripts.dll_backfill_projection as proj_mod
from scripts.dll_backfill_projection import project_table


def _storage_table(agents: list[int]) -> pa.Table:
    n = len(agents)
    return pa.table({
        "timestamp":  pa.array([0] * n, type=pa.timestamp("us")),
        "ticker":     pa.array(["WDOG23"] * n, type=pa.string()),
        "price":      pa.array([5000.0] * n, type=pa.float64()),
        "qty":        pa.array([1] * n, type=pa.int64()),
        "aggressor":  pa.array(["BUY"] * n, type=pa.string()),
        "buy_agent":  pa.array(agents, type=pa.int64()),
        "sell_agent": pa.array(agents, type=pa.int64()),
    })


def test_ac4_buy_agent_dtype_is_int64_not_string():
    t = _storage_table([308, 386, 90])
    projected, _ = project_table(t)
    assert projected.schema.field("buy_agent").type == pa.int64()
    assert projected.schema.field("sell_agent").type == pa.int64()


def test_ac4_no_string_coercion_no_zero_pad():
    agents = [1, 308, 9999]
    t = _storage_table(agents)
    projected, _ = project_table(t)
    out = projected.column("buy_agent").to_pylist()
    assert out == agents  # NOT ["00001", "00308", "09999"]
    # Verify type is integer, not string
    assert projected.column("buy_agent").type == pa.int64()


def test_ac4_byte_equal_pre_post_for_agents():
    agents = [42, 308, 386, 1000, 9999]
    t = _storage_table(agents)
    projected, _ = project_table(t)
    assert projected.column("buy_agent").equals(t.column("buy_agent"))
    assert projected.column("sell_agent").equals(t.column("sell_agent"))


def test_ac4_docstring_contains_f2_accepted_divergence_marker():
    doc = proj_mod.__doc__ or ""
    assert "F2 ACCEPTED DIVERGENCE" in doc, \
        "module docstring must contain F2 ACCEPTED DIVERGENCE marker"


def test_ac4_docstring_references_d02_or_council_2026_05_03():
    doc = proj_mod.__doc__ or ""
    # Either D-02 register OR Council 2026-05-03 ratification reference.
    has_ref = ("D-02" in doc) or ("2026-05-03" in doc) or ("AUDIT-2026-05-03" in doc)
    assert has_ref, "module docstring must trace F2 to D-02 / Council 2026-05-03"


def test_ac4_readme_companion_exists():
    here = Path(__file__).resolve().parent.parent.parent
    readme = here / "scripts" / "dll_backfill_projection.README.md"
    assert readme.exists(), f"README companion missing: {readme}"
    text = readme.read_text(encoding="utf-8")
    assert "F2" in text
    assert "Council 2026-05-03" in text or "COUNCIL-2026-05-03" in text
