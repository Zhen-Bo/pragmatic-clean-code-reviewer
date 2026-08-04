# Security and Privacy

**Purpose:** Authorization, sensitive data, input trust boundaries, and attack surface.

Correctness of security and authorization is a review-wide obligation. Quality Level never relaxes it. Prefer concrete code evidence over generic checklists. This pack does not claim a complete security audit.

## Trust boundaries

- All external input (HTTP, CLI, files, queues, webhooks) validated or constrained before use.
- Injection risks: SQL, command, template, path, LDAP, and similar composition of untrusted data into interpreters.
- Deserialization of untrusted data; unsafe eval or dynamic code execution.
- SSRF, open redirects, and URL handling that trusts client-supplied targets.

Optional rule references: PP-36, PP-72.

## Authorization and session

- Missing or bypassable authorization checks on sensitive operations.
- Confused deputy: acting with elevated privilege on caller-controlled identifiers.
- Insecure direct object references; IDOR-style access by guessing identifiers.
- Session fixation, weak session handling, or cookies missing security attributes where the stack requires them.

## Sensitive data

- Secrets, tokens, passwords, or private keys in source, logs, fixtures, or client-visible payloads.
- Secrets that should live in environment or a secret store, not hardcoded configuration.
- PII or credentials written to logs, error messages, or analytics.
- Paths ignored by `.gitignore` are never read during review (secret-leak risk); if a tracked file still contains secrets, report it.

Optional rule references: PP-55, PP-72.

## Attack surface and dependencies

- Unnecessarily large public API or debug endpoints left enabled.
- Cryptography misused (home-grown crypto, broken modes, weak randomness for security decisions).
- Dependencies with known vulnerabilities when the repository evidence shows fixed versions available or advisories referenced.
- Security patches delayed without a stated compensating control.

Optional rule references: PP-72, PP-73, CC-108, CC-158.

## Severity guidance

Use Finding Severity from the skill contract. Typical mappings when consequence is supported:

- **Critical** — authorization bypass; sensitive-data disclosure; authoritative data corruption via an abuse path.
- **Important** — exploitable injection with limited blast radius; missing auth on non-core but sensitive action.
- **Minor** — defense-in-depth gap with no demonstrated exploit path, or local hardening only.

Never inflate severity without a supported consequence.

## Symptom index

| Symptom | Look for |
| --- | --- |
| Hardcoded secret | Config/env/secret store; rotate if committed |
| String-built SQL/command | Parameterized API / safe API |
| Auth check only on UI | Enforce on server/handler |
| Stack trace to client | Sanitize errors at boundary |
| Over-broad CORS or public admin route | Restrict by default |
| Outdated vulnerable dependency | Upgrade or pin with rationale |
