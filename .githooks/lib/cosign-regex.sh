#!/usr/bin/env bash
# .githooks/lib/cosign-regex.sh
#
# Single-source-of-truth for the canonical-invariant cosign-flag regex literal.
# Sourced by:
#   - .githooks/pre-commit-canonical-invariant (L1 hook)
#   - .github/workflows/canonical-invariant-protection.yml (L2 CI)
#
# Story: docs/stories/R15.2-canonical-invariant-hardening-impl.story.md (AC2)
# Authority: ADR-5 §4.1 ratification (3-disjunct regex extension to VCS boundary).
# Source: MWF-20260422-1 L213 (`^MC-\d{8}-\d+$` literal) generalised to 3 disjuncts.
#
# DO NOT duplicate this regex elsewhere. Drift between hook and CI is detectable
# via single-file sha verification of THIS file.

# shellcheck disable=SC2034  # exported for sourcing callers
export COSIGN_REGEX='^(MWF-[0-9]{8}-[0-9]+|R1-1-WAIVER-[0-9]{8}-[0-9]+|MC-[0-9]{8}-[0-9]+)$'
