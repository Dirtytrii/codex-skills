#!/usr/bin/env python3
"""Offline contract tests; never read user transcripts or install real hooks."""
from __future__ import annotations

import concurrent.futures
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/skill-system-governance/scripts/workflow_observation.py"
spec = importlib.util.spec_from_file_location("observation", SCRIPT)
obs = importlib.util.module_from_spec(spec)
spec.loader.exec_module(obs)
sys.path.insert(0, str(SCRIPT.parent))
import install_workflow_observation as installer


class ObservationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project with spaces"
        self.project.mkdir()
        self.data = self.project / ".codex/telemetry"
        self.data.mkdir(parents=True)
        self.config = self.data / "config.json"
        self.config.write_text(json.dumps({"schema_version": 1, "enabled": True}), encoding="utf-8")
        self.sessions = self.root / "sessions"
        self.sessions.mkdir()
        self.manifest = {"schema_version": 1, "enabled": True, "salt": "a" * 64,
                         "transcript_roots": [str(self.sessions)],
                         "projects": [{"project_id": "p1", "root": str(self.project),
                                       "worktrees": [str(self.project)]}]}
        self.payload = {"hook_event_name": "Stop", "cwd": str(self.project),
                        "session_id": "private-session", "turn_id": "private-turn", "model": "test-model",
                        "last_assistant_message": "SECRET-RAW-TEXT", "prompt": "SECRET-PROMPT"}

    def rows(self):
        return [json.loads(line) for path in sorted(self.data.glob("events-*.jsonl"))
                for line in path.read_text(encoding="utf-8").splitlines()]

    def transcript(self, total=100, **overrides):
        path = self.sessions / "rollout.jsonl"
        meta = {"id": "private-session", "cwd": str(self.project)}
        meta.update(overrides)
        rows = [{"type": "session_meta", "payload": meta},
                {"type": "turn_context", "payload": {"turn_id": "private-turn", "model": "test-model", "effort": "high"}},
                {"type": "event_msg", "payload": {"type": "token_count", "info": {
                    "total_token_usage": {"input_tokens": total-10 if type(total) is int else 90,
                                          "output_tokens": 10, "total_tokens": total,
                                          "cached_input_tokens": 20}}}},
                {"type": "response_item", "payload": {"text": "SECRET-TRANSCRIPT"}}]
        path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")
        self.payload["transcript_path"] = str(path)
        return path

    def test_disabled_and_unknown_project_write_nothing(self):
        self.manifest["enabled"] = False
        self.assertFalse(obs.collect(self.manifest, self.payload))
        self.manifest["enabled"] = True
        self.payload["cwd"] = str(self.root)
        self.assertFalse(obs.collect(self.manifest, self.payload))
        self.assertEqual([], self.rows())
        self.assertFalse((self.root / ".codex").exists())

    def test_allowlist_and_pseudonymization(self):
        self.transcript()
        self.assertTrue(obs.collect(self.manifest, self.payload))
        row = self.rows()[0]
        text = json.dumps(row)
        for private in ("SECRET", "private-session", "private-turn", str(self.project)):
            self.assertNotIn(private, text)
        self.assertEqual("high", row["thinking"])
        self.assertEqual(100, row["usage_snapshot"]["total_tokens"])
        self.assertIsNone(row["quality_pass"])
        self.assertIsNone(row["skills_observed"])

    def test_malformed_or_wrong_transcript_is_not_evidence(self):
        for total in (-1, True, "100"):
            self.transcript(total)
            obs.collect(self.manifest, self.payload)
            self.assertIsNone(self.rows()[-1]["usage_snapshot"])
        self.transcript(cwd=str(self.root / "unrelated"))
        obs.collect(self.manifest, self.payload)
        self.assertEqual("unavailable", self.rows()[-1]["transcript_evidence"])
        self.assertIsNone(self.rows()[-1]["thinking"])

    def test_transcript_outside_allowlist_or_symlink_is_rejected(self):
        source = self.transcript()
        outside = self.root / "outside.jsonl"
        outside.write_bytes(source.read_bytes())
        self.payload["transcript_path"] = str(outside)
        obs.collect(self.manifest, self.payload)
        self.assertIsNone(self.rows()[-1]["usage_snapshot"])

    def test_subagent_does_not_inherit_parent_model(self):
        self.payload.update(hook_event_name="SubagentStart", agent_id="worker-1")
        obs.collect(self.manifest, self.payload)
        row = self.rows()[0]
        self.assertIsNone(row["actual_model"])
        self.assertEqual("test-model", row["hook_model"])
        self.assertNotEqual(row["session_id"], row["agent_id"])

    def test_local_disable_is_strict_and_effective(self):
        for value in (False, "true", 1, None):
            self.config.write_text(json.dumps({"schema_version": 1, "enabled": value}), encoding="utf-8")
            self.assertFalse(obs.collect(self.manifest, self.payload))
        self.assertEqual([], self.rows())

    def test_concurrent_jsonl_writes_are_complete(self):
        with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda i: obs.collect(self.manifest, dict(self.payload, turn_id=f"t{i}")), range(40)))
        self.assertTrue(all(results))
        self.assertEqual(40, len(self.rows()))

    def test_retention_preserves_unowned_files(self):
        (self.data / "events-2000-01-01.jsonl").write_text("{}\n", encoding="utf-8")
        (self.data / "user-notes.jsonl").write_text("keep", encoding="utf-8")
        obs.collect(self.manifest, self.payload)
        self.assertFalse((self.data / "events-2000-01-01.jsonl").exists())
        self.assertEqual("keep", (self.data / "user-notes.jsonl").read_text(encoding="utf-8"))

    def test_hook_never_controls_agent_or_leaks_error(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        for payload in ("broken SECRET", json.dumps(self.payload), "[]"):
            result = subprocess.run([sys.executable, "-B", str(SCRIPT), "hook", "--manifest", str(path)],
                                    input=payload, text=True, capture_output=True)
            self.assertEqual(0, result.returncode)
            self.assertEqual({}, json.loads(result.stdout))
            self.assertEqual("", result.stderr)

    def open_pipe_hook(self, command, chunks):
        process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        started = time.monotonic()
        try:
            for chunk in chunks:
                process.stdin.write(chunk)
                process.stdin.flush()
                time.sleep(0.02)
            # Deliberately keep stdin open until the hook has exited.
            process.wait(timeout=2.8)
            self.assertLess(time.monotonic() - started, 2.8)
            self.assertEqual(0, process.returncode)
            self.assertEqual({}, json.loads(process.stdout.read()))
            self.assertEqual(b"", process.stderr.read())
        finally:
            try:
                process.stdin.close()
            except BrokenPipeError:
                pass
            try:
                process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
            process.stdout.close()
            process.stderr.close()

    def test_complete_json_exits_without_newline_or_stdin_eof(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        raw = json.dumps(dict(self.payload, prompt="\u4e2d\u6587"), ensure_ascii=False).encode("utf-8")
        split = raw.index("\u4e2d".encode("utf-8")) + 1
        self.open_pipe_hook([sys.executable, "-B", str(SCRIPT), "hook", "--manifest", str(path)],
                            [raw[:split], raw[split:]])
        self.assertEqual(1, len(self.rows()))

    def test_incomplete_or_empty_open_pipe_exits_within_hook_budget(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        for chunks in ([], [b'{"prompt":"unfinished']):
            with self.subTest(chunks=chunks):
                self.open_pipe_hook([sys.executable, "-B", str(SCRIPT), "hook", "--manifest", str(path)], chunks)
        self.assertEqual([], self.rows())

    def test_oversized_input_is_dropped(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        raw = json.dumps(dict(self.payload, prompt="x" * obs.MAX_INPUT)).encode("utf-8")
        result = subprocess.run([sys.executable, "-B", str(SCRIPT), "hook", "--manifest", str(path)],
                                input=raw, capture_output=True, timeout=3)
        self.assertEqual(0, result.returncode)
        self.assertEqual({}, json.loads(result.stdout))
        self.assertEqual(b"", result.stderr)
        self.assertEqual([], self.rows())

    def test_slow_collection_does_not_block_host(self):
        path = self.root / "manifest.json"
        path.write_text(json.dumps(self.manifest), encoding="utf-8")
        code = ("import runpy,sys,time; m=runpy.run_path(sys.argv[1]); "
                "m['run_hook'].__globals__['collect']=lambda *args: time.sleep(10); "
                "m['run_hook'](sys.argv[2])")
        self.open_pipe_hook([sys.executable, "-B", "-c", code, str(SCRIPT), str(path)],
                            [json.dumps(self.payload).encode("utf-8")])
        self.assertEqual([], self.rows())

    def test_summary_pairs_turn_counters_not_cumulative_totals(self):
        self.transcript(100)
        obs.collect(self.manifest, dict(self.payload, hook_event_name="UserPromptSubmit"))
        self.transcript(160)
        obs.collect(self.manifest, self.payload)
        obs.collect(self.manifest, self.payload)
        summary = obs.summarize(self.manifest)["projects"][0]
        self.assertEqual(1, summary["complete_usage_turns"])
        self.assertEqual(60, summary["per_session_token_delta"])
        self.assertEqual("not_evaluable", summary["membership_savings"])
        self.assertEqual("not_evaluable", summary["quality"])

    def test_smoke_events_are_not_real_observations(self):
        obs.collect(self.manifest, self.payload, smoke=True)
        self.assertEqual(0, obs.summarize(self.manifest)["projects"][0]["observed_events"])

    def install_target(self):
        project = self.root / "installation project"
        project.mkdir()
        (project / ".git").mkdir()
        hooks = self.root / "user-hooks.json"
        previous = {"description": "keep me", "hooks": {"PreCompact": [{"matcher": "auto", "hooks": [
            {"type": "command", "command": "existing-command", "timeout": 60}]}]}}
        hooks.write_text(json.dumps(previous), encoding="utf-8")
        return project, hooks, previous

    def test_install_plan_has_no_side_effects_and_default_off(self):
        project, hooks, previous = self.install_target()
        result = installer.install([{"root": str(project)}], self.root / "runtime", hooks, [self.sessions])
        self.assertEqual("plan", result["action"])
        self.assertFalse(result["enabled"])
        self.assertFalse((project / ".codex").exists())
        self.assertFalse((self.root / "runtime").exists())
        self.assertEqual(previous, obs.read_json(hooks))

    def test_install_is_additive_idempotent_and_preserves_project_id(self):
        project, hooks, previous = self.install_target()
        arguments = ([{"root": str(project)}], self.root / "runtime", hooks, [self.sessions])
        result = installer.install(*arguments, enabled=True, write=True)
        first_manifest = obs.read_json(result["manifest"])
        first_hooks = hooks.read_bytes()
        again = installer.install(*arguments, enabled=True, write=True)
        self.assertEqual(0, again["new_hook_groups"])
        self.assertEqual(first_manifest, obs.read_json(result["manifest"]))
        self.assertEqual(first_hooks, hooks.read_bytes())
        self.assertEqual(previous["hooks"]["PreCompact"], obs.read_json(hooks)["hooks"]["PreCompact"])
        self.assertEqual("*\n", (project / ".codex/telemetry/.gitignore").read_text(encoding="utf-8"))
        self.assertEqual("requires_host_review", result["native_hook_trust"])

    def test_exact_installed_hook_command_transports_stdin(self):
        project, hooks, _ = self.install_target()
        result = installer.install([{"root": str(project)}], self.root / "runtime", hooks, [self.sessions], enabled=True, write=True)
        command = obs.read_json(hooks)["hooks"]["Stop"][0]["hooks"][0]["command"]
        payload = dict(self.payload, cwd=str(project))
        process = subprocess.run(command if sys.platform == "win32" else __import__("shlex").split(command),
                                 input=json.dumps(payload), text=True, capture_output=True)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual({}, json.loads(process.stdout))
        summary = obs.summarize(obs.read_json(result["manifest"]))
        self.assertEqual(1, summary["projects"][0]["observed_events"])

    def test_installed_command_exits_before_stdin_eof(self):
        project, hooks, _ = self.install_target()
        result = installer.install([{"root": str(project)}], self.root / "runtime", hooks, [self.sessions], enabled=True, write=True)
        command = obs.read_json(hooks)["hooks"]["Stop"][0]["hooks"][0]["command"]
        self.open_pipe_hook(command if sys.platform == "win32" else __import__("shlex").split(command),
                            [json.dumps(dict(self.payload, cwd=str(project))).encode("utf-8")])
        self.assertEqual(1, obs.summarize(obs.read_json(result["manifest"]))["projects"][0]["observed_events"])

    def test_install_conflicts_do_not_replace_user_hooks(self):
        project, hooks, _ = self.install_target()
        (project / ".codex/telemetry").mkdir(parents=True)
        before = hooks.read_bytes()
        with self.assertRaises(ValueError):
            installer.install([{"root": str(project)}], self.root / "runtime", hooks, [self.sessions], enabled=True, write=True)
        self.assertEqual(before, hooks.read_bytes())
        self.assertFalse((self.root / "runtime").exists())

    def legacy_installation(self):
        project, hooks, previous_hooks = self.install_target()
        old_source = self.root / "workflow_observation.py"
        old_source.write_bytes(SCRIPT.read_bytes() + b"\n# previous revision\n")
        with patch.object(installer, "SOURCE", old_source):
            result = installer.install([{"root": str(project)}], self.root / "runtime", hooks, [self.sessions], enabled=True, write=True)
        return project, hooks, previous_hooks, obs.read_json(result["manifest"])

    def test_explicit_upgrade_preserves_data_identity_switches_and_other_hooks(self):
        project, hooks, previous_hooks, before = self.legacy_installation()
        config = project / ".codex/telemetry/config.json"
        config.write_bytes(b'{"schema_version":1,"enabled":false}\n')
        events = project / ".codex/telemetry/events-2020-01-01.jsonl"
        events.write_bytes(b'{"keep":"historical"}\n')
        arguments = (before["projects"], self.root / "runtime", hooks, before["transcript_roots"])
        old_hooks = hooks.read_bytes()
        plan = installer.install(*arguments, upgrade=True)
        self.assertEqual(5, plan["updated_hook_groups"])
        self.assertEqual(old_hooks, hooks.read_bytes())
        self.assertEqual(before, obs.read_json(self.root / "runtime/installation.json"))
        result = installer.install(*arguments, upgrade=True, write=True)
        after = obs.read_json(result["manifest"])
        for field in ("salt", "projects", "enabled", "transcript_roots"):
            self.assertEqual(before[field], after[field])
        self.assertEqual(hashlib.sha256(SCRIPT.read_bytes()).hexdigest(), after["collector_revision"])
        self.assertEqual(b'{"schema_version":1,"enabled":false}\n', config.read_bytes())
        self.assertEqual(b'{"keep":"historical"}\n', events.read_bytes())
        self.assertEqual(previous_hooks["hooks"]["PreCompact"], obs.read_json(hooks)["hooks"]["PreCompact"])
        again = installer.install(*arguments, upgrade=True, write=True)
        self.assertEqual(0, again["updated_hook_groups"])
        self.assertEqual(0, again["new_hook_groups"])

    def test_upgrade_rejects_modified_hook_without_writes(self):
        project, hooks, _, before = self.legacy_installation()
        document = obs.read_json(hooks)
        document["hooks"]["Stop"][0]["hooks"][0]["command"] = "unknown-user-command"
        hooks.write_text(json.dumps(document), encoding="utf-8")
        old_hooks = hooks.read_bytes()
        with self.assertRaises(ValueError):
            installer.install(before["projects"], self.root / "runtime", hooks, before["transcript_roots"], upgrade=True, write=True)
        self.assertEqual(old_hooks, hooks.read_bytes())
        self.assertEqual(before, obs.read_json(self.root / "runtime/installation.json"))

    def test_upgrade_rejects_scope_changes_without_writes(self):
        project, hooks, _, before = self.legacy_installation()
        extra = self.root / "new worktree"
        extra.mkdir()
        selection = [{"root": str(project), "worktrees": [str(project), str(extra)]}]
        old_hooks = hooks.read_bytes()
        with self.assertRaises(ValueError):
            installer.install(selection, self.root / "runtime", hooks, before["transcript_roots"], upgrade=True, write=True)
        self.assertEqual(old_hooks, hooks.read_bytes())
        self.assertEqual(before, obs.read_json(self.root / "runtime/installation.json"))


if __name__ == "__main__":
    unittest.main()
