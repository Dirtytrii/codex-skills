#!/usr/bin/env python3
"""Audit the context cost and invocation policy of the skill catalog."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skill_catalog import SkillRecord, discover_skills


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
DESCRIPTION_LIMIT = 360
CATALOG_HARD_LIMIT = 20_000
CATALOG_SOFT_TARGET = 8_000


def requires_explicit_invocation(record: SkillRecord) -> bool:
    text = record.description.lower()
    return (
        "not a user-facing skill" in text
        or "internal sub-agent" in text
        or "compatibility adapter" in text
    )


def audit(records: list[SkillRecord]) -> tuple[dict[str, object], list[str]]:
    top_level = [record for record in records if record.top_level]
    nested = [record for record in records if not record.top_level]
    explicit_only = [record for record in records if record.allow_implicit_invocation is False]
    errors: list[str] = []

    for record in records:
        if len(record.description) > DESCRIPTION_LIMIT:
            errors.append(
                f"{record.relative_path}: description has {len(record.description)} chars; "
                f"limit is {DESCRIPTION_LIMIT}"
            )
        if requires_explicit_invocation(record) and record.allow_implicit_invocation is not False:
            errors.append(
                f"{record.relative_path}: internal or compatibility skill must set "
                "allow_implicit_invocation: false"
            )

    catalog_chars = sum(record.catalog_chars for record in records)
    if catalog_chars > CATALOG_HARD_LIMIT:
        errors.append(
            f"catalog estimate is {catalog_chars} chars; hard limit is {CATALOG_HARD_LIMIT}"
        )

    report: dict[str, object] = {
        "skill_count": len(records),
        "top_level_count": len(top_level),
        "nested_count": len(nested),
        "description_chars": sum(len(record.description) for record in records),
        "catalog_chars": catalog_chars,
        "catalog_hard_limit": CATALOG_HARD_LIMIT,
        "catalog_soft_target": CATALOG_SOFT_TARGET,
        "agents_file_count": sum(record.agents_file.is_file() for record in records),
        "explicit_only_count": len(explicit_only),
        "largest_descriptions": [
            {
                "name": record.name,
                "chars": len(record.description),
                "path": record.relative_path.as_posix(),
            }
            for record in sorted(records, key=lambda item: len(item.description), reverse=True)[:10]
        ],
    }
    return report, errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    parser.add_argument("--strict", action="store_true", help="Fail when hard checks fail")
    args = parser.parse_args()

    try:
        records = discover_skills(SKILLS)
        report, errors = audit(records)
    except Exception as exc:  # noqa: BLE001
        print(f"Skill catalog audit failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps({**report, "errors": errors}, ensure_ascii=False, indent=2))
    else:
        print(
            "Skill catalog: "
            f"{report['skill_count']} total "
            f"({report['top_level_count']} public, {report['nested_count']} nested), "
            f"{report['catalog_chars']}/{report['catalog_hard_limit']} estimated chars."
        )
        if report["catalog_chars"] > report["catalog_soft_target"]:
            print(
                "Advisory: catalog remains above the 8,000-char progressive-disclosure "
                "target; consolidate large skill families before enforcing that target."
            )
        for error in errors:
            print(f"- {error}")

    return 1 if args.strict and errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
