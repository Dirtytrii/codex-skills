#!/usr/bin/env python3
"""Append opt-in role reports with bounded project-file evidence, without scoring tasks."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
import uuid

from workflow_observation import (MAX_INPUT, append_event, choose_project, contained,
                                  data_directory, event_files, linked, pseudonym,
                                  read_hook_payload, read_json, resolved_path)

# Core packages both skills. Reuse the role registry parser instead of guessing roles.
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "agent-role-orchestrator" / "scripts"))
from validate_role_loop import parse_ledger_table

REVIEW_ROLES = {"架构", "QA", "测试", "安全", "DBA", "运维", "总控", "内容主编"}
KINDS = {"review", "rework", "skill_usage"}
MAX_EVIDENCE_FILE = 2 * 1024 * 1024


def identifier(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value):
        raise ValueError("invalid session or turn identifier")
    return value


def skills(value):
    if not isinstance(value, list) or len(value) > 32 or any(
            not isinstance(item, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9:_-]{0,95}", item) for item in value):
        raise ValueError("invalid skill list")
    return sorted(set(value))


def registered_roles(project):
    path = Path(project["root"]) / ".codex" / "role-windows.md"
    if linked(path) or not contained(path, project["root"]) or path.stat().st_size > MAX_INPUT:
        raise ValueError("invalid role registry")
    rows, errors = parse_ledger_table(path.read_text(encoding="utf-8-sig"))
    if errors:
        raise ValueError("role registry cannot be parsed")
    roles = {}
    for row in rows:
        sid = row.get("thread id", "").strip().strip("`")
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", sid):
            continue
        if sid in roles:
            raise ValueError("ambiguous role registry")
        roles[sid] = row["角色"].strip()
    return roles


def file_evidence(project, values):
    if not isinstance(values, list) or not 1 <= len(values) <= 8:
        raise ValueError("one to eight project report files required")
    root = resolved_path(project["root"])
    output = []
    for raw in values:
        if not isinstance(raw, str):
            raise ValueError("invalid evidence path")
        relative = Path(raw)
        if relative.is_absolute() or ".." in relative.parts or any(char in raw for char in "*?[]"):
            raise ValueError("evidence must use exact project-relative paths")
        posix = relative.as_posix()
        if not posix.startswith((".codex/tasks/", ".codex/reports/", "docs/", "target/surefire-reports/", "test-results/")):
            raise ValueError("evidence must be a task, review or test report")
        path = root / relative
        if path.suffix.lower() not in {".md", ".json", ".txt", ".xml"} or linked(path) or not contained(path, root):
            raise ValueError("unsafe evidence file")
        with path.open("rb") as stream:
            raw_bytes = stream.read(MAX_EVIDENCE_FILE + 1)
        if len(raw_bytes) > MAX_EVIDENCE_FILE:
            raise ValueError("evidence report exceeds size limit")
        output.append({"relative_path": posix, "sha256": hashlib.sha256(raw_bytes).hexdigest()})
    return output


def record(manifest, report):
    if not isinstance(report, dict) or report.get("schema_version") != 1 or report.get("kind") not in KINDS:
        raise ValueError("invalid evidence report schema")
    project = choose_project(manifest, report.get("cwd"))
    if project is None:
        raise ValueError("project not enabled or not registered")
    directory = data_directory(project)
    config = directory / "config.json"
    if linked(config):
        raise ValueError("unsafe project observation configuration")
    settings = read_json(config)
    if settings.get("schema_version") != 1 or settings.get("enabled") is not True:
        raise ValueError("project observation is disabled")
    target = identifier(report.get("session_id"))
    turn = identifier(report.get("turn_id"))
    reporter = identifier(report.get("reporter_session_id"))
    target_hash, turn_hash = pseudonym(manifest, target), pseudonym(manifest, turn)
    seen = False
    for path in event_files(directory):
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                row = json.loads(line)
                if (row.get("evidence_source") == "host_hook" and row.get("project_id") == project["project_id"]
                        and row.get("session_id") == target_hash and row.get("turn_id") == turn_hash
                        and not row.get("agent_id")):
                    seen = True
            except (ValueError, AttributeError):
                continue
    if not seen:
        raise ValueError("target turn has no matching native observation")
    roles = registered_roles(project)
    if target not in roles or reporter not in roles:
        raise ValueError("target and reporter must have registered role threads")
    kind = report["kind"]
    row = {"schema_version": 1, "event_id": uuid.uuid4().hex,
           "recorded_at": datetime.now(timezone.utc).isoformat(), "kind": kind,
           "evidence_source": "registered_review_report" if kind == "review" else "role_self_report",
           "project_id": project["project_id"], "session_id": target_hash, "turn_id": turn_hash,
           "reporter_id": pseudonym(manifest, reporter), "reporter_role": roles[reporter],
           "collector_revision": manifest.get("collector_revision"),
           "quality_pass": None, "safety_pass": None, "retries": None,
           "skills_loaded": None, "skills_used": None, "skills_missed": None, "skills_misfired": None,
           "review_independence": None, "evidence_files": file_evidence(project, report.get("evidence_files"))}
    if kind == "review":
        base_role = re.sub(r"\d+号$", "", roles[reporter])
        if reporter == target or base_role not in REVIEW_ROLES:
            raise ValueError("review requires a different registered review thread")
        if any(type(report.get(key)) is not bool for key in ("quality_pass", "safety_pass")):
            raise ValueError("review requires explicit quality and safety decisions")
        row.update(quality_pass=report["quality_pass"], safety_pass=report["safety_pass"],
                   review_independence="different_registered_review_thread_not_proof_of_review_quality")
    elif kind == "rework":
        if reporter != target or type(report.get("retries")) is not int or not 0 <= report["retries"] <= 10000:
            raise ValueError("rework requires owner self-report and a non-negative retry count")
        row["retries"] = report["retries"]
    else:
        if reporter != target:
            raise ValueError("skill usage requires the participating role's own report")
        for key in ("skills_loaded", "skills_used", "skills_missed", "skills_misfired"):
            row[key] = skills(report.get(key))
        loaded = set(row["skills_loaded"])
        if not set(row["skills_used"]) <= loaded or not set(row["skills_misfired"]) <= loaded or loaded & set(row["skills_missed"]):
            raise ValueError("inconsistent skill report")
    if not append_event(directory, row, prefix="evidence"):
        raise ValueError("observation storage is full")
    return {"recorded": True, "kind": kind, "evidence_source": row["evidence_source"], "event_id": row["event_id"]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    args = parser.parse_args()
    try:
        print(json.dumps(record(read_json(args.manifest), read_hook_payload(sys.stdin.fileno())), ensure_ascii=False))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        # Do not expose raw input, identities or private paths in diagnostics.
        reason = str(exc) if type(exc) is ValueError else "invalid_or_unavailable_evidence; check schema, scope, role registry and files"
        print(json.dumps({"recorded": False, "reason": reason}))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
