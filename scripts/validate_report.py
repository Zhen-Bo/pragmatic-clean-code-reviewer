#!/usr/bin/env python3
"""Validate a Markdown-canonical smell-check report bundle."""

from __future__ import annotations

import argparse
import ast
import re
import sys
import unicodedata
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from typing import Any

MAX_FINDINGS_PER_SHARD = 100
ID_RE = re.compile(r"^F-([1-9][0-9]*)$")
RULE_RE = re.compile(r"^(?:code|test)\.[a-z0-9]+(?:-[a-z0-9]+)+$")
MARKDOWN_PATH_RE = re.compile(
    r"^findings/([a-z0-9]+(?:-[a-z0-9]+)*)-(active|dismissed)-([0-9]{3})\.md$"
)
LOCATION_RE = re.compile(r"^(.+):([1-9][0-9]*)$")
FINDING_HEADING_RE = re.compile(
    r"^## (F-[1-9][0-9]*)\s+(?:—|-|:)\s+(.+?)\s*$", re.MULTILINE
)
FIELD_RE = re.compile(r"^- `([a-z_]+)`: `([^`]+)`\s*$", re.MULTILINE)
VALID_STATUSES = {"active", "dismissed"}
VALID_RANKS = {"mechanical", "semantic", "estimate"}
STATUS_ORDER = {"active": 0, "dismissed": 1}
SUMMARY_SECTIONS = (
    "Rule summary",
    "Synthesis",
    "Finding reports",
    "Environment",
)
INVENTORY_COLUMNS = ("status", "area", "report", "count")
RULE_SUMMARY_COLUMNS = ("rule", "active", "dismissed", "evidence rank")
KNOWN_METADATA = {
    "schema_version",
    "repo",
    "commit",
    "date",
    "scope",
    "status",
    "language",
    "active",
    "dismissed",
    "profile_name",
    "profile_source",
    "profile_lines",
    "profile_basis",
}


class ReportError(ValueError):
    """A report bundle violates its Markdown or output contract."""


class SelfContainedHTMLParser(HTMLParser):
    """Find resource references that make index.html depend on another file."""

    RESOURCE_ATTRIBUTES = {
        "audio": {"src"},
        "embed": {"src"},
        "form": {"action"},
        "iframe": {"src"},
        "img": {"src", "srcset"},
        "input": {"src"},
        "object": {"data"},
        "source": {"src", "srcset"},
        "track": {"src"},
        "video": {"poster", "src"},
    }

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.violation: str | None = None
        self._style_depth = 0

    def check_css(self, css: str) -> None:
        if self.violation or re.search(r"@import\b", css, re.IGNORECASE):
            self.violation = self.violation or "CSS @import"
            return
        for match in re.finditer(r"url\(\s*([^)]*?)\s*\)", css, re.IGNORECASE):
            value = match.group(1).strip().strip("'\"")
            if value and not value.startswith("#") and not value.lower().startswith("data:"):
                self.violation = f"CSS url({value})"
                return

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        tag = tag.lower()
        if tag == "style":
            self._style_depth += 1
        for name, raw_value in attrs:
            name = name.lower()
            value = (raw_value or "").strip()
            if name == "style":
                self.check_css(value)
            if tag in {"script", "link"} and name in {"src", "href"}:
                self.violation = f"<{tag}> {name}"
            elif name in self.RESOURCE_ATTRIBUTES.get(tag, set()):
                if name == "srcset" or (
                    value
                    and not value.startswith("#")
                    and not value.lower().startswith("data:")
                ):
                    self.violation = f"<{tag}> {name}"

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "style" and self._style_depth:
            self._style_depth -= 1

    def handle_data(self, data: str) -> None:
        if self._style_depth:
            self.check_css(data)


def read_text(path: Path) -> str:
    try:
        content = path.read_text(encoding="utf-8")
    except FileNotFoundError as exc:
        raise ReportError(f"missing file: {path}") from exc
    if not content.strip():
        raise ReportError(f"{path} must not be empty")
    return content


