#!/usr/bin/env python3
"""
Skill Validator - Validates skill folder structure and content.

Usage:
    python scripts/validate_skill.py [skill_directory]
    python scripts/validate_skill.py [skill_directory] --expected-version 2.0.0
    python scripts/validate_skill.py --self-check

Defaults to the current working directory when skill_directory is omitted.
Exit 0 on full pass; non-zero if any check fails (or on usage/self-check failure).
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

# Rule ID prefixes → canonical reference file (relative to skill root)
CANONICAL = {
    "CC": "references/clean-code.md",
    "CA": "references/clean-architecture.md",
    "PP": "references/pragmatic-programmer.md",
}
ID_RANGES = {"CC": (1, 202), "CA": (1, 48), "PP": (1, 100)}

MAX_SKILL_LINES = 438
MAX_SKILL_WORDS = 3250

# references/*.md longer than this must carry a table of contents
TOC_REQUIRED_OVER_LINES = 100
TOC_SCAN_LINES = 30

# Frontmatter contract. Top-level `version` is deliberately absent: the version
# lives at metadata.version, and a stray top-level key would silently shadow it.
ALLOWED_FRONTMATTER = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

# Closed 19-point checklist taxonomy: A1–A5, B1–B4, C1–C6, D1–D2, E1–E2
CHECKLIST_GROUPS = (("A", 5), ("B", 4), ("C", 6), ("D", 2), ("E", 2))
CHECKLIST_IDS = tuple(
    f"{group}{n}" for group, count in CHECKLIST_GROUPS for n in range(1, count + 1)
)
CHECKLIST_ID_SET = frozenset(CHECKLIST_IDS)

# Each entry is a tuple of accepted heading phrases (any one satisfies it).
REQUIRED_HEADINGS: tuple[tuple[str, ...], ...] = (
    ("Review Integrity",),
    ("Profile Discovery and Calibration",),
    ("Scope Manifest",),
    ("Review Protocol",),
    ("Coverage Ledger", "Coverage Cell Grammar"),
    ("Whole-Scope Checks",),
    ("Coverage Reconciliation",),
    ("Verdict",),
    ("Reference Loading",),
)

REQUIRED_FILES = ("references/review-profile.md",)

# Range separator: en-dash, em-dash, tilde, or hyphen between two numbers
RANGE_RE = re.compile(
    r"\b(CC|CA|PP)-(\d+)\s*[–—~\-]\s*(\d+)\b"
)
SINGLE_RE = re.compile(r"\b(CC|CA|PP)-(\d+)\b")
# Markdown links (images included): [text](target)
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# Changelog version heading: ## 1.2.3 / ## [1.2.3] - 2024-01-01 / ## 1.2.3-rc1
CHANGELOG_VER_RE = re.compile(
    r"^##\s+\[?v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\]?(?:\s|$|[(\-–—])",
    re.MULTILINE,
)
# A checklist point definition: a list item or heading whose content starts with the
# point ID, either bolded ("- **A1 Contract integrity** — ...", "- **A1 — ...**") or
# bare and followed by a separator ("### A1 — ..."). Line-anchored so that prose
# mentions, table rows, and ledger cells are not counted as definitions.
CHECKLIST_DEF_RE = re.compile(
    r"^[ \t]*(?:[-*+][ \t]+)?(?:#{1,6}[ \t]+)?"
    r"(?:\*\*([A-E]\d)\b|([A-E]\d)[ \t]*[—–:.-])",
    re.MULTILINE,
)
# Per-finding point field: "Point: A2"
POINT_FIELD_RE = re.compile(r"Point:\s*([^\s|`*,;)\]]+)")
# Point-prefixed ledger cell token: "A2:F1", "E1:Pass; E2:Gated:L4"
LEDGER_POINT_RE = re.compile(r"\b([A-E]\d):")
# TOC signals inside the head of a reference file
TOC_HEADING_RE = re.compile(r"^#{1,6}\s+.*\bcontents\b", re.IGNORECASE | re.MULTILINE)
TOC_LINK_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\[[^\]]+\]\(#", re.MULTILINE)

# Literal regressions that must hold in the example report
REPORT_EXAMPLE = "references/report-example.md"
REPORT_MUST_CONTAIN = (
    ("Point:", re.compile(r"Point:")),
    ("D2 / R3 / C2", re.compile(r"D2\s*/\s*R3\s*/\s*C2")),
    ("6/10", re.compile(r"6/10")),
)
REPORT_MUST_NOT_CONTAIN = (("N/A:no tests", re.compile(r"N/A:no tests")),)

# --- Coverage Ledger grammar and arithmetic (references/report-example.md) ---
# The five ledger domains, in column order. A table is a Coverage Ledger only if
# its header names all five.
LEDGER_DOMAINS = (
    "Contract & Safety",
    "Readability",
    "Design & Architecture",
    "Testing",
    "Performance & Operability",
)
# One point-qualified cell token. A point-qualified `Pass` is valid here; a bare
# `Pass` is valid only as the entire cell (checked separately).
LEDGER_TOKEN_RE = re.compile(
    r"^[A-E]\d:(?:"
    r"Pass"
    r"|F\d+(?:,F\d+)*"
    r"|N/A:[a-z-]+"
    r"|Gated:L[1-5]"
    r"|Waived:F\d+/W\d+"
    r"|CappedMinor:\d+"
    r")$"
)
# A cell value that starts with an unqualified deviation keyword hides which
# points it covers; `Gated` is the one the report contract calls out by name.
BARE_GATED_RE = re.compile(r"^Gated\b")
# `—`/`-` and empty are deliberate "not accounted" markers, not grammar errors
BLANK_LEDGER_CELLS = frozenset({"", "-", "--", "–", "—"})
TABLE_DELIM_RE = re.compile(r"^\s*\|(?:\s*:?-+:?\s*\|)+\s*$")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})(.*)$")
FINDING_ID_RE = re.compile(r"\bF\d+\b")
# A reported finding: "- **[src/a.ts:41] F1 — title**"
FINDING_HEADING_RE = re.compile(
    r"^[ \t]*[-*+][ \t]+\*\*\[[^\]]+\][ \t]*(F\d+)\b", re.MULTILINE
)
WAIVER_HEADING_RE = re.compile(r"^#{1,6}[ \t]+.*Waiver Disclosure", re.MULTILINE)
ANY_HEADING_RE = re.compile(r"^#{1,6}[ \t]+", re.MULTILINE)
WHOLE_SCOPE_HEADER = ["Check", "Result", "Finding"]
IN_SCOPE_RE = re.compile(r"In scope:\s*(\d+)")
# "Domain cells accounted: 15/15" and "15/15 domain cells"
CELL_CLAIM_RES = (
    re.compile(r"Domain cells accounted:\s*(\d+)\s*/\s*(\d+)"),
    re.compile(r"(\d+)\s*/\s*(\d+)\s+domain cells"),
)
# Claims that must exist and survive recomputation, so the arithmetic check can
# never pass vacuously by deleting the worked examples' own totals.
REQUIRED_CELL_CLAIMS = ((15, 15), (6, 10))

# --- Document content regressions ------------------------------------------
# Decisions that are only visible as wording. Each entry is
# (relative path, label, pattern); whitespace is tolerated, wording is not.
CONTENT_MUST_CONTAIN = (
    # Important-verdict breadth weight, replacing the retired scope formula
    ("SKILL.md", "min(affected_files, 3)", re.compile(r"min\(affected_files,\s*3\)")),
    # Overlapping profiles resolve to the stricter candidate, not an L3 fallback
    ("references/review-profile.md", "stricter", re.compile(r"stricter")),
    (
        "references/review-profile.md",
        "effective level / effective_level",
        re.compile(r"effective[ _]level", re.IGNORECASE),
    ),
    ("docs/metrics.md", "50%", re.compile(r"50%")),
)
# The scope-scaled Important threshold was withdrawn; neither spelling may return.
CONTENT_MUST_NOT_CONTAIN = (
    ("SKILL.md", "floor(files/5)", re.compile(r"floor\(files\s*/\s*5\)")),
    ("SKILL.md", "floor(in_scope_files", re.compile(r"floor\(in_scope_files")),
)

# `[fundamental]` is an Important architecture tag, never a severity of its own.
# Flags a single line that re-attaches it to the Critical tier. `[^.\n]` stops at
# a sentence boundary, and requiring `Critical` to come *first* keeps the two
# legitimate shapes clear: "`[fundamental]` … without requiring Critical
# severity" and "Important at L3–L5, never `[fundamental]`". Nothing is
# whitelisted; if a lane needs to write "Critical … never `[fundamental]`" in one
# sentence, narrow this to `Critical (?:architecture )?finding tagged` instead of
# adding an exception.
CRITICAL_FUNDAMENTAL_RE = re.compile(r"Critical[^.\n]{0,60}\[fundamental\]")


def _scalar(val: str) -> str:
    """Strip matching surrounding quotes from a YAML scalar."""
    if len(val) >= 2 and (
        (val.startswith('"') and val.endswith('"'))
        or (val.startswith("'") and val.endswith("'"))
    ):
        return val[1:-1]
    return val


def parse_frontmatter(content: str) -> tuple[dict | None, str | None]:
    """
    Parse simple YAML frontmatter without PyYAML.

    Supports flat scalars, `>` / `|` block scalars, and ONE level of indented
    children under a key with an empty value (e.g. `metadata:` → dict).
    """
    if not content.startswith("---"):
        return None, "No YAML frontmatter found"
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return None, "Invalid frontmatter format"

    data: dict = {}
    key: str | None = None
    block_lines: list[str] = []
    in_block = False
    nested_key: str | None = None
    nested: dict[str, str] = {}

    def finish_block() -> None:
        nonlocal in_block, block_lines
        if in_block and key is not None:
            # Folded-style join is enough for validation (length / angle brackets)
            data[key] = " ".join(line.strip() for line in block_lines if line.strip())
        in_block = False
        block_lines = []

    def finish_nested() -> None:
        nonlocal nested_key, nested
        # No `child: value` pairs found (e.g. a sequence) → keep the scalar value
        if nested_key is not None and nested:
            data[nested_key] = nested
        nested_key = None
        nested = {}

    for line in match.group(1).split("\n"):
        if in_block:
            if line.startswith("  ") or line.startswith("\t") or line.strip() == "":
                block_lines.append(line)
                continue
            finish_block()

        if nested_key is not None:
            if line.strip() == "":
                continue
            if line.startswith(" ") or line.startswith("\t"):
                child = re.match(r"^[ \t]+([A-Za-z0-9_.-]+):\s*(.*)$", line)
                if child:
                    nested[child.group(1)] = _scalar(child.group(2).strip())
                continue
            finish_nested()

        m = re.match(r"^([A-Za-z0-9_-]+):\s*(.*)$", line)
        if not m:
            continue
        key, val = m.group(1), m.group(2).strip()
        if val in (">", "|", ">-", "|-"):
            in_block = True
            block_lines = []
            data[key] = ""
        elif val == "":
            # Either an empty scalar or the parent of an indented block
            data[key] = ""
            nested_key = key
            nested = {}
        else:
            data[key] = _scalar(val)

    finish_block()
    finish_nested()
    return data, None


def metadata_version(frontmatter: dict) -> str | None:
    """metadata.version as a non-empty string, else None."""
    meta = frontmatter.get("metadata")
    if not isinstance(meta, dict):
        return None
    version = meta.get("version")
    if isinstance(version, str) and version.strip():
        return version.strip()
    return None


def check_frontmatter(skill_md: Path) -> tuple[bool, list[str], dict]:
    """Frontmatter shape, allowed keys, and required license/metadata.version."""
    msgs: list[str] = []
    if not skill_md.exists():
        return False, [f"{skill_md.name}: SKILL.md not found"], {}

    content = skill_md.read_text(encoding="utf-8")
    frontmatter, err = parse_frontmatter(content)
    if err:
        return False, [f"{skill_md.name}: {err}"], {}
    assert frontmatter is not None

    unexpected = set(frontmatter.keys()) - ALLOWED_FRONTMATTER
    if unexpected:
        detail = ""
        if "version" in unexpected:
            detail = (
                " Top-level 'version' is rejected: declare the version at "
                "metadata.version instead."
            )
        return (
            False,
            [
                f"{skill_md.name}: Unexpected key(s) in frontmatter: "
                f"{', '.join(sorted(unexpected))}. "
                f"Allowed: {', '.join(sorted(ALLOWED_FRONTMATTER))}.{detail}"
            ],
            frontmatter,
        )

    if "name" not in frontmatter:
        msgs.append(f"{skill_md.name}: Missing 'name' in frontmatter")
    if "description" not in frontmatter:
        msgs.append(f"{skill_md.name}: Missing 'description' in frontmatter")

    license_value = frontmatter.get("license")
    if not isinstance(license_value, str) or not license_value.strip():
        msgs.append(f"{skill_md.name}: Missing 'license' in frontmatter")

    if "metadata" not in frontmatter:
        msgs.append(f"{skill_md.name}: Missing 'metadata' block in frontmatter")
    elif not isinstance(frontmatter["metadata"], dict):
        msgs.append(
            f"{skill_md.name}: 'metadata' must be a block of indented key: value "
            "pairs containing 'version'"
        )
    elif metadata_version(frontmatter) is None:
        msgs.append(f"{skill_md.name}: Missing 'metadata.version' in frontmatter")

    name = frontmatter.get("name", "")
    if "name" in frontmatter and not isinstance(name, str):
        msgs.append(f"{skill_md.name}: Name must be a string, got {type(name).__name__}")
        name = ""
    name = name.strip() if isinstance(name, str) else ""
    if name:
        if not re.match(r"^[a-z0-9-]+$", name):
            msgs.append(
                f"{skill_md.name}: Name '{name}' should be hyphen-case "
                "(lowercase letters, digits, and hyphens only)"
            )
        if name.startswith("-") or name.endswith("-") or "--" in name:
            msgs.append(
                f"{skill_md.name}: Name '{name}' cannot start/end with hyphen "
                "or contain consecutive hyphens"
            )
        if len(name) > 64:
            msgs.append(
                f"{skill_md.name}: Name is too long ({len(name)} characters). "
                "Maximum is 64 characters."
            )

    description = frontmatter.get("description", "")
    if "description" in frontmatter and not isinstance(description, str):
        msgs.append(
            f"{skill_md.name}: Description must be a string, "
            f"got {type(description).__name__}"
        )
        description = ""
    description = description.strip() if isinstance(description, str) else ""
    if description:
        if "<" in description or ">" in description:
            msgs.append(
                f"{skill_md.name}: Description cannot contain angle brackets (< or >)"
            )
        if len(description) > 1024:
            msgs.append(
                f"{skill_md.name}: Description is too long "
                f"({len(description)} characters). Maximum is 1024 characters."
            )

    return (len(msgs) == 0, msgs or ["Frontmatter OK"], frontmatter)


def load_defined_ids(skill_path: Path) -> dict[str, set[str]]:
    """Load rule IDs defined in each canonical reference file."""
    defined: dict[str, set[str]] = {p: set() for p in CANONICAL}
    for prefix, rel in CANONICAL.items():
        path = skill_path / rel
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        # Robust: any PREFIX-N token in the defining file counts as defined
        for m in SINGLE_RE.finditer(text):
            if m.group(1) == prefix:
                defined[prefix].add(f"{prefix}-{int(m.group(2))}")
    return defined


def iter_doc_files(skill_path: Path) -> list[Path]:
    """Markdown files scanned for citations and links."""
    files: list[Path] = []
    for name in ("SKILL.md", "README.md"):
        p = skill_path / name
        if p.exists():
            files.append(p)
    for sub in ("references", "docs"):
        d = skill_path / sub
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    return files


def iter_reference_files(skill_path: Path) -> list[Path]:
    d = skill_path / "references"
    return sorted(d.glob("*.md")) if d.is_dir() else []


def iter_active_files(skill_path: Path) -> list[Path]:
    """
    Markdown that states the skill's active contract.

    `docs/*.md` is deliberately non-recursive: docs/reports/ archives review
    reports that quote superseded wording on purpose, so they are not active.
    """
    files: list[Path] = []
    skill_md = skill_path / "SKILL.md"
    if skill_md.is_file():
        files.append(skill_md)
    for sub in ("references", "docs"):
        d = skill_path / sub
        if d.is_dir():
            files.extend(sorted(d.glob("*.md")))
    return files


def expand_citation_tokens(text: str) -> list[tuple[str, int]]:
    """
    Return list of (TOKEN, line_no) for each cited rule ID.
    Range forms (en-dash/tilde/hyphen) contribute both endpoints.
    """
    results: list[tuple[str, int]] = []
    # Mark range spans so singles inside them are not double-counted
    range_spans: list[tuple[int, int]] = []

    for m in RANGE_RE.finditer(text):
        prefix, a, b = m.group(1), int(m.group(2)), int(m.group(3))
        line_no = text.count("\n", 0, m.start()) + 1
        results.append((f"{prefix}-{a}", line_no))
        results.append((f"{prefix}-{b}", line_no))
        range_spans.append((m.start(), m.end()))

    def in_range_span(pos: int) -> bool:
        return any(s <= pos < e for s, e in range_spans)

    for m in SINGLE_RE.finditer(text):
        if in_range_span(m.start()):
            continue
        prefix, num = m.group(1), int(m.group(2))
        line_no = text.count("\n", 0, m.start()) + 1
        results.append((f"{prefix}-{num}", line_no))

    return results


def check_rule_citations(skill_path: Path) -> tuple[bool, list[str]]:
    defined = load_defined_ids(skill_path)
    failures: list[str] = []
    # Canonical path resolution for skip
    canonical_paths = {
        prefix: (skill_path / rel).resolve() for prefix, rel in CANONICAL.items()
    }

    for path in iter_doc_files(skill_path):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(skill_path)
        resolved = path.resolve()

        for token, line_no in expand_citation_tokens(text):
            prefix = token.split("-", 1)[0]
            # Skip tokens inside the canonical file that defines them
            if resolved == canonical_paths.get(prefix):
                continue

            lo, hi = ID_RANGES[prefix]
            num = int(token.split("-", 1)[1])
            if num < lo or num > hi:
                failures.append(
                    f"{rel}:{line_no}: {token} out of range "
                    f"({prefix} must be {lo}–{hi})"
                )
                continue

            if token not in defined[prefix]:
                can_rel = CANONICAL[prefix]
                failures.append(
                    f"{rel}:{line_no}: {token} not found in {can_rel}"
                )

    if failures:
        return False, failures
    return True, ["All cited rule IDs exist and are in range"]


def check_relative_links(skill_path: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for path in iter_doc_files(skill_path):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(skill_path)
        for m in LINK_RE.finditer(text):
            target = m.group(2).strip()
            # Strip title: url "title" or url 'title'
            target = re.split(r"\s+", target, maxsplit=1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            # fragment only already handled; strip anchors from path
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            # Ignore absolute filesystem paths and protocol-ish targets
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", file_part):
                continue
            dest = (path.parent / file_part).resolve()
            line_no = text.count("\n", 0, m.start()) + 1
            if not dest.exists():
                failures.append(
                    f"{rel}:{line_no}: broken relative link → {target}"
                )
    if failures:
        return False, failures
    return True, ["All relative markdown links resolve"]


def check_version_changelog(
    skill_path: Path, frontmatter: dict
) -> tuple[bool, list[str]]:
    version = metadata_version(frontmatter)
    if version is None:
        return False, ["SKILL.md frontmatter missing 'metadata.version'"]

    changelog = skill_path / "CHANGELOG.md"
    if not changelog.exists():
        return False, ["CHANGELOG.md not found"]

    text = changelog.read_text(encoding="utf-8")
    found = CHANGELOG_VER_RE.findall(text)
    if version in found:
        return True, [f"metadata.version {version} appears in CHANGELOG.md"]
    return False, [
        f"metadata.version '{version}' not found as '## {version}' heading in "
        f"CHANGELOG.md (found: {', '.join(found[:8]) or 'none'})"
    ]


def check_expected_version(
    frontmatter: dict, expected: str
) -> tuple[bool, list[str]]:
    """Bind a release tag to metadata.version (CI tag validation)."""
    version = metadata_version(frontmatter)
    if version is None:
        return False, [
            f"expected version {expected} but SKILL.md has no metadata.version"
        ]
    if version != expected:
        return False, [
            f"version mismatch: expected '{expected}', "
            f"SKILL.md metadata.version is '{version}'"
        ]
    return True, [f"metadata.version matches expected {expected}"]


def check_skill_budgets(skill_path: Path) -> tuple[bool, list[str]]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    words = len(text.split())
    failures: list[str] = []
    if lines > MAX_SKILL_LINES:
        failures.append(f"SKILL.md has {lines} lines (max {MAX_SKILL_LINES})")
    if words > MAX_SKILL_WORDS:
        failures.append(f"SKILL.md has {words} words (max {MAX_SKILL_WORDS})")
    if failures:
        return False, failures
    return True, [
        f"SKILL.md has {lines} lines (≤ {MAX_SKILL_LINES}) "
        f"and {words} words (≤ {MAX_SKILL_WORDS})"
    ]


def check_required_headings(skill_path: Path) -> tuple[bool, list[str]]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    # Any heading level counts; heading text may carry emoji or punctuation
    headings = [m.group(2).strip() for m in HEADING_RE.finditer(text)]

    failures: list[str] = []
    for alternatives in REQUIRED_HEADINGS:
        if not any(phrase in h for phrase in alternatives for h in headings):
            wanted = " or ".join(repr(a) for a in alternatives)
            failures.append(f"SKILL.md: missing required heading containing {wanted}")
    if failures:
        return False, failures
    return True, [f"All {len(REQUIRED_HEADINGS)} required headings present"]


def checklist_section(text: str) -> tuple[str, bool]:
    """
    Body of the heading whose title contains 'checklist', up to the next heading
    of the same or higher level. Returns (section_text, scoped).
    Falls back to the whole document when no such heading exists.
    """
    headings = list(HEADING_RE.finditer(text))
    for i, m in enumerate(headings):
        if "checklist" not in m.group(2).lower():
            continue
        level = len(m.group(1))
        start = m.end()
        for nxt in headings[i + 1:]:
            if len(nxt.group(1)) <= level:
                return text[start:nxt.start()], True
        return text[start:], True
    return text, False


def check_checklist_ids(skill_path: Path) -> tuple[bool, list[str]]:
    """SKILL.md must define exactly the 19 checklist points, once each."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    section, scoped = checklist_section(skill_md.read_text(encoding="utf-8"))

    counts: dict[str, int] = {}
    for m in CHECKLIST_DEF_RE.finditer(section):
        point = m.group(1) or m.group(2)
        counts[point] = counts.get(point, 0) + 1

    failures: list[str] = []
    if not scoped:
        failures.append(
            "SKILL.md: no heading containing 'Checklist' found; "
            "scanned the whole document for point definitions"
        )
    missing = [i for i in CHECKLIST_IDS if i not in counts]
    extra = sorted(set(counts) - CHECKLIST_ID_SET)
    duplicated = sorted(i for i, n in counts.items() if n > 1)
    if missing:
        failures.append(f"SKILL.md: undefined checklist point(s): {', '.join(missing)}")
    if extra:
        failures.append(f"SKILL.md: unexpected checklist point(s): {', '.join(extra)}")
    if duplicated:
        failures.append(
            f"SKILL.md: duplicate checklist point definition(s): "
            f"{', '.join(duplicated)}"
        )
    if failures:
        return False, failures
    return True, [f"All {len(CHECKLIST_IDS)} checklist points defined exactly once"]


