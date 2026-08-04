# Research Reproducibility

**Purpose:** Whether experimental, analytical, or evaluation work can be re-run with the same results and understood by others.

Apply this pack whenever the scope includes experiments, benchmarks, notebooks, data pipelines, model training, statistical analysis, or evaluation harnesses. For ordinary application code with no research artifact, still report concrete reproducibility problems if they appear; do not force research ceremony onto unrelated code.

## Runnable path

- A documented entry command or script that re-runs the experiment or analysis end-to-end.
- Hidden manual steps, local-only paths, or "run these cells in order" without a non-interactive path when the project claims automation.
- Prototype or notebook code promoted to a shared pipeline without cleaning nondeterminism and undocumented parameters.

Optional rule references: PP-20, PP-21, PP-25, PP-68, PP-94.

## Configuration and parameters

- Seeds, hyperparameters, feature flags, and environment assumptions recorded next to results or in versioned config.
- Hardcoded machine-specific paths, credentials, or silent defaults that change outcomes.
- Plain-text, reviewable config preferred over opaque binary experiment state when the project standard allows.

Optional rule references: PP-25, PP-55.

## Data and provenance

- Dataset version, query, or snapshot identity recorded; floating "latest" data without pin when results are claimed comparable.
- Train/test leakage; preprocessing fit on full data then applied to holdout.
- Missing checksums or schema checks when the pipeline already uses them elsewhere.
- Results tables or figures without a link to the code revision and config that produced them.

## Determinism and environments

- Unseeded random number use in paths that claim comparable metrics.
- Parallelism, GPU reduction, or unordered iteration that changes numeric results without note.
- Dependency lockfiles or environment specs absent when the repo otherwise pins them.
- Timezone, locale, or BLAS threading affecting results without documentation.

## Evaluation integrity

- Metrics computed on the wrong split; cherry-picked seeds reported as single runs without variance.
- Baselines not re-run under the same protocol as the proposed method.
- Benchmarks that measure a different code path than the paper or README describes (doc-vs-code finding).

## Symptom index

| Symptom | Look for |
| --- | --- |
| "Just run the notebook" | Scripted entry; fixed seeds |
| Results without config/commit | Record revision + params |
| Data path `/Users/me/...` | Relative or configured path |
| Unpinned dataset "latest" | Version or hash |
| Metric on training set only | Correct split; leakage check |
| Float noise across machines | Seeds, thread settings, noted tolerance |
