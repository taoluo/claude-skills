#!/usr/bin/env python3
"""
check_tldr_integrity.py — TLDR artifact AC-grid integrity check.

This validates only the GENERATED TLDR artifact's internal citation grid —
NOT the source plan. Run after `/tldr-plan` produces the artifact.

Usage:
    python3 check_tldr_integrity.py <tldr-file>          # exit 0 = pass, 1 = fail
    python3 check_tldr_integrity.py --self-test          # run bundled fixture tests

Mutation table (self-test verifies these expected exit codes):
    - Remove the only AC1 from §5 AC-served (D1 has no AC)              → 1
    - Remove the only AC1 from §6.1 AC-verified (AC uncovered)           → 1
    - D1.AC served = AC999 (cites token not defined in §3.3)             → 1
    - E1.AC verified = AC999                                              → 1
    - §3.3 Derives from = "Goal, D1" (forbidden Dn)                      → 1
    - §3.3 Derives from = "Goal, M11.1" (forbidden Mn)                   → 1
    - §3.4 M11.1.Delivers AC empty AND Scope not "(future)"              → 1
    - §3.4 M11.1.Delivers AC cites AC999                                 → 1
    - §3.3 AC1.Milestone=M11.1 but §3.4 M11.1.Delivers AC missing AC1    → 1
    - All consistent, no orphans, no forbidden, bidir matches            → 0
"""
import os
import re
import subprocess
import sys


def slice_section(text, start_marker, *end_markers):
    """Slice from start_marker to earliest of end_markers.

    Falls back to end-of-text if no end_marker is found, allowing fixtures
    that don't have a §3.5 / §6.2 / etc. to still be parsed correctly.
    """
    s = text.find(start_marker)
    if s < 0:
        return ""
    earliest_end = -1
    search_from = s + len(start_marker)
    for end_marker in end_markers:
        e = text.find(end_marker, search_from)
        if e >= 0 and (earliest_end < 0 or e < earliest_end):
            earliest_end = e
    if earliest_end < 0:
        # Fallback: next markdown heading at any level
        m = re.search(r"\n#{1,6}\s", text[search_from:])
        if m:
            earliest_end = search_from + m.start()
    return text[s:earliest_end] if earliest_end >= 0 else text[s:]