def check_point_references(skill_path: Path) -> tuple[bool, list[str]]:
    """`Point: X#` fields and point-prefixed ledger cells must name a real point."""
    failures: list[str] = []

    def scan(path: Path, pattern: re.Pattern[str], label: str) -> None:
        if not path.exists():
            return
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(skill_path)
        for m in pattern.finditer(text):
            token = m.group(1).rstrip(".:,")
            if token in CHECKLIST_ID_SET:
                continue
            line_no = text.count("\n", 0, m.start()) + 1
            failures.append(
                f"{rel}:{line_no}: {label} '{token}' is not a checklist point"
            )

    for path in iter_reference_files(skill_path):
        scan(path, POINT_FIELD_RE, "Point:")

    for rel in ("SKILL.md", REPORT_EXAMPLE):
        scan(skill_path / rel, LEDGER_POINT_RE, "ledger point prefix")

    if failures:
        return False, failures
    return True, ["All point references name one of the 19 checklist points"]


def has_toc(text: str) -> bool:
    """A 'Contents' heading or a link list inside the head of the file."""
    head = "\n".join(text.splitlines()[:TOC_SCAN_LINES])
    if TOC_HEADING_RE.search(head):
        return True
    return len(TOC_LINK_RE.findall(head)) >= 3


def check_reference_tocs(skill_path: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    checked = 0
    for path in iter_reference_files(skill_path):
        text = path.read_text(encoding="utf-8")
        n = len(text.splitlines())
        if n <= TOC_REQUIRED_OVER_LINES:
            continue
        checked += 1
        if not has_toc(text):
            failures.append(
                f"{path.relative_to(skill_path)}: {n} lines but no table of contents "
                f"('Contents' heading or ≥3 anchor links) in the first "
                f"{TOC_SCAN_LINES} lines"
            )
    if failures:
        return False, failures
    return True, [
        f"All {checked} reference file(s) over {TOC_REQUIRED_OVER_LINES} lines "
        "have a TOC"
    ]


def check_report_example(skill_path: Path) -> tuple[bool, list[str]]:
    """Regression guards for the worked example report."""
    path = skill_path / REPORT_EXAMPLE
    if not path.exists():
        return False, [f"{REPORT_EXAMPLE} not found"]
    text = path.read_text(encoding="utf-8")

    failures = [
        f"{REPORT_EXAMPLE}: missing required content {label!r}"
        for label, pattern in REPORT_MUST_CONTAIN
        if not pattern.search(text)
    ]
    failures += [
        f"{REPORT_EXAMPLE}: contains stale content {label!r}"
        for label, pattern in REPORT_MUST_NOT_CONTAIN
        if pattern.search(text)
    ]
    if failures:
        return False, failures
    return True, [f"{REPORT_EXAMPLE} regression markers present"]


def check_content_regressions(skill_path: Path) -> tuple[bool, list[str]]:
    """Wording decisions that only a literal marker can protect."""
    failures: list[str] = []
    checked = 0

    for rel, label, pattern in CONTENT_MUST_CONTAIN:
        path = skill_path / rel
        if not path.is_file():
            failures.append(f"{rel}: not found (must contain {label!r})")
            continue
        checked += 1
        if not pattern.search(path.read_text(encoding="utf-8")):
            failures.append(f"{rel}: missing required content {label!r}")

    for rel, label, pattern in CONTENT_MUST_NOT_CONTAIN:
        path = skill_path / rel
        if not path.is_file():
            failures.append(f"{rel}: not found (must not contain {label!r})")
            continue
        checked += 1
        text = path.read_text(encoding="utf-8")
        for m in pattern.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            failures.append(f"{rel}:{line_no}: contains retired content {label!r}")

    if failures:
        return False, failures
    return True, [f"All {checked} document content marker(s) hold"]


def check_critical_fundamental(skill_path: Path) -> tuple[bool, list[str]]:
    """No active file may put `[fundamental]` back in the Critical tier."""
    failures: list[str] = []
    files = iter_active_files(skill_path)
    for path in files:
        rel = path.relative_to(skill_path)
        for line_no, line in enumerate(
            path.read_text(encoding="utf-8").split("\n"), start=1
        ):
            if CRITICAL_FUNDAMENTAL_RE.search(line):
                failures.append(
                    f"{rel}:{line_no}: Critical-tier `[fundamental]` phrasing "
                    f"({line.strip()!r}); the tag is an Important architecture tag"
                )
    if failures:
        return False, failures
    return True, [
        f"No Critical-tier `[fundamental]` phrasing in {len(files)} active file(s)"
    ]


def split_top_sections(text: str) -> list[tuple[str, list[tuple[int, str]]]]:
    """
    Split on `## ` headings that are outside fenced code blocks.

    The worked examples embed a whole report inside a ```` fence, and that report
    has `##` headings of its own; splitting on them would tear an example apart.
    Returns [(heading_text, [(line_no, line), ...]), ...]; the text before the
    first heading is returned under an empty title.
    """
    sections: list[tuple[str, list[tuple[int, str]]]] = []
    title = ""
    body: list[tuple[int, str]] = []
    fence: tuple[str, int] | None = None

    for line_no, line in enumerate(text.split("\n"), start=1):
        m = FENCE_RE.match(line)
        if m:
            token, rest = m.group(1), m.group(2)
            if fence is None:
                fence = (token[0], len(token))
            elif token[0] == fence[0] and len(token) >= fence[1] and not rest.strip():
                fence = None
        elif fence is None and line.startswith("## "):
            sections.append((title, body))
            title, body = line[3:].strip(), []
            continue
        body.append((line_no, line))

    sections.append((title, body))
    return sections


def split_table_cells(line: str) -> list[str]:
    """Cells of a markdown table row (no escaped-pipe support; none is used)."""
    stripped = line.strip()
    if stripped.startswith("|"):
        stripped = stripped[1:]
    if stripped.endswith("|"):
        stripped = stripped[:-1]
    return [cell.strip() for cell in stripped.split("|")]


def iter_md_tables(
    numbered: list[tuple[int, str]]
) -> list[tuple[list[str], list[tuple[int, list[str]]]]]:
    """Every pipe table in the block, as (header_cells, [(line_no, cells)])."""
    tables: list[tuple[list[str], list[tuple[int, list[str]]]]] = []
    i = 0
    while i + 1 < len(numbered):
        if "|" in numbered[i][1] and TABLE_DELIM_RE.match(numbered[i + 1][1]):
            header = split_table_cells(numbered[i][1])
            rows: list[tuple[int, list[str]]] = []
            j = i + 2
            while j < len(numbered) and "|" in numbered[j][1]:
                rows.append((numbered[j][0], split_table_cells(numbered[j][1])))
                j += 1
            tables.append((header, rows))
            i = j
        else:
            i += 1
    return tables


def classify_ledger_cell(cell: str) -> tuple[str, str]:
    """
    Classify one Coverage Ledger domain cell.

    Returns (status, detail) where status is 'blank' (unaccounted on purpose),
    'valid' (accounted), or 'invalid' (grammar violation).
    """
    text = cell.strip()
    if text in BLANK_LEDGER_CELLS:
        return "blank", ""

    tokens = [t.strip() for t in text.split(";")]
    if any(not t for t in tokens):
        return "invalid", "empty token around a ';' separator"
    if len(tokens) == 1 and tokens[0] == "Pass":
        return "valid", ""

    for token in tokens:
        if token == "Pass":
            return "invalid", "a bare `Pass` must be the whole cell"
        if BARE_GATED_RE.match(token):
            return "invalid", (
                "bare `Gated` hides the other points in this domain; "
                "qualify every point (`E1:Pass; E2:Gated:L4`)"
            )
        if not LEDGER_TOKEN_RE.match(token):
            return "invalid", f"token {token!r} does not match the cell grammar"
    return "valid", ""


def waiver_disclosure_body(body: str) -> str:
    """Text under the Waiver Disclosure heading, up to the next heading."""
    match = WAIVER_HEADING_RE.search(body)
    if not match:
        return ""
    rest = body[match.end():]
    nxt = ANY_HEADING_RE.search(rest)
    return rest[: nxt.start()] if nxt else rest


def audit_ledger_example(
    label: str, numbered: list[tuple[int, str]]
) -> tuple[int, int, list[str]]:
    """
    Recompute one worked example's ledger accounting.

    Returns (accounted_cells, total_cells, failures). Total is in-scope files × 5
    domains; accounted counts every syntactically valid nonblank cell, PARTIAL
    rows included.
    """
    failures: list[str] = []
    body = "\n".join(line for _, line in numbered)
    ledger_rows = 0
    accounted = 0
    refs: set[str] = set()

    for header, rows in iter_md_tables(numbered):
        if all(domain in header for domain in LEDGER_DOMAINS):
            columns = [(d, header.index(d)) for d in LEDGER_DOMAINS]
            for line_no, cells in rows:
                if len(cells) != len(header):
                    failures.append(
                        f"{REPORT_EXAMPLE}:{line_no}: {label}: ledger row has "
                        f"{len(cells)} column(s), header has {len(header)}"
                    )
                    continue
                ledger_rows += 1
                for domain, index in columns:
                    cell = cells[index]
                    status, detail = classify_ledger_cell(cell)
                    if status == "valid":
                        accounted += 1
                        refs.update(FINDING_ID_RE.findall(cell))
                    elif status == "invalid":
                        failures.append(
                            f"{REPORT_EXAMPLE}:{line_no}: {label}: invalid ledger "
                            f"cell in {domain}: {cell!r} — {detail}"
                        )
        elif header[:3] == WHOLE_SCOPE_HEADER:
            for _, cells in rows:
                refs.update(FINDING_ID_RE.findall(" ".join(cells)))

    if ledger_rows == 0:
        failures.append(
            f"{REPORT_EXAMPLE}: {label}: no Coverage Ledger table found "
            f"(its header must name all five domains)"
        )
        return 0, 0, failures

    declared = IN_SCOPE_RE.search(body)
    files = int(declared.group(1)) if declared else ledger_rows
    if files != ledger_rows:
        failures.append(
            f"{REPORT_EXAMPLE}: {label}: manifest declares {files} file(s) in "
            f"scope but the ledger has {ledger_rows} row(s)"
        )

    # Finding IDs must resolve in both directions, counted as unique IDs
    entries = set(FINDING_HEADING_RE.findall(body))
    entries.update(FINDING_ID_RE.findall(waiver_disclosure_body(body)))
    def by_number(fid: str) -> int:
        return int(fid[1:])

    for fid in sorted(refs - entries, key=by_number):
        failures.append(
            f"{REPORT_EXAMPLE}: {label}: {fid} is referenced by the ledger or "
            f"whole-scope table but has no finding or waiver-disclosure entry"
        )
    for fid in sorted(entries - refs, key=by_number):
        failures.append(
            f"{REPORT_EXAMPLE}: {label}: {fid} is reported or waived but is never "
            f"referenced by the ledger or whole-scope table"
        )

    return accounted, files * len(LEDGER_DOMAINS), failures


def iter_cell_claims(
    numbered: list[tuple[int, str]]
) -> list[tuple[int, int, int]]:
    """Every 'X/Y domain cells' claim as (line_no, numerator, denominator)."""
    claims: list[tuple[int, int, int]] = []
    for line_no, line in numbered:
        for pattern in CELL_CLAIM_RES:
            for m in pattern.finditer(line):
                claims.append((line_no, int(m.group(1)), int(m.group(2))))
    return claims


def check_ledger_arithmetic(skill_path: Path) -> tuple[bool, list[str]]:
    """Ledger cell grammar, recomputed cell counts, and finding-ID closure."""
    path = skill_path / REPORT_EXAMPLE
    if not path.exists():
        return False, [f"{REPORT_EXAMPLE} not found"]

    sections = split_top_sections(path.read_text(encoding="utf-8"))
    failures: list[str] = []
    audited: dict[str, tuple[int, int]] = {}

    for title, numbered in sections:
        if "example" not in title.lower():
            continue
        accounted, total, section_failures = audit_ledger_example(title, numbered)
        failures.extend(section_failures)
        audited[title] = (accounted, total)

    if not audited:
        return False, [f"{REPORT_EXAMPLE}: no '## Example …' section found"]

    verified: set[tuple[int, int]] = set()
    for title, numbered in sections:
        expected = audited.get(title)
        for line_no, num, den in iter_cell_claims(numbered):
            if expected is not None and (num, den) != expected:
                failures.append(
                    f"{REPORT_EXAMPLE}:{line_no}: {title} claims {num}/{den} domain "
                    f"cells; recomputation gives {expected[0]}/{expected[1]}"
                )
            elif expected is None and (num, den) not in set(audited.values()):
                failures.append(
                    f"{REPORT_EXAMPLE}:{line_no}: claim {num}/{den} domain cells "
                    f"matches no worked example "
                    f"({', '.join(f'{a}/{b}' for a, b in audited.values())})"
                )
            else:
                verified.add((num, den))

    for num, den in REQUIRED_CELL_CLAIMS:
        if (num, den) not in verified:
            failures.append(
                f"{REPORT_EXAMPLE}: no verified '{num}/{den} domain cells' claim; "
                f"the worked examples must keep stating their own totals"
            )

    if failures:
        return False, failures
    totals = " · ".join(f"{t}: {a}/{b}" for t, (a, b) in audited.items())
    return True, [f"{REPORT_EXAMPLE} ledger grammar and arithmetic hold ({totals})"]


def check_required_files(skill_path: Path) -> tuple[bool, list[str]]:
    failures = [
        f"missing required file: {rel}"
        for rel in REQUIRED_FILES
        if not (skill_path / rel).is_file()
    ]
    if failures:
        return False, failures
    return True, [f"All {len(REQUIRED_FILES)} required file(s) present"]


def report(name: str, ok: bool, messages: list[str]) -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}")
    # Failures: all details; pass: one-line summary
    for msg in (messages if not ok else messages[:1]):
        print(f"  {msg}")
    return ok


