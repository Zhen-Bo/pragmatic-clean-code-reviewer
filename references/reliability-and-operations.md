# Reliability and Operations

**Purpose:** Failure handling, resource lifecycle, concurrency, and operational readiness.

## Error handling and failure modes

- Fail fast on impossible states; avoid continuing with corrupt or partial results.
- Empty catch blocks; swallowed errors; generic exceptions without context.
- Error handling mixed with happy-path logic when separation would clarify both.
- Language-appropriate error style (exceptions, Result/Either, error returns) used consistently at boundaries.
- Retries without backoff, jitter, or idempotency where duplicates hurt.

Optional rule references: CC-34–36, CC-86–93, PP-32, PP-36–39.

## Resource lifecycle

- Files, connections, locks, transactions, and temporary resources always released (including error paths).
- Partial failure leaving external systems half-updated without compensation or transaction boundaries.
- Shutdown and cancellation: in-flight work, listeners, and worker pools stopped cleanly.

Optional rule references: PP-40, CC-138.

## Concurrency and state

- Shared mutable state without adequate synchronization or immutability.
- Race conditions; check-then-act; non-atomic read-modify-write.
- Deadlock risk from lock ordering; oversized critical sections.
- Thread-unsafe collections used across threads.
- Time and scheduling assumptions that fail under load or reordering.

Optional rule references: CC-131–139, PP-56–60, PP-57–58.

## Operational readiness

- Logging that is missing on failure paths, or so noisy it hides incidents.
- Metrics/traces absent for core operations when the codebase already uses an observability stack.
- Health checks that always succeed while dependencies are down.
- Configuration required at runtime but undocumented or unsafe defaults for production.
- Manual runbooks required for routine deploy/rollback when automation is the project norm.

Optional rule references: PP-55, PP-94, CC-145–146.

## Performance as reliability

Algorithmic cost and resource use matter when they threaten service availability or correctness under realistic load. Premature micro-optimization without evidence is not a finding by itself.

Optional rule references: PP-63, PP-64.

## Symptom index

| Symptom | Look for |
| --- | --- |
| Swallowed exception | Log/rethrow/result; never empty catch |
| Connection not closed | `defer`/`finally`/ARM/use |
| Global mutable cache | Sync, actor, or confine to one thread |
| Retry storms | Backoff, cap, idempotent handler |
| O(n²) on large input | Measure; choose better structure |
| Deploy needs hand steps | Automate build/release path |
