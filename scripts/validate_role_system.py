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
TECHNICAL_HIGHLIGHTS = ROOT / "docs" / "technical-highlights.md"
BROWSER_AUTOMATION_DOC = ROOT / "docs" / "browser-automation.md"
ROLE_USAGE = ROOT / "docs" / "role-usage.md"
PUBLICATION_CHECKLIST = ROOT / "docs" / "publication-checklist.md"
REGISTRY = ROOT / "registry" / "skills.json"
ORCHESTRATOR = ROOT / "skills" / "agent-role-orchestrator"
SKILL_MD = ORCHESTRATOR / "SKILL.md"
ROLE_CARDS = ORCHESTRATOR / "references" / "role-cards.md"
MODEL_ROUTING = ORCHESTRATOR / "references" / "model-routing.md"
TOOL_ROUTING = ORCHESTRATOR / "references" / "tool-routing.md"
CONTENT_ROUTING = ORCHESTRATOR / "references" / "content-routing.md"
BROWSER_ROUTER = ROOT / "skills" / "browser-automation-router" / "SKILL.md"
PLAYWRIGHT_SKILL = ROOT / "skills" / "playwright" / "SKILL.md"
XHS_COMMENT_RESEARCH = ROOT / "skills" / "xhs-comment-research" / "SKILL.md"
XHS_CHROME_SNIPPETS = ROOT / "skills" / "xhs-comment-research" / "references" / "chrome-snippets.md"
XHS_AUTOMATION_PUBLISHER = ROOT / "skills" / "xhs-automation-publisher" / "SKILL.md"
UI_WORKFLOW = ROOT / "skills" / "ui-implementation-workflow" / "SKILL.md"
UI_SOURCE_CATALOG = UI_WORKFLOW.parent / "references" / "source-catalog.md"
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
            "任务分发决策",
            "`tiny`",
            "`small`",
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
            "小红书自动化发布门禁",
            "xhs-automation-publisher",
            "反老登味 / 反 AI 味内容闸门",
            "预览图实现路线选择",
            "仅完成台账更新不算闭环",
            "<codex_delegation>",
            "gpt-5.6-terra` + `high",
            "gpt-5.6-sol` + `xhigh",
            "gpt-5.6-luna` + `high",
            "gpt-5.3-codex-spark` + `high",
            "gpt-5.4-mini` + `high",
            "--execution-profile parallel",
            "--prefer-spark --spark-available",
            "docs/technical-highlights.md",
            "browser-automation-router",
            "docs/browser-automation.md",
            "2026-06-11",
            "ui-implementation-workflow",
            "1440/768/390",
            "动态换源",
        ],
        errors,
    )
    require_contains(
        TECHNICAL_HIGHLIGHTS,
        [
            "CEO-First 与负责人分层",
            "可折叠的 Multi-Window Loop",
            "Fail-Closed Tool Layer",
            "Token-Aware Prompt Architecture",
            "稳定模型路由与 Spark 机会通道",
            "可量化的 Skill Routing",
            "CodeGraph、开源参考与治理",
        ],
        errors,
    )
    require_contains(
        BROWSER_AUTOMATION_DOC,
        [
            "Support Floor",
            "2026-06-11",
            "Codex in-app Browser",
            "Codex Chrome extension",
            "Playwright",
            "Fail-Closed Checks",
        ],
        errors,
    )

    readme_text = read(README)
    if len(readme_text.splitlines()) > 260:
        errors.append(f"README.md exceeds line budget: {len(readme_text.splitlines())} > 260")
    if len(readme_text.encode("utf-8")) > 20000:
        errors.append(f"README.md exceeds byte budget: {len(readme_text.encode('utf-8'))} > 20000")
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
            "任务分发决策",
            "`tiny`",
            "`small`",
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
            "xhs-automation-publisher",
            "点击发布和互动动作二次授权",
            "反老登味 / 反 AI 味内容闸门",
            "预览图实现路线选择",
            "仅完成第 1 项不算闭环",
            "<codex_delegation>",
            "gpt-5.6-terra` + `high",
            "gpt-5.6-sol` + `xhigh",
            "gpt-5.6-luna` + `high",
            "gpt-5.3-codex-spark` + `high",
            "gpt-5.4-mini` + `high",
            "3-5 个 worker",
            "--prefer-spark --spark-available",
            "browser-automation-router",
            "原生 Chrome",
            "ui-implementation-workflow",
            "UI implementation plan",
            "1440/768/390",
            "换源台账",
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
            "CEO Task Dispatch Decision Rule",
            "--task-size tiny|small|medium|large|critical",
            "任务分发决策：",
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
            "Xiaohongshu Automation Publisher Gate",
            "$xhs-automation-publisher",
            "Content Tone Gate",
            "反老登味 / 反 AI 味内容闸门",
            "UI Preview Implementation Route Rule",
            "不要默认拿 CSS 硬干",
            "Completion is fail-closed",
            "仅完成第 1 项不算闭环",
            "<codex_delegation>",
            "gpt-5.6-terra` + `high",
            "gpt-5.6-sol` + `xhigh",
            "gpt-5.6-luna` + `high",
            "gpt-5.3-codex-spark",
            "gpt-5.4-mini` + `high",
            "Spark Opportunity Lane",
            "--prefer-spark --spark-available",
            "Native Browser Routing Rule",
            "$browser-automation-router",
            "$ui-implementation-workflow",
            "1440/768/390",
            "reference ledger",
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
            "任务分发决策",
            "--profile auto",
            "反老登味 / 反 AI 味内容闸门",
            "预览图实现路线选择",
            "preview implementation route decision",
            "$xhs-automation-publisher",
            "fail-closed callback status",
            "ui-implementation-workflow",
            "1440/768/390",
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
    for needle in ("总控/CEO", "CTO", "内容主编", "Luna 有界执行", "Spark 独立额度机会通道", "显式并行 worker 门禁", "原生 Browser/Chrome fail-closed 路由", "反老登味/反AI味内容闸门", "UI预览图实现路线选择", "来源thread压缩回调闭环", "fail-closed"):
        if needle not in summary:
            errors.append(f"agent-role-orchestrator summary missing: {needle}")

    browser_item = next((entry for entry in registry if entry.get("name") == "browser-automation-router"), None)
    if not browser_item:
        errors.append("registry missing browser-automation-router")
    else:
        for needle in ("Browser", "Chrome", "Playwright", "2026-06-11", "fail-closed"):
            if needle not in browser_item.get("summary", ""):
                errors.append(f"browser-automation-router summary missing: {needle}")

    ui_item = next((entry for entry in registry if entry.get("name") == "ui-implementation-workflow"), None)
    if not ui_item:
        errors.append("registry missing ui-implementation-workflow")
    else:
        for needle in ("页面分类", "完整参考源库存", "最多三份", "动态换源", "换源台账", "UI implementation plan", "语义 Token", "1440/768/390"):
            if needle not in ui_item.get("summary", ""):
                errors.append(f"ui-implementation-workflow summary missing: {needle}")


