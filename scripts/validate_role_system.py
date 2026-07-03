#!/usr/bin/env python3
"""Validate the reusable role-system contract for PR checks."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
README = ROOT / "README.md"
ROLE_USAGE = ROOT / "docs" / "role-usage.md"
PUBLICATION_CHECKLIST = ROOT / "docs" / "publication-checklist.md"
REGISTRY = ROOT / "registry" / "skills.json"
ORCHESTRATOR = ROOT / "skills" / "agent-role-orchestrator"
SKILL_MD = ORCHESTRATOR / "SKILL.md"
ROLE_CARDS = ORCHESTRATOR / "references" / "role-cards.md"
RENDER_PROMPT = ORCHESTRATOR / "scripts" / "render_role_prompt.py"
VALIDATE_LOOP = ORCHESTRATOR / "scripts" / "validate_role_loop.py"
ENSURE_FILES = ORCHESTRATOR / "scripts" / "ensure_project_role_files.py"
CHECK_CODEGRAPH = ORCHESTRATOR / "scripts" / "check_codegraph.py"
AGGREGATE_SKILL_HITS = ORCHESTRATOR / "scripts" / "aggregate_skill_hits.py"
ROLE_SCRIPTS = (RENDER_PROMPT, VALIDATE_LOOP, ENSURE_FILES, CHECK_CODEGRAPH, AGGREGATE_SKILL_HITS)


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def run(args: list[str], errors: list[str], expect_success: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if expect_success and result.returncode != 0:
        errors.append(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    if not expect_success and result.returncode == 0:
        errors.append(
            f"command unexpectedly succeeded: {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )
    return result


def require_contains(path: Path, needles: list[str], errors: list[str]) -> None:
    text = read(path)
    for needle in needles:
        if needle not in text:
            errors.append(f"{path.relative_to(ROOT)} missing required text: {needle}")


def validate_docs(errors: list[str]) -> None:
    require_contains(
        README,
        [
            "总控 / CEO",
            "架构 / CTO",
            "内容主编",
            "Fail-Closed Tool Layer",
            "render_role_prompt.py",
            "validate_role_loop.py",
            "ensure_project_role_files.py",
            "check_codegraph.py",
            "aggregate_skill_hits.py",
            "上下文预算",
            "Token Budget Profile",
            "`compact`",
            "`standard`",
            "`full`",
            "Loop 深度",
            "总控只直接对接负责人层",
            "开发负责人 / Dev Lead",
            "开发执行 subagent",
            "窗口内一次性",
            "X MCP 内容研究源",
            "https://docs.x.com/tools/mcp",
            "反老登味 / 反 AI 味内容闸门",
            "预览图实现路线选择",
            "仅完成台账更新不算闭环",
            "<codex_delegation>",
            "gpt-5.5` + `medium",
        ],
        errors,
    )
    require_contains(
        ROLE_USAGE,
        [
            "总控 / CEO",
            "架构 / CTO",
            "内容主编",
            "Fail-Closed 工具层",
            "render_role_prompt.py",
            "validate_role_loop.py",
            "ensure_project_role_files.py",
            "check_codegraph.py",
            "aggregate_skill_hits.py",
            "压缩交接卡",
            "Token Budget Profile",
            "`compact`",
            "`standard`",
            "`full`",
            "Loop 深度",
            "总控只直接对接负责人层",
            "开发负责人 / Dev Lead",
            "开发执行 subagent",
            "窗口内一次性",
            "X MCP 内容研究源",
            "https://docs.x.com/tools/mcp",
            "反老登味 / 反 AI 味内容闸门",
            "预览图实现路线选择",
            "仅完成第 1 项不算闭环",
            "<codex_delegation>",
            "gpt-5.5` + `medium",
        ],
        errors,
    )
    require_contains(PUBLICATION_CHECKLIST, ["validate_role_system.py", "ensure_project_role_files.py"], errors)


def validate_orchestrator(errors: list[str]) -> None:
    require_contains(
        SKILL_MD,
        [
            "Fail-Closed Tool Layer Rule",
            "render_role_prompt.py",
            "validate_role_loop.py",
            "ensure_project_role_files.py",
            "check_codegraph.py",
            "aggregate_skill_hits.py",
            "总控 / CEO",
            "架构 / CTO",
            "内容主编",
            "模型建议：",
            "技能命中回传：",
            "上下文预算",
            "Token Budget Profile Rule",
            "--profile auto",
            "`compact`",
            "`standard`",
            "`full`",
            "Loop Depth And Owner-Layer Routing Rule",
            "负责人交互边界",
            "开发负责人",
            "开发执行 subagent",
            "in-window one-shot",
            "X MCP Content Research Source",
            "https://docs.x.com/tools/mcp",
            "Content Tone Gate",
            "反老登味 / 反 AI 味内容闸门",
            "UI Preview Implementation Route Rule",
            "不要默认拿 CSS 硬干",
            "Completion is fail-closed",
            "仅完成第 1 项不算闭环",
            "<codex_delegation>",
            "gpt-5.5` + `medium",
        ],
        errors,
    )
    require_contains(
        ROLE_CARDS,
        [
            "## 总控",
            "Act as `架构` / `CTO`",
            "## 内容主编",
            "ensure_project_role_files.py",
            "validate_role_loop.py",
            "check_codegraph.py",
            "aggregate_skill_hits.py",
            "Token Budget Profile",
            "--profile auto",
            "反老登味 / 反 AI 味内容闸门",
            "预览图实现路线选择",
            "preview implementation route decision",
            "fail-closed callback status",
        ],
        errors,
    )


def validate_registry(errors: list[str]) -> None:
    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"cannot parse registry/skills.json: {exc}")
        return

    item = next((entry for entry in registry if entry.get("name") == "agent-role-orchestrator"), None)
    if not item:
        errors.append("registry missing agent-role-orchestrator")
        return

    roles = set(item.get("consumed_by_roles") or [])
    missing_roles = {"总控", "架构", "内容主编"} - roles
    if missing_roles:
        errors.append("agent-role-orchestrator registry missing consumed_by_roles: " + "、".join(sorted(missing_roles)))

    summary = item.get("summary", "")
    for needle in ("总控/CEO", "CTO", "内容主编", "反老登味/反AI味内容闸门", "UI预览图实现路线选择", "来源thread压缩回调闭环", "fail-closed"):
        if needle not in summary:
            errors.append(f"agent-role-orchestrator summary missing: {needle}")


def validate_scripts(errors: list[str]) -> None:
    for script in ROLE_SCRIPTS:
        if not script.is_file():
            errors.append(f"missing role-system script: {script.relative_to(ROOT)}")

    require_contains(
        RENDER_PROMPT,
        ["--profile", "effective_token_profile", "build_compact_prompt", "Token Budget Profile"],
        errors,
    )
    run([PYTHON, "-m", "py_compile", *(str(script) for script in ROLE_SCRIPTS), str(Path(__file__))], errors)

    with tempfile.TemporaryDirectory() as temp:
        temp_path = Path(temp)
        prompt = temp_path / "prompt.md"
        good_callback = temp_path / "good-callback.md"
        bad_callback = temp_path / "bad-callback.md"
        project = temp_path / "project"
        project.mkdir()

        run(
            [
                PYTHON,
                str(RENDER_PROMPT),
                "--role",
                "开发",
                "--objective",
                "实现订单列表筛选修复",
                "--source-role",
                "架构",
                "--source-thread",
                "thread-123",
                "--read-orchestrator",
                "--read-ledger",
                "--required-skill",
                "gstack-investigate",
                "--validation",
                "npm test",
                "--output",
                str(prompt),
            ],
            errors,
        )
        run([PYTHON, str(VALIDATE_LOOP), "--prompt", str(prompt)], errors)
        if prompt.exists():
            prompt_text = prompt.read_text(encoding="utf-8")
            if "profile：compact" not in prompt_text:
                errors.append("render_role_prompt.py auto profile did not compact an L1 execution prompt")

        good_callback.write_text(
            """压缩回调：