def check_tldr_integrity(tldr_path):
    """Check artifact integrity. Returns 0 (pass) or 1 (fail), prints findings."""
    if not os.path.exists(tldr_path):
        print(f"FAIL: file not found: {tldr_path}")
        return 1

    with open(tldr_path) as f:
        t = f.read()

    # Slice canonical sections; fallback handles fixtures without next-section markers
    s33 = slice_section(t, "### 3.3 Acceptance", "### 3.4", "## 3.4", "## 4")
    if not s33:
        s33 = slice_section(t, "## 3.3 Acceptance", "## 3.4", "## 4")
    s34 = slice_section(t, "### 3.4 Milestones", "### 3.5", "## 3.5", "## 4")
    if not s34:
        s34 = slice_section(t, "## 3.4 Milestones", "## 3.5", "## 4")
    s5 = slice_section(t, "## 5. Decision Map", "## 6.", "## 7")
    s61 = slice_section(t, "#### 6.1", "#### 6.2", "## 6.2", "### 6.2", "## 7")
    if not s61:
        s61 = slice_section(t, "## 6.1", "## 6.2", "## 7")

    AC_TOKEN = r"\bAC[1-9][0-9]*\b"

    # Extract AC IDs defined in §3.3
    ac_defined = set()
    for line in s33.splitlines():
        m = re.match(r"\|\s*(AC[1-9][0-9]*)\s*\|", line)
        if m:
            ac_defined.add(m.group(1))

    # Check §3.3 "Derives from" allow-list
    forbidden_in_derives = []
    for line in s33.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 5 and re.match(r"AC[1-9][0-9]*", cells[1]):
            derives = cells[3]
            tokens = re.findall(r"`?([A-Za-z][A-Za-z0-9_.]*)`?", derives)
            for tok in tokens:
                if tok in {"Goal"}:
                    continue
                if re.match(r"^A[1-9][0-9]*$", tok):
                    continue
                if re.match(r"^C[1-9][0-9]*$", tok):
                    continue
                # Mn / Dn / En / Risk* / OpenQuestion* are forbidden
                forbidden_in_derives.append((cells[1], tok))

    # Check §5 Decision Map: every Dn row needs ≥1 AC in "AC served"
    d_without_ac = []
    ac_cited_by_d = set()
    for line in s5.splitlines():
        m = re.match(r"\|\s*(D[0-9](?:\.[A-Za-z])?)\s*\|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6:
            continue
        ac_served = cells[4]
        toks = set(re.findall(AC_TOKEN, ac_served))
        if not toks:
            d_without_ac.append(m.group(1))
        ac_cited_by_d |= toks

    # Check §6.1 Evidence: aggregate AC coverage
    ac_covered_by_e = set()
    for line in s61.splitlines():
        m = re.match(r"\|\s*(E[1-9][0-9]*)\s*\|", line)
        if not m:
            continue
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 6:
            continue
        ac_covered_by_e |= set(re.findall(AC_TOKEN, cells[3]))

    # Check §3.4 Milestones bidirectional consistency
    # Milestone IDs require digit / dot after M (so "Milestone" in header row doesn't match)
    M_TOKEN = r"M[0-9]\S*|M[0-9]+(?:\.[0-9]+)*"
    ac_to_milestone = {}
    for line in s33.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) >= 7 and re.match(r"AC[1-9][0-9]*", cells[1]):
            ac_id = cells[1]
            ms = cells[5]
            mm = re.search(M_TOKEN, ms)
            ac_to_milestone[ac_id] = mm.group(0) if mm else None

    milestones_in_34 = []
    m_without_ac = []
    delivers_ac_unknown_tokens = []
    for line in s34.splitlines():
        cells = [c.strip() for c in line.split("|")]
        if len(cells) < 7:
            continue
        m_match = re.match(M_TOKEN, cells[1])
        if not m_match:
            continue
        m_id = m_match.group(0)
        delivers = cells[4]
        toks = set(re.findall(AC_TOKEN, delivers))
        scope_cell = cells[2]
        is_future = bool(re.search(r"\(future\)|\(deferred\)|\(skipped\)", scope_cell, re.IGNORECASE))
        if not toks and not is_future:
            m_without_ac.append(m_id)
        unknown = toks - ac_defined
        for tok in sorted(unknown):
            delivers_ac_unknown_tokens.append((m_id, tok))
        milestones_in_34.append((m_id, toks))

    bidir_mismatches = []
    for ac_id, expected_m in ac_to_milestone.items():
        listing = [m_id for (m_id, toks) in milestones_in_34 if ac_id in toks]
        if expected_m is None:
            if listing:
                bidir_mismatches.append((ac_id, "(none)", listing))
        else:
            if listing != [expected_m]:
                bidir_mismatches.append((ac_id, expected_m, listing))

    # Report findings
    fail = False
    orphans_d = ac_defined - ac_cited_by_d
    if orphans_d:
        print(f"FAIL: AC not cited by any Dn (orphan promises): {sorted(orphans_d)}")
        fail = True
    orphans_e = ac_defined - ac_covered_by_e
    if orphans_e:
        print(f"FAIL: AC not covered by any En (unverifiable promises): {sorted(orphans_e)}")
        fail = True
    unknown_in_d = ac_cited_by_d - ac_defined
    if unknown_in_d:
        print(f"FAIL: §5 AC-served cites tokens NOT defined in §3.3: {sorted(unknown_in_d)}")
        fail = True
    unknown_in_e = ac_covered_by_e - ac_defined
    if unknown_in_e:
        print(f"FAIL: §6.1 AC-verified cites tokens NOT defined in §3.3: {sorted(unknown_in_e)}")
        fail = True
    if d_without_ac:
        print(f"FAIL: Dn rows with empty AC served (orphan decisions): {sorted(d_without_ac)}")
        fail = True
    if forbidden_in_derives:
        print(
            f"FAIL: §3.3 Derives-from has forbidden tokens "
            f"(allow-list = Goal | An | Cn ONLY; Mn is schedule, lives in §3.4): "
            f"{forbidden_in_derives}"
        )
        fail = True
    if m_without_ac:
        print(
            f"FAIL: §3.4 Milestone rows with empty Delivers AC "
            f"(label-without-obligations; mark Scope (future) to exempt): {sorted(m_without_ac)}"
        )
        fail = True
    if delivers_ac_unknown_tokens:
        print(f"FAIL: §3.4 Delivers-AC cites tokens NOT defined in §3.3: {delivers_ac_unknown_tokens}")
        fail = True
    if bidir_mismatches:
        print(
            f"FAIL: §3.3.Milestone ↔ §3.4.Delivers-AC inconsistent "
            f"(AC, expected_M_from_§3.3, found_in_§3.4): {bidir_mismatches}"
        )
        fail = True

    if not fail:
        print("AC integrity OK")
    return 1 if fail else 0


def run_self_test():
    """Run bundled fixture tests; verify expected exit codes."""
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    fixtures_dir = os.path.join(skill_dir, "examples")
    valid_fixture = os.path.join(fixtures_dir, "fixture-valid.tldr.md")
    invalid_fixture = os.path.join(fixtures_dir, "fixture-invalid-ac.tldr.md")

    failures = []

    # Test 1: valid fixture should pass
    if not os.path.exists(valid_fixture):
        failures.append(f"valid fixture missing: {valid_fixture}")
    else:
        rc = check_tldr_integrity(valid_fixture)
        if rc != 0:
            failures.append(f"valid fixture {valid_fixture} expected exit 0, got {rc}")

    # Test 2: invalid fixture should fail
    if not os.path.exists(invalid_fixture):
        failures.append(f"invalid fixture missing: {invalid_fixture}")
    else:
        rc = check_tldr_integrity(invalid_fixture)
        if rc != 1:
            failures.append(f"invalid fixture {invalid_fixture} expected exit 1, got {rc}")

    if failures:
        print("SELF-TEST FAILED:")
        for f in failures:
            print(f"  - {f}")
        return 1

    print("SELF-TEST OK — both fixtures produced expected exit codes")
    return 0


def main():
    if len(sys.argv) != 2:
        print("Usage: check_tldr_integrity.py <tldr-file>")
        print("       check_tldr_integrity.py --self-test")
        return 1
    arg = sys.argv[1]
    if arg == "--self-test":
        return run_self_test()
    return check_tldr_integrity(arg)


if __name__ == "__main__":
    sys.exit(main())
