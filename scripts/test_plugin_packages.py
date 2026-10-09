#!/usr/bin/env python3
"""Regression tests for core and domain plugin packaging."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from plugin_packages import CATALOG_TARGET, compare_skill_trees, load_package_specs
from validate_plugins import validate


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
PLUGIN_GUIDE = ROOT / "docs" / "plugin-packaging.md"
PACKAGE_REGISTRY = ROOT / "registry" / "plugin-packages.json"
BUNDLED_PACKAGE_REGISTRY = (
    ROOT
    / "plugins"
    / "codex-skills-core"
    / "registry"
    / "plugin-packages.json"
)


def run(args: list[str], check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def test_marketplace_and_package_registry_are_valid() -> None:
    errors, report = validate()
    assert errors == []
    assert report["canonical_public_skills"] == 68
    packages = report["packages"]
    assert [item["name"] for item in packages] == [
        "codex-skills-core",
        "codex-skills-engineering",
        "codex-skills-operations",
        "codex-skills-content",
        "codex-skills-visual-delivery",
    ]
    assert [item["name"] for item in packages if item["default_install"]] == [
        "codex-skills-core"
    ]
    assert all(
        item["catalog_chars"] <= CATALOG_TARGET
        for item in report["default_plus_domain"]
    )


def test_generated_bundles_are_exact_copies() -> None:
    result = run([PYTHON, "scripts/sync_plugin_bundles.py", "--check"])
    assert "match canonical skills" in result.stdout


def test_context_audit_adds_core_and_reports_legacy_duplicates() -> None:
    with tempfile.TemporaryDirectory() as temp:
        home = Path(temp)
        legacy = home / ".codex" / "skills" / "humanizer-zh"
        legacy.mkdir(parents=True)
        (legacy / "SKILL.md").write_text("---\nname: humanizer-zh\n---\n", encoding="utf-8")
        result = run(
            [
                PYTHON,
                "scripts/audit_plugin_context.py",
                "--plugin",
                "codex-skills-content",
                "--scan-user-roots",
                "--home",
                str(home),
                "--strict",
                "--json",
            ]
        )
        report = json.loads(result.stdout)
        assert report["selected_plugins"] == [
            "codex-skills-core",
            "codex-skills-content",
        ]
        assert report["within_target"] is True
        assert report["legacy_root_scan"][1]["duplicates_selected_plugins"] == [
            "humanizer-zh"
        ]


def test_context_audit_fails_closed_for_oversized_multi_domain_set() -> None:
    result = run(
        [
            PYTHON,
            "scripts/audit_plugin_context.py",
            "--plugin",
            "codex-skills-content",
            "--plugin",
            "codex-skills-visual-delivery",
            "--strict",
            "--json",
        ],
        check=False,
    )
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["catalog_chars"] > CATALOG_TARGET
    assert report["within_target"] is False


def test_tree_comparison_detects_changed_and_stale_files() -> None:
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        source = root / "source"
        bundle = root / "bundle"
        source.mkdir()
        bundle.mkdir()
        (source / "SKILL.md").write_text("source", encoding="utf-8")
        (bundle / "SKILL.md").write_text("changed", encoding="utf-8")
        (bundle / "stale.txt").write_text("stale", encoding="utf-8")
        errors = compare_skill_trees(source, bundle)
        assert "changed bundled file: SKILL.md" in errors
        assert "stale bundled file: stale.txt" in errors


def test_package_registry_source_stays_canonical() -> None:
    source_root, specs, marketplace = load_package_specs()
    assert source_root == (ROOT / "skills").resolve()
    assert marketplace == "dirtytrii-codex-skills"
    assert len({skill for spec in specs for skill in spec.skills}) == 68
    expected_roles = {
        "总控",
        "架构",
        "开发",
        "UI/PPT",
        "测试",
        "QA",
        "安全",
        "DBA",
        "运维",
        "内容主编",
        "公众号发布",
        "小红书",
        "视频",
        "知识库",
        "技能维护",
        "文档/交付",
    }
    assert {role for spec in specs for role in spec.roles} == expected_roles
    assert sum(len(spec.roles) for spec in specs) == len(expected_roles)


def test_core_bundles_runtime_plugin_registry() -> None:
    assert BUNDLED_PACKAGE_REGISTRY.read_bytes() == PACKAGE_REGISTRY.read_bytes()


def test_documented_package_metrics_match_validator() -> None:
    errors, report = validate()
    assert errors == []
    guide = PLUGIN_GUIDE.read_text(encoding="utf-8")
    for item in report["packages"]:
        assert f"| `{item['name']}` |" in guide
        assert f"| {item['catalog_chars']} |" in guide
    assert "目录估算" in guide


def main() -> int:
    tests = [
        test_marketplace_and_package_registry_are_valid,
        test_generated_bundles_are_exact_copies,
        test_context_audit_adds_core_and_reports_legacy_duplicates,
        test_context_audit_fails_closed_for_oversized_multi_domain_set,
        test_tree_comparison_detects_changed_and_stale_files,
        test_package_registry_source_stays_canonical,
        test_core_bundles_runtime_plugin_registry,
        test_documented_package_metrics_match_validator,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    print(f"Passed {len(tests)} plugin packaging tests.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
