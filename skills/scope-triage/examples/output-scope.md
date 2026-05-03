# Scope Triage

Feature: Per-tenant rate limit cache
Source plan: examples/input-plan.md
TLDR context: missing (no sibling input-plan.tldr.md generated)
Scope review state: SCOPE_REVIEW_READY_WITH_DEFAULTS

## 0. Executive Summary

- MVP boundary: Redis-backed per-tenant counter middleware between auth and routing; fail-closed on backend outage.
- P0 risks: missing `X-Tenant-Id` (C1), cross-tenant key collision (C3), silent unlimited traffic on Redis outage (C4).
- Main correctness floor: per-tenant key isolation + fail-closed on backend failure.
- Main overengineering risk: generic policy DSL / pluggable backend interface — no second consumer exists.
- Blocking questions: None (no MVP-affecting Scope Delta divergence; every row has `MVP set impact: no`).
- Scope delta divergent rows: 5 non-`ALIGNED` — F10/F11/F12 (`CATEGORY_REFRAMED`, plan-MVP-tests vs triage-DEV-ONLY, same MVP set), F16/F17 (`TRIAGE_MORE_AGGRESSIVE`, plan-future-nice-to-have vs triage-NO-OVERENGINEERING, both reject from MVP). All 5 non-blocking.

## 1. Blocking Questions

None. Non-blocking deltas and low-confidence defaults are listed in §11 (three populating sources: `Confidence: Low` rows, non-`ALIGNED` rows with `MVP set impact: no`, and `CATEGORY_REFRAMED` rows).

## 2. Scope Delta Matrix

This table compares the source plan's declared scope with `scope-triage`'s inferred classification. Any row with a non-`ALIGNED` delta should be reviewed by a human.

19 items < 20-row threshold, so all rows shown directly (no Divergent/Aligned split). Canonical 9-column format.