def validate_skill(skill_path: Path, expected_version: str | None = None) -> bool:
    skill_path = skill_path.resolve()
    all_ok = True

    ok, msgs, frontmatter = check_frontmatter(skill_path / "SKILL.md")
    all_ok &= report("Frontmatter", ok, msgs)

    if expected_version is not None:
        ok, msgs = check_expected_version(frontmatter, expected_version)
        all_ok &= report("Expected version", ok, msgs)

    ok, msgs = check_required_files(skill_path)
    all_ok &= report("Required files", ok, msgs)

    ok, msgs = check_rule_citations(skill_path)
    all_ok &= report("Rule-citation existence", ok, msgs)

    ok, msgs = check_relative_links(skill_path)
    all_ok &= report("Relative markdown links", ok, msgs)

    ok, msgs = check_version_changelog(skill_path, frontmatter)
    all_ok &= report("Version/changelog agreement", ok, msgs)

    ok, msgs = check_skill_budgets(skill_path)
    all_ok &= report("SKILL.md budgets", ok, msgs)

    ok, msgs = check_required_headings(skill_path)
    all_ok &= report("Required SKILL.md headings", ok, msgs)

    ok, msgs = check_checklist_ids(skill_path)
    all_ok &= report("Checklist point definitions", ok, msgs)

    ok, msgs = check_point_references(skill_path)
    all_ok &= report("Checklist point references", ok, msgs)

    ok, msgs = check_reference_tocs(skill_path)
    all_ok &= report("Reference TOCs", ok, msgs)

    ok, msgs = check_report_example(skill_path)
    all_ok &= report("Report example regressions", ok, msgs)

    ok, msgs = check_content_regressions(skill_path)
    all_ok &= report("Document content regressions", ok, msgs)

    ok, msgs = check_critical_fundamental(skill_path)
    all_ok &= report("Fundamental-tag severity", ok, msgs)

    ok, msgs = check_ledger_arithmetic(skill_path)
    all_ok &= report("Ledger grammar and arithmetic", ok, msgs)

    return all_ok


