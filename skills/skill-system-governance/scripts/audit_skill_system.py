#!/usr/bin/env python3
"""Run deterministic, read-only governance checks for this skill repository."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import NamedTuple, Sequence


DEFAULT_REPO = Path(__file__).resolve().parents[3]
QUICK_CHECK_NAMES = (
    "catalog",
    "public_skills",
    "role_system",
    "plugins",
    "bundle_sync",
    "routing_cases",
)
REQUIRED_REPO_PATHS = (
    "registry/skills.json",
    "registry/plugin-packages.json",
    "scripts/audit_skill_catalog.py",
    "scripts/validate_public_skills.py",
    "scripts/validate_role_system.py",
    "scripts/validate_plugins.py",
    "scripts/sync_plugin_bundles.py",
    "scripts/evaluate_skill_routing.py",
    "skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py",
)


class CheckPlan(NamedTuple):
    name: str
    command: tuple[str, ...] | None
    required: bool
    unavailable_reason: str = ""


def command_for(repo: Path, relative_script: str, *args: str) -> tuple[str, ...]:
    return (sys.executable, str(repo / relative_script), *args)


def build_check_plans(
    repo: Path,
    mode: str,
    observed: Path | None,
    callbacks: Sequence[Path],
) -> list[CheckPlan]:
    """Build a read-only audit plan; commands never mutate canonical sources."""
    repo = repo.resolve()
    plans = [
        CheckPlan(
            "catalog",
            command_for(repo, "scripts/audit_skill_catalog.py", "--strict", "--json"),
            True,
        ),
        CheckPlan(
            "public_skills",
            command_for(repo, "scripts/validate_public_skills.py"),
            True,
        ),
        CheckPlan(
            "role_system",
            command_for(repo, "scripts/validate_role_system.py"),
            True,
        ),
        CheckPlan(
            "plugins",
            command_for(repo, "scripts/validate_plugins.py", "--json"),
            True,
        ),
        CheckPlan(
            "bundle_sync",
            command_for(repo, "scripts/sync_plugin_bundles.py", "--check"),
            True,
        ),
        CheckPlan(
            "routing_cases",
            command_for(
                repo,
                "scripts/evaluate_skill_routing.py",
                "--validate-only",
                "--strict",
            ),
            True,
        ),
    ]

    if observed is None:
        plans.append(
            CheckPlan(
                "routing_observed",
                None,
                False,
                "No observed routing artifact was supplied; routing accuracy is not evaluable.",
            )
        )
    else:
        plans.append(
            CheckPlan(
                "routing_observed",
                command_for(
                    repo,
                    "scripts/evaluate_skill_routing.py",
                    "--observed",
                    str(observed.resolve()),
                    "--strict",
                ),
                True,
            )
        )

    if callbacks:
        plans.append(
            CheckPlan(
                "skill_hits",
                command_for(
                    repo,
                    "skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py",
                    "--json",
                    *(str(path.resolve()) for path in callbacks),
                ),
                True,
            )
        )
    else:
        plans.append(
            CheckPlan(
                "skill_hits",
                None,
                False,
                "No callback artifacts were supplied; hit, miss, and misfire rates are not evaluable.",
            )
        )

    if mode == "full":
        plans.extend(
            [
                CheckPlan(
                    "contract_tests",
                    command_for(repo, "scripts/test_skill_contract_regressions.py"),
                    True,
                ),
                CheckPlan(
                    "role_tests",
                    command_for(repo, "scripts/test_role_system_tools.py"),
                    True,
                ),
                CheckPlan(
                    "plugin_tests",
                    command_for(repo, "scripts/test_plugin_packages.py"),
                    True,
                ),
            ]
        )
    return plans


def missing_repo_paths(repo: Path) -> list[str]:
    return [relative for relative in REQUIRED_REPO_PATHS if not (repo / relative).is_file()]


def output_tail(value: str | bytes, line_limit: int = 24) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    lines = value.strip().splitlines()
    return "\n".join(lines[-line_limit:])


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def run_check(plan: CheckPlan, repo: Path, timeout: int) -> dict[str, object]:
    if plan.command is None:
        return {
            "name": plan.name,
            "required": plan.required,
            "status": "not_evaluable",
            "reason": plan.unavailable_reason,
        }

    started = time.monotonic()
    try:
        completed = subprocess.run(
            plan.command,
            cwd=repo,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
            check=False,
        )
        status = "passed" if completed.returncode == 0 else "failed"
        return {
            "name": plan.name,
            "required": plan.required,
            "status": status,
            "exit_code": completed.returncode,
            "duration_seconds": round(time.monotonic() - started, 3),
            "command": list(plan.command),
            "stdout_tail": output_tail(completed.stdout),
            "stderr_tail": output_tail(completed.stderr),
        }
    except subprocess.TimeoutExpired as exc:
        return {
            "name": plan.name,
            "required": plan.required,
            "status": "failed",
            "exit_code": None,
            "duration_seconds": round(time.monotonic() - started, 3),
            "command": list(plan.command),
            "stdout_tail": output_tail(exc.stdout or ""),
            "stderr_tail": output_tail(exc.stderr or ""),
            "reason": f"Timed out after {timeout} seconds.",
        }


def run_audit(
    repo: Path,
    mode: str,
    observed: Path | None,
    callbacks: Sequence[Path],
    timeout: int,
) -> dict[str, object]:
    repo = repo.resolve()
    checks = [
        run_check(plan, repo, timeout)
        for plan in build_check_plans(repo, mode, observed, callbacks)
    ]
    required_failures = [
        item["name"]
        for item in checks
        if item["required"] and item["status"] != "passed"
    ]
    return {
        "ok": not required_failures,
        "status": "passed" if not required_failures else "failed",
        "mode": mode,
        "repository": str(repo),
        "required_failures": required_failures,
        "checks": checks,
    }


def print_human(report: dict[str, object]) -> None:
    print(f"Skill-system governance audit: {report['status']} ({report['mode']})")
    for item in report["checks"]:
        suffix = ""
        if item["status"] == "not_evaluable":
            suffix = f" - {item['reason']}"
        elif item["status"] == "failed" and item.get("stderr_tail"):
            suffix = f" - {str(item['stderr_tail']).splitlines()[-1]}"
        print(f"- {item['name']}: {item['status']}{suffix}")


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO)
    parser.add_argument("--mode", choices=("quick", "full"), default="quick")
    parser.add_argument("--observed", type=Path)
    parser.add_argument("--callbacks", type=Path, action="append", default=[])
    parser.add_argument("--timeout", type=positive_int, default=180)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    repo = args.repo.resolve()
    missing = missing_repo_paths(repo)
    if missing:
        report: dict[str, object] = {
            "ok": False,
            "status": "invalid_repository",
            "repository": str(repo),
            "missing": missing,
        }
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print("Skill-system governance audit refused: invalid repository.", file=sys.stderr)
            for relative in missing:
                print(f"- missing: {relative}", file=sys.stderr)
        return 2

    report = run_audit(repo, args.mode, args.observed, args.callbacks, args.timeout)
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
