#!/usr/bin/env python3
"""Opt-in, local-only lifecycle observations. Hook stdout is always inert JSON."""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import contextmanager
from datetime import datetime, timedelta, timezone
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import sys
import threading
import time
import uuid

EVENTS = {"UserPromptSubmit", "SubagentStart", "SubagentStop", "Stop", "Interrupt"}
TOKEN_KEYS = ("input_tokens", "cached_input_tokens", "output_tokens", "reasoning_output_tokens", "total_tokens")
EFFORTS = {"none", "minimal", "low", "medium", "high", "xhigh", "max", "ultra"}
MAX_INPUT = 1024 * 1024
MAX_TAIL = 2 * 1024 * 1024
MAX_STORAGE = 10 * 1024 * 1024
RETENTION_DAYS = 30
HOOK_BUDGET_SECONDS = 1.5


def read_hook_payload(fd):
    """Read one complete JSON value, without requiring a newline or pipe EOF."""
    raw = bytearray()
    while len(raw) <= MAX_INPUT:
        chunk = os.read(fd, min(65536, MAX_INPUT + 1 - len(raw)))
        if not chunk:
            raise ValueError("incomplete hook input")
        raw.extend(chunk)
        if len(raw) > MAX_INPUT:
            raise ValueError("hook input too large")
        try:
            return json.loads(raw)
        except ValueError:
            continue  # JSON or a UTF-8 character may span multiple pipe writes.


def run_hook(manifest_path):
    def observe():
        try:
            payload = read_hook_payload(sys.stdin.fileno())
            collect(read_json(manifest_path), payload)
        except Exception:
            pass  # Observability failure must never steer, block, or expose a task.

    # os.read avoids holding Python's buffered-stdin lock during process shutdown.
    # The daemon lives only in this short-lived hook process, never a background service.
    worker = threading.Thread(target=observe, daemon=True)
    worker.start()
    worker.join(HOOK_BUDGET_SECONDS)
    print("{}")
    return 0


def read_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def contained(path, root):
    return Path(path).resolve().is_relative_to(Path(root).resolve())


def linked(path):
    path = Path(path)
    if path.is_symlink():
        return True
    return bool(getattr(path.lstat(), "st_file_attributes", 0) & 0x400) if path.exists() else False


def data_directory(project):
    root = Path(project["root"]).resolve(strict=True)
    target = root / ".codex" / "telemetry"
    for path in (root / ".codex", target):
        if linked(path) or not contained(path, root):
            raise ValueError("unsafe observation directory")
    return target


def choose_project(manifest, cwd):
    if manifest.get("schema_version") != 1 or manifest.get("enabled") is not True or not isinstance(cwd, str):
        return None
    matches = [(len(str(root)), project) for project in manifest.get("projects", [])
               for root in project.get("worktrees", [project["root"]]) if contained(cwd, root)]
    return max(matches, key=lambda pair: pair[0])[1] if matches else None


def pseudonym(manifest, value):
    if not isinstance(value, str) or not value:
        return None
    return hmac.new(bytes.fromhex(manifest["salt"]), value.encode("utf-8"), hashlib.sha256).hexdigest()[:24]


def model_slug(value):
    if not isinstance(value, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._:-]{0,95}", value):
        return None
    return None if value.lower().startswith(("sk-", "ghp_", "gho_", "bearer")) else value


def usage(value):
    if not isinstance(value, dict):
        return None
    required = ("input_tokens", "output_tokens", "total_tokens")
    if any(type(value.get(key)) is not int or value[key] < 0 for key in required):
        return None
    if any(key in value and (type(value[key]) is not int or value[key] < 0) for key in TOKEN_KEYS):
        return None
    if value["total_tokens"] != value["input_tokens"] + value["output_tokens"]:
        return None
    return {key: value.get(key) for key in TOKEN_KEYS}


