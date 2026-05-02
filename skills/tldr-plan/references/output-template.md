# TLDR Plan Output Template

# TLDR Plan

Feature: **...**
Source: [...]

## 0. Audit Dashboard

**Goal:** ...
**Top-level architecture decision:** ...
**Main behavior change:** ...
**Highest-risk decision:** ...
**Likely touched files/modules:** ...
**Must-not-change behavior:** ...
**User audit focus:** D1, D3, D5

## 1. Decision Map

```mermaid
flowchart TD
  D0[D0 Goal]
  D1[D1 Architecture insertion]
  D2[D2 Module boundary]
  D3[D3 Runtime path]
  D4[D4 State/API shape]
  D5[D5 Key implementation anchors]
  D6[D6 Evidence]

  D0 --> D1
  D1 --> D2
  D1 --> D3
  D2 --> D4
  D3 --> D4
  D4 --> D5
  D3 --> D6
  D5 --> D6
```

| Decision | Chosen | Depends On | Audit |
|---|---|---|---|
| D1 | ... | D0 | [ ] ... |
| D2 | ... | D1 | [ ] ... |
| D3 | ... | D1, D2 | [ ] ... |

## 2. Critical Views

### 2.1 Architecture Integration View

```mermaid
flowchart LR
  Entry[Existing entry]
  Boundary[Modified boundary]
  New[New logic]
  Stable[Stable downstream]

  Entry --> Boundary
  Boundary --> New
  New --> Stable
```

**Architectural insertion point:** ...
**Downstream decisions unlocked:** ...

### 2.2 Runtime / Data Path View

```mermaid
sequenceDiagram
  participant Caller
  participant Entry
  participant NewLogic
  participant Downstream

  Caller->>Entry: request
  Entry->>NewLogic: critical change
  NewLogic->>Downstream: unchanged contract
```

**Before path:** ...
**After path:** ...
**Key invariant:** ...
**Important branches:** ...

## 3. Audit Checkpoints

- [ ] D1: ...
- [ ] D2: ...
- [ ] D3: ...
- [ ] D4: ...
- [ ] D5: ...
- [ ] D6: ...

## Appendix A: Full Decision Trace

| Decision | Layer | Chosen | Rejected | Depends On | Unlocks | User Audit |
|---|---|---|---|---|---|---|
| D0 | Goal | ... | ... | none | D1 | [ ] |
| D1 | Architecture | ... | ... | D0 | D2, D3 | [ ] |

## Appendix B: Full Module / File Boundary

| File / Module | Role | Allowed Change | Forbidden Responsibility | Parent Decision |
|---|---|---|---|---|
| `...` | ... | ... | ... | D2 |

## Appendix C: Full Risk -> Evidence Matrix

| Decision | Risk | Required Evidence | Stop Condition |
|---|---|---|---|
| D1 | ... | ... | ... |

## Appendix D: Implementation Detail Trace

| Implementation Detail | Parent Decision | Reason | Drift Risk |
|---|---|---|---|
| ... | D2, D3 | ... | medium |

## Appendix E: Execution Anchors

### Allowed Changes

- ...

### Forbidden Changes

- ...

### Stop Conditions

Stop and ask the user if:
- ...

### Done Criteria

- ...
