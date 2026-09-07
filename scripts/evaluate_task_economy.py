#!/usr/bin/env python3
"""Compare paired observed workflows without inventing prices or billing savings."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def evaluate(records: list[dict]) -> dict:
    pairs: dict[tuple[str, str], dict[str, dict]] = {}
    for row in records:
        for field in ("case_id", "contract_id", "variant", "evidence"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                raise ValueError(f"{field} must be a non-empty string")
        if row["variant"] not in {"direct", "delegated"}:
            raise ValueError("variant must be direct or delegated")
        for field in ("quality_pass", "safety_pass"):
            if type(row.get(field)) is not bool:
                raise ValueError(f"{field} must be an explicit boolean")
        if type(row.get("retries")) is not int or row["retries"] < 0:
            raise ValueError("retries must be a non-negative integer")
        tokens = row.get("total_tokens")
        if tokens is not None and (type(tokens) is not int or tokens < 0):
            raise ValueError("total_tokens must be a non-negative integer or null")
        models = row.get("actual_models")
        if not isinstance(models, list) or not models or not all(
            isinstance(item, dict) and all(isinstance(item.get(key), str) and item[key].strip()
                                          for key in ("model", "thinking")) for item in models
        ):
            raise ValueError("actual_models requires actual model/thinking for all participating agents")
        key = (row["case_id"], row["contract_id"])
        pair = pairs.setdefault(key, {})
        if row["variant"] in pair:
            raise ValueError("duplicate case/contract/variant; use separate case IDs for repeated trials")
        pair[row["variant"]] = row

    complete = [pair for pair in pairs.values() if set(pair) == {"direct", "delegated"}]
    quality_ok = all(row["quality_pass"] and row["safety_pass"] for pair in complete for row in pair.values())
    retries_ok = all(pair["delegated"]["retries"] <= pair["direct"]["retries"] for pair in complete)
    token_evaluable = bool(complete) and all(
        row.get("total_tokens") is not None for pair in complete for row in pair.values())
    direct = sum(pair["direct"]["total_tokens"] for pair in complete) if token_evaluable else None
    delegated = sum(pair["delegated"]["total_tokens"] for pair in complete) if token_evaluable else None
    # An unsafe unpaired observation must not disappear from the quality gate.
    safety_ok = all(row["safety_pass"] for row in records)
    if not safety_ok or not quality_ok or not retries_ok:
        verdict = "quality_or_safety_regression"
    elif len(complete) < 3 or len(complete) != len(pairs) or not token_evaluable:
        verdict = "not_evaluable"
    elif delegated < direct:
        verdict = "token_reduction_candidate_for_manual_review"
    else:
        verdict = "no_token_reduction"
    return {
        "verdict": verdict,
        "paired_cases": len(complete),
        "unpaired_cases": len(pairs) - len(complete),
        "direct_total_tokens": direct,
        "delegated_total_tokens": delegated,
        "token_reduction_fraction": round((direct - delegated) / direct, 4) if direct else None,
        "membership_savings": "not_evaluable",
        "evidence_basis": "provided_observations_not_independently_verified",
        "note": "Include owner planning, all executors, verification and rework in totals; never auto-change model defaults.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--observed", type=Path, help="JSONL; omitted means not_evaluable")
    args = parser.parse_args()
    try:
        rows = ([json.loads(line) for line in args.observed.read_text(encoding="utf-8").splitlines()
                 if line.strip()] if args.observed else [])
        if not all(isinstance(row, dict) for row in rows):
            raise ValueError("each observation must be an object")
        result = evaluate(rows)
    except (OSError, ValueError) as exc:
        print(json.dumps({"status": "invalid_observations", "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result["verdict"] == "quality_or_safety_regression" else 0


if __name__ == "__main__":
    raise SystemExit(main())
