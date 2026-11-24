#!/usr/bin/env python3
"""Checks the PM guide written with the mx-pm-guide skill.

  docs/pm/*.md        plain English, every rule tagged and traceable
  docs/rules/*.md     every rule has its required fields
  docs/evidence/*.md  every query has a result and a run date

Run from the repository root:

  python .github/skills/mx-pm-guide/scripts/lint_pm.py
  python .github/skills/mx-pm-guide/scripts/lint_pm.py --coverage path/to/list_fix.txt docs/rules/fix.md

Exit code 1 when there is at least one ERROR.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

RULE_ID = r"[A-Z]{2,8}-\d{3}"
QUERY_ID = r"Q-[A-Z]{2,8}-\d{3}-[a-z]"
CONFIDENCE = ("Verified", "Code only", "Inferred", "Never happens")

RULE_HEAD = re.compile(rf"^###\s+({RULE_ID})\b")
QUERY_HEAD = re.compile(rf"^#{{2,4}}\s+({QUERY_ID})\b")
ANY_HEAD = re.compile(r"^#{1,4}\s")
RULE_REF = re.compile(rf"\[\s*({RULE_ID}(?:\s*,\s*{RULE_ID})*)\s*\]")
QUERY_REF = re.compile(QUERY_ID)
CONF_TAG = re.compile(r"\[(Verified|Code only|Inferred|Never happens)\]")
NUMBERED = re.compile(r"^\s*\d+[.)]\s+")
TABLE_ROW = re.compile(r"^\s*\|")
TABLE_SEP = re.compile(r"^\s*\|?\s*:?-{3,}")
FENCE = re.compile(r"^\s*(```+|~~~+)\s*([\w-]*)")
FIELD = re.compile(r"^\s*-\s+\*\*([A-Za-z ]+):\*\*\s*(.*)$")
DATE = re.compile(r"\b20\d\d-\d\d-\d\d\b")
LINK_TARGET = re.compile(r"\]\([^)]*\)")

JARGON = [
    (re.compile(r"\b[A-Z][A-Z0-9]*_[A-Z0-9_]*[A-Z0-9]\b"),
     "technical name (record, field, role or ticket id)"),
    (re.compile(r"\.pcode\b|\b[A-Za-z_]+\\[A-Za-z_]+"), "file path"),
    (re.compile(r"\b(SavePreChange|SavePostChange|SaveEdit|FieldChange|FieldEdit|FieldDefault|FieldFormula"
                r"|RowInit|RowInsert|RowDelete|RowSelect|PreBuild|PostBuild|SearchInit|SearchSave"
                r"|OnExecute|OnRequest|OnNotify)\b"), "PeopleCode event"),
    (re.compile(r"\b(SQLExec|CreateSQL|CreateRowset|CreateRecord|GetRowset|GetLevel0|GetRow|MsgGet\w*"
                r"|MessageBox|SendMail|LongTranslateValue|IsChanged|OriginalValue)\b"), "PeopleCode function"),
    (re.compile(r"(?<![\w%])%[A-Z][A-Za-z]+"), "PeopleCode system variable"),
    (re.compile(r"\bPeopleCode\b|\browsets?\b|\bapp(?:lication)? (?:package|class)(?:es)?\b"
                r"|\bcomponent interfaces?\b|\bApplication Engine\b", re.I), "PeopleSoft technical term"),
    (re.compile(r"\b(SELECT|WHERE|JOIN|GROUP BY)\b"), "SQL"),
]
HEDGE = re.compile(r"\b(usually|typically|generally|normally|in most cases|mostly|often|rarely|sometimes)\b", re.I)
PERCENT = re.compile(r"\d\s?%")
PERSONAL_EMAIL = re.compile(r"\b[a-z]+\.[a-z]+(?:\+[\w.-]+)?@[\w.-]+\b", re.I)
CODE_SPAN = re.compile(r"`[^`]+`")
MAX_WORDS = 35


class Report:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.errors = 0
        self.warnings = 0

    def _where(self, path: Path, line: int) -> str:
        try:
            shown = path.resolve().relative_to(self.root.resolve())
        except ValueError:
            shown = path
        return f"{shown}:{line}"

    def error(self, path: Path, line: int, message: str) -> None:
        self.errors += 1
        print(f"{self._where(path, line)}: ERROR {message}")

    def warn(self, path: Path, line: int, message: str) -> None:
        self.warnings += 1
        print(f"{self._where(path, line)}: WARN  {message}")


def read(path: Path) -> str:
    raw = path.read_bytes()
    if raw.startswith((b"\xff\xfe", b"\xfe\xff")):  # UTF-16, e.g. written by PowerShell
        return raw.decode("utf-16", errors="replace")
    return raw.decode("utf-8-sig", errors="replace")


def parse_rules(path: Path, rep: Report, all_rules: dict, query_refs: list) -> None:
    lines = read(path).splitlines()
    state = {"id": None, "start": 0, "fields": {}}

    def close() -> None:
        rid, start, fields = state["id"], state["start"], state["fields"]
        if rid is None:
            return
        if fields.get("Status", (0, ""))[1].strip().lower().startswith("removed"):
            return
        missing = [f for f in ("Trigger", "Effect", "Code", "Confidence") if f not in fields]
        if missing:
            rep.error(path, start, f"{rid}: missing {', '.join(missing)}")
        if "Confidence" in fields:
            value = fields["Confidence"][1].strip()
            level = next((c for c in CONFIDENCE if value.startswith(c)), None)
            if level is None:
                rep.error(path, fields["Confidence"][0],
                          f"{rid}: Confidence must start with one of: {', '.join(CONFIDENCE)}")
            elif level in ("Verified", "Never happens"):
                data_check = fields.get("Data check", (0, ""))[1]
                if not QUERY_REF.search(data_check):
                    rep.error(path, start, f"{rid}: '{level}' needs a Data check citing a query (Q-...)")

    for number, line in enumerate(lines, 1):
        head = RULE_HEAD.match(line)
        if head or ANY_HEAD.match(line):
            close()
            state.update(id=None, start=number, fields={})
            if head:
                rid = head.group(1)
                if rid in all_rules:
                    rep.error(path, number, f"duplicate rule ID {rid} (also at {all_rules[rid]})")
                else:
                    all_rules[rid] = f"{path.name}:{number}"
                state["id"] = rid
            continue
        if state["id"]:
            field = FIELD.match(line)
            if field:
                state["fields"][field.group(1).strip()] = (number, field.group(2))
        for query in QUERY_REF.findall(line):
            query_refs.append((path, number, query))
    close()


def parse_evidence(path: Path, rep: Report, all_queries: dict) -> None:
    lines = read(path).splitlines()
    state = {"id": None, "start": 0, "body": []}

    def close() -> None:
        qid = state["id"]
        if qid is None:
            return
        body = "\n".join(state["body"])
        if "**Result:**" not in body:
            rep.warn(path, state["start"], f"{qid}: no **Result:** line")
        if not DATE.search(body):
            rep.warn(path, state["start"], f"{qid}: no run date (YYYY-MM-DD)")

    for number, line in enumerate(lines, 1):
        head = QUERY_HEAD.match(line)
        if head or ANY_HEAD.match(line):
            close()
            state.update(id=None, start=number, body=[])
            if head:
                qid = head.group(1)
                if qid in all_queries:
                    rep.error(path, number, f"duplicate query ID {qid} (also at {all_queries[qid]})")
                else:
                    all_queries[qid] = f"{path.name}:{number}"
                state["id"] = qid
            continue
        if state["id"]:
            state["body"].append(line)
    close()


def check_guide(path: Path, rep: Report, known_rules: dict) -> None:
    lines = read(path).splitlines()
    is_glossary = path.name.lower() == "glossary.md"
    in_fence = False
    for index, line in enumerate(lines):
        number = index + 1
        fence = FENCE.match(line)
        if fence:
            if not in_fence and fence.group(2).lower() != "mermaid":
                rep.error(path, number, "code block in a guide (only mermaid diagrams are allowed)")
            in_fence = not in_fence
            continue
        if in_fence or not line.strip():
            continue

        for pattern, label in JARGON:
            for hit in pattern.finditer(line):
                rep.error(path, number, f"{label}: {hit.group(0)}")
        if CODE_SPAN.search(line):
            rep.warn(path, number, "code formatting: put on-screen names in quotes instead")
        for hit in PERSONAL_EMAIL.finditer(line):
            rep.warn(path, number, f"looks like a personal email address: {hit.group(0)}")

        for ref in RULE_REF.finditer(line):
            for rid in re.findall(RULE_ID, ref.group(1)):
                if rid not in known_rules:
                    rep.error(path, number, f"rule {rid} is not in docs/rules")

        is_table = bool(TABLE_ROW.match(line))
        is_label = (line.lstrip().startswith("#") or bool(TABLE_SEP.match(line))
                    or (is_table and index + 1 < len(lines) and bool(TABLE_SEP.match(lines[index + 1]))))
        if is_label:
            continue

        hedge = HEDGE.search(line)
        if hedge and not re.search(r"\d", line):
            rep.warn(path, number, f"'{hedge.group(0)}' without a number: give the share from a query, or remove it")
        if PERCENT.search(line) and not RULE_REF.search(line):
            rep.warn(path, number, "percentage without a rule ID: cite the rule whose data check gives it")

        if NUMBERED.match(line):
            if not CONF_TAG.search(line):
                rep.error(path, number, "numbered item without a tag ([Verified], [Code only], [Inferred], "
                                        "[Never happens]) on its first line")
            if not RULE_REF.search(line):
                rep.error(path, number, "numbered item without a rule ID on its first line")

        if is_table:
            if not is_glossary and not RULE_REF.search(line):
                rep.warn(path, number, "table row without a rule ID")
            continue

        if not line.lstrip().startswith(("#", ">")):
            prose = LINK_TARGET.sub("]", line)
            for sentence in re.split(r"(?<=[.!?])\s+", prose):
                words = len(sentence.split())
                if words > MAX_WORDS:
                    rep.warn(path, number, f"sentence of {words} words: split it")


def program_of(line: str) -> str:
    tokens = line.split()
    return next((t for t in tokens if t.lower().endswith(".pcode")), tokens[0])


def normalise(text: str) -> str:
    return text.replace("/", "\\").lower()


def check_coverage(list_path: Path, rules_path: Path, rep: Report) -> None:
    if not list_path.is_file() or not rules_path.is_file():
        rep.error(list_path, 0, f"coverage: file not found ({list_path} or {rules_path})")
        return
    rules_text = normalise(read(rules_path))
    for number, line in enumerate(read(list_path).splitlines(), 1):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        program = program_of(line.strip())
        if normalise(program) not in rules_text:
            rep.error(list_path, number, f"not in the coverage table of {rules_path.name}: {program}")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(errors="replace")
    parser = argparse.ArgumentParser(description="Lint the PM guide, rules and evidence files.")
    parser.add_argument("--docs", default="docs", help="docs folder (default: docs)")
    parser.add_argument("--coverage", nargs=2, action="append", default=[],
                        metavar=("PROGRAM_LIST", "RULES_FILE"),
                        help="check every program of the list appears in the rules file (repeatable)")
    args = parser.parse_args()

    docs = Path(args.docs)
    if not docs.is_dir():
        print(f"No '{docs}' folder (run from the repository root, or pass --docs).")
        return 2
    rep = Report(Path.cwd())

    all_rules: dict = {}
    query_refs: list = []
    all_queries: dict = {}
    for path in sorted((docs / "rules").glob("*.md")):
        parse_rules(path, rep, all_rules, query_refs)
    for path in sorted((docs / "evidence").glob("*.md")):
        parse_evidence(path, rep, all_queries)
    for path, number, query in query_refs:
        if query not in all_queries:
            rep.error(path, number, f"query {query} is not in docs/evidence")
    for path in sorted((docs / "pm").glob("*.md")):
        check_guide(path, rep, all_rules)
    for list_name, rules_name in args.coverage:
        check_coverage(Path(list_name), Path(rules_name), rep)

    print(f"\n{len(all_rules)} rules, {len(all_queries)} queries: "
          f"{rep.errors} error(s), {rep.warnings} warning(s)")
    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