# --------------------------------------------------------------------------
# Self-check
# --------------------------------------------------------------------------

FIXTURE_SKILL = """---
name: demo-skill
description: >
  Demo skill used by the validator self-check.
license: MIT
compatibility: claude-code
metadata:
  version: 1.2.3
  author: fixture
---

# Demo Skill

## Review Integrity

## Profile Discovery and Calibration

| Axis | Code |
|------|------|
| D2 | R3 |

## Scope Manifest

## Review Protocol

## Coverage Ledger

Cells: `Pass` · `A2:F1` · `E1:Pass; E2:Gated:L4`

## Whole-Scope Checks

## Coverage Reconciliation

## Verdict

An Important finding weighs `min(affected_files, 3)`; breadth raises the weight
of one finding and never creates a second one.

## Reference Loading

## Nineteen-Point Review Checklist

Domains: **A** Contract & Safety · **B** Readability · **C** Design & Architecture ·
**D** Testing · **E** Performance & Operability.

- **A1 Contract integrity** — honors its advertised contract. (CC-1)
- **A2 Boundaries, errors, and concrete logic paths** — cues here. (CC-64~77)
- **A3 Security and secrets** — always active. (PP-1)
- **A4 Resource lifecycle.**
- **A5 — State mutation and concurrency.**
- **B1 Names reveal intent.** (CA-8–12)
- **B2 Functions, control flow, and nesting** — cues here.
- **B3 Comments and dead code** — why, not what.
- **B4 Magic values and configuration.**
- **C1 SRP and cohesion** — cue: God class.
- **C2 Duplication / DRY** — whole-scope check.
- **C3 Dependency direction** — whole-scope check.
- **C4 Coupling, layer boundaries, and architecture smells.**
- **C5 KISS, YAGNI, and over-engineering.**
- **C6 Public contracts and compatibility (L4+).**
- **D1 Tests for changed behavior**, including a regression test.
- **D2 Test quality** — isolation, readability, FIRST.
- **E1 Algorithmic complexity (L3+).**
- **E2 Observability and operational failure behavior (L4+).**

### Point Tie-Breaks

Security consequence → A3 · state corruption → A5 · other concrete behavior → A2.
"""

