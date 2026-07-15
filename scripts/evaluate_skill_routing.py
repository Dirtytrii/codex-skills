#!/usr/bin/env python3
"""Validate routing eval cases and score observed skill selections."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from skill_catalog import discover_skills


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CASES = ROOT / "evals" / "skill-routing-cases.jsonl"
SKILLS = ROOT / "skills"
LIST_FIELDS = ("required_skills", "allowed_skills", "forbidden_skills")


def load_jsonl(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    for line_number, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            value = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_number}: invalid JSON: {exc}") from exc
        if not isinstance(value, dict):
            raise ValueError(f"{path}:{line_number}: record must be an object")
        records.append(value)
    return records


def validate_cases(cases: list[dict[str, object]], known_skills: set[str]) -> list[str]:
    errors: list[str] = []
    seen: set[str] = set()
    for index, case in enumerate(cases, 1):
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"case {index}: id must be a non-empty string")
            continue
        if case_id in seen:
            errors.append(f"case {case_id}: duplicate id")
        seen.add(case_id)
        if not isinstance(case.get("prompt"), str) or not str(case.get("prompt")).strip():
            errors.append(f"case {case_id}: prompt must be a non-empty string")

        groups: dict[str, set[str]] = {}
        for field in LIST_FIELDS:
            value = case.get(field, [])
            if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
                errors.append(f"case {case_id}: {field} must be a string list")
                groups[field] = set()
                continue
            groups[field] = set(value)
            unknown = groups[field] - known_skills
            if unknown:
                errors.append(f"case {case_id}: {field} contains unknown skills {sorted(unknown)}")

        if groups.get("required_skills", set()) & groups.get("forbidden_skills", set()):
            errors.append(f"case {case_id}: required and forbidden skills overlap")
        if groups.get("allowed_skills", set()) & groups.get("forbidden_skills", set()):
            errors.append(f"case {case_id}: allowed and forbidden skills overlap")
    return errors


def score(
    cases: list[dict[str, object]], observations: list[dict[str, object]]
) -> dict[str, object]:
    observed_by_id: dict[str, set[str]] = {}
    observation_errors: list[str] = []
    for item in observations:
        case_id = item.get("id")
        selected = item.get("selected_skills")
        if not isinstance(case_id, str) or not isinstance(selected, list) or not all(
            isinstance(skill, str) for skill in selected
        ):
            observation_errors.append("observations require string id and selected_skills list")
            continue
        if case_id in observed_by_id:
            observation_errors.append(f"duplicate observation id {case_id}")
            continue
        observed_by_id[case_id] = set(selected)

    results: list[dict[str, object]] = []
    required_total = 0
    required_selected = 0
    for case in cases:
        case_id = str(case["id"])
        if case_id not in observed_by_id:
            continue
        selected = observed_by_id[case_id]
        required = set(case.get("required_skills", []))
        allowed = set(case.get("allowed_skills", []))
        forbidden = set(case.get("forbidden_skills", []))
        missing = required - selected
        forbidden_selected = forbidden & selected
        unexpected = selected - required - allowed
        required_total += len(required)
        required_selected += len(required & selected)
        results.append(
            {
                "id": case_id,
                "passed": not missing and not forbidden_selected and not unexpected,
                "selected_skills": sorted(selected),
                "missing_required_skills": sorted(missing),
                "forbidden_selected_skills": sorted(forbidden_selected),
                "unexpected_skills": sorted(unexpected),
            }
        )

    evaluated = len(results)
    passed = sum(bool(item["passed"]) for item in results)
    return {
        "case_count": len(cases),
        "evaluated_case_count": evaluated,
        "unevaluated_case_count": len(cases) - evaluated,
        "passed_case_count": passed,
        "case_pass_rate": None if evaluated == 0 else round(passed / evaluated, 4),
        "required_skill_recall": (
            None if required_total == 0 else round(required_selected / required_total, 4)
        ),
        "observation_errors": observation_errors,
        "results": results,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cases", type=Path, default=DEFAULT_CASES)
    parser.add_argument("--observed", type=Path)
    parser.add_argument("--validate-only", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    try:
        cases = load_jsonl(args.cases)
        known_skills = {record.name for record in discover_skills(SKILLS)}
        errors = validate_cases(cases, known_skills)
    except Exception as exc:  # noqa: BLE001
        print(f"Skill routing evaluation failed: {exc}", file=sys.stderr)
        return 1

    if errors:
        print(json.dumps({"case_count": len(cases), "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    if args.validate_only or not args.observed:
        print(
            json.dumps(
                {
                    "case_count": len(cases),
                    "status": "valid",
                    "note": "Provide --observed to score actual routing decisions.",
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    try:
        payload = score(cases, load_jsonl(args.observed))
    except Exception as exc:  # noqa: BLE001
        print(f"Skill routing evaluation failed: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    failed = bool(payload["observation_errors"]) or payload["unevaluated_case_count"] > 0
    failed = failed or payload["passed_case_count"] != payload["evaluated_case_count"]
    return 1 if args.strict and failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
