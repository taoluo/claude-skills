#!/usr/bin/env bash
# validate_mermaid.sh — TLDR artifact mermaid block syntax check.
#
# This validates only the GENERATED TLDR artifact's mermaid blocks — NOT the source plan.
# Run after `/tldr-plan` produces the artifact.
#
# Usage:
#     bash validate_mermaid.sh <tldr-file>
#
# Exit codes:
#     0  - no Mermaid blocks present, OR all blocks compile
#     1  - at least one Mermaid block fails to parse
#     2  - dependency missing (node or npx unavailable) — NOT a hard failure;
#          caller treats exit 2 as SKIP

set -u

if [[ $# -ne 1 ]]; then
    echo "Usage: validate_mermaid.sh <tldr-file>" >&2
    exit 2
fi

TLDR_FILE="$1"

if [[ ! -f "$TLDR_FILE" ]]; then
    echo "FAIL: file not found: $TLDR_FILE" >&2
    exit 1
fi

# Dependency check — exit 2 (SKIP) if missing
if ! command -v node >/dev/null 2>&1 || ! command -v npx >/dev/null 2>&1; then
    echo "SKIP mermaid syntax check: npx unavailable; install Node.js for mermaid validation"
    exit 2
fi

# Derive scratch dir from filename stem
TLDR_BASENAME=$(basename "$TLDR_FILE" .md)
SCRATCH_DIR="tmp/${TLDR_BASENAME}-mermaid-check"

rm -rf "$SCRATCH_DIR"
mkdir -p "$SCRATCH_DIR"

# Extract mermaid blocks
export TLDR_FILE SCRATCH_DIR
COUNT=$(node -e '
const fs = require("fs");
const t = fs.readFileSync(process.env.TLDR_FILE, "utf8");
let i = 0;
for (const m of t.matchAll(/```mermaid\n([\s\S]*?)\n```/g)) {
    i++;
    fs.writeFileSync(`${process.env.SCRATCH_DIR}/diagram-${i}.mmd`, m[1]);
}
console.log(i);
')

if [[ "$COUNT" == "0" ]]; then
    echo "MERMAID OK (no Mermaid blocks present)"
    rm -rf "$SCRATCH_DIR"
    exit 0
fi

# Validate each block
fail=0
for f in "$SCRATCH_DIR"/*.mmd; do
    if npx -y @mermaid-js/mermaid-cli -i "$f" -o "${f%.mmd}.svg" -b transparent >/dev/null 2>&1; then
        echo "OK  $f"
    else
        echo "FAIL $f"
        fail=1
        npx -y @mermaid-js/mermaid-cli -i "$f" -o "${f%.mmd}.svg" -b transparent 2>&1 | grep -A2 "Error: Parse" || true
    fi
done

if [[ $fail -eq 0 ]]; then
    echo "MERMAID OK ($COUNT block(s) compiled)"
    rm -rf "$SCRATCH_DIR"
    exit 0
else
    echo "MERMAID VALIDATION FAILED" >&2
    # Leave scratch dir for debugging on failure
    exit 1
fi
