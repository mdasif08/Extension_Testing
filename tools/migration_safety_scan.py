#!/usr/bin/env python3
"""Generic migration safety scanner.

Scans SQL migration files for destructive schema operations and writes a
machine-readable evidence file. It is intentionally simple so it can be used as
a portable test fixture in any repository.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class Rule:
    rule_id: str
    title: str
    severity: str
    pattern: re.Pattern[str]
    safe_alternative: str


@dataclass(frozen=True)
class Finding:
    rule_id: str
    title: str
    severity: str
    file: str
    line: int
    matched_text: str
    safe_alternative: str


RULES: tuple[Rule, ...] = (
    Rule(
        rule_id="DB-MIGRATION-DROP-COLUMN",
        title="Direct column drop detected",
        severity="error",
        pattern=re.compile(r"\balter\s+table\b[\s\S]*?\bdrop\s+column\b", re.IGNORECASE),
        safe_alternative="Use a phased backward-compatible rollout and remove the column only after all running application versions stop reading it.",
    ),
    Rule(
        rule_id="DB-MIGRATION-RENAME-COLUMN",
        title="Direct column rename detected",
        severity="error",
        pattern=re.compile(r"\balter\s+table\b[\s\S]*?\brename\s+column\b", re.IGNORECASE),
        safe_alternative="Add the new column, dual-write or backfill data, switch readers, then remove the old column in a later release.",
    ),
    Rule(
        rule_id="DB-MIGRATION-DROP-TABLE",
        title="Direct table drop detected",
        severity="error",
        pattern=re.compile(r"\bdrop\s+table\b", re.IGNORECASE),
        safe_alternative="Stop writes and reads first, preserve or archive data if required, then drop the table in a later controlled release.",
    ),
)


def iter_sql_files(root: Path) -> Iterable[Path]:
    if root.is_file() and root.suffix.lower() == ".sql":
        yield root
        return
    for path in sorted(root.rglob("*.sql")):
        if path.is_file():
            yield path


def line_number_for_match(text: str, start_index: int) -> int:
    return text.count("\n", 0, start_index) + 1


def normalize_match(value: str) -> str:
    return " ".join(value.strip().split())[:180]


def scan_file(path: Path, base_dir: Path) -> list[Finding]:
    text = path.read_text(encoding="utf-8")
    findings: list[Finding] = []
    for rule in RULES:
        for match in rule.pattern.finditer(text):
            findings.append(
                Finding(
                    rule_id=rule.rule_id,
                    title=rule.title,
                    severity=rule.severity,
                    file=str(path.relative_to(base_dir.parent if base_dir.is_dir() else path.parent)),
                    line=line_number_for_match(text, match.start()),
                    matched_text=normalize_match(match.group(0)),
                    safe_alternative=rule.safe_alternative,
                )
            )
    return findings


def build_evidence(root: Path, findings: list[Finding]) -> dict:
    failed = any(f.severity == "error" for f in findings)
    return {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scanner": {
            "name": "migration_safety_scan",
            "version": "1.0.0",
        },
        "signal": {
            "category": "database_migration_safety",
            "status": "failed" if failed else "passed",
            "requires_human_review": failed,
            "release_gate_recommended_action": "block" if failed else "allow",
        },
        "input": {
            "path": str(root),
            "file_glob": "**/*.sql",
        },
        "summary": {
            "total_findings": len(findings),
            "error_findings": sum(1 for f in findings if f.severity == "error"),
        },
        "findings": [asdict(f) for f in findings],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan SQL migrations for destructive schema operations.")
    parser.add_argument("path", type=Path, help="SQL file or directory containing SQL migration files")
    parser.add_argument(
        "--evidence-file",
        type=Path,
        default=Path("migration-safety-evidence.json"),
        help="Path to write JSON evidence output",
    )
    args = parser.parse_args()

    if not args.path.exists():
        print(f"Migration path not found: {args.path}", file=sys.stderr)
        return 2

    sql_files = list(iter_sql_files(args.path))
    if not sql_files:
        evidence = build_evidence(args.path, [])
        try:
            args.evidence_file.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
        except FileNotFoundError:
            # Do not create missing directories or files; continue without writing evidence
            pass
        print("No SQL migration files found.")
        return 0
    findings: list[Finding] = []
    for sql_file in sql_files:
        findings.extend(scan_file(sql_file, args.path))

    evidence = build_evidence(args.path, findings)
    try:
        args.evidence_file.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    except FileNotFoundError:
        # Do not create missing directories or files; continue without writing evidence
        pass

    if findings:
        print(f"Migration safety scan failed: {len(findings)} finding(s).")
        for finding in findings:
            print(f"- {finding.severity.upper()} {finding.file}:{finding.line} {finding.title}")
        try:
            # Only report the evidence path if writing succeeded
            if args.evidence_file.exists():
                print(f"Evidence written to: {args.evidence_file}")
        except Exception:
            pass
        return 1

    print("Migration safety scan passed: no destructive operations detected.")
    try:
        if args.evidence_file.exists():
            print(f"Evidence written to: {args.evidence_file}")
    except Exception:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
