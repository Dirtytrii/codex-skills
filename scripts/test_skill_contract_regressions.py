#!/usr/bin/env python3
"""Adversarial contract tests; fixtures never access real projects or model APIs."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "skills" / "agent-role-orchestrator" / "scripts"))
import check_codegraph as graph
import render_role_prompt as renderer
import validate_role_loop as validator


class CodeGraphSchemaTests(unittest.TestCase):
    def status(self, payload: object) -> dict:
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            (project / ".codegraph").mkdir()
            completed = subprocess.CompletedProcess([], 0, json.dumps(payload), "")
            with patch.object(graph.subprocess, "run", return_value=completed) as run:
                status = graph.build_status(project, "fixture-codegraph")
            self.assertEqual(run.call_count, 1)
            self.assertEqual(run.call_args.args[0][1:3], ["status", "--json"])
            return status

    def fresh(self) -> dict:
        return {"initialized": True,
                "pendingChanges": {"added": 0, "modified": 0, "removed": 0},
                "worktreeMismatch": None}

    def test_fresh_stale_and_mismatched_states(self):
        self.assertTrue(self.status(self.fresh())["ready"])
        for change in ({"modified": 10}, {"added": 1}, {"removed": 2}):
            payload = self.fresh()
            payload["pendingChanges"].update(change)
            self.assertFalse(self.status(payload)["ready"])
        for mismatch in (True, {"expected": "one", "actual": "two"}):
            payload = self.fresh()
            payload["worktreeMismatch"] = mismatch
            self.assertFalse(self.status(payload)["ready"])

    def test_unknown_schema_never_becomes_ready(self):
        invalid = [{"pendingChanges": {}},
                   {"initialized": True, "pendingChanges": {"modified": "10"}}]
        for field in ("initialized", "pendingChanges", "worktreeMismatch"):
            payload = self.fresh()
            del payload[field]
            invalid.append(payload)
        for value in ("0", "10", True, False, -1, 0.0, None):
            payload = self.fresh()
            payload["pendingChanges"]["modified"] = value
            invalid.append(payload)
        for value in (None, "true", 1):
            payload = self.fresh()
            payload["initialized"] = value
            invalid.append(payload)
        for value in ({}, [], "", 0):
            payload = self.fresh()
            payload["worktreeMismatch"] = value
            invalid.append(payload)
        for payload in invalid:
            with self.subTest(payload=payload):
                status = self.status(payload)
                self.assertFalse(status["ready"])
                self.assertFalse(status["status_checked"])
                self.assertEqual(status["freshness_status"], "无法确认")
                self.assertTrue(status["status_parse_error"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
