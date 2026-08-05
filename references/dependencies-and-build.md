# Dependencies and Build

**Purpose:** Third-party use, dependency direction, and build or release automation.

## Third-party boundaries

- External libraries and services isolated behind clear boundaries when the domain depends on them heavily.
- Learning tests or contract tests for critical third-party behavior when the repository already invests in them.
- Direct use of vendor types deep in domain code when a thin adapter would limit blast radius of upgrades.
- Pinned vs floating versions: accidental major upgrades, or pins so stale they block security fixes without rationale.

Optional rule references: CC-94–98, PP-73, CA-36–38.

## Dependency direction and structure

- Source dependencies point inward toward policy/domain, not outward toward frameworks and drivers.
- Business rules importing UI, HTTP, or database frameworks directly.
- Circular dependencies between packages or components.
- Stable packages that are entirely concrete; volatile packages depended on by many others.
- Components that force unused transitive dependencies on consumers (CRP).

Optional rule references: CA-12, CA-18–20, CA-31, CA-45, CA-47.

## Build, test, and release automation

- Build or test requires many manual steps when a single entry command is expected.
- CI missing for a repository that claims continuous integration, or CI not running the tests that matter.
- Release process undocumented or only tribal knowledge.
- Version control not driving builds and releases when the project standard says it should.

Optional rule references: CC-145–146, PP-28, PP-88–90, PP-94.

## Supply chain hygiene

- Unnecessary dependencies added for a few lines of trivial logic.
- Multiple libraries solving the same problem without migration.
- Post-install scripts or binary deps without review notes when unusual.
- License or provenance concerns when the repository tracks them and the change violates that policy.

## Symptom index

| Symptom | Look for |
| --- | --- |
| Domain imports ORM/HTTP types | Port/adapter; depend on own interface |
| Package cycle A↔B | Extract shared, or invert with interface |
| `npm install` / build needs wiki | One documented command |
| New heavy dependency for tiny helper | Prefer stdlib or existing dep |
| Lockfile conflict ignored | Resolve; don't commit broken lock |
| CI green but tests skipped | Fix skip or fix product |
