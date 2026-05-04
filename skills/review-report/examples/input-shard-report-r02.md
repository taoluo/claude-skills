# Review Shard Report

Shard ID: R02
Shard title: Startup fail-fast constraints review
Reviewer: Subagent B
Inputs reviewed: plans/miles-port-unified-plan.md (C5, C7, AC4 sections), plans/miles-port-unified-plan.review.md (R02 spec)
Code areas reviewed: miles/router/router.py (init, validate, bind methods)
Plan anchors: C5, C7, AC4
Debug-log bugs reviewed: (none)
Review angles: PLAN_ADHERENCE_REVIEW, ERROR_HANDLING_FAIL_FAST_REVIEW

## Verdict

`PASS_WITH_NOTES`

## Findings

| Finding ID | Severity | Type | Title | Plan anchors | Code area | Evidence | Recommendation |
|---|---|---|---|---|---|---|---|
| R02-01 | MEDIUM | OBSERVABILITY_GAP | C7 missing-env-var error message is non-actionable | C7, AC4 | miles/router/router.py:42 | Error says "missing required configuration" without naming the env var | Include the env var name in the error |

## Detailed Findings

### R02-01: C7 missing-env-var error message is non-actionable

(MEDIUM-severity finding — full Detailed Findings block omitted per `finding-rules.md` since only BLOCKER/HIGH require all 7 fields. Included for completeness as a one-line summary in §6 of the final report.)

#### Background

C7 requires the router to fail fast when the `RLIX_ROUTER_BIND` environment variable is missing. The fail-fast itself is correctly implemented (raises immediately, no silent default), but the error message is generic.

#### Finding

The exception message reads `"missing required configuration"` without naming `RLIX_ROUTER_BIND`. A new operator hitting this won't know which variable to set without grepping the source.

#### Evidence

`miles/router/router.py:42` — `raise ConfigError("missing required configuration")`. Compare to C5 enforcement at line 38, which does name the variable (`raise ConfigError(f"missing required configuration: {var_name}")`).

#### Impact

Slow down for new operators. No correctness impact. No `BUG-*` follow-up needed.

#### Recommended action

Change line 42 to match the C5 pattern: `raise ConfigError(f"missing required configuration: RLIX_ROUTER_BIND")`.

#### Routing

- Debug-log update: none.
- PLAN.md revision: none.
- Rerun needed: none.

## Evidence Gaps

(none)

## Adversarial Checks

| Check | Result | Evidence |
|---|---|---|
| What if C5 (single-process binding) fails because the port is held by a stale process — is the error fail-fast or does the router silently retry on a different port? | PASSED | router.py:38 raises immediately on `OSError: address already in use`; no retry logic. |
| What if C7 (required environment variable) is missing — does the router log a warning and proceed with a default, or raise immediately? | PASSED (with R02-01 note) | router.py:42 raises immediately; no default. The error message is non-actionable per R02-01 but the fail-fast behavior is correct. |

## Reviewer Notes

R02-01 is a MEDIUM finding only because correctness is preserved. If the team values operator experience highly, it could be promoted to HIGH; defaulting to MEDIUM per `finding-rules.md` severity guidance.
