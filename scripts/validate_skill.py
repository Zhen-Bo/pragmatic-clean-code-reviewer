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

# v2 budgets: SKILL.md ~224 lines / ~1474 words; modest headroom
MAX_SKILL_LINES = 300
MAX_SKILL_WORDS = 2000

EXPECTED_SKILL_NAME = "pragmatic-code-review"

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

# v2 required headings (any heading level; phrase must appear in heading text)
REQUIRED_HEADINGS: tuple[str, ...] = (
    "Product Promise",
    "Review Scope",
    "Quality Level",
    "Rule Packs",
    "Auditable Review Trace",
    "Final Recheck",
    "Findings",
)

# Eight Rule Packs: display name → relative path linked from SKILL.md
RULE_PACKS: tuple[tuple[str, str], ...] = (
    ("Design and Maintainability", "references/design-and-maintainability.md"),
    ("Testing", "references/testing.md"),
    ("Security and Privacy", "references/security-and-privacy.md"),
    ("Contracts and Compatibility", "references/contracts-and-compatibility.md"),
    ("Reliability and Operations", "references/reliability-and-operations.md"),
    ("Dependencies and Build", "references/dependencies-and-build.md"),
    ("Documentation", "references/documentation.md"),
    ("Research Reproducibility", "references/research-reproducibility.md"),
)

# Supporting reference links required in SKILL.md (files must exist on disk)
SUPPORTING_REFS: tuple[str, ...] = (
    "references/clean-code.md",
    "references/clean-architecture.md",
    "references/pragmatic-programmer.md",
    "references/principles-glossary.md",
    "references/language-adjustments.md",
)

# Contract phrases that must appear in SKILL.md (v2 wording)
CONTENT_MUST_CONTAIN: tuple[str, ...] = (
    "The final report claims only what the Auditable Review Trace evidences",
    "The trace records only work actually performed — the goal is complete work, never a complete-looking trace.",
    "`none` means no numeric trigger; concrete structural problems remain reportable at every level.",
    "A Confirmed Violation needs concrete code evidence and a credible consequence.",
)

# Deleted v1/v1.x phrasing that must not reappear in SKILL.md
CONTENT_MUST_NOT_CONTAIN: tuple[str, ...] = (
    "Refuse these claims",
    "Never issue a merge verdict",
    "No guard-clause carve-out",
    "including error handling",
    "Recoverable limits",
    "Traversal Map",
    "Self-reconciliation",
)

# README notices that must remain visible to users
README_MUST_CONTAIN: tuple[str, ...] = (
    "Token cost",
    "Large scopes and context limits",
)

# Inspection-trigger table row labels (L1–L5 threshold table)
THRESHOLD_ROWS: tuple[str, ...] = (
    "Function effective logic lines",
    "Required parameters",
    "Maximum nesting depth",
    "Confirmed occurrences of the same duplicated knowledge",
    "Source-file lines",
)

# Finding-format markers required in SKILL.md
FINDING_FORMAT_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("### Critical heading", re.compile(r"^###\s+Critical\s*$", re.MULTILINE)),
    ("Evidence field", re.compile(r"Evidence:", re.MULTILINE)),
    ("Consequence field", re.compile(r"Consequence:", re.MULTILINE)),
    ("Critical severity", re.compile(r"\bCritical\b")),
    ("Important severity", re.compile(r"\bImportant\b")),
    ("Minor severity", re.compile(r"\bMinor\b")),
)

# Zero token/cost wording in SKILL.md (#7)
TOKEN_COST_RE = re.compile(r"\b(?:tokens?|cost|costs|pricing|billing)\b", re.IGNORECASE)