| ID | Feature / Item | Source plan scope | TLDR mirrored scope | Triage classification | Delta | MVP set impact | Review action | Anchors |
|---|---|---|---|---|---|---|---|---|
| F01 | Reject request with no `X-Tenant-Id` | `SOURCE-FORBIDDEN` (C1) | (no TLDR) | P0-FORBIDDEN | `ALIGNED` | no | No action | C1 |
| F02 | Cross-tenant cache-key collision | `SOURCE-FORBIDDEN` (C3) | (no TLDR) | P0-FORBIDDEN | `ALIGNED` | no | No action | C3 |
| F03 | Silent unlimited traffic on Redis outage | `SOURCE-FORBIDDEN` (C4) | (no TLDR) | P0-FORBIDDEN | `ALIGNED` | no | No action | C4 |
| F04 | Per-tenant counter independence | `SOURCE-MVP` (AC1) | (no TLDR) | P0-CORRECTNESS-FLOOR | `ALIGNED` | no | No action | AC1, C3 |
| F05 | Overflow tenant returns `429` + `Retry-After` | `SOURCE-MVP` (C2, AC2) | (no TLDR) | P0-CORRECTNESS-FLOOR | `ALIGNED` | no | No action | C2, AC2 |
| F06 | Redis `INCR` + first-touch TTL | `SOURCE-MVP` (D2) | (no TLDR) | P1-HAPPY-PATH | `ALIGNED` | no | No action | D2 |
| F07 | Middleware insertion between auth and routing | `SOURCE-MVP` (D1) | (no TLDR) | P1-HAPPY-PATH | `ALIGNED` | no | No action | D1 |
| F08 | Metric per decision | `SOURCE-MVP` (D4) | (no TLDR) | P1-OBSERVABILITY-FLOOR | `ALIGNED` | no | No action | D4 |
| F09 | INFO log on denial | `SOURCE-MVP` (D4) | (no TLDR) | P1-OBSERVABILITY-FLOOR | `ALIGNED` | no | No action | D4 |
| F10 | Two-tenant parallel integration test | `SOURCE-MVP` (E1) | (no TLDR) | DEV-ONLY | `CATEGORY_REFRAMED` | no | Non-blocking (NQ3) | E1, AC1 |
| F11 | Load test for `429` p99 latency | `SOURCE-MVP` (E2) | (no TLDR) | DEV-ONLY | `CATEGORY_REFRAMED` | no | Non-blocking (NQ3) | E2, AC2 |
| F12 | Fault-injection test killing Redis | `SOURCE-MVP` (E3) | (no TLDR) | DEV-ONLY | `CATEGORY_REFRAMED` | no | Non-blocking (NQ3) | E3, AC3 |
| F13 | Multi-region cache replication | `SOURCE-FUTURE` | (no TLDR) | P3-DEFER-HARDENING | `ALIGNED` | no | No action | future-work |
| F14 | Per-endpoint rate budgets | `SOURCE-FUTURE` | (no TLDR) | P3-DEFER-HARDENING | `ALIGNED` | no | No action | future-work |
| F15 | Auto-tuning rate budgets | `SOURCE-FUTURE` ("nice-to-have") | (no TLDR) | P3-DEFER-HARDENING | `ALIGNED` (low confidence — see §11 NQ1) | no | Non-blocking (NQ1) | future-work |
| F16 | Generic policy DSL (YAML) | `SOURCE-FUTURE` ("nice-to-have") | (no TLDR) | NO-OVERENGINEERING | `TRIAGE_MORE_AGGRESSIVE` | no | Non-blocking — plan didn't explicitly endorse | future-work |
| F17 | Pluggable backend interface | `SOURCE-FUTURE` ("nice-to-have") | (no TLDR) | NO-OVERENGINEERING | `TRIAGE_MORE_AGGRESSIVE` | no | Non-blocking — premature abstraction | future-work |
| F18 | Pretty-printed admin dashboard | `SOURCE-FUTURE` ("nice-to-have") | (no TLDR) | P4-POLISH | `ALIGNED` (low confidence — see §11 NQ2) | no | Non-blocking (NQ2) | future-work |
| F19 | Token-bucket in-process variant | `SOURCE-OUT-OF-SCOPE` (rejected alternative) | (no TLDR) | NO-OVERENGINEERING | `ALIGNED` | no | No action | rejected-alt |

**No MVP-affecting deltas** (every row has `MVP set impact: no`).

- F10/F11/F12 `CATEGORY_REFRAMED`: plan classifies these tests as `SOURCE-MVP` (Layer 7-equivalent — required to verify AC1/AC2/AC3 in MVP); triage classifies them as `DEV-ONLY` (test scaffolding, env/process-isolated). Same MVP set, different category framing — by definition non-blocking.
- F16/F17 `TRIAGE_MORE_AGGRESSIVE`: both reject items the plan classifies as future ("nice-to-have"), so neither changes MVP membership — agreement-in-direction with the plan's deferral, just stricter on whether to ever build them.

## 3. Category Table