- 当前状态：完成
- 本轮变化：已实现并验证订单列表筛选修复
- 证据链接/文件/命令：npm test
- 需要决策：无
- 下一回流对象：架构
技能命中回传：
- 已加载并使用：gstack-investigate
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：gstack-investigate
规则沉淀：
- 可复用优化沉淀：无
""",
            encoding="utf-8",
        )
        bad_callback.write_text(
            """压缩回调：
- 当前状态：完成
- 本轮变化：修复
- 证据链接/文件/命令：npm test
- 需要决策：无
- 下一回流对象：
技能命中回传：
- 已加载并使用：
- 来源窗口要求但未使用：
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：无
规则沉淀：
- 可复用优化沉淀：无
""",
            encoding="utf-8",
        )
        run([PYTHON, str(VALIDATE_LOOP), "--callback", str(good_callback), "--required-skill", "gstack-investigate"], errors)
        run(
            [PYTHON, str(VALIDATE_LOOP), "--callback", str(bad_callback), "--required-skill", "gstack-investigate"],
            errors,
            expect_success=False,
        )

        dry_run = run([PYTHON, str(ENSURE_FILES), "--project", str(project)], errors)
        if "DRY-RUN" not in dry_run.stdout:
            errors.append("ensure_project_role_files dry-run did not report DRY-RUN")
        if (project / "AGENTS.md").exists():
            errors.append("ensure_project_role_files created AGENTS.md without --write")

        run([PYTHON, str(ENSURE_FILES), "--project", str(project), "--write"], errors)
        agents = project / "AGENTS.md"
        ledger = project / ".codex" / "role-windows.md"
        if not agents.exists():
            errors.append("ensure_project_role_files --write did not create AGENTS.md")
        if not ledger.exists():
            errors.append("ensure_project_role_files --write did not create .codex/role-windows.md")
        if agents.exists() and agents.read_text(encoding="utf-8").count("BEGIN agent-role-orchestrator entry rule") != 1:
            errors.append("AGENTS.md managed block is missing or duplicated")
        if ledger.exists() and "| 总控 | 待确认 | 待确认 | 用户 | 入口分流" not in ledger.read_text(encoding="utf-8"):
            errors.append("role-windows.md missing default 总控 row")
        if agents.exists():
            agents_text = agents.read_text(encoding="utf-8")
            machine_path_fragment = "\\".join(["C:", "Users"]) + "\\"
            if machine_path_fragment in agents_text:
                errors.append("AGENTS.md template contains a machine-specific Windows user path")
        if ledger.exists() and "## 压缩交接卡" not in ledger.read_text(encoding="utf-8"):
            errors.append("role-windows.md missing 压缩交接卡 section")

        run([PYTHON, str(VALIDATE_LOOP), "--project", str(project)], errors)

        codegraph = run([PYTHON, str(CHECK_CODEGRAPH), "--project", str(project), "--json"], errors)
        try:
            codegraph_payload = json.loads(codegraph.stdout)
            if codegraph_payload.get("initialization_status") not in {"已初始化", "未初始化"}:
                errors.append("check_codegraph.py returned an invalid initialization_status")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"check_codegraph.py did not emit JSON: {exc}")

        aggregate = run([PYTHON, str(AGGREGATE_SKILL_HITS), str(good_callback), "--json"], errors)
        try:
            aggregate_payload = json.loads(aggregate.stdout)
            if aggregate_payload.get("required_skill_count") != 0:
                errors.append("aggregate_skill_hits.py should not infer required skills from callback-only fixture")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"aggregate_skill_hits.py did not emit JSON: {exc}")


def validate_no_machine_specific_paths(errors: list[str]) -> None:
    forbidden_fragments = [
        "\\".join(["C:", "Users"]) + "\\",
        "/".join(["C:", "Users", ""]),
        "12" + "156",
    ]
    allowed_suffixes = {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".jar", ".class", ".pyc"}
    for root_name in ("README.md", "docs", "registry", "scripts", "skills"):
        root = ROOT / root_name
        paths = [root] if root.is_file() else [path for path in root.rglob("*") if path.is_file()]
        for path in paths:
            if path.suffix.lower() in allowed_suffixes:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for fragment in forbidden_fragments:
                if fragment in text:
                    errors.append(f"{path.relative_to(ROOT)} contains machine-specific path fragment: {fragment}")


def main() -> int:
    errors: list[str] = []
    validate_docs(errors)
    validate_orchestrator(errors)
    validate_registry(errors)
    validate_scripts(errors)
    validate_no_machine_specific_paths(errors)

    if errors:
        print("Role system validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print("Role system validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
