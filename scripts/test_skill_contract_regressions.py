#!/usr/bin/env python3
"""Adversarial contract tests; fixtures never access real projects or model APIs."""

from __future__ import annotations

import json
import itertools
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


class PromptContractTests(unittest.TestCase):
    def prompt(self, *args):
        return renderer.build_prompt(renderer.parse_args([
            "--role", "开发", "--objective", "修改单个常量", "--source-role", "开发",
            "--source-thread", "fixture-owner", "--allow", "src/constant.py",
            "--read-first", "task-card.md@baseline", "--validation", "python -m unittest",
            "--exit-condition", "单测通过，否则 STOP", *args]))

    def errors(self, text):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "prompt.md"
            path.write_text(text, encoding="utf-8")
            return validator.validate_prompt(path).errors

    def test_executor_does_not_inherit_owner_closure(self):
        for tier, profile in itertools.product(("mechanical", "bounded", "semantic"),
                                               ("auto", "compact", "standard", "full")):
            with self.subTest(tier=tier, profile=profile):
                text = self.prompt("--executor-tier", tier, "--profile", profile)
                self.assertIn("actor-kind：executor", text)
                self.assertIn("fanout-policy：forbidden", text)
                self.assertNotIn("更新 .codex/role-windows.md 并提交", text)
                self.assertNotIn("串行使用一个一次性 worker", text)
                self.assertNotIn("技能路由台账", text)
                self.assertLess(len(text), 1500)
                self.assertEqual(self.errors(text), [])
                bad = text + "\n闭环完成条件：更新 .codex/role-windows.md 并提交\n"
                self.assertTrue(self.errors(bad))
                self.assertTrue(self.errors(text.replace("fanout-policy：forbidden", "fanout-policy：required")))

    def test_executor_cannot_fan_out(self):
        with self.assertRaisesRegex(ValueError, "one-shot executor.*serial"):
            self.prompt("--executor-tier", "bounded", "--execution-profile", "parallel",
                        "--worker-count", "2", "--disjoint-scope", "two files",
                        "--independent-validation", "two tests")

    def test_explicit_codegraph_check_survives_short_templates(self):
        for tier in ("owner", "mechanical"):
            text = self.prompt("--executor-tier", tier, "--profile", "compact", "--codegraph-policy", "check")
            self.assertIn("CodeGraph policy：check", text)
            self.assertIn("门禁结果：只读检查未就绪", text)
            self.assertEqual(self.errors(text), [])

    def test_l3_gates_survive_every_display_profile(self):
        for risk, depth, profile in itertools.product(("normal", "critical", "extreme"),
                ("L0", "L1", "L2", "L3"), ("auto", "compact", "standard", "full")):
            if risk == "normal" and depth != "L3":
                continue
            with self.subTest(risk=risk, depth=depth, profile=profile):
                text = self.prompt("--risk", risk, "--loop-depth", depth, "--profile", profile)
                for field in ("独立复核角色与证据", "失败/回滚条件与执行责任人",
                              "未解决风险、剩余不确定性与影响范围", "最终 go/no-go 决策方"):
                    self.assertIn(field + "：", text)
                    self.assertTrue(self.errors(text.replace(field + "：", "omitted：")))
                self.assertEqual(self.errors(text), [])


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