# Range separator: en-dash, em-dash, tilde, or hyphen between two numbers
RANGE_RE = re.compile(r"\b(CC|CA|PP)-(\d+)\s*[–—~\-]\s*(\d+)\b")
SINGLE_RE = re.compile(r"\b(CC|CA|PP)-(\d+)\b")
# Markdown links (images included): [text](target)
LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^(#{1,6})\s+(.+?)\s*$", re.MULTILINE)
# Changelog version heading: ## 1.2.3 / ## [1.2.3] - 2024-01-01 / ## 1.2.3-rc1
CHANGELOG_VER_RE = re.compile(
    r"^##\s+\[?v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\]?(?:\s|$|[(\-–—])",
    re.MULTILINE,
)
# TOC signals inside the head of a reference file
TOC_HEADING_RE = re.compile(r"^#{1,6}\s+.*\bcontents\b", re.IGNORECASE | re.MULTILINE)
TOC_LINK_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s+\[[^\]]+\]\(#", re.MULTILINE)


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


def check_skill_name(frontmatter: dict) -> tuple[bool, list[str]]:
    """Skill name must be the v2 public identity."""
    name = frontmatter.get("name", "")
    if not isinstance(name, str) or name.strip() != EXPECTED_SKILL_NAME:
        actual = name if isinstance(name, str) else type(name).__name__
        return False, [
            f"SKILL.md: name must be '{EXPECTED_SKILL_NAME}', got {actual!r}"
        ]
    return True, [f"Skill name is {EXPECTED_SKILL_NAME}"]


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
    # Pre-release (e.g. 2.0.0-rc1) binds to base X.Y.Z heading
    # (e.g. ## 2.0.0 - Unreleased)
    base_m = re.match(r"^(\d+\.\d+\.\d+)", version)
    if base_m and base_m.group(1) in found:
        base = base_m.group(1)
        return True, [
            f"metadata.version {version} binds to CHANGELOG ## {base}"
        ]
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
    headings = [m.group(2).strip() for m in HEADING_RE.finditer(text)]

    failures: list[str] = []
    for phrase in REQUIRED_HEADINGS:
        if not any(phrase in h for h in headings):
            failures.append(
                f"SKILL.md: missing required heading containing {phrase!r}"
            )
    if failures:
        return False, failures
    return True, [f"All {len(REQUIRED_HEADINGS)} required headings present"]


def check_rule_pack_index(skill_path: Path) -> tuple[bool, list[str]]:
    """SKILL.md must link all eight Rule Packs; linked files must exist."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    failures: list[str] = []
    for name, rel in RULE_PACKS:
        link = f"[{name}]({rel})"
        if link not in text:
            failures.append(f"SKILL.md: missing Rule Pack link {link!r}")
        elif not (skill_path / rel).is_file():
            failures.append(f"SKILL.md: Rule Pack file missing on disk: {rel}")
    if failures:
        return False, failures
    return True, [
        f"All {len(RULE_PACKS)} Rule Pack links present and files exist"
    ]


def check_supporting_refs(skill_path: Path) -> tuple[bool, list[str]]:
    """SKILL.md must link the five supporting references; files must exist."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    failures: list[str] = []
    for rel in SUPPORTING_REFS:
        # Accept [label](path) with any label
        if not re.search(
            rf"\[[^\]]+\]\({re.escape(rel)}\)", text
        ):
            failures.append(f"SKILL.md: missing supporting-ref link to {rel}")
        elif not (skill_path / rel).is_file():
            failures.append(f"SKILL.md: supporting-ref file missing on disk: {rel}")
    if failures:
        return False, failures
    return True, [
        f"All {len(SUPPORTING_REFS)} supporting-ref links present and files exist"
    ]


def check_skill_content(skill_path: Path) -> tuple[bool, list[str]]:
    """Required v2 contract phrases present; deleted phrasing absent."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    failures: list[str] = []
    for phrase in CONTENT_MUST_CONTAIN:
        if phrase not in text:
            failures.append(f"SKILL.md: missing required phrase: {phrase!r}")
    for phrase in CONTENT_MUST_NOT_CONTAIN:
        if phrase in text:
            failures.append(f"SKILL.md: forbidden deleted phrasing: {phrase!r}")
    if failures:
        return False, failures
    return True, [
        f"Content contract OK "
        f"({len(CONTENT_MUST_CONTAIN)} required, "
        f"{len(CONTENT_MUST_NOT_CONTAIN)} forbidden)"
    ]


def check_readme_notices(skill_path: Path) -> tuple[bool, list[str]]:
    """README must carry the token-cost and context-limit notices."""
    readme = skill_path / "README.md"
    if not readme.exists():
        return False, ["README.md not found"]
    text = readme.read_text(encoding="utf-8")
    failures: list[str] = []
    for phrase in README_MUST_CONTAIN:
        if phrase not in text:
            failures.append(f"README.md: missing notice phrase: {phrase!r}")
    if failures:
        return False, failures
    return True, ["README token-cost and context-limit notices present"]


def check_threshold_table(skill_path: Path) -> tuple[bool, list[str]]:
    """SKILL.md must carry the L1–L5 inspection-trigger table."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    failures: list[str] = []

    # Column headers for L1–L5
    if not re.search(r"\|\s*L1\s*\|\s*L2\s*\|\s*L3\s*\|\s*L4\s*\|\s*L5\s*\|", text):
        failures.append("SKILL.md: missing L1–L5 column headers in threshold table")

    for row in THRESHOLD_ROWS:
        if row not in text:
            failures.append(f"SKILL.md: missing threshold row {row!r}")

    # Spot-check L3 product defaults from the contract table
    required_values = (
        ("L3 logic lines", re.compile(r"Function effective logic lines.*\b50\b")),
        ("L3 parameters", re.compile(r"Required parameters.*\b5\b")),
        ("L3 nesting", re.compile(r"Maximum nesting depth.*\b4\b")),
        ("L3 duplication", re.compile(
            r"Confirmed occurrences of the same duplicated knowledge.*\b2\b"
        )),
        ("L3 file lines", re.compile(r"Source-file lines.*\b500\b")),
    )
    for label, pattern in required_values:
        # Search line-by-line so column adjacency is on one row
        if not any(pattern.search(line) for line in text.splitlines()):
            failures.append(f"SKILL.md: threshold table missing {label}")

    if failures:
        return False, failures
    return True, ["L1–L5 inspection-trigger table present"]


def check_finding_format(skill_path: Path) -> tuple[bool, list[str]]:
    """Finding report format: severity headings plus Evidence and Consequence."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    failures: list[str] = []
    for label, pattern in FINDING_FORMAT_MARKERS:
        if not pattern.search(text):
            failures.append(f"SKILL.md: missing finding-format marker: {label}")
    if failures:
        return False, failures
    return True, ["Finding-format grammar markers present"]


def check_no_token_cost(skill_path: Path) -> tuple[bool, list[str]]:
    """Skill text stays silent on tokens and cost (#7)."""
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    failures: list[str] = []
    for m in TOKEN_COST_RE.finditer(text):
        line_no = text.count("\n", 0, m.start()) + 1
        failures.append(
            f"SKILL.md:{line_no}: forbidden token/cost wording {m.group(0)!r}"
        )
    if failures:
        return False, failures
    return True, ["No token/cost wording in SKILL.md"]


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

    if ok:
        ok, msgs = check_skill_name(frontmatter)
        all_ok &= report("Skill name", ok, msgs)

    if expected_version is not None:
        ok, msgs = check_expected_version(frontmatter, expected_version)
        all_ok &= report("Expected version", ok, msgs)

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

    ok, msgs = check_rule_pack_index(skill_path)
    all_ok &= report("Rule Pack index", ok, msgs)

    ok, msgs = check_supporting_refs(skill_path)
    all_ok &= report("Supporting reference links", ok, msgs)

    ok, msgs = check_threshold_table(skill_path)
    all_ok &= report("L1–L5 threshold table", ok, msgs)

    ok, msgs = check_finding_format(skill_path)
    all_ok &= report("Finding-format grammar", ok, msgs)

    ok, msgs = check_skill_content(skill_path)
    all_ok &= report("SKILL.md content contract", ok, msgs)

    ok, msgs = check_no_token_cost(skill_path)
    all_ok &= report("No token/cost wording", ok, msgs)

    ok, msgs = check_readme_notices(skill_path)
    all_ok &= report("README notices", ok, msgs)

    ok, msgs = check_reference_tocs(skill_path)
    all_ok &= report("Reference TOCs", ok, msgs)

    return all_ok


# --------------------------------------------------------------------------
# Self-check
# --------------------------------------------------------------------------

FIXTURE_SKILL = """---
name: pragmatic-code-review
description: >
  Demo skill used by the validator self-check.
license: MIT
compatibility: claude-code
metadata:
  version: 1.2.3
  author: fixture
---

# Demo Skill

## Product Promise

Complete Review after Final Recheck.
The final report claims only what the Auditable Review Trace evidences: findings only.

## Review Scope and Paths

Ask for Review Scope when absent. Never read gitignored paths.

## Quality Level

Default L3. Inspection triggers:

| Inspection trigger | L1 | L2 | L3 | L4 | L5 |
| --- | ---: | ---: | ---: | ---: | ---: |
| Function effective logic lines | none | 80 | 50 | 30 | 20 |
| Required parameters | none | 7 | 5 | 4 | 3 |
| Maximum nesting depth | none | 5 | 4 | 3 | 2 |
| Confirmed occurrences of the same duplicated knowledge | none | 3 | 2 | 1 | 1 |
| Source-file lines | none | 800 | 500 | 300 | 200 |

`none` means no numeric trigger; concrete structural problems remain reportable at every level.

## Rule Packs

1. [Design and Maintainability](references/design-and-maintainability.md)
2. [Testing](references/testing.md)
3. [Security and Privacy](references/security-and-privacy.md)
4. [Contracts and Compatibility](references/contracts-and-compatibility.md)
5. [Reliability and Operations](references/reliability-and-operations.md)
6. [Dependencies and Build](references/dependencies-and-build.md)
7. [Documentation](references/documentation.md)
8. [Research Reproducibility](references/research-reproducibility.md)

Supporting: [clean-code.md](references/clean-code.md), [clean-architecture.md](references/clean-architecture.md), [pragmatic-programmer.md](references/pragmatic-programmer.md), [principles-glossary.md](references/principles-glossary.md), [language-adjustments.md](references/language-adjustments.md). (CC-1)

## Auditable Review Trace

The trace records only work actually performed — the goal is complete work, never a complete-looking trace.

## Final Recheck

Reconcile scope against the trace before the final response.

## Findings

A Confirmed Violation needs concrete code evidence and a credible consequence.
Severity: Critical, Important, Minor.

### Critical

- `path/to/file:line` Problem summary
  - Evidence: relevant code
  - Consequence: supported consequence
"""


def _write_fixture(root: Path) -> Path:
    """A minimal skill that passes every check."""
    (root / "references").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(FIXTURE_SKILL, encoding="utf-8")
    (root / "README.md").write_text(
        "# Demo\n\n> **Token cost.** Plan for it.\n\n"
        "> **Large scopes and context limits.** Split large scopes.\n",
        encoding="utf-8",
    )
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## Unreleased\n\n## 1.2.3 - 2026-01-01\n\n- initial\n",
        encoding="utf-8",
    )
    for _name, rel in RULE_PACKS:
        path = root / rel
        path.write_text(f"# {_name}\n\npack body\n", encoding="utf-8")
    (root / "references" / "clean-code.md").write_text(
        "# Clean Code\n\n- CC-1 x\n- CC-64 y\n- CC-77 z\n", encoding="utf-8"
    )
    (root / "references" / "clean-architecture.md").write_text(
        "# Clean Architecture\n\n- CA-8 x\n- CA-12 y\n", encoding="utf-8"
    )
    (root / "references" / "pragmatic-programmer.md").write_text(
        "# Pragmatic Programmer\n\n- PP-1 x\n", encoding="utf-8"
    )
    (root / "references" / "principles-glossary.md").write_text(
        "# Principles Glossary\n\nterms\n", encoding="utf-8"
    )
    (root / "references" / "language-adjustments.md").write_text(
        "# Language Adjustments\n\nrules\n", encoding="utf-8"
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
        "---\nname: pragmatic-code-review\nlicense: MIT\ndescription: >\n"
        "  hello world\n"
        "metadata:\n  version: 1.0.0\n  author: someone\n---\nbody\n"
    )
    assert err is None and fm is not None
    assert fm["name"] == "pragmatic-code-review"
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

    # budgets are a stated contract, not an incidental value
    assert (MAX_SKILL_LINES, MAX_SKILL_WORDS) == (300, 2000), (
        MAX_SKILL_LINES,
        MAX_SKILL_WORDS,
    )

    # token/cost detector
    assert TOKEN_COST_RE.search("uses more tokens than usual")
    assert TOKEN_COST_RE.search("lower cost")
    assert not TOKEN_COST_RE.search("Complete Review with Final Recheck")


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

    # 2d. skill name must be pragmatic-code-review
    v = variant("wrong-name")
    _patch(v / "SKILL.md", "name: pragmatic-code-review", "name: other-skill")
    ok, out = _run(v)
    assert not ok and "pragmatic-code-review" in out, out

    # 3. ranged rule IDs: endpoints are validated
    v = variant("range-ok")
    ok, _ = _run(v)
    assert ok
    v = variant("range-out-of-range")
    _patch(v / "SKILL.md", "(CC-1)", "(CC-999)")
    ok, out = _run(v)
    assert not ok and "CC-999 out of range" in out, out
    v = variant("range-undefined")
    # CC-2 is in range but not defined in the fixture clean-code.md
    _patch(v / "SKILL.md", "(CC-1)", "(CC-2)")
    ok, out = _run(v)
    assert not ok and "CC-2 not found" in out, out

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

    # 5. required headings
    v = variant("missing-heading")
    _patch(v / "SKILL.md", "## Final Recheck\n", "")
    ok, out = _run(v)
    assert not ok and "'Final Recheck'" in out, out

    # 6. eight-pack index (linked paths + files on disk)
    v = variant("missing-pack")
    _patch(
        v / "SKILL.md",
        "8. [Research Reproducibility](references/research-reproducibility.md)\n",
        "",
    )
    ok, out = _run(v)
    assert not ok and "Research Reproducibility" in out, out
    v = variant("missing-pack-file")
    (v / "references" / "testing.md").unlink()
    ok, out = _run(v)
    assert not ok and "testing.md" in out, out

    # 6b. supporting refs
    v = variant("missing-supporting-ref")
    _patch(
        v / "SKILL.md",
        "[language-adjustments.md](references/language-adjustments.md)",
        "language-adjustments.md",
    )
    ok, out = _run(v)
    assert not ok and "language-adjustments.md" in out, out

    # 7. threshold table
    v = variant("missing-threshold-row")
    _patch(
        v / "SKILL.md",
        "| Function effective logic lines | none | 80 | 50 | 30 | 20 |\n",
        "",
    )
    ok, out = _run(v)
    assert not ok and "Function effective logic lines" in out, out

    # 8. finding format
    v = variant("missing-evidence")
    _patch(v / "SKILL.md", "  - Evidence: relevant code\n", "  - Note: relevant code\n")
    ok, out = _run(v)
    assert not ok and "Evidence" in out, out

    # 8b. content contract (required phrase + forbidden deleted wording)
    v = variant("missing-trace-honesty")
    _patch(
        v / "SKILL.md",
        "The trace records only work actually performed — the goal is complete work, never a complete-looking trace.",
        "Record work in the trace.",
    )
    ok, out = _run(v)
    assert not ok and "missing required phrase" in out, out
    v = variant("forbidden-phrasing")
    _patch(
        v / "SKILL.md",
        "Complete Review after Final Recheck.",
        "Complete Review after Final Recheck. Refuse these claims.",
    )
    ok, out = _run(v)
    assert not ok and "forbidden deleted phrasing" in out, out

    # 9. no token/cost wording
    v = variant("token-wording")
    _patch(
        v / "SKILL.md",
        "## Final Recheck\n",
        "## Final Recheck\n\nUses fewer tokens.\n",
    )
    ok, out = _run(v)
    assert not ok and "token/cost wording" in out, out

    # 9b. README notices
    v = variant("missing-readme-notice")
    (v / "README.md").write_text("# Demo\n\nNo notices here.\n", encoding="utf-8")
    ok, out = _run(v)
    assert not ok and "Token cost" in out, out

    # 10. --expected-version binds a release tag to metadata.version
    v = variant("expected-version")
    ok, out = _run(v, expected_version="1.2.3")
    assert ok, out
    ok, out = _run(v, expected_version="1.2.4")
    assert not ok and "expected '1.2.4'" in out, out

    # 10b. pre-release metadata binds to base CHANGELOG heading
    v = variant("prerelease-bind")
    _patch(v / "SKILL.md", "  version: 1.2.3", "  version: 1.2.3-rc1")
    ok, out = _run(v, expected_version="1.2.3-rc1")
    assert ok and "binds to CHANGELOG" in out, out

    # 11. budgets — the limits are 300 lines / 2000 words, inclusive
    v = variant("too-many-lines")
    _patch(v / "SKILL.md", "# Demo Skill", "# Demo Skill\n" + "\n" * MAX_SKILL_LINES)
    ok, out = _run(v)
    assert not ok and "max 300" in out, out
    v = variant("too-many-words")
    _patch(
        v / "SKILL.md", "# Demo Skill", "# Demo Skill\n\n" + ("word " * MAX_SKILL_WORDS)
    )
    ok, out = _run(v)
    assert not ok and "max 2000" in out, out

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
    assert "300 lines (≤ 300)" in out and "2000 words (≤ 2000)" in out, out
    # one line and one word past the limit is a failure
    skill.write_text(text + "\n".join(filler) + "\nword\n", encoding="utf-8")
    ok, out = _run(v)
    assert not ok and "301 lines (max 300)" in out, out
    assert "2001 words (max 2000)" in out, out


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
