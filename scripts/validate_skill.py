#!/usr/bin/env python3
"""
smell-check v3 skill validator.

Usage:
    python scripts/validate_skill.py [skill_directory]
    python scripts/validate_skill.py [skill_directory] --expected-version X.Y.Z
    python scripts/validate_skill.py --self-check

Exit 0 on full pass; non-zero if any check fails.
Stdlib only.
"""

from __future__ import annotations

import argparse
import io
import re
import shutil
import subprocess
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

# Line budget carried from v2 (SKILL.md body stays short).
MAX_SKILL_LINES = 300

# Metric keys emitted by measurement — not rule keys (allowlist).
METRIC_KEY_ALLOWLIST = frozenset(
    {
        "test.assertion-sites",
        "test.gate-nodes",
    }
)

# Legacy product names (split so this file is not itself a hit).
LEGACY_NAMES: tuple[str, ...] = (
    "pragmatic" + "-clean-code-reviewer",
    "pragmatic" + "-code-reviewer",
    "pragmatic" + "-reviewer",
    "pragmatic" + "-code-review",
)

# v2 contract phrases that must not remain outside CHANGELOG history.
V2_PHRASES: tuple[str, ...] = (
    "Quality" + " Level",
    "Auditable" + " Review Trace",
    "Product" + " Promise",
    "Final" + " Recheck",
    "Complete" + " Review",
)
# Independent quality-level tokens from the prior major version (word boundary).
L_LEVEL_RE = re.compile(r"\bL[1-5]\b")

ALLOWED_FRONTMATTER = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}

LINK_RE = re.compile(r"!?\[([^\]]*)\]\(([^)]+)\)")
CHANGELOG_VER_RE = re.compile(
    r"^##\s+\[?v?(\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?)\]?(?:\s|$|[(\-–—])",
    re.MULTILINE,
)
# Rule headings: ### code.foo or ### `code.foo`
RULE_HEADING_RE = re.compile(
    r"^###\s+`?((?:code|test)\.[a-z0-9]+(?:-[a-z0-9]+)+)`?\s*$",
    re.MULTILINE,
)
# Backtick rule/metric tokens (require hyphen so framework tags like test.skip skip).
BACKTICK_KEY_RE = re.compile(
    r"`((?:code|test)\.[a-z0-9]+(?:-[a-z0-9]+)+)`"
)
# Preset data row: | `key` | metric | personal | small | medium | large | ultimate |
PRESET_ROW_RE = re.compile(
    r"^\|\s*`((?:code|test)\.[a-z0-9]+(?:-[a-z0-9]+)+)`\s*\|"
    r"[^|]*\|"
    r"\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|"
    r"\s*$",
    re.MULTILINE,
)

# Shipped-markdown hygiene (SKILL.md, README.md, references/*.md only).
BACKTICK_MD_RE = re.compile(r"`[A-Za-z0-9._/-]*\.md`")
TILDE_RANGE_RE = re.compile(r"\b(?:CC|CA|PP)-\d+~")
PLAN_TOKEN_RE = re.compile(r"\b(?:AE|KTD)\d+\b")

SWEEP_EXEMPT_NAMES = frozenset({"CHANGELOG.md"})


# ---------------------------------------------------------------------------
# Frontmatter (minimal YAML, no PyYAML)
# ---------------------------------------------------------------------------


def _scalar(val: str) -> str:
    if len(val) >= 2 and (
        (val.startswith('"') and val.endswith('"'))
        or (val.startswith("'") and val.endswith("'"))
    ):
        return val[1:-1]
    return val


def parse_frontmatter(content: str) -> tuple[dict | None, str | None]:
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
            data[key] = " ".join(line.strip() for line in block_lines if line.strip())
        in_block = False
        block_lines = []

    def finish_nested() -> None:
        nonlocal nested_key, nested
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
            data[key] = ""
            nested_key = key
            nested = {}
        else:
            data[key] = _scalar(val)

    finish_block()
    finish_nested()
    return data, None


