#!/usr/bin/env node
/**
 * Deterministic TS/JS metrics for smell-check.
 * Zero own dependencies; loads `typescript` from the subject repo via createRequire.
 */
import { createRequire } from "node:module";
import fs from "node:fs";
import path from "node:path";
import process from "node:process";

const RULE_LONG_FUNCTION = "code.long-function";
const RULE_DEEP_NESTING = "code.deep-nesting";
const RULE_LONG_PARAMS = "code.long-parameter-list";
const RULE_ASSERT_SITES = "test.assertion-sites";
const RULE_GATE_NODES = "test.gate-nodes";

function loadTypescript(root) {
  const resolveFrom = path.join(root, "package.json");
  const base = fs.existsSync(resolveFrom) ? resolveFrom : path.join(root, "index.js");
  const require = createRequire(base);
  try {
    return require("typescript");
  } catch {
    try {
      return require(path.join(root, "node_modules", "typescript"));
    } catch {
      return null;
    }
  }
}

function row(rule, location, symbol, value) {
  return { rule, location, symbol, value };
}

function formatRows(rows) {
  const ordered = [...rows].sort((a, b) => {
    if (a.rule !== b.rule) return a.rule < b.rule ? -1 : 1;
    if (a.location !== b.location) return a.location < b.location ? -1 : 1;
    if (a.symbol !== b.symbol) return a.symbol < b.symbol ? -1 : 1;
    return a.value - b.value;
  });
  return ordered.map((r) => `${r.rule}\t${r.location}\t${r.symbol}\t${r.value}`).join("\n") + (ordered.length ? "\n" : "");
}

function isTestName(name) {
  return typeof name === "string" && /^test/i.test(name);
}