def transcript_snapshot(manifest, project, payload):
    empty = {"model": None, "thinking": None, "usage": None, "evidence": "unavailable", "bytes": None}
    child = payload["hook_event_name"] in {"SubagentStart", "SubagentStop"}
    raw = payload.get("agent_transcript_path" if child else "transcript_path")
    if not isinstance(raw, str):
        return empty
    path = Path(raw)
    if path.suffix != ".jsonl" or linked(path) or not any(contained(path, root) for root in manifest.get("transcript_roots", [])):
        return empty
    try:
        with path.open("rb") as stream:
            header_line = stream.readline(256 * 1024)
            if not header_line.endswith(b"\n"):
                return empty
            header = json.loads(header_line)
            meta = header.get("payload", {})
            expected = payload.get("agent_id" if child else "session_id")
            if header.get("type") != "session_meta" or (meta.get("id") or meta.get("session_id")) != expected:
                return empty
            if not isinstance(meta.get("cwd"), str) or not any(contained(meta["cwd"], root) for root in project["worktrees"]):
                return empty
            size = stream.seek(0, os.SEEK_END)
            offset = max(0, size - MAX_TAIL)
            stream.seek(offset)
            if offset:
                stream.readline()  # The tail may start inside a JSON line.
            tail = stream.read(MAX_TAIL)
        snapshot = dict(empty, evidence="bounded_transcript_metadata", bytes=size)
        for line in tail.splitlines():
            try:
                row = json.loads(line)
                item = row.get("payload", {})
                if row.get("type") == "turn_context" and (child or item.get("turn_id") == payload.get("turn_id")):
                    snapshot["model"] = model_slug(item.get("model"))
                    snapshot["thinking"] = item.get("effort") if item.get("effort") in EFFORTS else None
                if row.get("type") == "event_msg" and item.get("type") == "token_count":
                    info = item.get("info")
                    snapshot["usage"] = usage(info.get("total_token_usage")) if isinstance(info, dict) else None
            except (ValueError, AttributeError, TypeError):
                continue
        return snapshot
    except (OSError, ValueError, TypeError, AttributeError):
        return empty


@contextmanager
def file_lock(directory):
    path = directory / ".write.lock"
    if linked(path):
        raise ValueError("unsafe lock")
    with path.open("a+b") as handle:
        handle.seek(0, os.SEEK_END)
        if not handle.tell():
            handle.write(b"0")
            handle.flush()
        deadline = time.monotonic() + 1
        while True:
            try:
                handle.seek(0)
                if os.name == "nt":
                    import msvcrt
                    msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                break
            except OSError:
                if time.monotonic() >= deadline:
                    raise TimeoutError("observation busy")
                time.sleep(0.01)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def event_files(directory):
    return sorted(path for path in directory.glob("events-*.jsonl")
                  if re.fullmatch(r"events-\d{4}-\d{2}-\d{2}\.jsonl", path.name)
                  and not linked(path) and contained(path, directory))


