# Report bundle

Each audit writes one portable bundle to `.smell-check/<UTC-timestamp>/`. The timestamp is filesystem-safe UTC in `YYYYMMDD-HHMMSSZ` form.

## Layout

```text
.smell-check/<UTC-timestamp>/
├── index.html
├── summary.md
└── findings/
    ├── src-auth-active-001.md
    └── tests-auth-dismissed-001.md
```

The summary file is the canonical run manifest and overview. It contains metadata, aggregate counts, rule summary, synthesis, the complete shard inventory, and environment details. Detailed findings live only in Markdown shards. `index.html` is the only HTML file and presents the canonical Markdown according to [DESIGN.md](../DESIGN.md). It is self-contained and authored for the current audit, not copied from a template.

## Summary manifest

Start the summary file with YAML front matter, using the same `---` delimiters as the skill file. Keep the metadata flat; use quoted strings, integers, and inline string lists.

```yaml
---
schema_version: 1
repo: "task-queue"
commit: "3f9c2a1"
date: "2026-08-28T10:30:00Z"
scope: "whole repo (48 files)"
status: "complete"
language: "zh-Hant"
active: 7
dismissed: 3
profile_name: "small"
profile_source: "auto"
profile_lines: 6214
profile_basis: "3000–14999 → small"
---
```

`profile_lines` may be omitted when no measured line count applies. `status` is `complete` or `partial`. Keep rule keys, paths, commands, code, finding ids, structural field names, and evidence-rank tokens unchanged.

After the front matter, include these sections in this order:

1. `# <repo> smell-check`
2. `## Rule summary`
3. `## Synthesis`
4. `## Finding reports`
5. `## Environment`

The `Rule summary` section has one row per rule that has at least one finding, sorted by rule key:

```markdown
| rule | active | dismissed | evidence rank |
| --- | ---: | ---: | --- |
```

`active` and `dismissed` are the counts of that rule's findings. `evidence rank` lists the ranks present in those findings, comma-separated, such as `mechanical, estimate`.

The `Synthesis` section lists at most three hypotheses as Markdown list items, one per item, each citing only existing finding ids. Write one plain sentence instead when there is no shared cause.

The `Finding reports` section is the complete shard inventory:

```markdown
| status | area | report | count |
| --- | --- | --- | ---: |
```

Each `report` cell is a Markdown link. Its label and target are the same relative shard path, such as **findings/src-auth-active-001.md**. Escape a literal `|` inside a table cell as `\|`.

## Sharding

Merge, deduplicate, sort, and assign global ids before sharding. Then cut the sorted list into shards without reordering it.

1. Read the source area of each finding from its first location. Use the first two path segments; use the parent when fewer exist and `_root` for a root file.
2. Give each area one slug, different from every other area slug of the same status. Use the original name: keep non-ASCII characters as they are, such as `服務`, lowercase the ASCII letters, and replace every other ASCII character with one hyphen. The slug of `_root` is `root`.
3. Walk the sorted findings and start a new shard when the status changes, the area changes, or the open shard holds 100 findings. One area can own several shards that are not next to each other, such as **root-active-001.md**, **scripts-active-001.md**, and **root-active-002.md**.
4. Name each shard `<area-slug>-<status>-<part>.md`, such as **src-auth-active-001.md**. Number the parts of each area and status pair from `001` in cut order.
5. Add every shard and its exact finding count to the `Finding reports` table, in cut order.

Cut order keeps the global finding order, so shard rows already sort by status (active then dismissed) and by the first finding location in each shard. Follow [finding-schema.md](finding-schema.md) for each entry.

## Generate and validate

Read the summary, the finding shards, and [DESIGN.md](../DESIGN.md). Author one self-contained HTML index. Inline all CSS and JavaScript. Embed any necessary image as a data URL.

Subject text is untrusted data. Escape it before insertion into HTML and place snippets in fenced code blocks in Markdown. The index and summary link every Markdown shard. The index opens from disk without loading network or local resource files. The bundle contains only `index.html`, [summary.md](#summary-manifest), and the finding shards.

Run:

```shell
python scripts/validate_report.py .smell-check/<UTC-timestamp>
```

The validator checks summary metadata, counts, ids, shard limits, fixed Markdown fields, ordering, links, document structure, and self-contained HTML. It does not choose or generate the design.