FIXTURE_LEDGER_HEADER = (
    "| File | Contract & Safety | Readability | Design & Architecture | Testing "
    "| Performance & Operability | Status |\n"
    "|------|-------------------|-------------|-----------------------|---------"
    "|---------------------------|--------|\n"
)

FIXTURE_REPORT = f"""# Example Report

Profile: D2 / R3 / C2 → L3

## Example 1 — Complete Review

- In scope: 3 · Excluded: 0

### Coverage Ledger

{FIXTURE_LEDGER_HEADER}\
| a.ts | Pass | B2:F2 | C2:Waived:F3/W1 | D1:Pass; D2:N/A:no-test-code-in-scope \
| E1:Pass; E2:Gated:L4 | DONE |
| b.ts | Pass | B4:F4 | C2:Waived:F3/W1 | D1:Pass; \
D2:N/A:no-test-code-in-scope | E1:Pass; E2:Gated:L4 | DONE |
| c.ts | A2:F1 | B4:CappedMinor:2 | Pass | D1:F5 | E1:Pass; E2:Gated:L4 | DONE |

### Whole-Scope Checks

| Check | Result | Finding |
|-------|--------|---------|
| C2 duplication clusters | Finding | F3 (waived by W1) |

### Findings

- **[a.ts:1] F1 — Something**
  - Point: A2
  - Rule: CC-1

- **[a.ts:8] F2 — Long function**
  - Point: B2

- **[b.ts:3] F4 — Unnamed literal** · Point: B4

- **[c.ts:5] F5 — Changed behavior ships without a test**
  - Point: D1

### Waiver Disclosure

| Waiver | Point | Paths | Finding | Expires | Approver |
|--------|-------|-------|---------|---------|----------|
| W1 | C2 | src/** | F3 | 2026-12-01 | team-lead |

- **F3** · Point: C2 · duplication cluster · suppressed by W1.

### Coverage Reconciliation

- Domain cells accounted: 15/15 (3 files × 5 domains)
- Status: COMPLETE

### Verdict

⚠️ Needs fixes at L3 · 3/3 files · 15/15 domain cells

## Example 2 — Incomplete Review

- In scope: 2 · Excluded: 0

### Coverage Ledger

{FIXTURE_LEDGER_HEADER}\
| a.ts | Pass | Pass | Pass | D1:Pass; D2:N/A:no-test-code-in-scope \
| E1:Pass; E2:Gated:L4 | DONE |
| b.ts | Pass | — | — | — | — | PARTIAL |

### Waiver Disclosure

- No waivers (no profile in this review).

### Coverage Reconciliation

- Domain cells accounted: 6/10 (5 valid cells on the DONE row + 1 on the PARTIAL row)
- Status: INCOMPLETE
"""