def validate_scripts(errors: list[str]) -> None:
    for script in ROLE_SCRIPTS:
        if not script.is_file():
            errors.append(f"missing role-system script: {script.relative_to(ROOT)}")

    require_contains(
        RENDER_PROMPT,
        [
            "--profile",
            "--task-size",
            "effective_token_profile",
            "task_dispatch_decision",
            "build_compact_prompt",
            "xhs_automation_publish_gate",
            "browser_automation_guidance",
            "BROWSER_ROLES",
            "$browser-automation-router",
            "Codex Desktop 2026-06-11",
            "gpt-5.6-terra",
            "gpt-5.6-sol",
            "gpt-5.6-luna",
            "gpt-5.3-codex-spark",
            "gpt-5.4-mini",
            "--executor-tier",
            "--prefer-spark",
            "--spark-available",
            "--execution-profile",
            "--worker-count",
            "--disjoint-scope",
            "--independent-validation",
            "Token Budget Profile",
            "任务分发决策",
            "ui_preview_route_guidance",
            "$ui-implementation-workflow",
            "UI implementation plan",
            "medium+：最多 3 份参考",
            "1440/768/390",
            "动态换源",
            "每轮只替换对应的一份参考",
            "tiny 不做外部换源",
            "medium+ 默认最多换源 2 轮",
        ],
        errors,
    )
    require_contains(
        MODEL_ROUTING,
        ["gpt-5.6-luna", "gpt-5.3-codex-spark", "gpt-5.4-mini", "gpt-5.6-terra", "gpt-5.6-sol", "Spark Opportunity Lane", "--prefer-spark --spark-available", "--execution-profile parallel", "--disjoint-scope", "--independent-validation"],
        errors,
    )
    require_contains(TOOL_ROUTING, ["Fail-Closed Scripts", "aggregate_skill_hits.py", "Skill Ledger", "$browser-automation-router", "$playwright", "$ui-implementation-workflow"], errors)
    require_contains(CONTENT_ROUTING, ["X MCP Content Research Source", "反老登味 / 反 AI 味内容闸门", "$browser-automation-router", "$xhs-automation-publisher"], errors)
    require_contains(BROWSER_ROUTER, ["Route Order", "2026-06-11", "existing Chrome profile", "Fail-Closed Capability Gate", "Write Gates"], errors)
    require_contains(PLAYWRIGHT_SKILL, ["deterministic CLI/CI lane", "$browser-automation-router", "Do not import cookies"], errors)
    require_contains(XHS_COMMENT_RESEARCH, ["$browser-automation-router", "Do not load repository-maintained JavaScript snippets", "Chrome plugin"], errors)
    require_contains(XHS_AUTOMATION_PUBLISHER, ["$browser-automation-router", "native Chrome surface", "deterministic Xiaohongshu batch/export fallback"], errors)
    require_contains(
        UI_WORKFLOW,
        [
            "Classify And Audit",
            "medium+",
            "UI Implementation Plan",
            "Semantic Tokens",
            "$browser-automation-router",
            "1440px",
            "768px",
            "390px",
            "first-pass screenshot",
            "Dynamic Reference Switching",
            "reference ledger",
            "Replace one role per iteration",
            "small` allows one switch round",
            "medium+` allows two switch rounds",
        ],
        errors,
    )
    require_contains(
        UI_SOURCE_CATALOG,
        [
            "Lapa Ninja",
            "Landing.love",
            "Landbook",
            "Recent.design",
            "Siteinspire",
            "shadcn/ui",
            "21st.dev",
            "Magic UI",
            "Aceternity UI",
            "React Bits",
            "Ant Design",
            "Element Plus",
            "Framer free templates",
            "Webflow free templates",
            "HTMLrev",
            "Dynamic Switch Matrix",
            "status: candidate | active | rejected | replaced",
            "license",
        ],
        errors,
    )
    if XHS_CHROME_SNIPPETS.exists():
        errors.append("xhs-comment-research still contains repository-maintained chrome-snippets.md")

    for path, max_lines, max_bytes in (
        (SKILL_MD, 350, 30000),
        (ROLE_CARDS, 180, 18000),
        (UI_WORKFLOW, 180, 20000),
        (UI_SOURCE_CATALOG, 180, 20000),
    ):
        text = read(path)
        if len(text.splitlines()) > max_lines:
            errors.append(f"{path.relative_to(ROOT)} exceeds line budget: {len(text.splitlines())} > {max_lines}")
        if len(text.encode("utf-8")) > max_bytes:
            errors.append(f"{path.relative_to(ROOT)} exceeds byte budget: {len(text.encode('utf-8'))} > {max_bytes}")
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
            if "任务分发决策：" not in prompt_text:
                errors.append("render_role_prompt.py output is missing 任务分发决策")

        small_direct = run(
            [
                PYTHON,
                str(RENDER_PROMPT),
                "--role",
                "开发",
                "--objective",
                "修改低风险单文件文案",
                "--source-role",
                "总控",
                "--task-size",
                "small",
            ],
            errors,
        )
        if "建议路径：总控直派开发" not in small_direct.stdout:
            errors.append("render_role_prompt.py did not allow small CEO -> 开发 dispatch")

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
