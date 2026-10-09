#!/usr/bin/env python3
"""Plan or explicitly install project-local observation and additive native hooks."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import secrets
import shlex
import subprocess
import sys
import tempfile

from workflow_observation import EVENTS, data_directory, linked, read_json

MARKER = "Local workflow observation"
SOURCE = Path(__file__).with_name("workflow_observation.py")


def encode(value):
    return (json.dumps(value, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def atomic_write(path, data, *, staging_dir=None):
    if linked(path):
        raise ValueError("refusing linked destination")
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=staging_dir or path.parent, prefix=".observation-", delete=False) as stream:
        temporary = Path(stream.name)
        stream.write(data)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def hook_command(python, runtime, manifest):
    arguments = [str(python), "-B", str(runtime), "hook", "--manifest", str(manifest)]
    if os.name != "nt":
        return shlex.join(arguments)
    command = "& " + " ".join("'" + argument.replace("'", "''") + "'" for argument in arguments)
    return subprocess.list2cmdline(["powershell.exe", "-NoProfile", "-NonInteractive", "-Command", command])


def install(projects, install_dir, hooks_path, transcript_roots, *, enabled=False, write=False, upgrade=False):
    install_dir, hooks_path = Path(install_dir).absolute(), Path(hooks_path).absolute()
    if linked(install_dir) or linked(hooks_path):
        raise ValueError("refusing linked installation target")
    source = SOURCE.read_bytes()
    revision = hashlib.sha256(source).hexdigest()
    runtime = install_dir / ("runtime-" + revision[:16]) / SOURCE.name
    manifest_path = install_dir / "installation.json"
    previous = read_json(manifest_path) if manifest_path.exists() else None
    if upgrade and not previous:
        raise ValueError("upgrade requires an existing installation")
    if previous and previous.get("collector_revision") != revision and not upgrade:
        raise ValueError("collector revision changed; use a new installation directory and review its hooks")
    previous_command = None
    if upgrade:
        old_revision = previous.get("collector_revision", "")
        if len(old_revision) != 64 or any(char not in "0123456789abcdef" for char in old_revision):
            raise ValueError("invalid previous collector revision")
        old_runtime = install_dir / ("runtime-" + old_revision[:16]) / SOURCE.name
        if linked(old_runtime.parent) or linked(old_runtime) or hashlib.sha256(old_runtime.read_bytes()).hexdigest() != old_revision:
            raise ValueError("previous runtime is not the recorded immutable version")
        previous_command = hook_command(sys.executable, old_runtime, manifest_path)
        enabled = previous.get("enabled")
        if type(enabled) is not bool:
            raise ValueError("invalid existing installation switch")
    existing_bytes = hooks_path.read_bytes() if hooks_path.exists() else None
    hooks_doc = json.loads(existing_bytes.decode("utf-8-sig")) if existing_bytes else {"hooks": {}}
    if not isinstance(hooks_doc, dict) or not isinstance(hooks_doc.get("hooks", {}), dict):
        raise ValueError("invalid hooks document")
    groups = hooks_doc.setdefault("hooks", {})
    command = hook_command(sys.executable, runtime, manifest_path)
    added = updated = 0
    for event in sorted(EVENTS):
        handlers = groups.setdefault(event, [])
        if not isinstance(handlers, list):
            raise ValueError("invalid hook event list")
        desired = {"hooks": [{"type": "command", "command": command, "timeout": 3, "statusMessage": MARKER}]}
        owned = [index for index, group in enumerate(handlers)
                 if any(handler.get("statusMessage") == MARKER for handler in group.get("hooks", []))]
        if len(owned) == 1 and handlers[owned[0]] == desired:
            continue
        if owned:
            expected = {"hooks": [{"type": "command", "command": previous_command, "timeout": 3, "statusMessage": MARKER}]}
            if not upgrade or len(owned) != 1 or handlers[owned[0]] != expected:
                raise ValueError("another observation hook exists; do not duplicate or silently replace it")
            handlers[owned[0]] = desired
            updated += 1
            continue
        handlers.append(desired)
        added += 1
    entries, configs, roots_seen, worktrees_seen = [], [], set(), set()
    prior_by_root = {item["root"]: item for item in previous["projects"]} if previous else {}
    for item in projects:
        root = Path(item["root"]).resolve(strict=True)
        if root.parent == root or not (root / ".git").exists() or str(root) in roots_seen:
            raise ValueError("expected distinct explicit Git project roots")
        roots_seen.add(str(root))
        worktrees = sorted({str(Path(path).resolve(strict=True)) for path in [str(root), *item.get("worktrees", [])]})
        if any(path in worktrees_seen for path in worktrees):
            raise ValueError("worktree belongs to multiple observation projects")
        worktrees_seen.update(worktrees)
        previous_entry = prior_by_root.get(str(root))
        entry = {"project_id": previous_entry["project_id"] if previous_entry else secrets.token_hex(12),
                 "root": str(root), "worktrees": worktrees}
        directory = data_directory(entry)
        config_path = directory / "config.json"
        if linked(config_path):
            raise ValueError("unsafe project configuration")
        if directory.exists() and previous_entry is None:
            raise ValueError("observation directory already exists without this installation; inspect before adopting")
        config = read_json(config_path) if config_path.exists() else {"schema_version": 1}
        if config.get("schema_version") != 1:
            raise ValueError("unsupported project observation config")
        if not upgrade:
            config["enabled"] = enabled
        configs.append((directory, config))
        entries.append(entry)
    if not entries:
        raise ValueError("no projects selected")
    if previous and set(prior_by_root) != roots_seen:
        raise ValueError("project selection changed; inspect the existing installation before changing scope")
    if upgrade and entries != previous["projects"]:
        raise ValueError("upgrade must preserve project and worktree scope")
    resolved_transcripts = [str(Path(path).resolve(strict=True)) for path in transcript_roots]
    if upgrade and resolved_transcripts != previous["transcript_roots"]:
        raise ValueError("upgrade must preserve transcript scope")
    manifest = {"schema_version": 1, "enabled": enabled,
                "salt": previous["salt"] if previous else secrets.token_hex(32),
                "collector_revision": revision, "projects": entries,
                "transcript_roots": resolved_transcripts}
    plan = {"action": ("upgrade" if upgrade else "install") if write else "plan", "project_count": len(entries),
            "worktree_count": len(worktrees_seen), "new_hook_groups": added, "updated_hook_groups": updated, "enabled": enabled,
            "runtime": str(runtime), "manifest": str(manifest_path), "collector_revision": revision,
            "native_hook_trust": "requires_host_review", "changes_global_config": False}
    if not write:
        return plan
    install_dir.mkdir(parents=True, exist_ok=True)
    if linked(runtime.parent) or linked(runtime):
        raise ValueError("refusing linked runtime")
    if runtime.exists() and runtime.read_bytes() != source:
        raise ValueError("immutable runtime was modified")
    if not runtime.exists():
        atomic_write(runtime, source)
    backup = install_dir / ("hooks-before-" + hashlib.sha256(existing_bytes or b"").hexdigest()[:16] + ".json")
    if not backup.exists():
        atomic_write(backup, existing_bytes or b"{}\n")
    for directory, config in ([] if upgrade else configs):
        directory.mkdir(parents=True, exist_ok=True)
        ignore = directory / ".gitignore"
        if ignore.exists() and ignore.read_text(encoding="utf-8") != "*\n":
            raise ValueError("unexpected observation ignore file")
        atomic_write(ignore, b"*\n")
        atomic_write(directory / "config.json", encode(config))
    atomic_write(manifest_path, encode(manifest))
    # Do not overwrite a concurrent edit to the user's hook file.
    if (hooks_path.read_bytes() if hooks_path.exists() else None) != existing_bytes:
        raise ValueError("hooks changed during installation; hook registration not written")
    if added or updated:
        atomic_write(hooks_path, encode(hooks_doc), staging_dir=install_dir)
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--projects", type=Path, required=True, help="Private JSON list of explicit roots and known worktrees")
    parser.add_argument("--install-dir", type=Path, required=True)
    parser.add_argument("--hooks-file", type=Path, required=True)
    parser.add_argument("--transcript-root", type=Path, action="append", required=True)
    parser.add_argument("--enable", action="store_true", help="Explicit opt-in; omitted means disabled")
    parser.add_argument("--write", action="store_true", help="Omitted means read-only plan")
    parser.add_argument("--upgrade", action="store_true", help="Replace only verified prior hooks; preserve switches, IDs, salt, scope and data")
    args = parser.parse_args()
    try:
        print(json.dumps(install(read_json(args.projects), args.install_dir, args.hooks_file, args.transcript_root,
                                 enabled=args.enable, write=args.write, upgrade=args.upgrade), ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "not_installed", "reason": str(exc)}, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