def _write_fixture(root: Path) -> Path:
    """A minimal skill that passes every check."""
    (root / "references").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(FIXTURE_SKILL, encoding="utf-8")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n\n## 1.2.3 - 2026-01-01\n\n- initial\n",
        encoding="utf-8",
    )
    (root / "references" / "clean-code.md").write_text(
        "# Clean Code\n\n- CC-1 x\n- CC-64 y\n- CC-77 z\n", encoding="utf-8"
    )
    (root / "references" / "clean-architecture.md").write_text(
        "# Clean Architecture\n\n- CA-8 x\n- CA-12 y\n", encoding="utf-8"
    )
    (root / "references" / "pragmatic-programmer.md").write_text(
        "# Pragmatic Programmer\n\n- PP-1 x\n", encoding="utf-8"
    )
    (root / "references" / "review-profile.md").write_text(
        "# Review Profile Schema\n\nfields.\n\nOverlapping profiles resolve to the "
        "stricter candidate; the effective level is what waivers revalidate "
        "against.\n",
        encoding="utf-8",
    )
    (root / "docs").mkdir(parents=True, exist_ok=True)
    (root / "docs" / "metrics.md").write_text(
        "# Metrics\n\nSuppression tripwire: 50% of candidates, minimum 10.\n",
        encoding="utf-8",
    )
    (root / "references" / "report-example.md").write_text(
        FIXTURE_REPORT, encoding="utf-8"
    )
    # >100 lines, so a TOC is required
    long_body = "\n".join(f"line {i}" for i in range(1, 121))
    (root / "references" / "long-guide.md").write_text(
        "# Long Guide\n\n## Contents\n\n- [One](#one)\n\n" + long_body + "\n",
        encoding="utf-8",
    )
    return root


def _patch(path: Path, old: str, new: str) -> None:
    text = path.read_text(encoding="utf-8")
    assert old in text, f"fixture patch target not found in {path.name}: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def _run(root: Path, expected_version: str | None = None) -> tuple[bool, str]:
    buf = io.StringIO()
    with redirect_stdout(buf):
        ok = validate_skill(root, expected_version)
    return ok, buf.getvalue()