| ID | Item | Category | Priority | Action | Anchors | Confidence | Reason |
|---|---|---|---|---|---|---|---|
| F01 | Reject request with no `X-Tenant-Id` (`400`) | P0-FORBIDDEN | P0 | assert at middleware entry | C1 | high | Allowing untagged traffic = unlimited unattributed budget |
| F02 | Cross-tenant cache-key collision | P0-FORBIDDEN | P0 | namespace key with tenant id | C3 | high | Collision = one tenant's counter affects another (violates AC1) |
| F03 | Silent unlimited traffic on Redis failure | P0-FORBIDDEN | P0 | fail closed → `503` | C4 | high | Silent pass-through = budget bypass, downstream overload |
| F04 | Per-tenant counter independence | P0-CORRECTNESS-FLOOR | P0 | tenant-prefixed Redis key + INCR | AC1, C3 | high | Without it the feature is not the feature |
| F05 | Overflow tenant returns `429` + `Retry-After` | P0-CORRECTNESS-FLOOR | P0 | translate INCR > budget → 429 | C2, AC2 | high | Plan promises specific status semantics |
| F06 | Redis `INCR` + first-touch TTL | P1-HAPPY-PATH | P1 | implement counter primitive | D2 | high | Main path |
| F07 | Middleware insertion between auth and routing | P1-HAPPY-PATH | P1 | wire into chain | D1 | high | Required ordering |
| F08 | Metric `rate_limit.decision{tenant, decision}` per request | P1-OBSERVABILITY-FLOOR | P1 | emit on every decision | D4 | high | Required to debug AC1 / AC3 in MVP |
| F09 | INFO log on denial with tenant id + path | P1-OBSERVABILITY-FLOOR | P1 | log line | D4 | high | Cheap; needed for incident response |
| F10 | Two-tenant parallel integration test | DEV-ONLY | P1 | test suite | E1, AC1 | high | Test scaffolding, isolated from prod |
| F11 | Load test for `429` p99 latency | DEV-ONLY | P1 | load harness | E2, AC2 | high | Test scaffolding |
| F12 | Fault-injection test killing Redis | DEV-ONLY | P1 | chaos harness | E3, AC3 | high | Test scaffolding |
| F13 | Multi-region cache replication | P3-DEFER-HARDENING | P3 | defer | future-work | high | A2 explicitly out of MVP; revisit when multi-region traffic appears |
| F14 | Per-endpoint rate budgets | P3-DEFER-HARDENING | P3 | defer | future-work | high | Trigger: customer ask for endpoint-level limits |
| F15 | Auto-tuning rate budgets | P3-DEFER-HARDENING | P3 | defer | future-work | medium | Useful but needs telemetry baseline first; see §11 NQ1 |
| F16 | Generic policy DSL (YAML) for ops-defined rules | NO-OVERENGINEERING | — | do not build | future-work | high | Speculative; one fixed rule shape suffices for MVP |
| F17 | Pluggable backend interface (Redis / Memcached / in-memory / "RateLimitDB") | NO-OVERENGINEERING | — | do not build | future-work | high | Premature abstraction; "RateLimitDB" is hypothetical |
| F18 | Pretty-printed admin dashboard | P4-POLISH | P4 | not-MVP | future-work | medium | Operator UX, not feature correctness; see §11 NQ2 |
| F19 | Token-bucket in-process memory variant | NO-OVERENGINEERING | — | rejected per plan | rejected-alt | high | Plan explicitly rejected |

## 4. AC Coverage Check

| AC | Source milestone | Covered by scope items | Delta warnings | Missing? |
|---|---|---|---|---|
| AC1 (per-tenant isolation) | (no milestone, MVP) | F04 (P0 floor), F02 (P0 forbidden enforces it), F10 (test) | None | no |
| AC2 (`429` p99 < 1ms) | (no milestone, MVP) | F05 (P0 floor), F11 (load test) | None | no |
| AC3 (cache outage → `503`) | (no milestone, MVP) | F03 (P0 forbidden), F12 (fault injection) | None | no |

All three AC have at least one P0/P1 item covering them and at least one DEV-ONLY test verifying them. No delta warnings on covering items.

## 5. P0 Must-Address

### F01 Reject request with no `X-Tenant-Id`

- Category: P0-FORBIDDEN
- Why it matters: Untagged traffic consumes no tenant's budget — equivalent to bypassing the rate limiter entirely. Also violates assumption A1 if it ever happens.
- Required implementation: middleware-entry guard returning `400 Bad Request` before any cache lookup; assert in tests that the guard fires before counter logic.
- Required test/evidence: unit test sending request without header → 400; integration test confirms counter for "no tenant" never incremented.
- Anchors: C1, A1

### F02 Cross-tenant cache-key collision