def safe_path(base: Path, relative: str, field: str) -> Path:
    candidate = Path(relative)
    if candidate.is_absolute():
        raise ReportError(f"{field} must be relative: {relative}")
    resolved = (base / candidate).resolve()
    base_resolved = base.resolve()
    if resolved != base_resolved and base_resolved not in resolved.parents:
        raise ReportError(f"{field} leaves its report directory: {relative}")
    return resolved


def require_meta_text(metadata: dict[str, Any], key: str) -> str:
    value = metadata.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ReportError(f"summary metadata {key} must be non-empty text")
    return value


def parse_front_matter(summary: str) -> tuple[dict[str, Any], str]:
    lines = summary.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ReportError("summary.md must start with YAML front matter")
    try:
        closing = next(
            index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---"
        )
    except StopIteration as exc:
        raise ReportError("summary.md YAML front matter is not closed") from exc
    metadata: dict[str, Any] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        match = re.fullmatch(r"([a-z][a-z0-9_]*)\s*:\s*(.+)", line)
        if not match:
            raise ReportError(f"invalid YAML metadata at summary.md:{line_number}")
        key, raw_value = match.groups()
        if key in metadata:
            raise ReportError(f"duplicate YAML metadata key: {key}")
        raw_value = raw_value.strip()
        if re.fullmatch(r"-?[0-9]+", raw_value):
            value: Any = int(raw_value)
        elif raw_value.startswith(('"', "'", "[")):
            try:
                value = ast.literal_eval(raw_value)
            except (SyntaxError, ValueError) as exc:
                raise ReportError(
                    f"invalid YAML metadata value at summary.md:{line_number}"
                ) from exc
        else:
            value = raw_value
        metadata[key] = value
    return metadata, "\n".join(lines[closing + 1 :])


def validate_metadata(metadata: dict[str, Any]) -> None:
    unknown = sorted(set(metadata) - KNOWN_METADATA)
    if unknown:
        raise ReportError("unknown summary metadata: " + ", ".join(unknown))
    if metadata.get("schema_version") != 1:
        raise ReportError("summary metadata schema_version must be 1")
    for key in (
        "repo",
        "commit",
        "date",
        "scope",
        "status",
        "language",
        "profile_name",
        "profile_source",
        "profile_basis",
    ):
        require_meta_text(metadata, key)
    if metadata["status"] not in {"complete", "partial"}:
        raise ReportError("summary metadata status must be complete or partial")
    for key in ("active", "dismissed"):
        value = metadata.get(key)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ReportError(f"summary metadata {key} must be a non-negative integer")
    if "profile_lines" in metadata:
        value = metadata["profile_lines"]
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ReportError("summary metadata profile_lines must be non-negative")


def section(markdown: str, heading: str) -> str:
    match = re.search(
        rf"^## {re.escape(heading)}\s*$\n?(.*?)(?=^## |\Z)",
        markdown,
        re.MULTILINE | re.DOTALL,
    )
    if not match:
        raise ReportError(f"summary.md is missing section: {heading}")
    return match.group(1).strip()


def split_table_row(line: str) -> list[str]:
    value = line.strip()
    if not value.startswith("|") or not value.endswith("|"):
        raise ReportError(f"invalid Markdown table row: {line}")
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in value[1:-1]:
        if escaped:
            current.append(character)
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(character)
    if escaped:
        current.append("\\")
    cells.append("".join(current).strip())
    return cells


def parse_table(section_text: str, columns: tuple[str, ...], context: str) -> list[dict[str, str]]:
    lines = section_text.splitlines()
    header_index = next(
        (index for index, line in enumerate(lines) if line.strip().startswith("|")),
        None,
    )
    if header_index is None or header_index + 1 >= len(lines):
        raise ReportError(f"{context} must contain a Markdown table")
    header = tuple(cell.lower() for cell in split_table_row(lines[header_index]))
    if header != columns:
        raise ReportError(f"{context} table columns must be: {', '.join(columns)}")
    separator = split_table_row(lines[header_index + 1])
    if len(separator) != len(columns) or any(
        not re.fullmatch(r":?-{3,}:?", cell) for cell in separator
    ):
        raise ReportError(f"{context} has an invalid table separator")
    rows: list[dict[str, str]] = []
    for line in lines[header_index + 2 :]:
        if not line.strip().startswith("|"):
            break
        values = split_table_row(line)
        if len(values) != len(columns):
            raise ReportError(f"{context} has a row with the wrong column count")
        rows.append(dict(zip(columns, values, strict=True)))
    return rows