function measureWithTs(ts, filePath, source) {
  const kind = ts.ScriptKind.TS;
  const sf = ts.createSourceFile(filePath, source, ts.ScriptTarget.Latest, true, kind);
  const rows = [];

  // Declaration start with decorators skipped (they are not part of the count).
  function declStartPos(node) {
    const decs = ts.canHaveDecorators && ts.canHaveDecorators(node) ? ts.getDecorators(node) || [] : [];
    let pos = node.getStart(sf);
    for (const d of decs) pos = Math.max(pos, d.getEnd());
    if (pos !== node.getStart(sf)) {
      const rest = source.slice(pos);
      pos += rest.length - rest.trimStart().length;
    }
    return pos;
  }

  function loc(node) {
    const { line } = sf.getLineAndCharacterOfPosition(declStartPos(node));
    return `${filePath.replace(/\\/g, "/")}:${line + 1}`;
  }

  function isFunctionLike(node) {
    return (
      ts.isFunctionDeclaration(node) ||
      ts.isFunctionExpression(node) ||
      ts.isArrowFunction(node) ||
      ts.isMethodDeclaration(node) ||
      ts.isConstructorDeclaration(node) ||
      ts.isGetAccessorDeclaration(node) ||
      ts.isSetAccessorDeclaration(node)
    );
  }

  function fnName(node, fallback) {
    if (node.name && ts.isIdentifier(node.name)) return node.name.text;
    if (ts.isConstructorDeclaration(node)) return "constructor";
    return fallback || "<anonymous>";
  }

  function declaredParams(node) {
    // Every declared value parameter counts once (optional, defaulted, rest,
    // destructured); the explicit `this` receiver does not.
    let n = 0;
    for (const p of node.parameters || []) {
      if (p.name && ts.isIdentifier(p.name) && p.name.text === "this") continue;
      n += 1;
    }
    return n;
  }

  function bodyStatements(node) {
    if (!node.body) return [];
    if (ts.isBlock(node.body)) return [...node.body.statements];
    // expression-bodied arrow: one expression statement worth of logic
    return null; // sentinel: expression body
  }

  const sourceLines = source.split(/\r?\n/);

  // Lines carrying at least one real token (comments and blanks are trivia).
  const codeLines = (() => {
    const scanner = ts.createScanner(ts.ScriptTarget.Latest, true, ts.LanguageVariant.Standard, source);
    const lines = new Set();
    let kind = scanner.scan();
    while (kind !== ts.SyntaxKind.EndOfFileToken) {
      const start = typeof scanner.getTokenStart === "function" ? scanner.getTokenStart() : scanner.getTokenPos();
      const end = Math.max(start, scanner.getTextPos() - 1);
      const s = sf.getLineAndCharacterOfPosition(start).line + 1;
      const e = sf.getLineAndCharacterOfPosition(end).line + 1;
      for (let l = s; l <= e; l++) lines.add(l);
      kind = scanner.scan();
    }
    return lines;
  })();

  function lineOf(pos) {
    return sf.getLineAndCharacterOfPosition(pos).line + 1;
  }

  // Every measured function is a "unit". The same set drives emission and
  // exclusion, so no function can disappear from both sides.
  const unitNodes = new Set();

  // Units and classes directly inside node's body (not inside a deeper unit).
  // Non-unit functions (expression-bodied callbacks) are transparent.
  function directExcluded(node) {
    const found = [];
    function walk(n) {
      ts.forEachChild(n, (child) => {
        if (unitNodes.has(child) || ts.isClassDeclaration(child) || ts.isClassExpression(child)) {
          found.push(child);
          return;
        }
        walk(child);
      });
    }
    if (node.body) walk(node.body);
    return found;
  }

  // Non-blank, non-comment lines from the declaration through the body.
  // Nested unit/class bodies are excluded; each nested declaration
  // still counts as one line of this function.
  function countNloc(node) {
    const counted = new Set();
    for (let l = lineOf(declStartPos(node)); l <= lineOf(node.getEnd()); l++) counted.add(l);
    for (const nested of directExcluded(node)) {
      for (let l = lineOf(nested.getStart(sf)); l <= lineOf(nested.getEnd()); l++) counted.delete(l);
      counted.add(lineOf(declStartPos(nested)));
    }
    let nloc = 0;
    for (const l of counted) {
      if (codeLines.has(l) && (sourceLines[l - 1] || "").trim() !== "") nloc += 1;
    }
    return nloc;
  }

  function maxNestInStatements(stmts, depth) {
    let peak = depth;
    for (const s of stmts) peak = Math.max(peak, maxNestInStmt(s, depth));
    return peak;
  }

  function maxNestInStmt(stmt, depth) {
    if (isFunctionLike(stmt) || ts.isClassDeclaration(stmt)) return depth;

    if (ts.isIfStatement(stmt)) {
      const d = depth + 1;
      let peak = d;
      peak = Math.max(peak, maxNestInNode(stmt.thenStatement, d));
      let cur = stmt.elseStatement;
      while (cur) {
        if (ts.isIfStatement(cur)) {
          peak = Math.max(peak, d);
          peak = Math.max(peak, maxNestInNode(cur.thenStatement, d));
          cur = cur.elseStatement;
        } else {
          peak = Math.max(peak, maxNestInNode(cur, d));
          break;
        }
      }
      return peak;
    }
    if (
      ts.isForStatement(stmt) ||
      ts.isForInStatement(stmt) ||
      ts.isForOfStatement(stmt) ||
      ts.isWhileStatement(stmt) ||
      ts.isDoStatement(stmt)
    ) {
      const d = depth + 1;
      return Math.max(d, maxNestInNode(stmt.statement, d));
    }
    if (ts.isTryStatement(stmt)) {
      const d = depth + 1;
      let peak = d;
      peak = Math.max(peak, maxNestInNode(stmt.tryBlock, d));
      if (stmt.catchClause) peak = Math.max(peak, maxNestInNode(stmt.catchClause.block, d));
      if (stmt.finallyBlock) peak = Math.max(peak, maxNestInNode(stmt.finallyBlock, d));
      return peak;
    }
    if (ts.isSwitchStatement(stmt)) {
      const d = depth + 1;
      let peak = d;
      for (const clause of stmt.caseBlock.clauses) {
        peak = Math.max(peak, maxNestInStatements(clause.statements, d));
      }
      return peak;
    }
    if (ts.isBlock(stmt)) return maxNestInStatements(stmt.statements, depth);
    if (ts.isLabeledStatement(stmt)) return maxNestInStmt(stmt.statement, depth);
    return depth;
  }

  function maxNestInNode(node, depth) {
    if (!node) return depth;
    if (ts.isBlock(node)) return maxNestInStatements(node.statements, depth);
    if (ts.isStatement(node)) return maxNestInStmt(node, depth);
    return depth;
  }

  function isAssertCall(call) {
    if (!ts.isCallExpression(call)) return false;
    const expr = call.expression;
    // expect(x).toBe(y) / expect(x).toHaveBeenCalled() — count matcher call once
    if (ts.isPropertyAccessExpression(expr) && ts.isCallExpression(expr.expression)) {
      const inner = expr.expression.expression;
      if (ts.isIdentifier(inner) && (inner.text === "expect" || inner.text === "assert")) return true;
    }
    // assert.equal(a, b) / assert.strictEqual
    if (
      ts.isPropertyAccessExpression(expr) &&
      ts.isIdentifier(expr.expression) &&
      expr.expression.text === "assert"
    ) {
      return true;
    }
    // bare assert(value)
    if (ts.isIdentifier(expr) && expr.text === "assert") return true;
    return false;
  }

  function countAssertsAndGates(fnNode) {
    let asserts = 0;
    let gates = 0;
    const body = fnNode.body;
    if (!body) return { asserts, gates };

    // Assertion sites anywhere inside the test body count toward the test,
    // including inside nested callbacks and helpers. Gates stop counting past
    // a statement-bodied function boundary (those bodies are excluded).
    function walk(node, countGates) {
      if (!node) return;
      let gatesHere = countGates;
      if (node !== fnNode && isFunctionLike(node) && node.body && ts.isBlock(node.body)) {
        gatesHere = false;
      }
      if (ts.isCallExpression(node) && isAssertCall(node)) asserts += 1;
      if (
        gatesHere &&
        node !== fnNode &&
        (ts.isIfStatement(node) ||
          ts.isForStatement(node) ||
          ts.isForInStatement(node) ||
          ts.isForOfStatement(node) ||
          ts.isWhileStatement(node) ||
          ts.isDoStatement(node) ||
          ts.isSwitchStatement(node) ||
          ts.isConditionalExpression(node))
      ) {
        gates += 1;
      }
      ts.forEachChild(node, (child) => walk(child, gatesHere));
    }

    if (ts.isBlock(body)) {
      for (const s of body.statements) walk(s, true);
    } else {
      walk(body, true);
    }
    return { asserts, gates };
  }

  function emitFunction(node, symbol) {
    const location = loc(node);
    const stmts = bodyStatements(node);
    const logic = countNloc(node);
    const nest = stmts === null ? 0 : maxNestInStatements(stmts, 0);
    const params = declaredParams(node);
    rows.push(row(RULE_LONG_FUNCTION, location, symbol, logic));
    rows.push(row(RULE_DEEP_NESTING, location, symbol, nest));
    rows.push(row(RULE_LONG_PARAMS, location, symbol, params));

    if (isTestName(symbol.split(".").pop())) {
      const { asserts, gates } = countAssertsAndGates(node);
      rows.push(row(RULE_ASSERT_SITES, location, symbol, asserts));
      rows.push(row(RULE_GATE_NODES, location, symbol, gates));
    }
  }

  // Pass 1: collect measured units. Named forms register first; any other
  // statement-bodied function still registers as <anonymous>, so the unit
  // set and the NLOC exclusion set are the same set.
  const units = [];
  function addUnit(node, symbol) {
    if (unitNodes.has(node)) return;
    unitNodes.add(node);
    units.push({ node, symbol });
  }

  function collect(node, className) {
    if (ts.isFunctionDeclaration(node) && node.body) {
      addUnit(node, fnName(node, "<function>"));
    } else if (ts.isMethodDeclaration(node) && node.body) {
      const name = fnName(node, "<method>");
      addUnit(node, className ? `${className}.${name}` : name);
    } else if (ts.isConstructorDeclaration(node) && node.body) {
      addUnit(node, className ? `${className}.constructor` : "constructor");
    } else if ((ts.isGetAccessorDeclaration(node) || ts.isSetAccessorDeclaration(node)) && node.body) {
      const name = fnName(node, "<accessor>");
      addUnit(node, className ? `${className}.${name}` : name);
    } else if (ts.isVariableStatement(node)) {
      for (const d of node.declarationList.declarations) {
        if (d.initializer && (ts.isArrowFunction(d.initializer) || ts.isFunctionExpression(d.initializer))) {
          const name = ts.isIdentifier(d.name) ? d.name.text : "<anonymous>";
          addUnit(d.initializer, name);
        }
      }
    } else if (
      (ts.isPropertyAssignment(node) || ts.isPropertyDeclaration(node)) &&
      node.initializer &&
      (ts.isArrowFunction(node.initializer) || ts.isFunctionExpression(node.initializer))
    ) {
      const name = node.name && ts.isIdentifier(node.name) ? node.name.text : "<anonymous>";
      addUnit(node.initializer, name);
    }

    // it('…', () => {}) / test('…', () => {})
    if (ts.isCallExpression(node) && ts.isIdentifier(node.expression)) {
      const cal = node.expression.text;
      if ((cal === "it" || cal === "test" || cal === "xit" || cal === "xtest") && node.arguments.length >= 2) {
        const fnArg = node.arguments[1];
        if (ts.isArrowFunction(fnArg) || ts.isFunctionExpression(fnArg)) {
          const title = node.arguments[0];
          let label = cal;
          if (ts.isStringLiteral(title) || ts.isNoSubstitutionTemplateLiteral(title)) {
            label = `${cal}:${title.text}`;
          }
          addUnit(fnArg, `test:${label}`);
        }
      }
    }

    // any remaining statement-bodied function (inline block callback)
    if (isFunctionLike(node) && node.body && ts.isBlock(node.body)) {
      addUnit(node, "<anonymous>");
    }

    let nextClass = className;
    if (ts.isClassDeclaration(node) && node.name) nextClass = node.name.text;
    ts.forEachChild(node, (child) => collect(child, nextClass));
  }

  collect(sf, null);
  // Pass 2: measure once the unit set is complete (NLOC exclusion needs it).
  for (const u of units) emitFunction(u.node, u.symbol);
  return rows;
}

