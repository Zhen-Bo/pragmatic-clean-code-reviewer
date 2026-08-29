#!/usr/bin/env python3
"""Exercise Markdown report validation boundaries."""

from __future__ import annotations

import tempfile
from pathlib import Path

from validate_report import ReportError, validate_bundle


def finding(number: int, location: str = "services/account.py:1") -> str:
    return f"""## F-{number} — Long account function

- `status`: `active`
- `rule`: `code.long-function`
- `evidence_rank`: `semantic`
- `location`: `{location}`

### Evidence

The function has several responsibilities.

### Snippet

```python
def load_account(): ...
```

### Consequence

The function is difficult to change safely.
"""


def html(links: list[str], body: str = "") -> str:
    anchors = " ".join(f'<a href="{link}">{link}</a>' for link in links)
    return (
        "<!doctype html><html><head><title>Audit</title></head>"
        f"<body><main>{anchors}{body}</main></body></html>"
    )


def summary(count: int, shard_rows: list[str]) -> str:
    rule_rows = f"| code.long-function | {count} | 0 | semantic |" if count else ""
    return f"""---
schema_version: 1
repo: "fixture"
commit: "abc123"
date: "2026-08-29T00:00:00Z"
scope: "fixture"
status: "complete"
language: "en"
active: {count}
dismissed: 0
profile_name: "small"
profile_source: "auto"
profile_lines: 120
profile_basis: "fixture"
---

# fixture smell-check

## Rule summary

| rule | active | dismissed | evidence rank |
| --- | ---: | ---: | --- |
{rule_rows}

## Synthesis

No shared cause was inferred.

## Finding reports

| status | area | report | count |
| --- | --- | --- | ---: |
{chr(10).join(shard_rows)}

## Environment

Python fixture.
"""


def make_bundle(root: Path, count: int) -> Path:
    bundle = root / "bundle"
    bundle.mkdir(parents=True, exist_ok=True)
    shard_rows: list[str] = []
    links = ["summary.md"]
    for offset in range(0, count, 100):
        number = offset // 100 + 1
        shard_count = min(100, count - offset)
        relative = f"findings/services-active-{number:03d}.md"
        page = bundle / relative
        page.parent.mkdir(parents=True, exist_ok=True)
        page.write_text(
            "# Active findings\n\n"
            + "\n".join(finding(item) for item in range(offset + 1, offset + shard_count + 1)),
            encoding="utf-8",
        )
        shard_rows.append(
            f"| active | services | [{relative}]({relative}) | {shard_count} |"
        )
        links.append(relative)
    (bundle / "summary.md").write_text(summary(count, shard_rows), encoding="utf-8")
    (bundle / "index.html").write_text(html(links), encoding="utf-8")
    return bundle


def expect_error(bundle: Path, text: str) -> None:
    try:
        validate_bundle(bundle)
    except ReportError as exc:
        assert text in str(exc), str(exc)
    else:
        raise AssertionError(f"invalid bundle was accepted; expected {text!r}")