def append_event(directory, row):
    encoded = (json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n").encode("utf-8")
    now = datetime.now(timezone.utc)
    path = directory / f"events-{now:%Y-%m-%d}.jsonl"
    if linked(path):
        raise ValueError("unsafe event file")
    with file_lock(directory):
        cutoff = f"events-{(now - timedelta(days=RETENTION_DAYS)):%Y-%m-%d}.jsonl"
        for candidate in event_files(directory):
            if candidate.name < cutoff:
                candidate.unlink()
        files = event_files(directory)
        total = sum(candidate.stat().st_size for candidate in files)
        for candidate in files:
            if total + len(encoded) <= MAX_STORAGE:
                break
            if candidate == path:
                return False  # Never rewrite today's observations to hide overflow.
            total -= candidate.stat().st_size
            candidate.unlink()
        with path.open("ab") as stream:
            stream.write(encoded)
            stream.flush()
        return True


def collect(manifest, payload, *, smoke=False):
    if not isinstance(payload, dict) or payload.get("hook_event_name") not in EVENTS:
        return False
    project = choose_project(manifest, payload.get("cwd"))
    if project is None:
        return False
    directory = data_directory(project)
    config_path = directory / "config.json"
    if linked(config_path) or not config_path.is_file():
        return False
    config = read_json(config_path)
    if config.get("schema_version") != 1 or config.get("enabled") is not True:
        return False
    snapshot = transcript_snapshot(manifest, project, payload)
    event = payload["hook_event_name"]
    child = event.startswith("Subagent")
    hook_model = model_slug(payload.get("model"))
    actual_model = snapshot["model"] if child else hook_model or snapshot["model"]
    row = {
        "schema_version": 1, "event_id": uuid.uuid4().hex,
        "recorded_at": datetime.now(timezone.utc).isoformat(), "event": event,
        "evidence_source": "synthetic_smoke" if smoke else "host_hook",
        "collector_revision": manifest.get("collector_revision"), "project_id": project["project_id"],
        "session_id": pseudonym(manifest, payload.get("session_id")),
        "turn_id": pseudonym(manifest, payload.get("turn_id")),
        "agent_id": pseudonym(manifest, payload.get("agent_id")) if child else None,
        "hook_model": hook_model,
        "actual_model": actual_model,
        "thinking": snapshot["thinking"] if actual_model == snapshot["model"] else None,
        "transcript_evidence": snapshot["evidence"],
        "transcript_bytes": snapshot["bytes"], "usage_snapshot": snapshot["usage"],
        "usage_scope": "transcript_session_cumulative_not_billing",
        "quality_pass": None, "safety_pass": None, "retries": None, "skills_observed": None,
    }
    return append_event(directory, row)


def summarize(manifest):
    output = []
    for project in manifest["projects"]:
        directory = data_directory(project)
        rows = []
        invalid = 0
        for path in event_files(directory):
            with path.open(encoding="utf-8") as stream:
                for line in stream:
                    try:
                        row = json.loads(line)
                        if row.get("evidence_source") == "host_hook" and row.get("project_id") == project["project_id"]:
                            rows.append(row)
                    except (ValueError, AttributeError):
                        invalid += 1
        turns = {}
        for row in rows:
            if not row.get("session_id") or not row.get("turn_id") or row.get("agent_id"):
                continue
            key = (row["session_id"], row["turn_id"])
            if row["event"] in {"UserPromptSubmit", "Stop", "Interrupt"}:
                turns.setdefault(key, {})[row["event"]] = row
        deltas, durations = [], []
        for turn in turns.values():
            start, end = turn.get("UserPromptSubmit"), turn.get("Stop") or turn.get("Interrupt")
            if not start or not end:
                continue
            if start.get("usage_snapshot") and end.get("usage_snapshot"):
                delta = end["usage_snapshot"]["total_tokens"] - start["usage_snapshot"]["total_tokens"]
                if delta >= 0:
                    deltas.append(delta)
            duration = (datetime.fromisoformat(end["recorded_at"]) - datetime.fromisoformat(start["recorded_at"])).total_seconds()
            if duration >= 0:
                durations.append(duration)
        output.append({"project_id": project["project_id"], "enabled": read_json(directory / "config.json").get("enabled") is True,
                       "observed_events": len(rows), "events": dict(Counter(row["event"] for row in rows)),
                       "model_event_counts": dict(Counter(row["actual_model"] for row in rows if row.get("actual_model"))),
                       "native_hook_seen": bool(rows),
                       "last_host_hook_at": rows[-1]["recorded_at"] if rows else None,
                       "storage_bytes": sum(path.stat().st_size for path in event_files(directory)),
                       "subagents_observed": len({row["agent_id"] for row in rows if row.get("agent_id")}),
                       "complete_usage_turns": len(deltas), "per_session_token_delta": sum(deltas) if deltas else None,
                       "complete_timed_turns": len(durations), "elapsed_seconds": round(sum(durations), 3) if durations else None,
                       "quality": "not_evaluable", "skill_hit_rate": "not_evaluable", "membership_savings": "not_evaluable",
                       "invalid_lines": invalid})
    return {"schema_version": 1, "projects": output,
            "note": "No quality inference. Token deltas need complete start/end pairs; parent/child usage may overlap. Do not treat as billing."}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("hook", "status", "summary", "smoke"))
    parser.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    if args.action == "hook":
        return run_hook(args.manifest)
    manifest = read_json(args.manifest)
    if args.action == "smoke":
        results = [{"project_id": project["project_id"], "written": collect(manifest, {
            "hook_event_name": "Stop", "cwd": project["root"], "session_id": "installation-smoke", "turn_id": "smoke"
        }, smoke=True)} for project in manifest["projects"]]
        print(json.dumps({"smoke": results, "native_hook_trust": "not_verified"}, indent=2))
        return 0 if all(item["written"] for item in results) else 1
    print(json.dumps(summarize(manifest), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