function applyThresholds(rows, { thresholdLines, thresholdNesting, thresholdParams }) {
  return rows.filter((r) => {
    if (r.rule === RULE_LONG_FUNCTION && thresholdLines != null && r.value <= thresholdLines) return false;
    if (r.rule === RULE_DEEP_NESTING && thresholdNesting != null && r.value <= thresholdNesting) return false;
    if (r.rule === RULE_LONG_PARAMS && thresholdParams != null && r.value <= thresholdParams) return false;
    return true;
  });
}

function selfCheck(ts) {
  const sample = `
export function short(a: number, b: number): number {
  return a + b;
}

export function nested(x: number, y = 1, ...rest: number[]): number {
  if (x) {
    if (x > 1) {
      return 1;
    }
  }
  return 0;
}

export function manyParams(a: number, b: number, c: number, d: number, e: number): void {}

export function opts(a: number, b?: string, c = 1): void {}

export function outer(): number {
  // helper
  function inner(): number {
    return 2;
  }

  return inner();
}

export function withCallback(items: number[]): number[] {
  return items.map((x) => {
    if (x > 1) {
      return x * 2;
    }
    return x;
  });
}

export function inline(items: number[]): number[] {
  return items.map((x) => x * 2);
}

export class Box {
  private v = 1;
  @dec()
  get value(): number {
    return this.v;
  }
}

export const helper = (n: number): number => n + 1;

export function test_each(items: number[]): void {
  items.forEach((i) => expect(i).toBe(1));
}

export function test_block(items: number[]): void {
  items.forEach((i) => {
    expect(i).toBe(1);
  });
}

export function test_ternary(x: number): void {
  expect(x ? 1 : 2).toBe(1);
}

export function test_ok(): void {
  expect(1).toBe(1);
}

export function test_branch(x: number): void {
  if (x) {
    expect(x).toBeTruthy();
  }
  return;
}

export function test_empty(): void {
  setup();
}
`;
  const rows = measureWithTs(ts, "sample.ts", sample);
  const text = formatRows(rows);
  const val = (rule, symbol) => {
    const hit = rows.find((r) => r.rule === rule && r.symbol === symbol);
    if (!hit) throw new Error(`missing ${rule} ${symbol}\n${text}`);
    return hit.value;
  };

  if (val(RULE_LONG_FUNCTION, "short") !== 3) throw new Error(`short nloc\n${text}`);
  if (val(RULE_DEEP_NESTING, "short") !== 0) throw new Error(`short nest\n${text}`);
  if (val(RULE_LONG_PARAMS, "short") !== 2) throw new Error(`short params\n${text}`);

  if (val(RULE_LONG_FUNCTION, "nested") !== 8) throw new Error(`nested nloc\n${text}`);
  if (val(RULE_DEEP_NESTING, "nested") !== 2) throw new Error(`nested depth\n${text}`);
  if (val(RULE_LONG_PARAMS, "nested") !== 3) throw new Error(`nested params\n${text}`);

  if (val(RULE_LONG_FUNCTION, "manyParams") !== 1) throw new Error(`manyParams nloc\n${text}`);
  if (val(RULE_LONG_PARAMS, "manyParams") !== 5) throw new Error(`many params\n${text}`);

  // optional and defaulted parameters count
  if (val(RULE_LONG_PARAMS, "opts") !== 3) throw new Error(`opts params\n${text}`);

  // comment and blank lines skipped; nested body excluded, its declaration counts once
  if (val(RULE_LONG_FUNCTION, "outer") !== 4) throw new Error(`outer nloc\n${text}`);
  if (val(RULE_LONG_FUNCTION, "inner") !== 3) throw new Error(`inner nloc\n${text}`);

  // block-bodied callback is its own <anonymous> unit, excluded from the outer count
  if (val(RULE_LONG_FUNCTION, "withCallback") !== 3) throw new Error(`withCallback nloc\n${text}`);
  if (val(RULE_LONG_FUNCTION, "<anonymous>") !== 6) throw new Error(`anonymous nloc\n${text}`);
  if (val(RULE_DEEP_NESTING, "<anonymous>") !== 1) throw new Error(`anonymous nest\n${text}`);

  // expression-bodied callback counts inline
  if (val(RULE_LONG_FUNCTION, "inline") !== 3) throw new Error(`inline nloc\n${text}`);

  // accessor is measured; decorator line excluded
  if (val(RULE_LONG_FUNCTION, "Box.value") !== 3) throw new Error(`Box.value nloc\n${text}`);

  // named expression-bodied arrow is a measured unit
  if (val(RULE_LONG_FUNCTION, "helper") !== 1) throw new Error(`helper nloc\n${text}`);

  // asserts inside expression-bodied callbacks still count for the test
  if (val(RULE_ASSERT_SITES, "test_each") !== 1) throw new Error(`test_each asserts\n${text}`);
  if (val(RULE_GATE_NODES, "test_each") !== 0) throw new Error(`test_each gates\n${text}`);

  // asserts inside block-bodied callbacks also count for the test
  if (val(RULE_ASSERT_SITES, "test_block") !== 1) throw new Error(`test_block asserts\n${text}`);
  if (val(RULE_GATE_NODES, "test_block") !== 0) throw new Error(`test_block gates\n${text}`);

  // conditional expression gates
  if (val(RULE_ASSERT_SITES, "test_ternary") !== 1) throw new Error(`test_ternary asserts\n${text}`);
  if (val(RULE_GATE_NODES, "test_ternary") !== 1) throw new Error(`test_ternary gates\n${text}`);

  if (val(RULE_ASSERT_SITES, "test_ok") !== 1) throw new Error(`test_ok asserts\n${text}`);
  if (val(RULE_GATE_NODES, "test_ok") !== 0) throw new Error(`test_ok gates\n${text}`);

  if (val(RULE_ASSERT_SITES, "test_branch") !== 1) throw new Error(`test_branch asserts\n${text}`);
  if (val(RULE_GATE_NODES, "test_branch") !== 1) throw new Error(`test_branch gates\n${text}`);

  if (val(RULE_ASSERT_SITES, "test_empty") !== 0) throw new Error(`test_empty asserts\n${text}`);

  if (formatRows(rows) !== formatRows(measureWithTs(ts, "sample.ts", sample))) {
    throw new Error("non-deterministic output");
  }

  console.log("measure_ts.mjs --self-check OK");
}