- Category: P0-FORBIDDEN
- Why it matters: Two tenants sharing a counter = one tenant's traffic exhausts another tenant's budget; violates AC1.
- Required implementation: cache key format `rl:{tenant_id}:{minute_bucket}` with explicit tenant_id position; never construct keys without tenant_id.
- Required test/evidence: AC1 integration test (E1) covers this; add unit test for key formation that asserts tenant_id appears in key.
- Anchors: C3, AC1

### F03 Silent unlimited traffic on Redis outage

- Category: P0-FORBIDDEN
- Why it matters: Fail-open on backend outage = unlimited unaccounted traffic during exactly the window where the system is most vulnerable.
- Required implementation: catch Redis connection / timeout exceptions and return `503 Service Unavailable`; do NOT fall through to "allow".
- Required test/evidence: E3 (kill Redis container, assert 503); add unit test mocking connection failure.
- Anchors: C4, AC3

### F04 Per-tenant counter independence

- Category: P0-CORRECTNESS-FLOOR
- Why it matters: This is the feature's core promise (AC1).
- Required implementation: tenant_id in cache key + Redis INCR atomicity per key.
- Required test/evidence: E1 two-tenant parallel integration test.
- Anchors: AC1, C3, D2

### F05 Overflow tenant returns `429` + `Retry-After`

- Category: P0-CORRECTNESS-FLOOR
- Why it matters: API contract guarantees specific HTTP semantics; clients rely on `Retry-After` for backoff.
- Required implementation: translate `INCR` result > budget into `429` response with `Retry-After` header set to remaining seconds in current minute.
- Required test/evidence: E2 load test asserts 429 status + presence of Retry-After header.
- Anchors: C2, AC2

## 6. MVP Implementation Set

Items in MVP scope:

- F01–F05 (P0 from §5)
- F06: Redis `INCR` + first-touch TTL
- F07: Middleware insertion between auth and routing
- F08: Metric emission per decision
- F09: INFO log on denial
- F10–F12: Tests required to verify AC1/AC2/AC3

## 7. Dev-Only Scaffolding

### F10 Two-tenant parallel integration test

- Purpose: verify AC1 (tenant isolation).
- How it accelerates implementation/debugging: catches cross-tenant key collision regressions during development.
- Required isolation from production: lives in `tests/integration/`; uses test Redis container, never production backend.
- Remove/keep policy: keep — runs in CI on every PR.

### F11 Load test for `429` p99 latency

- Purpose: verify AC2 (latency under burst).
- How it accelerates implementation/debugging: surfaces head-of-line blocking early.
- Required isolation from production: separate load-test environment; never run against production traffic.
- Remove/keep policy: keep — gated to release pipeline (not every PR).

### F12 Fault-injection test killing Redis

- Purpose: verify AC3 (fail-closed behavior).
- How it accelerates implementation/debugging: catches accidental fail-open paths.
- Required isolation from production: chaos harness in test env only.
- Remove/keep policy: keep — runs in nightly CI.

## 8. Release Blockers

(None declared in this plan. All release-relevant items are MVP correctness or dev-only tests.)

## 9. Deferred Hardening

### F13 Multi-region cache replication

- Why deferred: A2 explicitly scopes MVP to single region.
- Revisit trigger: business expansion to multi-region traffic; observed cross-region budget leakage.
- Risk if never implemented: a multi-region tenant gets `region_count × budget` effectively.

### F14 Per-endpoint rate budgets

- Why deferred: not required by current plan; one-budget-per-tenant covers AC1/AC2/AC3.
- Revisit trigger: customer request for endpoint-level limiting.
- Risk if never implemented: noisy endpoint can still exhaust tenant budget for quiet endpoints.

### F15 Auto-tuning rate budgets

- Why deferred: needs telemetry baseline; risky without it.
- Revisit trigger: ops requests dynamic budget adjustment.
- Risk if never implemented: manual budget tuning continues; not a correctness gap.

## 10. Explicitly Not Doing

### F16 Generic policy DSL (YAML) for ops-defined rules