def validate_html(path: Path) -> str:
    content = read_text(path)
    lowered = content.lower()
    for token in ("<!doctype html", "<html", "<title", "<main"):
        if token not in lowered:
            raise ReportError(f"{path} is missing {token}")
    parser = SelfContainedHTMLParser()
    parser.feed(content)
    if parser.violation:
        raise ReportError(f"{path} is not self-contained: {parser.violation}")
    return content


def require_html_link(index: str, relative: str) -> None:
    if not re.search(
        rf"href\s*=\s*(['\"]){re.escape(relative)}(?:#[^'\"]*)?\1",
        index,
        re.IGNORECASE,
    ):
        raise ReportError(f"index.html does not link {relative}")


def location_key(location: str, context: str) -> tuple[str, int]:
    match = LOCATION_RE.fullmatch(location)
    if not match:
        raise ReportError(f"{context} must be a repo-relative path:line")
    path = match.group(1)
    pure_path = PurePosixPath(path)
    if (
        "\\" in path
        or pure_path.is_absolute()
        or ".." in pure_path.parts
        or re.match(r"^[A-Za-z]:", path)
    ):
        raise ReportError(f"{context} must be a repo-relative path:line")
    return path, int(match.group(2))


def finding_sort_key(record: dict[str, Any]) -> tuple[int, str, int, str, int]:
    path, line = location_key(record["locations"][0], f"finding {record['id']} location")
    return (
        STATUS_ORDER[record["status"]],
        path,
        line,
        record["rule"],
        int(ID_RE.fullmatch(record["id"]).group(1)),
    )


def subsection(body: str, heading: str, context: str) -> str:
    match = re.search(
        rf"^### {re.escape(heading)}\s*$\n?(.*?)(?=^### |\Z)",
        body,
        re.MULTILINE | re.DOTALL,
    )
    if not match or not match.group(1).strip():
        raise ReportError(f"{context} is missing section: {heading}")
    return match.group(1).strip()


def parse_findings(page: str, expected_status: str, path: Path) -> list[dict[str, Any]]:
    matches = list(FINDING_HEADING_RE.finditer(page))
    records: list[dict[str, Any]] = []
    for index, match in enumerate(matches):
        body_end = matches[index + 1].start() if index + 1 < len(matches) else len(page)
        body = page[match.end() : body_end]
        context = f"{path} finding {match.group(1)}"
        metadata_end = body.find("\n### ")
        metadata_text = body if metadata_end < 0 else body[:metadata_end]
        pairs = FIELD_RE.findall(metadata_text)
        fields: dict[str, str] = {}
        locations: list[str] = []
        for key, value in pairs:
            if key == "location":
                locations.append(value)
            elif key not in {"status", "rule", "evidence_rank"}:
                raise ReportError(f"{context} has unknown field: {key}")
            elif key in fields:
                raise ReportError(f"{context} repeats field: {key}")
            else:
                fields[key] = value
        required = {"status", "rule", "evidence_rank"}
        missing = sorted(required - fields.keys())
        if missing:
            raise ReportError(f"{context} missing fields: {', '.join(missing)}")
        if fields["status"] != expected_status or fields["status"] not in VALID_STATUSES:
            raise ReportError(f"{context}.status does not match shard status")
        if not RULE_RE.fullmatch(fields["rule"]):
            raise ReportError(f"{context}.rule is invalid")
        if fields["evidence_rank"] not in VALID_RANKS:
            raise ReportError(f"{context}.evidence_rank is invalid")
        if not locations:
            raise ReportError(f"{context} needs at least one location")
        for location in locations:
            location_key(location, f"{context} location")
        record: dict[str, Any] = {
            "id": match.group(1),
            "title": match.group(2).strip(),
            "status": fields["status"],
            "rule": fields["rule"],
            "evidence_rank": fields["evidence_rank"],
            "locations": locations,
            "evidence": subsection(body, "Evidence", context),
        }
        snippet_block = subsection(body, "Snippet", context)
        snippet_match = re.fullmatch(
            r"(```|~~~)[^\n]*\n(.*?)\n\1", snippet_block, re.DOTALL
        )
        if not snippet_match:
            raise ReportError(f"{context} Snippet must contain one fenced code block")
        record["snippet"] = snippet_match.group(2)
        if len(record["snippet"].splitlines()) > 10:
            raise ReportError(f"{context} snippet exceeds 10 lines")
        outcome = "Consequence" if expected_status == "active" else "Removal reason"
        record["outcome"] = subsection(body, outcome, context)
        records.append(record)
    return records