def _unit_checks() -> None:
    text = "see CC-64~77 and CA-8–12 and PP-1 plus CC-20"
    tokens = expand_citation_tokens(text)
    ids = [t for t, _ in tokens]
    assert "CC-64" in ids and "CC-77" in ids, ids
    assert "CA-8" in ids and "CA-12" in ids, ids
    assert "PP-1" in ids and "CC-20" in ids, ids
    # endpoints only for ranges (not every middle id)
    assert "CC-65" not in ids, ids
    # range-span must not double-count start as single
    assert ids.count("CC-64") == 1, ids

    fm, err = parse_frontmatter(
        "---\nname: demo-skill\nlicense: MIT\ndescription: >\n  hello world\n"
        "metadata:\n  version: 1.0.0\n  author: someone\n---\nbody\n"
    )
    assert err is None and fm is not None
    assert fm["name"] == "demo-skill"
    assert "hello world" in fm["description"]
    # nested metadata parsed one level deep
    assert fm["metadata"] == {"version": "1.0.0", "author": "someone"}, fm["metadata"]
    assert metadata_version(fm) == "1.0.0"
    assert "version" not in fm, "top-level version must not be synthesized"

    # block scalar followed by a nested block, and quoted nested scalars
    fm2, err2 = parse_frontmatter(
        '---\ndescription: |\n  line one\n  line two\nmetadata:\n'
        '  version: "2.0.0"\nname: x\n---\n'
    )
    assert err2 is None and fm2 is not None
    assert fm2["metadata"] == {"version": "2.0.0"}, fm2
    assert fm2["name"] == "x"

    # a key with an indented sequence keeps its scalar value (no bogus dict)
    fm3, _ = parse_frontmatter("---\nallowed-tools:\n  - Read\n  - Grep\nname: y\n---\n")
    assert fm3 is not None and fm3["allowed-tools"] == "", fm3

    # TOC heuristics
    assert has_toc("# T\n\n## Table of Contents\n\n- [a](#a)\n")
    assert has_toc("# T\n\n- [a](#a)\n- [b](#b)\n- [c](#c)\n")
    assert not has_toc("# T\n\nprose only\n")
    assert not has_toc("\n" * 40 + "## Contents\n"), "TOC must be near the top"

    # checklist section scoping ignores headings after the section
    section, scoped = checklist_section(
        "## Checklist\n\n- **A1 — x.**\n\n## Later\n\n- **A9 — y.**\n"
    )
    assert scoped and "A1" in section and "A9" not in section, section

    # accepted definition shapes vs. mere mentions
    def defs(text: str) -> list[str]:
        return [m.group(1) or m.group(2) for m in CHECKLIST_DEF_RE.finditer(text)]

    assert defs("- **A1 Contract integrity** — honors it.") == ["A1"]
    assert defs("- **A1 — Contract integrity.**") == ["A1"]
    assert defs("- **A1** — Contract integrity.") == ["A1"]
    assert defs("#### A1 — Contract integrity") == ["A1"]
    assert defs("| D2 | R3 | C2 | L3 | Internal SDK |") == []
    assert defs("  cohesion across modules → C1 · dependency direction → C3") == []
    assert defs("| a.ts | A2:F1 | D1:Pass |") == []
    assert defs("Domains: **A** Contract & Safety · **B** Readability") == []

    # ledger cell grammar
    def cell(text: str) -> str:
        return classify_ledger_cell(text)[0]

    assert cell("Pass") == "valid"
    assert cell("A2:F1") == "valid"
    assert cell("A2:F1,F7") == "valid"
    assert cell("D1:Pass; D2:N/A:no-test-code-in-scope") == "valid"
    # a point-qualified Pass is valid inside a multi-token cell
    assert cell("E1:Pass; E2:Gated:L4") == "valid"
    assert cell("C2:Waived:F3/W1") == "valid"
    assert cell("B4:CappedMinor:2") == "valid"
    assert cell("—") == "blank" and cell("") == "blank"
    # a bare Pass may not share its cell; a bare Gated hides its siblings
    assert cell("Pass; E2:Gated:L4") == "invalid"
    assert cell("Gated:L4") == "invalid"
    assert "bare `Gated`" in classify_ledger_cell("Gated:L4")[1]
    assert cell("E2:Gated:L9") == "invalid"
    assert cell("D1:N/A:no tests") == "invalid"
    assert cell("A2:Finding") == "invalid"
    assert cell("F1") == "invalid"
    assert cell("E1:Pass;") == "invalid"

    # `##` headings inside a ```` fence must not split a section
    sections = split_top_sections(
        "## Example 1\n\n````markdown\n## Report\n\n```ts\nx\n```\n````\n\n"
        "## Arithmetic notes\n"
    )
    assert [t for t, _ in sections] == ["", "Example 1", "Arithmetic notes"], sections
    assert any("## Report" == line for _, line in sections[1][1]), sections[1]

    # budgets are a stated contract, not an incidental value
    assert (MAX_SKILL_LINES, MAX_SKILL_WORDS) == (438, 3250), (
        MAX_SKILL_LINES,
        MAX_SKILL_WORDS,
    )

    # Critical-tier `[fundamental]` phrasing, and the shapes that are not it
    def crit(line: str) -> bool:
        return CRITICAL_FUNDAMENTAL_RE.search(line) is not None

    assert crit("2. 🚫 Major rework — ≥1 Critical finding tagged `[fundamental]`.")
    assert crit("Critical architecture finding tagged `[fundamental]`")
    # the demoted wording: Important tier, tag never reaches Critical
    assert not crit("≥1 active Important architecture finding tagged `[fundamental]`.")
    assert not crit("Important at L3–L5, never `[fundamental]`.")
    # tag first, `Critical` only as the tier it does *not* need
    assert not crit(
        "| `[fundamental]` | Important architecture finding | "
        "without requiring Critical severity |"
    )
    # a sentence boundary ends the window
    assert not crit("≥3 active Critical findings. Never tagged `[fundamental]`.")
    # and so does distance
    assert not crit("Critical" + " x" * 40 + " `[fundamental]`")