- Why not now: speculative; only one rule shape exists ("per-tenant per-minute count"). Building a DSL before the second rule shape exists is premature.
- What evidence would justify revisiting: ≥3 distinct rule shapes requested by ops in production.
- How to prevent accidental implementation: forbid in scope file; if a future PR introduces YAML parsing for rate-limit config, reject.

### F17 Pluggable backend interface

- Why not now: only Redis is in scope; "RateLimitDB" is hypothetical. Interface-before-second-consumer = premature abstraction.
- What evidence would justify revisiting: a second concrete backend (Memcached) is committed to.
- How to prevent accidental implementation: do not introduce `RateLimitBackend` ABC; call Redis client directly.

### F19 Token-bucket in-process variant

- Why not now: explicitly rejected by plan (multi-instance gateway breaks shared budget).
- What evidence would justify revisiting: never (architectural mismatch).
- How to prevent accidental implementation: assert in middleware that Redis client is in use, not an in-process counter.

**P4-POLISH (one-line entries):**

- F18 Admin dashboard — operator UX, not feature correctness. Ship MVP without it; revisit after first incident report needs better visibility.

## 11. Non-blocking Questions / Low-confidence Defaults

Non-blocking deltas and low-confidence defaults. Three populating sources:

1. Items with `Confidence: Low` in §3 Category Table.
2. Non-`ALIGNED` Scope Delta rows where `MVP set impact: no`.
3. `CATEGORY_REFRAMED` rows (always non-blocking by definition).

| QID | Feature / Item | Question | Suggested default | Affects | Reason |
|---|---|---|---|---|---|
| NQ1 | F15 Auto-tuning rate budgets | Is this `P3-DEFER-HARDENING` (deferred) or `NO-OVERENGINEERING` (do not implement)? | `P3-DEFER-HARDENING` — plan calls it "nice-to-have", suggesting future intent rather than full rejection | F15 row in §3 + §2 | Plan's "nice-to-have" wording is ambiguous between defer and overengineering; default to defer because plan does not explicitly reject it |
| NQ2 | F18 Admin dashboard | `P4-POLISH` or `P3-DEFER-HARDENING`? | `P4-POLISH` — plan describes it as operator UX, not robustness | F18 row in §3 + §2 | "Pretty-printed admin dashboard" wording leans cosmetic; default to polish |
| NQ3 | F10/F11/F12 tests | Plan classifies as `SOURCE-MVP` (Layer 7-equivalent, required for AC1/AC2/AC3 verification); triage classifies as `DEV-ONLY` (test-only, env/process-isolated). Same MVP set, different category framing — accept the reframing or patch the source plan to label them DEV-ONLY explicitly? | Accept reframing — both classifications agree the tests ship in MVP; the `DEV-ONLY` label captures that they're scaffolding, not production receiver-API surface | F10/F11/F12 rows in §3 + §2 | `CATEGORY_REFRAMED` delta by definition; non-blocking; recorded for audit visibility |