def parse_inventory(summary_body: str) -> list[dict[str, Any]]:
    rows = parse_table(
        section(summary_body, "Finding reports"),
        INVENTORY_COLUMNS,
        "Finding reports",
    )
    inventory: list[dict[str, Any]] = []
    seen_paths: set[str] = set()
    next_part: dict[tuple[str, str], int] = {}
    for index, row in enumerate(rows):
        context = f"Finding reports row {index + 1}"
        if row["status"] not in VALID_STATUSES:
            raise ReportError(f"{context} status is invalid")
        if not row["area"]:
            raise ReportError(f"{context} area must not be empty")
        link = re.fullmatch(r"\[([^]]+)]\(([^)]+)\)", row["report"])
        if not link or link.group(1) != link.group(2):
            raise ReportError(f"{context} report must link its exact relative path")
        relative = link.group(2)
        filename = MARKDOWN_PATH_RE.fullmatch(relative)
        if not filename:
            raise ReportError(
                f"{context} report must be findings/<area>-<status>-<part>.md"
            )
        area_slug = unicodedata.normalize("NFKD", row["area"])
        area_slug = area_slug.encode("ascii", "ignore").decode("ascii").lower()
        area_slug = re.sub(r"[^a-z0-9]+", "-", area_slug).strip("-") or "root"
        if filename.group(1) != area_slug or filename.group(2) != row["status"]:
            raise ReportError(f"{context} report name does not match its area and status")
        group = (row["status"], row["area"])
        expected_part = next_part.get(group, 1)
        if int(filename.group(3)) != expected_part:
            raise ReportError(f"{context} report part must be {expected_part:03d}")
        next_part[group] = expected_part + 1
        if relative in seen_paths:
            raise ReportError(f"{context} reuses a shard path")
        seen_paths.add(relative)
        try:
            count = int(row["count"])
        except ValueError as exc:
            raise ReportError(f"{context} count must be an integer") from exc
        if count < 1 or count > MAX_FINDINGS_PER_SHARD:
            raise ReportError(f"{context} count must be from 1 to 100")
        inventory.append({**row, "report": relative, "count": count})
    return inventory