def _fixture_checks(tmp: Path) -> None:
    base = _write_fixture(tmp / "base")
    ok, out = _run(base)
    assert ok, f"baseline fixture must pass:\n{out}"

    def variant(name: str) -> Path:
        dst = tmp / name
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(base, dst)
        return dst

    # 1. nested metadata drives version/changelog agreement
    v = variant("nested-version")
    _patch(v / "SKILL.md", "  version: 1.2.3", "  version: 9.9.9")
    ok, out = _run(v)
    assert not ok and "9.9.9" in out and "CHANGELOG" in out, out

    # 2. top-level version is a hard error
    v = variant("toplevel-version")
    _patch(v / "SKILL.md", "license: MIT", "license: MIT\nversion: 1.2.3")
    ok, out = _run(v)
    assert not ok and "Top-level 'version' is rejected" in out, out

    # 2b. license is required
    v = variant("no-license")
    _patch(v / "SKILL.md", "license: MIT\n", "")
    ok, out = _run(v)
    assert not ok and "Missing 'license'" in out, out

    # 2c. metadata.version is required
    v = variant("no-metadata-version")
    _patch(v / "SKILL.md", "  version: 1.2.3\n", "")
    ok, out = _run(v)
    assert not ok and "metadata.version" in out, out

    # 3. ranged rule IDs: endpoints are validated
    v = variant("range-ok")
    ok, _ = _run(v)
    assert ok
    v = variant("range-out-of-range")
    _patch(v / "SKILL.md", "(CC-64~77)", "(CC-64~999)")
    ok, out = _run(v)
    assert not ok and "CC-999 out of range" in out, out
    v = variant("range-undefined")
    _patch(v / "SKILL.md", "(CC-64~77)", "(CC-64~78)")
    ok, out = _run(v)
    assert not ok and "CC-78 not found" in out, out

    # 4. TOC required only for long reference files
    v = variant("no-toc")
    _patch(v / "references" / "long-guide.md", "## Contents\n\n- [One](#one)\n\n", "")
    ok, out = _run(v)
    assert not ok and "no table of contents" in out, out
    v = variant("short-no-toc")
    (v / "references" / "short.md").write_text(
        "# Short\n\n" + "\n".join(f"l{i}" for i in range(50)) + "\n", encoding="utf-8"
    )
    ok, out = _run(v)
    assert ok, out

    # 5. point references must name a real checklist point
    v = variant("bad-point-field")
    _patch(v / "references" / "report-example.md", "Point: A2", "Point: A9")
    ok, out = _run(v)
    assert not ok and "'A9' is not a checklist point" in out, out
    v = variant("bad-ledger-prefix")
    _patch(v / "SKILL.md", "`A2:F1`", "`A7:F1`")
    ok, out = _run(v)
    assert not ok and "'A7' is not a checklist point" in out, out

    # 6. checklist taxonomy is closed
    v = variant("missing-point")
    _patch(v / "SKILL.md", "- **C6 Public contracts and compatibility (L4+).**\n", "")
    ok, out = _run(v)
    assert not ok and "undefined checklist point(s): C6" in out, out
    v = variant("extra-point")
    _patch(
        v / "SKILL.md",
        "- **E2 Observability",
        "- **E3 Extra point.**\n- **E2 Observability",
    )
    ok, out = _run(v)
    assert not ok and "unexpected checklist point(s): E3" in out, out
    v = variant("duplicate-point")
    _patch(
        v / "SKILL.md",
        "- **B4 Magic values and configuration.**",
        "- **B4 Magic values and configuration.**\n- **B4 Magic values again.**",
    )
    ok, out = _run(v)
    assert not ok and "duplicate checklist point definition(s): B4" in out, out

    # 7. report-example regressions
    v = variant("stale-report")
    _patch(v / "references" / "report-example.md", "D1:Pass", "N/A:no tests")
    ok, out = _run(v)
    assert not ok and "stale content 'N/A:no tests'" in out, out
    v = variant("report-missing-score")
    _patch(v / "references" / "report-example.md", "6/10", "7/10")
    ok, out = _run(v)
    assert not ok and "missing required content '6/10'" in out, out

    # 7b. ledger grammar and arithmetic
    v = variant("ledger-corrupt-cell")
    _patch(v / "references" / "report-example.md", "B2:F2", "B2:broken")
    ok, out = _run(v)
    assert not ok and "invalid ledger cell in Readability" in out, out

    v = variant("ledger-bare-gated")
    _patch(
        v / "references" / "report-example.md",
        "E1:Pass; E2:Gated:L4 | DONE |\n| b.ts",
        "Gated:L4 | DONE |\n| b.ts",
    )
    ok, out = _run(v)
    assert not ok and "bare `Gated`" in out, out

    v = variant("ledger-wrong-total")
    _patch(
        v / "references" / "report-example.md",
        "Domain cells accounted: 15/15",
        "Domain cells accounted: 14/15",
    )
    ok, out = _run(v)
    assert not ok and "claims 14/15 domain cells; recomputation gives 15/15" in out, out

    v = variant("ledger-blanked-cell")
    _patch(v / "references" / "report-example.md", "| c.ts | A2:F1 |", "| c.ts | — |")
    ok, out = _run(v)
    assert not ok and "recomputation gives 14/15" in out, out

    v = variant("ledger-dangling-ref")
    _patch(v / "references" / "report-example.md", "D1:F5", "D1:F9")
    ok, out = _run(v)
    assert not ok and "F9 is referenced by the ledger" in out, out
    assert "F5 is reported or waived but is never referenced" in out, out

    # the waived finding is referenced from two cells; both must go
    v = variant("ledger-unreferenced-waiver")
    _patch(v / "references" / "report-example.md", "C2:Waived:F3/W1", "Pass")
    _patch(v / "references" / "report-example.md", "C2:Waived:F3/W1", "Pass")
    _patch(v / "references" / "report-example.md", "| F3 (waived by W1) |", "| — |")
    ok, out = _run(v)
    assert not ok and "F3 is reported or waived" in out, out

    v = variant("ledger-row-count")
    _patch(v / "references" / "report-example.md", "- In scope: 3", "- In scope: 4")
    ok, out = _run(v)
    assert not ok and "declares 4 file(s) in scope but the ledger has 3 row(s)" in out

    v = variant("ledger-claim-deleted")
    _patch(
        v / "references" / "report-example.md",
        "- Domain cells accounted: 6/10 (5 valid cells on the DONE row + 1 on the "
        "PARTIAL row)\n",
        "",
    )
    ok, out = _run(v)
    assert not ok and "no verified '6/10 domain cells' claim" in out, out

    # 8. required headings, with the Coverage Ledger alternative accepted
    v = variant("heading-alias")
    _patch(v / "SKILL.md", "## Coverage Ledger\n", "## Coverage Cell Grammar\n")
    ok, out = _run(v)
    assert ok, out
    v = variant("missing-heading")
    _patch(v / "SKILL.md", "## Verdict\n", "")
    ok, out = _run(v)
    assert not ok and "'Verdict'" in out, out

    # 9. profile schema must live in references/
    v = variant("no-profile-schema")
    (v / "references" / "review-profile.md").unlink()
    ok, out = _run(v)
    assert not ok and "references/review-profile.md" in out, out

    # 10. --expected-version binds a release tag to metadata.version
    v = variant("expected-version")
    ok, out = _run(v, expected_version="1.2.3")
    assert ok, out
    ok, out = _run(v, expected_version="1.2.4")
    assert not ok and "expected '1.2.4'" in out, out

    # 11. budgets — the limits are 438 lines / 3250 words, inclusive
    v = variant("too-many-lines")
    _patch(v / "SKILL.md", "# Demo Skill", "# Demo Skill\n" + "\n" * MAX_SKILL_LINES)
    ok, out = _run(v)
    assert not ok and "max 438" in out, out
    v = variant("too-many-words")
    _patch(
        v / "SKILL.md", "# Demo Skill", "# Demo Skill\n\n" + ("word " * MAX_SKILL_WORDS)
    )
    ok, out = _run(v)
    assert not ok and "max 3250" in out, out

    # exactly at both limits still passes, and the message states them
    v = variant("budget-at-limit")
    skill = v / "SKILL.md"
    text = skill.read_text(encoding="utf-8")
    pad_lines = MAX_SKILL_LINES - len(text.splitlines())
    pad_words = MAX_SKILL_WORDS - len(text.split())
    assert pad_lines >= 1 and pad_words >= pad_lines, (pad_lines, pad_words)
    filler = ["word " * (pad_words - pad_lines + 1)] + ["word"] * (pad_lines - 1)
    skill.write_text(text + "\n".join(filler) + "\n", encoding="utf-8")
    ok, out = _run(v)
    assert ok, out
    assert "438 lines (≤ 438)" in out and "3250 words (≤ 3250)" in out, out
    # one line and one word past the limit is a failure
    skill.write_text(text + "\n".join(filler) + "\nword\n", encoding="utf-8")
    ok, out = _run(v)
    assert not ok and "439 lines (max 438)" in out, out
    assert "3251 words (max 3250)" in out, out

    # 12. document content regressions
    v = variant("missing-breadth-weight")
    _patch(v / "SKILL.md", "min(affected_files, 3)", "min(files, 3)")
    ok, out = _run(v)
    assert not ok and "missing required content 'min(affected_files, 3)'" in out, out

    v = variant("retired-floor-files")
    _patch(
        v / "SKILL.md", "## Verdict\n", "## Verdict\n\nbase(level) + floor(files/5)\n"
    )
    ok, out = _run(v)
    assert not ok and "contains retired content 'floor(files/5)'" in out, out

    v = variant("retired-floor-in-scope")
    _patch(
        v / "SKILL.md",
        "## Verdict\n",
        "## Verdict\n\nbase(level) + floor(in_scope_files / 5)\n",
    )
    ok, out = _run(v)
    assert not ok and "contains retired content 'floor(in_scope_files'" in out, out

    v = variant("missing-stricter")
    _patch(v / "references" / "review-profile.md", "stricter", "looser")
    ok, out = _run(v)
    assert not ok and "missing required content 'stricter'" in out, out

    v = variant("missing-effective-level")
    _patch(v / "references" / "review-profile.md", "effective level", "level")
    ok, out = _run(v)
    assert not ok and "'effective level / effective_level'" in out, out

    v = variant("missing-metrics-rate")
    _patch(v / "docs" / "metrics.md", "50%", "30%")
    ok, out = _run(v)
    assert not ok and "docs/metrics.md: missing required content '50%'" in out, out

    # 13. `[fundamental]` may not be re-attached to the Critical tier
    v = variant("critical-fundamental-skill")
    _patch(
        v / "SKILL.md",
        "## Verdict\n",
        "## Verdict\n\n🚫 Major rework — ≥1 Critical finding tagged `[fundamental]`.\n",
    )
    ok, out = _run(v)
    assert not ok and "Critical-tier `[fundamental]` phrasing" in out, out

    v = variant("critical-fundamental-docs")
    _patch(
        v / "docs" / "metrics.md",
        "# Metrics\n",
        "# Metrics\n\nCritical severity is required for `[fundamental]`.\n",
    )
    ok, out = _run(v)
    assert not ok and "docs/metrics.md:3" in out, out

    # archived reports keep superseded wording on purpose
    v = variant("critical-fundamental-archived")
    (v / "docs" / "reports").mkdir(parents=True, exist_ok=True)
    (v / "docs" / "reports" / "old.md").write_text(
        "# Old\n\nCritical severity was required for `[fundamental]`.\n",
        encoding="utf-8",
    )
    ok, out = _run(v)
    assert ok, out


def self_check() -> int:
    _unit_checks()
    with tempfile.TemporaryDirectory(prefix="validate-skill-") as tmp:
        _fixture_checks(Path(tmp))
    print("[PASS] self-check")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="validate_skill.py",
        description="Validate skill folder structure and content.",
    )
    parser.add_argument(
        "skill_directory",
        nargs="?",
        help="skill root (default: current working directory)",
    )
    parser.add_argument(
        "--expected-version",
        metavar="X.Y.Z",
        help="fail unless SKILL.md metadata.version equals this value",
    )
    parser.add_argument(
        "--self-check",
        "-t",
        action="store_true",
        help="run the validator's own fixtures and exit",
    )
    args = parser.parse_args()

    if args.self_check:
        if args.skill_directory or args.expected_version:
            parser.error("--self-check takes no other arguments")
        try:
            sys.exit(self_check())
        except AssertionError as e:
            print(f"[FAIL] self-check: {e}")
            sys.exit(1)

    skill_dir = Path(args.skill_directory) if args.skill_directory else Path.cwd()
    if not skill_dir.is_dir():
        print(f"❌ Not a directory: {skill_dir}")
        sys.exit(1)

    ok = validate_skill(skill_dir, args.expected_version)
    if ok:
        print("✅ Skill is valid!")
    else:
        print("❌ Skill validation failed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
