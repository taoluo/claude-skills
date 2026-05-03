# TLDR Plan

Feature: **Per-tenant rate limit middleware (deliberately broken AC grid for self-test)**
Source: examples/fixture-invalid-ac.tldr.md (synthetic — for self-test only)

## 0. Audit Dashboard

- Goal: per-tenant rate limit cache (deliberate AC orphan for self-test)
- Top-level architecture decision: middleware between auth and routing
- Main behavior change: HTTP 429 on tenant overflow with Retry-After
- Highest-risk decision: D3
- Highest-risk assumption: A1
- Highest-risk constraint: C1
- Most important decision to audit first: D3
- Likely touched files/modules: `middleware/rate_limit.py` (new)
- Must-not-change behavior: existing auth semantics
- User audit focus: D3

## 2. Assumptions

| ID | Assumption | Why it matters | Evidence / check | If it fails |
| -- | ---------- | -------------- | ---------------- | ----------- |
| A1 | `X-Tenant-Id` header always present after auth | required for D2 cache key | C1 | untagged traffic bypasses budget |

## 3. Scope & Constraints

### 3.1 Out of Scope

- Multi-region cache replication

### 3.2 Hard Constraints

| ID | Constraint | Enforced by | Source |
| -- | ---------- | ----------- | ------ |
| C1 | request without `X-Tenant-Id` returns 400 | assert | spec |
| C4 | Redis outage returns 503 | handler | spec |

### 3.3 Acceptance Criteria

| ID | Acceptance Criterion (outcome) | Derives from | Verified by | Milestone |
| -- | ------------------------------ | ------------ | ----------- | --------- |
| AC1 | two tenants in parallel — isolation | Goal, A1 | E1 | M1 |
| AC2 | burst → 429 with Retry-After | Goal, C4 | E1 | M1 |
| AC3 | cache outage produces 503 | Goal, C4 | E1 | M1 |

### 3.4 Milestones

| Milestone | Scope | Key deliverables | Delivers AC | Gates |
| --------- | ----- | ---------------- | ----------- | ----- |
| M1 | First build | middleware + tests | `AC1 ∧ AC2` | Gate 1 |

## 4. Critical Views

### 4.1 Architecture Integration View

```mermaid
flowchart LR
    Client --> Auth
    Auth --> RL
    RL --> Routing
```

## 5. Decision Map

| Decision | Chosen | Depends On | AC served | Audit |
| -------- | ------ | ---------- | --------- | ----- |
| D1 | middleware insertion | A1 | AC1 | order |
| D2 | Redis INCR | C1 | AC1, AC2 | test |
| D3 | fail-closed | C4 |  | review |

## 6. Evidence & Stop Conditions

### 6.1 Evidence Required (per plan)

| ID | Binds to | AC verified | Evidence the plan defines | Before Done? |
| -- | -------- | ----------- | ------------------------- | ------------ |
| E1 | D2 | AC1, AC2 | two-tenant parallel integration test | yes |

### 6.2 Stop Conditions

The plan instructs the agent to stop and ask if A1 fails.

## 7. Audit Checkpoints

- [ ] Shippability: every Dn cites ≥1 AC.
