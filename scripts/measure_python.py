#!/usr/bin/env python3
"""Deterministic Python metrics for smell-check (stdlib ast only)."""

from __future__ import annotations

import argparse
import ast
import io
import sys
import tokenize
from dataclasses import dataclass
from pathlib import Path


# Columns: rule, location, symbol, value (TSV). Sorted by those fields.
RULE_LONG_FUNCTION = "code.long-function"
RULE_DEEP_NESTING = "code.deep-nesting"
RULE_LONG_PARAMS = "code.long-parameter-list"
RULE_ASSERT_SITES = "test.assertion-sites"
RULE_GATE_NODES = "test.gate-nodes"

# Assertion call name prefixes / exact names (registry: assert/expect, pytest.raises, mock verify).
ASSERT_CALL_NAMES = frozenset(
    {
        "assertEqual",
        "assertequals",
        "asserttrue",
        "assertfalse",
        "assertis",
        "assertisnot",
        "assertisin",
        "assertnotisin",
        "assertisnone",
        "assertisnotnone",
        "assertraises",
        "assertraisesregex",
        "assertalmostequal",
        "assertlistEqual",
        "assertdictequal",
        "assertsetequal",
        "assertin",
        "assertnotin",
        "assertgreater",
        "assertgreaterEqual",
        "assertless",
        "assertlessequal",
        "assertregex",
        "assertcountEqual",
        "assert_called",
        "assert_called_once",
        "assert_called_with",
        "assert_called_once_with",
        "assert_any_call",
        "assert_has_calls",
        "assert_not_called",
        "assert_awaited",
        "assert_awaited_once",
        "assert_awaited_with",
        "assert_awaited_once_with",
        "assertcalled",
        "assertcalledonce",
        "assertcalledwith",
        "assertcalledoncewith",
        "assertanycall",
        "asserthascalls",
        "assertnotcalled",
        "raises",
        "warns",
        "deprecated_call",
        "expect",
    }
)
ASSERT_ATTR_PREFIXES = ("assert_called", "assert_awaited", "assertcalled", "tohavebeencalled")


@dataclass(frozen=True, order=True)
class Row:
    rule: str
    location: str
    symbol: str
    value: int

    def line(self) -> str:
        return f"{self.rule}\t{self.location}\t{self.symbol}\t{self.value}"


def _is_docstring(node: ast.stmt) -> bool:
    if not isinstance(node, ast.Expr):
        return False
    v = node.value
    return isinstance(v, ast.Constant) and isinstance(v.value, str)


def _call_name(node: ast.AST) -> str | None:
    if not isinstance(node, ast.Call):
        return None
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


def _is_assert_call(node: ast.Call) -> bool:
    name = _call_name(node)
    if name is None:
        return False
    low = name.lower()
    if low in ASSERT_CALL_NAMES:
        return True
    if low.startswith("assert") and low != "assert_":
        # unittest-style assert* and mock assert_*
        return True
    if any(low.startswith(p) for p in ASSERT_ATTR_PREFIXES):
        return True
    # pytest.raises / pytest.warns via attribute
    if isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
        if node.func.value.id == "pytest" and node.func.attr in {"raises", "warns", "deprecated_call"}:
            return True
    return False


def _direct_nested_defs(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
) -> list[ast.stmt]:
    """Defs/classes directly inside node's body (not inside a deeper def/class)."""
    found: list[ast.stmt] = []

    def walk(stmt: ast.stmt) -> None:
        if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            found.append(stmt)
            return
        for child in ast.iter_child_nodes(stmt):
            if isinstance(child, ast.stmt):
                walk(child)

    for stmt in node.body:
        walk(stmt)
    return found


NON_CODE_TOKENS = frozenset(
    {
        tokenize.COMMENT,
        tokenize.NL,
        tokenize.NEWLINE,
        tokenize.INDENT,
        tokenize.DEDENT,
        tokenize.ENCODING,
        tokenize.ENDMARKER,
    }
)


def code_line_set(source: str) -> set[int]:
    """Line numbers carrying at least one real token (comments/blanks are not)."""
    lines: set[int] = set()
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type in NON_CODE_TOKENS:
            continue
        lines.update(range(tok.start[0], tok.end[0] + 1))
    return lines


