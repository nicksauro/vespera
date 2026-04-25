"""CPCVConfig — frozen configuration for the CPCV engine.

Reads from spec yaml `cv_scheme` block (T002 v0.2.0 L147-154) via
``CPCVConfig.from_spec_yaml``. Rejects spec with `cv_scheme.type != "CPCV"`.

Authority: AFML Ch.12 §12.4 (CPCV) — N groups, k test groups per split,
embargo_sessions buffer, purge formula tag.

Story: T002.0c (T1)
"""

from __future__ import annotations

import hashlib
import math
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class CPCVConfig:
    """Immutable CPCV parameters.

    Attributes
    ----------
    n_groups:
        Number of contiguous temporal groups (AFML §12.3). T002: 10.
    k:
        Test groups per split (AFML §12.4). T002: 2.
    embargo_sessions:
        Sessions to drop after each test block (AFML §7.4.2). T002: 1.
    seed:
        RNG seed for any downstream stochastic component (bootstrap CI in
        ``vespera_metrics``). CPCV partition + purge + embargo are
        deterministic by construction; seed is plumbed through for R6.
    purge_formula_id:
        Canonical tag identifying the purge formula. T002 default:
        ``"AFML_7_4_1_intraday_H_eq_session"`` per Mira spec §8.
    """

    n_groups: int
    k: int
    embargo_sessions: int
    seed: int
    purge_formula_id: str = "AFML_7_4_1_intraday_H_eq_session"

    def __post_init__(self) -> None:
        if self.n_groups < 2:
            raise ValueError(
                f"n_groups must be >= 2 (got {self.n_groups}); "
                "CPCV is undefined for fewer than 2 groups."
            )
        if self.k < 1 or self.k >= self.n_groups:
            raise ValueError(
                f"k must satisfy 1 <= k < n_groups (got k={self.k}, "
                f"n_groups={self.n_groups})."
            )
        if self.embargo_sessions < 0:
            raise ValueError(
                f"embargo_sessions must be >= 0 (got {self.embargo_sessions})."
            )
        if not isinstance(self.purge_formula_id, str) or not self.purge_formula_id:
            raise ValueError(
                "purge_formula_id must be a non-empty string."
            )

    @property
    def n_paths(self) -> int:
        """Number of CPCV paths = C(n_groups, k)."""
        return math.comb(self.n_groups, self.k)

    def content_sha256(self) -> str:
        """Deterministic hash of the config for DeterminismStamp."""
        payload = (
            f"{self.n_groups}|{self.k}|{self.embargo_sessions}|"
            f"{self.seed}|{self.purge_formula_id}"
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    @classmethod
    def from_spec_yaml(
        cls,
        path: str | Path,
        *,
        seed: int | None = None,
    ) -> "CPCVConfig":
        """Build from a Mira spec yaml — reads ``cv_scheme`` block.

        Parameters
        ----------
        path:
            Path to the spec yaml (e.g.
            ``docs/ml/specs/T002-end-of-day-inventory-unwind-wdo-v0.2.0.yaml``).
        seed:
            Override seed. Default: read ``SPEC_SEED`` env var, fall back to 42.

        Raises
        ------
        ValueError:
            If ``cv_scheme.type != "CPCV"``.
        FileNotFoundError:
            If the spec file does not exist.
        """
        import yaml  # lazy import — only needed when constructing from yaml

        spec_path = Path(path)
        if not spec_path.exists():
            raise FileNotFoundError(f"Spec yaml not found: {spec_path}")

        with spec_path.open("r", encoding="utf-8") as f:
            spec: dict[str, Any] = yaml.safe_load(f)

        cv = spec.get("cv_scheme")
        if not isinstance(cv, dict):
            raise ValueError(
                f"Spec yaml at {spec_path} missing or malformed 'cv_scheme' block."
            )
        if cv.get("type") != "CPCV":
            raise ValueError(
                f"Unsupported cv_scheme.type: {cv.get('type')!r}; "
                "CPCVConfig only supports CPCV."
            )

        if seed is None:
            env_seed = os.environ.get("SPEC_SEED")
            seed = int(env_seed) if env_seed is not None else 42

        return cls(
            n_groups=int(cv["n_groups"]),
            k=int(cv["k"]),
            embargo_sessions=int(cv["embargo_sessions"]),
            seed=int(seed),
        )


__all__ = ["CPCVConfig"]
