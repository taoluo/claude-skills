# Plan: Per-tenant rate limit cache

## Goal

Add a per-tenant rate-limit middleware to the API gateway. Each tenant's
counter must be independently rate-limited to prevent one noisy tenant
from starving others.

## Assumptions

- A1: Tenant identifier is reliably present in `X-Tenant-Id` header before
  reaching the middleware (upstream auth already enforces).
- A2: A single cache backend (Redis) is sufficient for MVP; multi-region
  consistency is not required.
- A3: The default rate budget (per tenant per minute) is configurable
  per-tenant and stored in the existing tenant config table.

## Hard constraints

- C1: A request with no `X-Tenant-Id` MUST be rejected with `400 Bad
  Request` before any rate-limit logic runs (assert at middleware entry).
- C2: A tenant whose counter has overflowed MUST receive `429 Too Many
  Requests` with a `Retry-After` header, never silently dropped.
- C3: The rate-limit cache key MUST include the tenant id; cross-tenant
  key collisions are forbidden.
- C4: Cache backend connection failure MUST NOT silently allow unlimited
  traffic — middleware fails closed (`503 Service Unavailable`).

## Acceptance criteria

- AC1: Two tenants in parallel — tenant A exhausting its budget does not
  affect tenant B's available budget.
- AC2: A burst exceeding budget receives `429` within 1ms of the
  decision (no head-of-line blocking).
- AC3: Cache-backend outage produces `503` (not silent pass-through).

## Design

### D1: Middleware insertion point

Insert between authentication middleware and routing middleware. Auth
guarantees `X-Tenant-Id` presence; routing should never see exhausted
tenants.

### D2: Counter representation

Use Redis `INCR` with TTL set on first key creation per minute.

### D3: Failure mode

On Redis connection failure, fail closed (`503`). Log error with tenant
id and request path.

### D4: Observability

Emit metric `rate_limit.decision{tenant=…, decision=allow|deny}` on
every request. Log denials at INFO level.

## Tests / evidence

- E1: AC1 verified via integration test with two simulated tenants in
  parallel.
- E2: AC2 verified via load test — 1000 req/s for 5s, measure 429
  latency p99.
- E3: AC3 verified via fault injection (kill Redis container during
  test; assert 503 response).

## Future work / nice-to-have

- Multi-region cache replication for global rate limits.
- Per-endpoint rate budgets (currently per-tenant only).
- Generic policy engine that lets ops define arbitrary rate-limit rules
  via a YAML DSL.
- A pluggable backend interface so the rate limiter can switch between
  Redis, Memcached, in-memory, and a hypothetical future "RateLimitDB"
  service.
- Auto-tuning rate budgets based on observed traffic patterns.
- Pretty-printed admin dashboard for viewing per-tenant counters.

## Rejected alternatives

- Token bucket implemented in middleware process memory: rejected —
  fails AC1 across multiple gateway instances.

## Stop conditions

- Stop and ask if `X-Tenant-Id` semantics differ from the assumed
  upstream auth contract.
- Stop and ask if Redis ops permission model requires a sidecar pattern
  not covered by C4.