def count_nloc(
    node: ast.FunctionDef | ast.AsyncFunctionDef,
    source_lines: list[str],
    code_lines: set[int],
) -> int:
    """Non-blank, non-comment lines from the `def` line through the body.

    Skips the leading docstring and nested def/class bodies (each nested
    declaration still counts as one line of this function).
    """
    counted = set(range(node.lineno, (node.end_lineno or node.lineno) + 1))

    if node.body and _is_docstring(node.body[0]):
        ds = node.body[0]
        doc_lines = set(range(ds.lineno, (ds.end_lineno or ds.lineno) + 1))
        # a line the docstring shares with the signature or a statement stays
        doc_lines.discard(node.lineno)
        if len(node.body) > 1:
            doc_lines.discard(node.body[1].lineno)
        counted -= doc_lines

    for nested in _direct_nested_defs(node):
        start = min(
            [d.lineno for d in getattr(nested, "decorator_list", [])] + [nested.lineno]
        )
        counted -= set(range(start, (nested.end_lineno or nested.lineno) + 1))
        counted.add(nested.lineno)

    # blank filter keeps parity with measure_ts.mjs for blank lines
    # inside multi-line strings
    nloc = 0
    for line_no in counted:
        if line_no not in code_lines:
            continue
        if line_no - 1 < len(source_lines) and source_lines[line_no - 1].strip():
            nloc += 1
    return nloc


def max_nesting(body: list[ast.stmt], *, skip_leading_docstring: bool) -> int:
    peak = 0
    for i, stmt in enumerate(body):
        if skip_leading_docstring and i == 0 and _is_docstring(stmt):
            continue
        peak = max(peak, _nesting_in_stmt(stmt, 0))
    return peak