In `SCOPE_REVIEW_READY_WITH_DEFAULTS` state (this artifact's state), the human MUST explicitly accept these defaults (or patch them into the source plan) before invoking a coding agent — see §14 precondition callout.

## 12. Drift / Missing Constraints

- **Missing P0 boundary** — plan does not explicitly forbid the dev-only token-bucket variant from sneaking into production code. Recommendation: add a `forbidden-line` to the middleware spec or a unit-test assertion that the in-process counter is never instantiated.
- **Ambiguous plan item** — F15 (auto-tuning) marked medium-confidence; plan calls it "nice-to-have" without specifying triggering criteria. Recommend adding a revisit trigger to the plan. See §11 NQ1.
- **Stale TLDR**: N/A (no sibling TLDR file exists for this example).

## 13. Recommended Implementation Order

1. F01–F03 P0 forbidden guards (assert / reject / fail-closed)
2. F04, F05 P0 correctness floor (per-tenant key, 429 + Retry-After)
3. F06, F07 P1 happy path (Redis INCR primitive + middleware insertion)
4. F08, F09 P1 observability floor (metric + log)
5. (no P1 lightweight defensive items in this plan)
6. F10–F12 P1/P2 dev-only test/simulation support
7. (no P2 release blockers declared)
8. F13–F15 P3 deferred hardening — only after explicit approval

## 14. Post-Review Handoff Draft (copy-paste, conditional on human review)

**This handoff is conditional on human review.** It does NOT auto-fire when the artifact is written.

> **Precondition for `SCOPE_REVIEW_READY_WITH_DEFAULTS`**: the human reviewer MUST accept §11 defaults (or patch them into the source plan) before passing this block to a coding agent. The state name signals "human review can proceed" — NOT "agent ready". Defaults that have NOT been explicitly accepted leave this artifact in an unbound state — the agent has no authority to act on them.

```text
PRECONDITION (HUMAN ONLY) — before passing this block to a coding agent, confirm:
- §1 Blocking Questions: none in this artifact (resolved)
- §2 Scope Delta Matrix: 5 non-`ALIGNED` rows, all `MVP set impact: no` —
  F10/F11/F12 (`CATEGORY_REFRAMED`, plan-MVP-tests vs triage-DEV-ONLY, same MVP set);
  F16/F17 (`TRIAGE_MORE_AGGRESSIVE`, both reject items the plan also classifies as
  future "nice-to-have"). All 5 accepted via §11 NQ3 / non-blocking notes; none
  affect MVP membership.
- §4 AC Coverage Check: AC1 / AC2 / AC3 all covered, no delta warnings
- §11 Non-blocking defaults: NQ1 F15 → P3-DEFER, NQ2 F18 → P4-POLISH,
  NQ3 F10/F11/F12 → DEV-ONLY classification accepted — defaults applied

If any of the above is unresolved, do NOT use this handoff. Resolve in source plan and rerun scope-triage.

You are implementing the feature described in examples/input-plan.md.

Source of truth: examples/input-plan.md (the full source plan).
Boundary control: examples/output-scope.md (this scope file).

Before writing code:
1. Read the source plan in full.
2. Read this scope file's §3 Category Table and §5 P0 Must-Address.
3. Implement only items classified P0-CORRECTNESS-FLOOR (F04, F05) and
   P1-* (F06–F09).
4. Add P0-FORBIDDEN guards F01–F03 at the boundaries the scope file
   identifies (middleware entry tenant-id check; tenant-prefixed cache
   key; fail-closed on Redis outage).
5. Add minimum observability F08 (metric per decision) and F09 (INFO
   log on denial).
6. Add P1/P2 dev-only tests F10–F12 only — do not invent additional
   test scaffolding.
7. `Scope review state:` is SCOPE_REVIEW_READY_WITH_DEFAULTS — you MUST
   have explicitly accepted §11 defaults (NQ1 F15 → P3-DEFER, NQ2 F18 →
   P4-POLISH, NQ3 F10/F11/F12 → DEV-ONLY classification reframing) before
   this handoff is valid. Defaults do NOT auto-apply.

Do NOT:
- Implement F16 (generic policy DSL) — NO-OVERENGINEERING.
- Implement F17 (pluggable backend interface) — NO-OVERENGINEERING.
- Implement F19 (token-bucket in-process) — explicitly rejected.
- Pull F13/F14/F15 (multi-region / per-endpoint / auto-tuning) into MVP
  without explicit approval from the user.

Stop and ask if:
- Implementation requires bypassing F01–F03 (P0-FORBIDDEN guards).
- The drift item in §12 (no spec-level guard against in-process token
  bucket) needs resolution before coding.
- A new requirement appears that does not map to any item F01–F19.
- PLAN.md (source plan) and PLAN.scope.md (this scope file) disagree on
  any item's scope/category. Do NOT let PLAN.scope.md silently override
  PLAN.md — Scope Delta Matrix entries with non-`ALIGNED` deltas surface
  real plan disagreement that the human must resolve in PLAN.md (or
  explicitly accept).
```
