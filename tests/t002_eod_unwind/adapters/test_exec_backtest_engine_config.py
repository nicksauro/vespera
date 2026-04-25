"""Tests for BacktestCosts.from_engine_config — Beckett T002.0e.

Validates engine-config.yaml wiring to Nova cost atlas v1.0.0:
  - happy path loads atlas-canonical values
  - SHA mismatch fails fast (atlas drift)
  - missing required fields raise EngineConfigInvalid
  - back-compat default constructor still works (deprecated path)
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from textwrap import dedent

import pytest
import yaml

from packages.t002_eod_unwind.adapters.exec_backtest import (
    BacktestCosts,
    CostAtlasShaMismatch,
    CostAtlasVersionMismatch,
    EngineConfigInvalid,
)


# =====================================================================
# Helpers
# =====================================================================

ATLAS_BODY_MIN = dedent(
    """\
    atlas_version: "1.0.0"
    product:
      tick_size_points: 0.5
      contract_multiplier_brl_per_point: 10.00
      contract_size_usd: 10000
    costs:
      brokerage:
        per_contract_one_way: 0.00
      exchange_fees:
        per_contract_one_way: 1.23
        breakdown:
          emolumentos_brl: 0.43
          registro_brl: 0.80
          liquidacao_brl: 0.00
      tax_day_trade:
        ir_rate: 0.20
        irrf_daily_rate: 0.01
        treatment_choice: "post_hoc_on_monthly_net_gain"
        darf_code: 8468
    """
)


def _sha256_lf_text(text: str) -> str:
    return hashlib.sha256(text.replace("\r\n", "\n").encode("utf-8")).hexdigest()


def _write_atlas(dir_: Path, body: str = ATLAS_BODY_MIN) -> tuple[Path, str]:
    """Write atlas under tmp/docs/backtest/ to mirror real layout, return (path, sha)."""
    atlas_dir = dir_ / "docs" / "backtest"
    atlas_dir.mkdir(parents=True, exist_ok=True)
    atlas_path = atlas_dir / "nova-cost-atlas.yaml"
    # write as binary with LF to ensure stable hash regardless of host EOL
    atlas_path.write_bytes(body.encode("utf-8"))
    sha = _sha256_lf_text(body)
    return atlas_path, sha


def _write_engine_config(
    dir_: Path,
    *,
    atlas_path_rel: str = "docs/backtest/nova-cost-atlas.yaml",
    atlas_version_lock: str = "1.0.0",
    atlas_sha256_lock: str,
    drop_keys: list[str] | None = None,
    slippage_overrides: dict | None = None,
) -> Path:
    cfg = {
        "engine_config_version": "1.0.0",
        "cost_atlas_ref": {
            "path": atlas_path_rel,
            "atlas_version_lock": atlas_version_lock,
            "atlas_sha256_lock": atlas_sha256_lock,
            "policy_on_version_mismatch": "fail_fast",
        },
        "cost_components": {
            "brokerage": {
                "from": "costs.brokerage.per_contract_one_way",
                "expected_brl": 0.00,
            },
            "exchange_fees": {
                "from": "costs.exchange_fees.per_contract_one_way",
                "expected_brl": 1.23,
            },
        },
        "slippage_model": {
            "type": "roll_half_plus_extra_ticks",
            "roll_spread_half_points": 0.5,
            "slippage_extra_ticks": 1,
        },
    }
    if slippage_overrides:
        cfg["slippage_model"].update(slippage_overrides)
    if drop_keys:
        for k in drop_keys:
            cfg.pop(k, None)

    cfg_dir = dir_ / "docs" / "backtest"
    cfg_dir.mkdir(parents=True, exist_ok=True)
    cfg_path = cfg_dir / "engine-config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding="utf-8")
    return cfg_path


# =====================================================================
# Happy path
# =====================================================================

def test_loads_engine_config_with_valid_sha(tmp_path: Path) -> None:
    """Atlas SHA matches lock; from_engine_config returns canonical Nova values."""
    _, sha = _write_atlas(tmp_path)
    cfg_path = _write_engine_config(tmp_path, atlas_sha256_lock=sha)

    costs = BacktestCosts.from_engine_config(cfg_path)

    # Atlas-canonical values (Nova v1.0.0)
    assert costs.brokerage_per_contract_side_rs == pytest.approx(0.00)
    assert costs.exchange_fees_per_contract_side_rs == pytest.approx(1.23)
    # Slippage preserved as Beckett deterministic default
    assert costs.roll_spread_half_points == pytest.approx(0.5)
    assert costs.slippage_extra_ticks == 1


def test_loads_engine_config_handles_crlf_atlas(tmp_path: Path) -> None:
    """Atlas with CRLF line endings still hashes to canonical LF SHA."""
    body_crlf = ATLAS_BODY_MIN.replace("\n", "\r\n")
    atlas_path, _ = _write_atlas(tmp_path)
    atlas_path.write_bytes(body_crlf.encode("utf-8"))  # overwrite with CRLF

    sha_lf = _sha256_lf_text(ATLAS_BODY_MIN)  # canonical LF hash
    cfg_path = _write_engine_config(tmp_path, atlas_sha256_lock=sha_lf)

    costs = BacktestCosts.from_engine_config(cfg_path)
    assert costs.exchange_fees_per_contract_side_rs == pytest.approx(1.23)


# =====================================================================
# Failure modes — atlas drift
# =====================================================================

def test_rejects_engine_config_with_drifted_atlas_sha(tmp_path: Path) -> None:
    """If atlas content drifts from lock, loader fails fast."""
    _, real_sha = _write_atlas(tmp_path)
    bogus_sha = "0" * 64
    assert real_sha != bogus_sha
    cfg_path = _write_engine_config(tmp_path, atlas_sha256_lock=bogus_sha)

    with pytest.raises(CostAtlasShaMismatch, match="SHA256 mismatch"):
        BacktestCosts.from_engine_config(cfg_path)


def test_rejects_atlas_version_mismatch(tmp_path: Path) -> None:
    """Atlas v1.0.0 but engine-config locks v0.9.0 -> fail."""
    _, sha = _write_atlas(tmp_path)
    cfg_path = _write_engine_config(
        tmp_path, atlas_sha256_lock=sha, atlas_version_lock="0.9.0"
    )

    with pytest.raises(CostAtlasVersionMismatch, match="version mismatch"):
        BacktestCosts.from_engine_config(cfg_path)


# =====================================================================
# Failure modes — invalid engine-config
# =====================================================================

def test_rejects_missing_required_fields(tmp_path: Path) -> None:
    """Engine-config without cost_components -> EngineConfigInvalid."""
    _, sha = _write_atlas(tmp_path)
    cfg_path = _write_engine_config(
        tmp_path, atlas_sha256_lock=sha, drop_keys=["cost_components"]
    )

    with pytest.raises(EngineConfigInvalid, match="cost_components"):
        BacktestCosts.from_engine_config(cfg_path)


def test_rejects_missing_slippage_model(tmp_path: Path) -> None:
    """Engine-config without slippage_model -> EngineConfigInvalid."""
    _, sha = _write_atlas(tmp_path)
    cfg_path = _write_engine_config(
        tmp_path, atlas_sha256_lock=sha, drop_keys=["slippage_model"]
    )

    with pytest.raises(EngineConfigInvalid, match="slippage_model"):
        BacktestCosts.from_engine_config(cfg_path)


def test_rejects_missing_atlas_file(tmp_path: Path) -> None:
    """Engine-config points at non-existent atlas -> FileNotFoundError."""
    _, sha = _write_atlas(tmp_path)
    cfg_path = _write_engine_config(
        tmp_path,
        atlas_path_rel="docs/backtest/does-not-exist.yaml",
        atlas_sha256_lock=sha,
    )

    with pytest.raises(FileNotFoundError, match="atlas not found"):
        BacktestCosts.from_engine_config(cfg_path)


def test_rejects_missing_engine_config_file(tmp_path: Path) -> None:
    """Bad path -> FileNotFoundError."""
    with pytest.raises(FileNotFoundError, match="engine-config not found"):
        BacktestCosts.from_engine_config(tmp_path / "nope.yaml")


# =====================================================================
# Back-compat — direct constructor still works
# =====================================================================

def test_back_compat_default_constructor_still_works() -> None:
    """Legacy BacktestCosts() with placeholder defaults must still construct.

    Tests/users that called BacktestCosts() before T002.0e wire keep working;
    the [DEPRECATED] tag in docstring guides migration but doesn't break.
    """
    costs = BacktestCosts()
    # Placeholder values from legacy defaults (NOT atlas-canonical)
    assert costs.brokerage_per_contract_side_rs == pytest.approx(0.25)
    assert costs.exchange_fees_per_contract_side_rs == pytest.approx(0.35)
    assert costs.roll_spread_half_points == pytest.approx(0.5)
    assert costs.slippage_extra_ticks == 1


def test_back_compat_explicit_overrides_still_work() -> None:
    """Direct kwargs still construct (used in existing test suite)."""
    costs = BacktestCosts(
        brokerage_per_contract_side_rs=0.00,
        exchange_fees_per_contract_side_rs=1.23,
        roll_spread_half_points=0.5,
        slippage_extra_ticks=1,
    )
    assert costs.brokerage_per_contract_side_rs == pytest.approx(0.00)
    assert costs.exchange_fees_per_contract_side_rs == pytest.approx(1.23)


# =====================================================================
# Real engine-config + real atlas integration
# =====================================================================

def test_loads_real_engine_config_against_real_atlas() -> None:
    """End-to-end: docs/backtest/engine-config.yaml + nova-cost-atlas.yaml v1.0.0.

    This is the gate that proves the wired config matches the committed atlas.
    If atlas SHA drifts (Nova republishes content), this test fails — Beckett
    must re-audit before bumping engine-config lock.
    """
    repo_root = Path(__file__).resolve().parents[3]
    cfg_path = repo_root / "docs" / "backtest" / "engine-config.yaml"
    atlas_path = repo_root / "docs" / "backtest" / "nova-cost-atlas.yaml"

    if not (cfg_path.is_file() and atlas_path.is_file()):
        pytest.skip("engine-config.yaml or atlas missing in repo")

    costs = BacktestCosts.from_engine_config(cfg_path)
    # Nova atlas v1.0.0 canonical values
    assert costs.brokerage_per_contract_side_rs == pytest.approx(0.00)
    assert costs.exchange_fees_per_contract_side_rs == pytest.approx(1.23)
    assert costs.roll_spread_half_points == pytest.approx(0.5)
    assert costs.slippage_extra_ticks == 1