def _nesting_in_stmt(stmt: ast.stmt, depth: int) -> int:
    """Return peak depth reached inside stmt; control structures enter at depth+1."""

    if isinstance(stmt, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
        return depth

    if isinstance(stmt, ast.If):
        d = depth + 1
        peak = d
        peak = max(peak, _max_in_body(stmt.body, d))
        orelse = stmt.orelse
        while orelse:
            if len(orelse) == 1 and isinstance(orelse[0], ast.If):
                peak = max(peak, d)  # elif at same depth as if
                peak = max(peak, _max_in_body(orelse[0].body, d))
                orelse = orelse[0].orelse
            else:
                peak = max(peak, d)  # else
                peak = max(peak, _max_in_body(orelse, d))
                break
        return peak

    if isinstance(stmt, (ast.For, ast.AsyncFor, ast.While)):
        d = depth + 1
        peak = d
        peak = max(peak, _max_in_body(stmt.body, d))
        if stmt.orelse:
            peak = max(peak, _max_in_body(stmt.orelse, d))
        return peak

    if isinstance(stmt, ast.Try):
        d = depth + 1
        peak = d
        peak = max(peak, _max_in_body(stmt.body, d))
        for handler in stmt.handlers:
            peak = max(peak, d)
            peak = max(peak, _max_in_body(handler.body, d))
        if stmt.orelse:
            peak = max(peak, _max_in_body(stmt.orelse, d))
        if stmt.finalbody:
            peak = max(peak, _max_in_body(stmt.finalbody, d))
        return peak

    if isinstance(stmt, (ast.With, ast.AsyncWith)):
        d = depth + 1
        return max(d, _max_in_body(stmt.body, d))

    if isinstance(stmt, ast.Match):
        d = depth + 1
        peak = d
        for case in stmt.cases:
            peak = max(peak, _max_in_body(case.body, d))
        return peak

    return depth


def _max_in_body(body: list[ast.stmt], depth: int) -> int:
    peak = depth
    for stmt in body:
        peak = max(peak, _nesting_in_stmt(stmt, depth))
    return peak


def declared_param_count(args: ast.arguments) -> int:
    """Every declared value parameter counts once; the receiver does not."""
    pos = list(args.posonlyargs) + list(args.args)
    if pos and pos[0].arg in {"self", "cls"}:
        pos = pos[1:]
    n = len(pos) + len(args.kwonlyargs)
    if args.vararg is not None:
        n += 1
    if args.kwarg is not None:
        n += 1
    return n


def _is_test_function(name: str, qual: str) -> bool:
    if name.startswith("test"):
        return True
    # unittest style: method on Test* class already filtered by name startswith test
    return False


def _count_asserts_and_gates(body: list[ast.stmt]) -> tuple[int, int]:
    asserts = 0
    gates = 0

    class V(ast.NodeVisitor):
        """Asserts count anywhere in the test body, including nested helpers;
        gates stop counting past a nested def/class boundary (excluded bodies)."""

        def __init__(self, count_gates: bool) -> None:
            self.count_gates = count_gates

        def _enter_nested(self, node: ast.stmt) -> None:
            sub = V(count_gates=False)
            for child in ast.iter_child_nodes(node):
                sub.visit(child)

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            self._enter_nested(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            self._enter_nested(node)

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self._enter_nested(node)

        def visit_Assert(self, node: ast.Assert) -> None:
            nonlocal asserts
            asserts += 1
            self.generic_visit(node)

        def visit_Call(self, node: ast.Call) -> None:
            nonlocal asserts
            if _is_assert_call(node):
                asserts += 1
            self.generic_visit(node)

        def _gate(self, node: ast.AST) -> None:
            nonlocal gates
            if self.count_gates:
                gates += 1
            self.generic_visit(node)

        def visit_If(self, node: ast.If) -> None:
            self._gate(node)

        def visit_For(self, node: ast.For) -> None:
            self._gate(node)

        def visit_AsyncFor(self, node: ast.AsyncFor) -> None:
            self._gate(node)

        def visit_While(self, node: ast.While) -> None:
            self._gate(node)

        def visit_Match(self, node: ast.Match) -> None:
            self._gate(node)

        def visit_IfExp(self, node: ast.IfExp) -> None:
            self._gate(node)

    for stmt in body:
        if _is_docstring(stmt):
            continue
        V(count_gates=True).visit(stmt)
    return asserts, gates


def _func_location(path: str, node: ast.AST) -> str:
    line = getattr(node, "lineno", 1)
    return f"{path}:{line}"


def measure_source(path: str, source: str) -> list[Row]:
    tree = ast.parse(source, filename=path)
    source_lines = source.splitlines()
    code_lines = code_line_set(source)
    rows: list[Row] = []

    def handle_function(node: ast.FunctionDef | ast.AsyncFunctionDef, qual: str) -> None:
        name = node.name
        qname = f"{qual}.{name}" if qual else name
        loc = _func_location(path, node)
        logic = count_nloc(node, source_lines, code_lines)
        nest = max_nesting(node.body, skip_leading_docstring=True)
        params = declared_param_count(node.args)
        rows.append(Row(RULE_LONG_FUNCTION, loc, qname, logic))
        rows.append(Row(RULE_DEEP_NESTING, loc, qname, nest))
        rows.append(Row(RULE_LONG_PARAMS, loc, qname, params))
        if _is_test_function(name, qname):
            asserts, gates = _count_asserts_and_gates(node.body)
            rows.append(Row(RULE_ASSERT_SITES, loc, qname, asserts))
            rows.append(Row(RULE_GATE_NODES, loc, qname, gates))

    class Walker(ast.NodeVisitor):
        def __init__(self) -> None:
            self.class_stack: list[str] = []

        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            self.class_stack.append(node.name)
            self.generic_visit(node)
            self.class_stack.pop()

        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            qual = ".".join(self.class_stack)
            handle_function(node, qual)
            # still walk nested functions as their own units
            self.generic_visit(node)

        def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
            qual = ".".join(self.class_stack)
            handle_function(node, qual)
            self.generic_visit(node)

    Walker().visit(tree)
    return rows


def measure_file(path: Path) -> list[Row]:
    source = path.read_text(encoding="utf-8")
    return measure_source(str(path).replace("\\", "/"), source)


def apply_thresholds(
    rows: list[Row],
    *,
    threshold_lines: int | None,
    threshold_nesting: int | None,
    threshold_params: int | None,
) -> list[Row]:
    out: list[Row] = []
    for r in rows:
        if r.rule == RULE_LONG_FUNCTION and threshold_lines is not None and r.value <= threshold_lines:
            continue
        if r.rule == RULE_DEEP_NESTING and threshold_nesting is not None and r.value <= threshold_nesting:
            continue
        if r.rule == RULE_LONG_PARAMS and threshold_params is not None and r.value <= threshold_params:
            continue
        out.append(r)
    return out


def format_rows(rows: list[Row]) -> str:
    ordered = sorted(rows)
    return "\n".join(r.line() for r in ordered) + ("\n" if ordered else "")


def self_check() -> None:
    sample = '''\
def short(a, b):
    """doc"""
    return a + b

def nested(x, y=1, *args, **kwargs):
    if x:
        if x > 1:
            return 1
    return 0

def many_params(a, b, c, d, e):
    pass

def documented(a):
    """Multi-line
    docstring."""

    # comment
    return a

def outer():
    def inner():
        pass
    return inner

def one_liner(): """doc"""; x = 1

def data(a):
    text = """
# not a comment
"""
    return text + a

class C:
    def m(self, a, b=1):
        return a

def test_ternary(x):
    assert (1 if x else 2) == 1

def doc_tail(a):
    """Doc
    ends"""; tail = a
    return tail

def test_helper():
    def check(v):
        assert v > 0
        if v > 10:
            assert v < 100
    check(5)

def test_ok():
    assert 1 == 1
    expect_not_real()

def test_branch(x):
    if x:
        assert x
    return

def test_empty():
    setup()
'''
    # expect_not_real is not an assert call; only `assert` counts in test_ok → 1
    rows = measure_source("sample.py", sample)
    text = format_rows(rows)

    def val(rule: str, symbol: str) -> int:
        for r in rows:
            if r.rule == rule and r.symbol == symbol:
                return r.value
        raise AssertionError(f"missing {rule} {symbol}\n{text}")

    # def line + return line; docstring line skipped
    assert val(RULE_LONG_FUNCTION, "short") == 2, text
    assert val(RULE_DEEP_NESTING, "short") == 0, text
    assert val(RULE_LONG_PARAMS, "short") == 2, text

    # five code lines; peak depth 2; params: x, y, *args, **kwargs
    assert val(RULE_LONG_FUNCTION, "nested") == 5, text
    assert val(RULE_DEEP_NESTING, "nested") == 2, text
    assert val(RULE_LONG_PARAMS, "nested") == 4, text

    assert val(RULE_LONG_PARAMS, "many_params") == 5, text

    # docstring, blank, and comment-only lines all skipped
    assert val(RULE_LONG_FUNCTION, "documented") == 2, text

    # nested def: declaration line counts once, body excluded
    assert val(RULE_LONG_FUNCTION, "outer") == 3, text
    assert val(RULE_LONG_FUNCTION, "inner") == 2, text

    # receiver excluded, defaulted param counted
    assert val(RULE_LONG_PARAMS, "C.m") == 2, text

    # one-line def keeps its def line despite the docstring on it
    assert val(RULE_LONG_FUNCTION, "one_liner") == 1, text

    # '#'-leading and blank-looking lines inside a string are string content
    assert val(RULE_LONG_FUNCTION, "data") == 5, text

    # conditional expression gates
    assert val(RULE_GATE_NODES, "test_ternary") == 1, text
    assert val(RULE_ASSERT_SITES, "test_ternary") == 1, text

    # docstring closing line shared with a statement stays counted
    assert val(RULE_LONG_FUNCTION, "doc_tail") == 3, text

    # asserts in nested helpers count for the test; their gates do not
    assert val(RULE_ASSERT_SITES, "test_helper") == 2, text
    assert val(RULE_GATE_NODES, "test_helper") == 0, text

    assert val(RULE_ASSERT_SITES, "test_ok") == 1, text
    assert val(RULE_GATE_NODES, "test_ok") == 0, text

    assert val(RULE_ASSERT_SITES, "test_branch") == 1, text
    assert val(RULE_GATE_NODES, "test_branch") == 1, text  # if only

    assert val(RULE_ASSERT_SITES, "test_empty") == 0, text

    # determinism
    assert format_rows(rows) == format_rows(measure_source("sample.py", sample))

    # threshold filter
    filtered = apply_thresholds(rows, threshold_lines=3, threshold_nesting=None, threshold_params=4)
    fl = [r for r in filtered if r.rule == RULE_LONG_FUNCTION]
    assert all(r.value > 3 for r in fl), fl
    fp = [r for r in filtered if r.rule == RULE_LONG_PARAMS]
    assert all(r.value > 4 for r in fp), fp

    print("measure_python.py --self-check OK")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Measure Python function metrics for smell-check.")
    p.add_argument("paths", nargs="*", type=Path, help="Python files to measure")
    p.add_argument("--threshold-lines", type=int, default=None)
    p.add_argument("--threshold-nesting", type=int, default=None)
    p.add_argument("--threshold-params", type=int, default=None)
    p.add_argument("--self-check", action="store_true")
    args = p.parse_args(argv)

    if args.self_check:
        self_check()
        return 0

    if not args.paths:
        p.error("provide paths or --self-check")

    rows: list[Row] = []
    for path in args.paths:
        if not path.is_file():
            print(f"skip missing file: {path}", file=sys.stderr)
            continue
        rows.extend(measure_file(path))

    rows = apply_thresholds(
        rows,
        threshold_lines=args.threshold_lines,
        threshold_nesting=args.threshold_nesting,
        threshold_params=args.threshold_params,
    )
    sys.stdout.write(format_rows(rows))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
