#!/usr/bin/env python3
"""Move broad leaf skills behind agent-role-orchestrator progressive loading."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
ORCHESTRATOR = SKILLS / "agent-role-orchestrator"
BUNDLES = ORCHESTRATOR / "references" / "skills"
REGISTRY = ROOT / "registry" / "skills.json"

GSTACK_LEAVES = (
    "gstack-autoplan",
    "gstack-canary",
    "gstack-careful",
    "gstack-cso",
    "gstack-design-consultation",
    "gstack-design-html",
    "gstack-design-review",
    "gstack-design-shotgun",
    "gstack-devex-review",
    "gstack-document-generate",
    "gstack-document-release",
    "gstack-freeze",
    "gstack-guard",
    "gstack-health",
    "gstack-investigate",
    "gstack-land-and-deploy",
    "gstack-learn",
    "gstack-office-hours",
    "gstack-plan-ceo-review",
    "gstack-plan-design-review",
    "gstack-plan-devex-review",
    "gstack-plan-eng-review",
    "gstack-plan-tune",
    "gstack-qa",
    "gstack-qa-only",
    "gstack-retro",
    "gstack-review",
    "gstack-setup-deploy",
    "gstack-ship",
    "gstack-spec",
    "gstack-unfreeze",
)

PLATFORM_SKILLS = (
    "wechat-ai-app-ops",
    "wechat-article-formatter",
    "wechat-tech-writer",
    "xhs-automation-publisher",
    "xhs-comment-research",
    "xhs-publish-assistant",
    "xhs-short-video-workflow",
    "xhs-visual-director",
)

OPS_SKILLS = (
    "application-problem-diagnosis-workflow",
    "package-update-check-and-plan",
    "post-deployment-readonly-verification",
    "pre-deployment-readonly-checklist",
    "proxy-dependent-python-service-diagnosis",
    "python-project-deployment-troubleshooting",
    "hermes-cron-empty-output-diagnosis",
    "hermes-python-script-wrapper-for-shell-cron",
)

CONTENT_GATES = (
    "content-model-handoff",
    "content-style-calibration-loop",
    "social-text-websense-gate",
)

BUNDLE_NAMES = GSTACK_LEAVES + PLATFORM_SKILLS + OPS_SKILLS + CONTENT_GATES
BUNDLE_NOTICE = """
## Bundled Reference Contract

This is an on-demand method bundled by `agent-role-orchestrator`, not an independently discoverable skill. Load it only after the orchestrator routes the current role and task here. Resolve `scripts/`, `references/`, and `assets/` relative to this file's directory. Do not scan or preload sibling bundles.
""".strip()


def add_bundle_notice(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "## Bundled Reference Contract" in text:
        return
    lines = text.splitlines()
    delimiters = [index for index, line in enumerate(lines) if line.strip() == "---"]
    insert_at = delimiters[1] + 1 if len(delimiters) >= 2 else 0
    updated = lines[:insert_at] + ["", BUNDLE_NOTICE, ""] + lines[insert_at:]
    path.write_text("\n".join(updated).rstrip() + "\n", encoding="utf-8")


def update_registry() -> None:
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    bundled = set(BUNDLE_NAMES)
    registry = [entry for entry in registry if entry.get("name") not in bundled]
    orchestrator = next(entry for entry in registry if entry.get("name") == "agent-role-orchestrator")
    orchestrator["bundled_skills"] = list(BUNDLE_NAMES)
    orchestrator["summary"] = (
        "总控/CEO 先行的角色编排与按需方法路由，含 L0-L3 loop、CTO 技术闭环、"
        "Terra/Sol/Mini/Luna 模型分层、内容主编、微信/小红书、Hermes/部署诊断、"
        "31 个 gstack 叶子方法、内容模型交接、反老登味/反AI味内容闸门、"
        "UI预览图实现路线选择、fail-closed 台账回调、来源thread压缩回调闭环、"
        "CodeGraph 检查和技能命中治理"
    )
    REGISTRY.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def apply() -> list[str]:
    errors: list[str] = []
    BUNDLES.mkdir(parents=True, exist_ok=True)
    for name in BUNDLE_NAMES:
        source = SKILLS / name
        target = BUNDLES / name
        if source.exists() and target.exists():
            errors.append(f"both standalone and bundled paths exist: {name}")
            continue
        if source.exists():
            shutil.move(str(source), str(target))
        elif not target.exists():
            errors.append(f"missing source skill: {name}")
            continue

        skill_md = target / "SKILL.md"
        reference_md = target / "REFERENCE.md"
        if skill_md.exists() and reference_md.exists():
            errors.append(f"both SKILL.md and REFERENCE.md exist: {name}")
            continue
        if skill_md.exists():
            skill_md.rename(reference_md)
        if not reference_md.exists():
            errors.append(f"missing bundled reference: {name}")
            continue
        add_bundle_notice(reference_md)

    if not errors:
        update_registry()
    return errors


def check() -> list[str]:
    errors: list[str] = []
    for name in BUNDLE_NAMES:
        if (SKILLS / name).exists():
            errors.append(f"standalone skill still exists: {name}")
        target = BUNDLES / name
        if not (target / "REFERENCE.md").is_file():
            errors.append(f"missing REFERENCE.md: {name}")
        if (target / "SKILL.md").exists():
            errors.append(f"discoverable SKILL.md remains in bundle: {name}")

    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    registry_names = {entry.get("name") for entry in registry}
    leaked = sorted(set(BUNDLE_NAMES) & registry_names)
    if leaked:
        errors.append("bundled names remain in registry: " + ", ".join(leaked))
    orchestrator = next((entry for entry in registry if entry.get("name") == "agent-role-orchestrator"), None)
    if orchestrator is None:
        errors.append("registry missing agent-role-orchestrator")
    elif orchestrator.get("bundled_skills") != list(BUNDLE_NAMES):
        errors.append("agent-role-orchestrator bundled_skills manifest does not match")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true", help="Move standalone skill folders into on-demand bundles.")
    args = parser.parse_args()

    errors = apply() if args.apply else check()
    if errors:
        print("Bundle validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    print(f"Validated {len(BUNDLE_NAMES)} on-demand skill bundles.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