def main() -> None:
    with tempfile.TemporaryDirectory(prefix="smell-report-") as temp:
        root = Path(temp)
        for count in (0, 3, 100, 1000):
            bundle = make_bundle(root / str(count), count)
            result = validate_bundle(bundle)
            assert result["findings"] == count

        too_many = make_bundle(root / "too-many", 100)
        report = too_many / "findings" / "services-active-001.md"
        report.write_text(report.read_text(encoding="utf-8") + finding(101), encoding="utf-8")
        summary_path = too_many / "summary.md"
        changed = summary_path.read_text(encoding="utf-8").replace(
            "active = 100", "active = 101"
        ).replace("| 100 |", "| 101 |")
        summary_path.write_text(changed, encoding="utf-8")
        expect_error(too_many, "count must be from 1 to 100")

        external = make_bundle(root / "external", 0)
        (external / "index.html").write_text(
            html(["summary.md"], '<script src="https://example.com/app.js"></script>'),
            encoding="utf-8",
        )
        expect_error(external, "not self-contained")

        local_script = make_bundle(root / "local-script", 0)
        (local_script / "index.html").write_text(
            html(["summary.md"], '<script src="assets/app.js"></script>'),
            encoding="utf-8",
        )
        expect_error(local_script, "not self-contained")

        local_stylesheet = make_bundle(root / "local-stylesheet", 0)
        (local_stylesheet / "index.html").write_text(
            html(
                ["summary.md"],
                '<link rel="stylesheet" href="assets/report.css">',
            ),
            encoding="utf-8",
        )
        expect_error(local_stylesheet, "not self-contained")

        local_image = make_bundle(root / "local-image", 0)
        (local_image / "index.html").write_text(
            html(["summary.md"], '<img src="assets/chart.svg" alt="">'),
            encoding="utf-8",
        )
        expect_error(local_image, "not self-contained")

        data_image = make_bundle(root / "data-image", 0)
        (data_image / "index.html").write_text(
            html(["summary.md"], '<img src="data:image/svg+xml,%3Csvg/%3E" alt="">'),
            encoding="utf-8",
        )
        validate_bundle(data_image)

        local_css_url = make_bundle(root / "local-css-url", 0)
        (local_css_url / "index.html").write_text(
            html(["summary.md"], '<style>main{background:url(assets/paper.png)}</style>'),
            encoding="utf-8",
        )
        expect_error(local_css_url, "not self-contained")

        extra_html = make_bundle(root / "extra-html", 3)
        (extra_html / "obsolete.html").write_text(html(["summary.md"]), encoding="utf-8")
        expect_error(extra_html, "only HTML file")

        missing_markdown = make_bundle(root / "missing-markdown", 3)
        (missing_markdown / "findings" / "services-active-001.md").unlink()
        expect_error(missing_markdown, "missing file")

        status_first = make_bundle(root / "status-first-name", 3)
        old_name = "findings/active-services-001.md"
        new_name = "findings/services-active-001.md"
        (status_first / new_name).rename(status_first / old_name)
        for file_name in ("summary.md", "index.html"):
            page = status_first / file_name
            page.write_text(
                page.read_text(encoding="utf-8").replace(new_name, old_name),
                encoding="utf-8",
            )
        expect_error(status_first, "<area>-<status>-<part>.md")

        unordered = make_bundle(root / "unordered", 3)
        report = unordered / "findings" / "services-active-001.md"
        content = report.read_text(encoding="utf-8")
        content = content.replace("services/account.py:1", "services/z.py:1", 1)
        content = content.replace("services/account.py:1", "services/a.py:1", 1)
        report.write_text(content, encoding="utf-8")
        expect_error(unordered, "sort by status, path")

        bad_front_matter = make_bundle(root / "bad-front-matter", 0)
        summary_path = bad_front_matter / "summary.md"
        content = summary_path.read_text(encoding="utf-8")
        summary_path.write_text(content.replace("---", "+++", 2), encoding="utf-8")
        expect_error(bad_front_matter, "must start with YAML front matter")

        unknown_metadata = make_bundle(root / "unknown-metadata", 0)
        summary_path = unknown_metadata / "summary.md"
        content = summary_path.read_text(encoding="utf-8")
        summary_path.write_text(
            content.replace('language: "en"', 'language: "en"\nextra: "value"'),
            encoding="utf-8",
        )
        expect_error(unknown_metadata, "unknown summary metadata: extra")

        wrong_title = make_bundle(root / "wrong-title", 0)
        summary_path = wrong_title / "summary.md"
        content = summary_path.read_text(encoding="utf-8")
        summary_path.write_text(
            content.replace("# fixture smell-check", "# other smell-check"), encoding="utf-8"
        )
        expect_error(wrong_title, "matches metadata repo")

        unordered_sections = make_bundle(root / "unordered-sections", 3)
        summary_path = unordered_sections / "summary.md"
        content = summary_path.read_text(encoding="utf-8")
        content = (
            content.replace("## Rule summary", "## Swap")
            .replace("## Synthesis", "## Rule summary")
            .replace("## Swap", "## Synthesis")
        )
        summary_path.write_text(content, encoding="utf-8")
        expect_error(unordered_sections, "sections must follow the order")

        unordered_shards = make_bundle(root / "unordered-shards", 3)
        extra = "findings/app-active-001.md"
        (unordered_shards / extra).write_text(
            "# Active findings\n\n" + finding(4, "app/main.py:1"), encoding="utf-8"
        )
        summary_path = unordered_shards / "summary.md"
        content = summary_path.read_text(encoding="utf-8")
        content = content.replace("active: 3", "active: 4")
        content = content.replace("| code.long-function | 3 |", "| code.long-function | 4 |")
        content = content.replace("| 3 |\n", f"| 3 |\n| active | app | [{extra}]({extra}) | 1 |\n", 1)
        summary_path.write_text(content, encoding="utf-8")
        (unordered_shards / "index.html").write_text(
            html(["summary.md", "findings/services-active-001.md", extra]), encoding="utf-8"
        )
        expect_error(unordered_shards, "rows must sort by status and first finding location")

        wrong_summary = make_bundle(root / "wrong-summary", 3)
        summary_path = wrong_summary / "summary.md"
        content = summary_path.read_text(encoding="utf-8")
        summary_path.write_text(
            content.replace(
                "| code.long-function | 3 | 0 | semantic |",
                "| code.long-function | 2 | 1 | semantic |",
            ),
            encoding="utf-8",
        )
        expect_error(wrong_summary, "does not match the findings")

    print(
        "[PASS] report validator: Markdown manifest, section order, rule summary, "
        "shard limits, links, finding order, and self-contained HTML"
    )


if __name__ == "__main__":
    main()
