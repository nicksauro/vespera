#!/usr/bin/env bash
# .githooks/install.sh
#
# One-shot bootstrap: point git at .githooks for this clone, make hooks executable.
# Run from repo root: `bash .githooks/install.sh`
#
# `core.hooksPath` is per-clone (not committable), so each developer must run this
# once after cloning. CI/L2 enforcement is server-side and non-skippable when
# branch protection (T6) is toggled — this script is a developer-experience aid,
# not a security boundary.
#
# Story: docs/stories/R15.2-canonical-invariant-hardening-impl.story.md (T3.4)

set -euo pipefail

REPO_ROOT=$(git rev-parse --show-toplevel)
cd "$REPO_ROOT"

if [[ ! -d .githooks ]]; then
    echo "ERROR: .githooks/ directory missing — run from repo root with R15.2 landed" >&2
    exit 1
fi

# Set the hooks path for this clone.
git config core.hooksPath .githooks
echo "[install] git config core.hooksPath .githooks"

# Pre-commit symlink: git looks for `pre-commit` (no extension) in core.hooksPath.
# Our hook is named `pre-commit-canonical-invariant` so it can coexist with
# future pre-commit hooks. Create a thin pre-commit dispatcher that invokes
# every hook starting with `pre-commit-`.
DISPATCHER=".githooks/pre-commit"
if [[ ! -f "$DISPATCHER" ]]; then
    cat > "$DISPATCHER" <<'EOF'
#!/usr/bin/env bash
# pre-commit dispatcher: runs every executable .githooks/pre-commit-* hook in order.
set -euo pipefail
REPO_ROOT=$(git rev-parse --show-toplevel)
shopt -s nullglob
for hook in "$REPO_ROOT"/.githooks/pre-commit-*; do
    if [[ -x "$hook" && -f "$hook" ]]; then
        echo "[pre-commit] running $(basename "$hook")"
        "$hook" "$@" || exit $?
    fi
done
EOF
    chmod +x "$DISPATCHER"
    echo "[install] created dispatcher $DISPATCHER"
fi

# Ensure hooks are executable (Windows often loses +x; chmod is a no-op there but
# the bit is recorded in the index when committed via core.fileMode handling).
chmod +x .githooks/pre-commit-canonical-invariant
chmod +x .githooks/install.sh
chmod +x "$DISPATCHER"

echo "[install] hooks installed at .githooks/, dispatcher in place."
echo "[install] Verify with: git config --get core.hooksPath"