function parseArgs(argv) {
  const out = {
    selfCheck: false,
    root: process.cwd(),
    paths: [],
    thresholdLines: null,
    thresholdNesting: null,
    thresholdParams: null,
  };
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === "--self-check") out.selfCheck = true;
    else if (a === "--root") out.root = path.resolve(argv[++i]);
    else if (a === "--threshold-lines") out.thresholdLines = Number(argv[++i]);
    else if (a === "--threshold-nesting") out.thresholdNesting = Number(argv[++i]);
    else if (a === "--threshold-params") out.thresholdParams = Number(argv[++i]);
    else if (a.startsWith("-")) {
      console.error(`unknown flag: ${a}`);
      process.exit(2);
    } else out.paths.push(path.resolve(a));
  }
  return out;
}

function main() {
  const args = parseArgs(process.argv.slice(2));
  const ts = loadTypescript(args.root);

  if (args.selfCheck) {
    if (!ts) {
      // try loading typescript from this script's journey: NODE_PATH or nearby
      const alt = loadTypescript(process.cwd());
      if (!alt) {
        console.error(
          "measure_ts.mjs: cannot load `typescript` from subject repo (node_modules/typescript). Install it in the measured project or set --root.",
        );
        process.exit(2);
      }
      selfCheck(alt);
      return;
    }
    selfCheck(ts);
    return;
  }

  if (!ts) {
    console.error(
      `measure_ts.mjs: typescript package not found under ${args.root} (looked at node_modules/typescript). Degrade to LLM estimate; do not invent mechanical numbers.`,
    );
    process.exit(2);
  }

  if (!args.paths.length) {
    console.error("provide file paths or --self-check");
    process.exit(2);
  }

  let rows = [];
  for (const file of args.paths) {
    if (!fs.existsSync(file)) {
      console.error(`skip missing file: ${file}`);
      continue;
    }
    const source = fs.readFileSync(file, "utf8");
    const rel = path.relative(args.root, file) || file;
    rows = rows.concat(measureWithTs(ts, rel.replace(/\\/g, "/"), source));
  }
  rows = applyThresholds(rows, {
    thresholdLines: args.thresholdLines,
    thresholdNesting: args.thresholdNesting,
    thresholdParams: args.thresholdParams,
  });
  process.stdout.write(formatRows(rows));
}

main();