def validate_bundle(bundle_dir: Path) -> dict[str, int]:
    index_path = bundle_dir / "index.html"
    index = validate_html(index_path)
    extra_html = sorted(
        path
        for path in bundle_dir.rglob("*")
        if path.is_file() and path.suffix.lower() == ".html" and path != index_path
    )
    if extra_html:
        raise ReportError(f"index.html must be the only HTML file: {extra_html[0]}")
    require_html_link(index, "summary.md")

    summary = read_text(bundle_dir / "summary.md")
    metadata, summary_body = parse_front_matter(summary)
    validate_metadata(metadata)
    title = re.search(
        rf"^# {re.escape(metadata['repo'])} smell-check\s*$", summary_body, re.MULTILINE
    )
    if not title:
        raise ReportError(
            "summary.md needs a '# <repo> smell-check' title that matches metadata repo"
        )
    positions: list[int] = [title.start()]
    for heading in SUMMARY_SECTIONS:
        section(summary_body, heading)
        positions.append(
            re.search(rf"^## {re.escape(heading)}\s*$", summary_body, re.MULTILINE).start()
        )
    if positions != sorted(positions):
        raise ReportError(
            "summary.md title and sections must follow the order: # <repo> smell-check, "
            + ", ".join(SUMMARY_SECTIONS)
        )

    inventory = parse_inventory(summary_body)
    findings: list[dict[str, Any]] = []
    declared_paths: set[Path] = set()
    seen_ids: set[str] = set()
    shard_keys: list[tuple[int, str, int]] = []
    for shard in inventory:
        shard_path = safe_path(bundle_dir, shard["report"], "finding report")
        declared_paths.add(shard_path)
        page = read_text(shard_path)
        require_html_link(index, shard["report"])
        records = parse_findings(page, shard["status"], shard_path)
        if len(records) != shard["count"]:
            raise ReportError(f"{shard_path} count does not match Finding reports")
        first_path, first_line = location_key(
            records[0]["locations"][0], f"{shard_path} first finding location"
        )
        shard_keys.append((STATUS_ORDER[shard["status"]], first_path, first_line))
        for record in records:
            if record["id"] in seen_ids:
                raise ReportError(f"duplicate finding id: {record['id']}")
            seen_ids.add(record["id"])
            findings.append(record)
    if shard_keys != sorted(shard_keys):
        raise ReportError(
            "Finding reports rows must sort by status and first finding location"
        )

    findings_dir = bundle_dir / "findings"
    actual_paths = (
        {path.resolve() for path in findings_dir.rglob("*.md") if path.is_file()}
        if findings_dir.exists()
        else set()
    )
    undeclared = sorted(actual_paths - declared_paths)
    if undeclared:
        raise ReportError(f"undeclared finding report: {undeclared[0]}")
    allowed_files = {
        index_path.resolve(),
        (bundle_dir / "summary.md").resolve(),
        *declared_paths,
    }
    actual_files = {
        path.resolve() for path in bundle_dir.rglob("*") if path.is_file()
    }
    unexpected_files = sorted(actual_files - allowed_files)
    if unexpected_files:
        raise ReportError(f"unexpected report file: {unexpected_files[0]}")
    active = sum(item["status"] == "active" for item in findings)
    dismissed = len(findings) - active
    if (active, dismissed) != (metadata["active"], metadata["dismissed"]):
        raise ReportError("summary counts do not match finding reports")
    numbers = [int(ID_RE.fullmatch(item["id"]).group(1)) for item in findings]
    if numbers != list(range(1, len(findings) + 1)):
        raise ReportError("findings must use one contiguous F-1 to F-n sequence")
    keys = [finding_sort_key(item) for item in findings]
    if keys != sorted(keys):
        raise ReportError(
            "findings must sort by status, path, line, rule, and id"
        )

    summary_rows = parse_table(
        section(summary_body, "Rule summary"), RULE_SUMMARY_COLUMNS, "Rule summary"
    )
    expected: dict[str, dict[str, Any]] = {}
    for item in findings:
        entry = expected.setdefault(
            item["rule"], {"active": 0, "dismissed": 0, "ranks": set()}
        )
        entry[item["status"]] += 1
        entry["ranks"].add(item["evidence_rank"])
    if [row["rule"] for row in summary_rows] != sorted(expected):
        raise ReportError(
            "Rule summary must have one row per finding rule, sorted by rule key"
        )
    for row in summary_rows:
        entry = expected[row["rule"]]
        ranks = {token.strip() for token in row["evidence rank"].split(",")}
        if (row["active"], row["dismissed"], ranks) != (
            str(entry["active"]),
            str(entry["dismissed"]),
            entry["ranks"],
        ):
            raise ReportError(
                f"Rule summary row for {row['rule']} does not match the findings"
            )

    synthesis = section(summary_body, "Synthesis")
    cited_ids = set(re.findall(r"\bF-[1-9][0-9]*\b", synthesis))
    unknown_ids = sorted(cited_ids - seen_ids)
    if unknown_ids:
        raise ReportError("Synthesis cites unknown findings: " + ", ".join(unknown_ids))
    hypotheses = re.findall(r"^(?:[-*]|[1-9][0-9]*\.)\s+", synthesis, re.MULTILINE)
    if len(hypotheses) > 3:
        raise ReportError("Synthesis must contain at most three hypotheses")
    return {"findings": len(findings), "shards": len(inventory)}


def main() -> None:
    parser = argparse.ArgumentParser(description="Validate a smell-check report bundle")
    parser.add_argument("bundle", type=Path)
    args = parser.parse_args()
    try:
        result = validate_bundle(args.bundle)
    except ReportError as exc:
        print(f"report validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
    print(f"valid report: {result['findings']} findings across {result['shards']} shards")


if __name__ == "__main__":
    main()