def metadata_version(frontmatter: dict) -> str | None:
    meta = frontmatter.get("metadata")
    if not isinstance(meta, dict):
        return None
    version = meta.get("version")
    if isinstance(version, str) and version.strip():
        return version.strip()
    return None


def check_frontmatter(skill_md: Path) -> tuple[bool, list[str], dict]:
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


def check_expected_version(
    frontmatter: dict, expected: str
) -> tuple[bool, list[str]]:
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


def check_version_changelog(
    skill_path: Path, frontmatter: dict
) -> tuple[bool, list[str]]:
    """Bind metadata.version to a CHANGELOG heading (pre-release → base X.Y.Z)."""
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
    base_m = re.match(r"^(\d+\.\d+\.\d+)", version)
    if base_m and base_m.group(1) in found:
        base = base_m.group(1)
        return True, [f"metadata.version {version} binds to CHANGELOG ## {base}"]
    return False, [
        f"metadata.version '{version}' not found as '## {version}' heading in "
        f"CHANGELOG.md (found: {', '.join(found[:8]) or 'none'})"
    ]


# ---------------------------------------------------------------------------
# Links
# ---------------------------------------------------------------------------


def check_relative_links(skill_path: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    if not (skill_path / "SKILL.md").is_file():
        failures.append("SKILL.md not found")
    for path in shipped_markdown_files(skill_path):
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(skill_path)
        for m in LINK_RE.finditer(text):
            target = m.group(2).strip()
            target = re.split(r"\s+", target, maxsplit=1)[0]
            if not target or target.startswith(("#", "http://", "https://", "mailto:")):
                continue
            file_part = target.split("#", 1)[0]
            if not file_part:
                continue
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:", file_part):
                continue
            dest = (path.parent / file_part).resolve()
            line_no = text.count("\n", 0, m.start()) + 1
            if not dest.exists():
                failures.append(f"{rel}:{line_no}: broken relative link → {target}")
    if failures:
        return False, failures
    return True, ["All relative markdown links in shipped markdown resolve"]


# ---------------------------------------------------------------------------
# Rule registries + presets
# ---------------------------------------------------------------------------


def load_registry_keys(skill_path: Path) -> tuple[set[str], list[str]]:
    """Keys from ### headings in rules-code.md and rules-test.md; report dupes."""
    keys: set[str] = set()
    failures: list[str] = []
    for rel in ("references/rules-code.md", "references/rules-test.md"):
        path = skill_path / rel
        if not path.is_file():
            failures.append(f"missing registry: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for m in RULE_HEADING_RE.finditer(text):
            key = m.group(1)
            if key in keys:
                line_no = text.count("\n", 0, m.start()) + 1
                failures.append(f"{rel}:{line_no}: duplicate rule key {key}")
            else:
                keys.add(key)
    return keys, failures


def check_registry_keys(skill_path: Path) -> tuple[bool, list[str], set[str]]:
    keys, failures = load_registry_keys(skill_path)
    if failures:
        return False, failures, keys
    if not keys:
        return False, ["no rule keys found in registries"], keys
    return True, [f"{len(keys)} unique rule keys in registries"], keys


def check_referenced_keys(
    skill_path: Path, registry: set[str]
) -> tuple[bool, list[str]]:
    failures: list[str] = []
    paths: list[Path] = []
    skill_md = skill_path / "SKILL.md"
    if skill_md.is_file():
        paths.append(skill_md)
    ref_dir = skill_path / "references"
    if ref_dir.is_dir():
        paths.extend(sorted(ref_dir.glob("*.md")))

    for path in paths:
        text = path.read_text(encoding="utf-8")
        rel = path.relative_to(skill_path)
        for m in BACKTICK_KEY_RE.finditer(text):
            key = m.group(1)
            if key in registry or key in METRIC_KEY_ALLOWLIST:
                continue
            line_no = text.count("\n", 0, m.start()) + 1
            failures.append(f"{rel}:{line_no}: unknown rule key `{key}`")

    if failures:
        return False, failures
    return True, ["All backtick code.*/test.* tokens resolve to registry or allowlist"]


def parse_preset_rows(text: str) -> list[tuple[str, list[int], int]]:
    """Return (key, [personal, small, medium, large, ultimate], line_no)."""
    rows: list[tuple[str, list[int], int]] = []
    for m in PRESET_ROW_RE.finditer(text):
        key = m.group(1)
        five = [int(m.group(i)) for i in range(2, 7)]
        line_no = text.count("\n", 0, m.start()) + 1
        rows.append((key, five, line_no))
    return rows


def check_presets(skill_path: Path, registry: set[str]) -> tuple[bool, list[str]]:
    path = skill_path / "references" / "presets.md"
    if not path.is_file():
        return False, ["references/presets.md not found"]
    text = path.read_text(encoding="utf-8")
    rows = parse_preset_rows(text)
    if not rows:
        return False, ["references/presets.md: no numeric threshold rows parsed"]

    failures: list[str] = []
    for key, five, line_no in rows:
        if key not in registry:
            failures.append(
                f"references/presets.md:{line_no}: preset key `{key}` not in registry"
            )
        if len(five) != 5:
            failures.append(
                f"references/presets.md:{line_no}: `{key}` needs five thresholds, "
                f"got {len(five)}"
            )
            continue
        # monotone non-increasing: personal ≥ small ≥ medium ≥ large ≥ ultimate
        for i in range(4):
            if five[i] < five[i + 1]:
                failures.append(
                    f"references/presets.md:{line_no}: `{key}` not monotone "
                    f"non-increasing: {five[0]}/{five[1]}/{five[2]}/{five[3]}/{five[4]}"
                )
                break

    if failures:
        return False, failures
    return True, [f"Preset table OK ({len(rows)} numeric rules, monotone)"]


def check_skill_budgets(skill_path: Path) -> tuple[bool, list[str]]:
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        return False, ["SKILL.md not found"]
    text = skill_md.read_text(encoding="utf-8")
    lines = len(text.splitlines())
    if lines > MAX_SKILL_LINES:
        return False, [f"SKILL.md has {lines} lines (max {MAX_SKILL_LINES})"]
    return True, [f"SKILL.md has {lines} lines (≤ {MAX_SKILL_LINES})"]


# ---------------------------------------------------------------------------
# Tracked-file sweeps
# ---------------------------------------------------------------------------


def list_tracked_files(skill_path: Path) -> list[Path]:
    """Prefer git ls-files (skips machine-local); fall back to a walk for fixtures."""
    try:
        proc = subprocess.run(
            ["git", "-C", str(skill_path), "ls-files", "-z"],
            capture_output=True,
            check=True,
            timeout=30,
        )
        names = [n for n in proc.stdout.decode("utf-8", errors="replace").split("\0") if n]
        return [skill_path / n for n in names if (skill_path / n).is_file()]
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        out: list[Path] = []
        for p in skill_path.rglob("*"):
            if not p.is_file():
                continue
            if ".git" in p.parts:
                continue
            out.append(p)
        return out


def _is_sweep_exempt(path: Path, skill_path: Path) -> bool:
    try:
        rel = path.relative_to(skill_path)
    except ValueError:
        return path.name in SWEEP_EXEMPT_NAMES
    return rel.name in SWEEP_EXEMPT_NAMES or str(rel) in SWEEP_EXEMPT_NAMES


def _read_text_loose(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            return None


def check_legacy_names(skill_path: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for path in list_tracked_files(skill_path):
        if _is_sweep_exempt(path, skill_path):
            continue
        text = _read_text_loose(path)
        if text is None:
            continue
        rel = path.relative_to(skill_path)
        for name in LEGACY_NAMES:
            start = 0
            while True:
                idx = text.find(name, start)
                if idx < 0:
                    break
                line_no = text.count("\n", 0, idx) + 1
                failures.append(f"{rel}:{line_no}: legacy name {name!r}")
                start = idx + len(name)
    if failures:
        return False, failures
    return True, ["No legacy product names in tracked files (CHANGELOG exempt)"]


def shipped_markdown_files(skill_path: Path) -> list[Path]:
    files = [skill_path / "SKILL.md", skill_path / "README.md"]
    ref_dir = skill_path / "references"
    if ref_dir.is_dir():
        files.extend(sorted(ref_dir.glob("*.md")))
    return [p for p in files if p.is_file()]


def check_shipped_markdown(skill_path: Path) -> tuple[bool, list[str]]:
    """Hygiene sweeps for shipped Markdown only (not CHANGELOG or machine-local docs)."""
    failures: list[str] = []
    sweeps = (
        (BACKTICK_MD_RE, "backticked file reference {} — use a markdown link"),
        (TILDE_RANGE_RE, "tilde range {} — renders as strikethrough; write 'CC-4 to CC-19'"),
        (PLAN_TOKEN_RE, "plan token {} — plan vocabulary must not ship"),
    )
    for path in shipped_markdown_files(skill_path):
        text = _read_text_loose(path)
        if text is None:
            continue
        rel = path.relative_to(skill_path)
        for regex, template in sweeps:
            for m in regex.finditer(text):
                line_no = text.count("\n", 0, m.start()) + 1
                failures.append(f"{rel}:{line_no}: " + template.format(m.group(0)))
    if failures:
        return False, failures
    return True, ["Shipped markdown clean (links, ranges, plan tokens)"]


def check_v2_phrases(skill_path: Path) -> tuple[bool, list[str]]:
    failures: list[str] = []
    for path in list_tracked_files(skill_path):
        if _is_sweep_exempt(path, skill_path):
            continue
        text = _read_text_loose(path)
        if text is None:
            continue
        rel = path.relative_to(skill_path)
        for phrase in V2_PHRASES:
            start = 0
            while True:
                idx = text.find(phrase, start)
                if idx < 0:
                    break
                line_no = text.count("\n", 0, idx) + 1
                failures.append(f"{rel}:{line_no}: v2 phrase {phrase!r}")
                start = idx + len(phrase)
        for m in L_LEVEL_RE.finditer(text):
            line_no = text.count("\n", 0, m.start()) + 1
            failures.append(f"{rel}:{line_no}: v2 level token {m.group(0)!r}")
    if failures:
        return False, failures
    return True, [
        "No v2 contract phrases or legacy level tokens (CHANGELOG exempt)"
    ]


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------


def report(name: str, ok: bool, messages: list[str]) -> bool:
    status = "PASS" if ok else "FAIL"
    print(f"[{status}] {name}")
    for msg in messages if not ok else messages[:1]:
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

    ok, msgs = check_version_changelog(skill_path, frontmatter)
    all_ok &= report("Version/changelog agreement", ok, msgs)

    ok, msgs = check_relative_links(skill_path)
    all_ok &= report("Relative markdown links", ok, msgs)

    ok, msgs, registry = check_registry_keys(skill_path)
    all_ok &= report("Registry key uniqueness", ok, msgs)

    ok, msgs = check_referenced_keys(skill_path, registry)
    all_ok &= report("Referenced rule keys", ok, msgs)

    ok, msgs = check_presets(skill_path, registry)
    all_ok &= report("Preset thresholds", ok, msgs)

    ok, msgs = check_skill_budgets(skill_path)
    all_ok &= report("SKILL.md line budget", ok, msgs)

    ok, msgs = check_legacy_names(skill_path)
    all_ok &= report("Legacy name sweep", ok, msgs)

    ok, msgs = check_v2_phrases(skill_path)
    all_ok &= report("v2 phrase sweep", ok, msgs)

    ok, msgs = check_shipped_markdown(skill_path)
    all_ok &= report("Shipped markdown hygiene", ok, msgs)

    return all_ok


# ---------------------------------------------------------------------------
# Self-check fixtures
# ---------------------------------------------------------------------------

FIXTURE_SKILL = """---
name: smell-check
description: >
  Demo skill for the validator self-check. Smell audit fixture only.
license: MIT
metadata:
  version: 1.2.3
---

# smell-check

Fixture body. See [rules-code.md](references/rules-code.md),
[rules-test.md](references/rules-test.md), and [presets.md](references/presets.md).
"""

FIXTURE_RULES_CODE = """# Code family rules

### code.long-function

- **key:** `code.long-function`
- **family:** code
- **status:** stable
"""

FIXTURE_RULES_TEST = """# Test family rules

### `test.assertion-free-test`

- **key:** `test.assertion-free-test`
- **family:** test
- **status:** stable
"""

FIXTURE_PRESETS = """# Presets

## Numeric thresholds

| rule key | metric | personal | small | medium | large | ultimate |
| --- | --- | ---: | ---: | ---: | ---: | ---: |
| `code.long-function` | non-blank, non-comment lines per function | 100 | 60 | 40 | 30 | 20 |
"""


def _write_fixture(root: Path) -> Path:
    (root / "references").mkdir(parents=True, exist_ok=True)
    (root / "SKILL.md").write_text(FIXTURE_SKILL, encoding="utf-8")
    (root / "README.md").write_text("# Demo\n\nFixture readme.\n", encoding="utf-8")
    (root / "CHANGELOG.md").write_text(
        "# Changelog\n\n## 1.2.3 - 2026-01-01\n\n- initial\n",
        encoding="utf-8",
    )
    (root / "references" / "rules-code.md").write_text(
        FIXTURE_RULES_CODE, encoding="utf-8"
    )
    (root / "references" / "rules-test.md").write_text(
        FIXTURE_RULES_TEST, encoding="utf-8"
    )
    (root / "references" / "presets.md").write_text(FIXTURE_PRESETS, encoding="utf-8")
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
    fm, err = parse_frontmatter(
        "---\nname: smell-check\nlicense: MIT\ndescription: >\n"
        "  hello world\n"
        "metadata:\n  version: 1.0.0\n  author: someone\n---\nbody\n"
    )
    assert err is None and fm is not None
    assert fm["name"] == "smell-check"
    assert "hello world" in fm["description"]
    assert fm["metadata"] == {"version": "1.0.0", "author": "someone"}, fm["metadata"]
    assert metadata_version(fm) == "1.0.0"

    rows = parse_preset_rows(FIXTURE_PRESETS)
    assert len(rows) == 1 and rows[0][0] == "code.long-function"
    assert rows[0][1] == [100, 60, 40, 30, 20]

    # monotone helper path via full check is covered in fixtures
    assert MAX_SKILL_LINES == 300
    assert "test.assertion-sites" in METRIC_KEY_ALLOWLIST


def _fixture_checks(tmp: Path) -> None:
    base = _write_fixture(tmp / "base")
    ok, out = _run(base)
    assert ok, f"baseline fixture must pass:\n{out}"

    def variant(name: str) -> Path:
        dst = tmp / name
        shutil.rmtree(dst, ignore_errors=True)
        shutil.copytree(base, dst)
        return dst

    # --- bad preset: non-monotone five values (large > medium) ---
    v = variant("preset-non-mono")
    _patch(
        v / "references" / "presets.md",
        "| `code.long-function` | non-blank, non-comment lines per function | 100 | 60 | 40 | 30 | 20 |",
        "| `code.long-function` | non-blank, non-comment lines per function | 100 | 60 | 40 | 50 | 20 |",
    )
    ok, out = _run(v)
    assert not ok and "not monotone" in out, out

    # --- bad preset: missing a profile column (only four thresholds) ---
    v = variant("preset-short")
    _patch(
        v / "references" / "presets.md",
        "| `code.long-function` | non-blank, non-comment lines per function | 100 | 60 | 40 | 30 | 20 |",
        "| `code.long-function` | non-blank, non-comment lines per function | 100 | 60 | 40 | 20 |",
    )
    ok, out = _run(v)
    # row no longer matches PRESET_ROW_RE → zero rows parsed
    assert not ok and (
        "no numeric threshold rows" in out or "needs five thresholds" in out
    ), out

    # --- shipped-markdown hygiene: backticked in-skill file reference ---
    v = variant("backtick-md")
    _patch(
        v / "SKILL.md",
        "Fixture body.",
        "Fixture body mentions `presets.md` inline.",
    )
    ok, out = _run(v)
    assert not ok and "backticked file reference" in out, out

    # --- shipped-markdown hygiene: tilde range ---
    v = variant("tilde-range")
    _patch(
        v / "references" / "rules-code.md",
        "# Code family rules",
        "# Code family rules\n\nCovers CC-4~19.",
    )
    ok, out = _run(v)
    assert not ok and "tilde range" in out, out

    # --- shipped-markdown hygiene: plan token ---
    v = variant("plan-token")
    _patch(
        v / "references" / "rules-test.md",
        "# Test family rules",
        "# Test family rules\n\nSee AE3 for the override shape.",
    )
    ok, out = _run(v)
    assert not ok and "plan token" in out, out

    # --- unknown referenced key (kebab form so the token matcher applies) ---
    v = variant("unknown-key")
    _patch(
        v / "SKILL.md",
        "Fixture body.",
        "Fixture body mentions `code.nonexistent-key` here.",
    )
    ok, out = _run(v)
    assert not ok and "code.nonexistent-key" in out, out

    # --- legacy name planted (contiguous only in fixture file) ---
    v = variant("legacy-name")
    (v / "note.md").write_text(
        "uses " + "pragmatic" + "-code-review" + " still\n", encoding="utf-8"
    )
    ok, out = _run(v)
    assert not ok and "legacy name" in out, out

    # --- v2 phrase planted ---
    v = variant("v2-phrase")
    (v / "note.md").write_text(
        "see " + "Product" + " Promise" + " section\n", encoding="utf-8"
    )
    ok, out = _run(v)
    assert not ok and "v2 phrase" in out, out

    # --- description over 1024 ---
    v = variant("long-desc")
    long_desc = "x" * 1025
    skill = (v / "SKILL.md").read_text(encoding="utf-8")
    skill = skill.replace(
        "  Demo skill for the validator self-check. Smell audit fixture only.\n",
        f"  {long_desc}\n",
    )
    (v / "SKILL.md").write_text(skill, encoding="utf-8")
    ok, out = _run(v)
    assert not ok and "1024" in out, out

    # --- changelog / expected-version still wired ---
    v = variant("version-mismatch")
    _patch(v / "SKILL.md", "  version: 1.2.3", "  version: 9.9.9")
    ok, out = _run(v)
    assert not ok and "9.9.9" in out, out

    v = variant("expected-ok")
    ok, out = _run(v, expected_version="1.2.3")
    assert ok, out
    ok, out = _run(v, expected_version="1.2.4")
    assert not ok and "expected '1.2.4'" in out, out

    # --- line budget ---
    v = variant("too-many-lines")
    _patch(
        v / "SKILL.md",
        "# smell-check",
        "# smell-check\n" + ("line\n" * MAX_SKILL_LINES),
    )
    ok, out = _run(v)
    assert not ok and f"max {MAX_SKILL_LINES}" in out, out

    # --- metric allowlist does not fail ---
    v = variant("metric-allow")
    (v / "references" / "measurement.md").write_text(
        "# Measurement\n\nMetric `test.assertion-sites` and `test.gate-nodes`.\n",
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
        description="Validate smell-check skill folder (v3 contract).",
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
        print(f"Not a directory: {skill_dir}")
        sys.exit(1)

    ok = validate_skill(skill_dir, args.expected_version)
    if ok:
        print("Skill is valid!")
    else:
        print("Skill validation failed")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
