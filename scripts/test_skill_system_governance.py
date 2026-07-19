#!/usr/bin/env python3
"""Regression tests for the skill-system-governance audit entrypoint."""

from __future__ import annotations

import argparse
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT_SCRIPT = (
    ROOT
    / "skills"
    / "skill-system-governance"
    / "scripts"
    / "audit_skill_system.py"
)


def load_audit_module():
    spec = importlib.util.spec_from_file_location("audit_skill_system", AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Cannot load {AUDIT_SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class AuditPlanTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = load_audit_module()

    def test_quick_plan_is_read_only_and_exposes_unavailable_evidence(self) -> None:
        plans = self.audit.build_check_plans(ROOT, "quick", None, [])

        self.assertEqual(
            [plan.name for plan in plans],
            [
                "catalog",
                "public_skills",
                "role_system",
                "plugins",
                "bundle_sync",
                "routing_cases",
                "routing_observed",
                "skill_hits",
            ],
        )
        commands = [part for plan in plans if plan.command for part in plan.command]
        self.assertNotIn("--write", commands)
        bundle = next(plan for plan in plans if plan.name == "bundle_sync")
        self.assertIn("--check", bundle.command)
        optional = {plan.name: plan for plan in plans[-2:]}
        self.assertIsNone(optional["routing_observed"].command)
        self.assertIsNone(optional["skill_hits"].command)
        self.assertFalse(optional["routing_observed"].required)
        self.assertFalse(optional["skill_hits"].required)

    def test_full_plan_adds_slow_regression_suites(self) -> None:
        plans = self.audit.build_check_plans(ROOT, "full", None, [])

        self.assertEqual(
            [plan.name for plan in plans[-2:]],
            ["role_tests", "plugin_tests"],
        )
        self.assertTrue(all(plan.required for plan in plans[-2:]))

    def test_observed_routing_and_callbacks_become_executable_checks(self) -> None:
        observed = ROOT / "observed.jsonl"
        callbacks = [ROOT / "callback-a.md", ROOT / "callback-b.md"]

        plans = self.audit.build_check_plans(ROOT, "quick", observed, callbacks)
        by_name = {plan.name: plan for plan in plans}

        self.assertIn("--observed", by_name["routing_observed"].command)
        self.assertIn(str(observed), by_name["routing_observed"].command)
        self.assertEqual(
            list(by_name["skill_hits"].command[-2:]),
            [str(callbacks[0]), str(callbacks[1])],
        )

    def test_invalid_repository_layout_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            stdout = io.StringIO()
            stderr = io.StringIO()
            with redirect_stdout(stdout), redirect_stderr(stderr):
                exit_code = self.audit.main(["--repo", temp_dir, "--json"])

        self.assertEqual(exit_code, 2)
        payload = json.loads(stdout.getvalue())
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["status"], "invalid_repository")

    def test_output_tail_decodes_timeout_bytes(self) -> None:
        self.assertEqual(self.audit.output_tail("first\nlast".encode()), "first\nlast")

    def test_timeout_must_be_positive(self) -> None:
        with self.assertRaises(argparse.ArgumentTypeError):
            self.audit.positive_int("0")


class AuditIntegrationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.audit = load_audit_module()

    def test_quick_audit_passes_current_repository(self) -> None:
        report = self.audit.run_audit(ROOT, "quick", None, [], timeout=180)

        self.assertTrue(report["ok"], report)
        results = {item["name"]: item for item in report["checks"]}
        self.assertTrue(
            all(results[name]["status"] == "passed" for name in self.audit.QUICK_CHECK_NAMES)
        )
        self.assertEqual(results["routing_observed"]["status"], "not_evaluable")
        self.assertEqual(results["skill_hits"]["status"], "not_evaluable")


if __name__ == "__main__":
    unittest.main()
