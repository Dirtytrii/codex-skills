#!/usr/bin/env python3
"""Regression tests for role-system fail-closed helper scripts."""

from __future__ import annotations

import subprocess
import sys
import tempfile
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PYTHON = sys.executable
README = ROOT / "README.md"
TECHNICAL_HIGHLIGHTS = ROOT / "docs" / "technical-highlights.md"
BROWSER_AUTOMATION_DOC = ROOT / "docs" / "browser-automation.md"
ENSURE = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "ensure_project_role_files.py"
RENDER_PROMPT = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "render_role_prompt.py"
VALIDATE_LOOP = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "validate_role_loop.py"
CHECK_CODEGRAPH = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "check_codegraph.py"
AGGREGATE_SKILL_HITS = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "aggregate_skill_hits.py"
VALIDATE_ROLE_SYSTEM = ROOT / "scripts" / "validate_role_system.py"
ORCHESTRATOR_SKILL = ROOT / "skills" / "agent-role-orchestrator" / "SKILL.md"
ROLE_CARDS = ROOT / "skills" / "agent-role-orchestrator" / "references" / "role-cards.md"
BROWSER_ROUTER = ROOT / "skills" / "browser-automation-router" / "SKILL.md"
PLAYWRIGHT_SKILL = ROOT / "skills" / "playwright" / "SKILL.md"
XHS_COMMENT_RESEARCH = ROOT / "skills" / "xhs-comment-research" / "SKILL.md"
XHS_CHROME_SNIPPETS = ROOT / "skills" / "xhs-comment-research" / "references" / "chrome-snippets.md"
XHS_AUTOMATION_PUBLISHER = ROOT / "skills" / "xhs-automation-publisher" / "SKILL.md"
UI_WORKFLOW = ROOT / "skills" / "ui-implementation-workflow" / "SKILL.md"
UI_SOURCE_CATALOG = UI_WORKFLOW.parent / "references" / "source-catalog.md"


def run(args: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        args,
        cwd=str(cwd or ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if check and result.returncode != 0:
        raise AssertionError(
            f"command failed ({result.returncode}): {' '.join(args)}\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )
    return result


def test_project_role_file_bootstrap() -> None:
    with tempfile.TemporaryDirectory() as temp:
        project = Path(temp)

        dry_run = run([PYTHON, str(ENSURE), "--project", str(project)])
        assert "DRY-RUN" in dry_run.stdout
        assert not (project / "AGENTS.md").exists()
        assert not (project / ".codex" / "role-windows.md").exists()

        written = run([PYTHON, str(ENSURE), "--project", str(project), "--write"])
        assert "WRITE" in written.stdout

        agents = project / "AGENTS.md"
        ledger = project / ".codex" / "role-windows.md"
        assert agents.exists()
        assert ledger.exists()
        agents_text = agents.read_text(encoding="utf-8")
        ledger_text = ledger.read_text(encoding="utf-8")
        assert "BEGIN agent-role-orchestrator entry rule" in agents_text
        assert "总控/架构/多角色/派发/回调/台账类任务必须先使用 agent-role-orchestrator" in agents_text
        machine_path_fragment = "\\".join(["C:", "Users"]) + "\\"
        assert machine_path_fragment not in agents_text
        assert "已安装的 agent-role-orchestrator/SKILL.md" in agents_text
        assert "| 总控 | 待确认 | 待确认 | 用户 | 入口分流" in ledger_text
        assert "## 压缩交接卡" in ledger_text

        run([PYTHON, str(VALIDATE_LOOP), "--project", str(project)])

        second = run([PYTHON, str(ENSURE), "--project", str(project), "--write"])
        assert "OK" in second.stdout
        assert agents.read_text(encoding="utf-8").count("BEGIN agent-role-orchestrator entry rule") == 1


def test_existing_agents_file_is_preserved() -> None:
    with tempfile.TemporaryDirectory() as temp:
        project = Path(temp)
        agents = project / "AGENTS.md"
        agents.write_text("# AGENTS.md\n\n- 原有项目规则\n", encoding="utf-8")

        run([PYTHON, str(ENSURE), "--project", str(project), "--write"])

        text = agents.read_text(encoding="utf-8")
        assert "- 原有项目规则" in text
        assert "BEGIN agent-role-orchestrator entry rule" in text


def test_role_ledger_rejects_duplicate_threads_and_bad_status() -> None:
    with tempfile.TemporaryDirectory() as temp:
        project = Path(temp)
        ledger = project / ".codex" / "role-windows.md"
        ledger.parent.mkdir(parents=True)
        ledger.write_text(
            """# 角色窗口台账

| 角色 | 状态 | thread id | 来源窗口 | 当前职责 | 下一步 | 循环状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 总控 | 已建立 | thread-1 | 用户 | 入口分流 | 继续验收 | 运行中 |
| 架构 | 已建立 | thread-1 | 总控 | 技术拆解 | 派发开发 | 运行中 |
| 内容主编 | 待确认 | 待确认 | 总控 | 内容分流 | 待确认 | 待确认 |
""",
            encoding="utf-8",
        )
        duplicate = run([PYTHON, str(VALIDATE_LOOP), "--project", str(project)], check=False)
        assert duplicate.returncode != 0
        assert "duplicate thread id" in duplicate.stdout

        ledger.write_text(
            """# 角色窗口台账

| 角色 | 状态 | thread id | 来源窗口 | 当前职责 | 下一步 | 循环状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 总控 | 已建立 | thread-1 | 用户 | 入口分流 | 继续验收 | 运行中 |
| 架构 | 忙碌中 | thread-2 | 总控 | 技术拆解 | 派发开发 | 运行中 |
| 内容主编 | 待确认 | 待确认 | 总控 | 内容分流 | 待确认 | 待确认 |
""",
            encoding="utf-8",
        )
        bad_status = run([PYTHON, str(VALIDATE_LOOP), "--project", str(project)], check=False)
        assert bad_status.returncode != 0
        assert "invalid status" in bad_status.stdout


def test_check_codegraph_reports_state_without_guessing() -> None:
    with tempfile.TemporaryDirectory() as temp:
        project = Path(temp)
        missing = run([PYTHON, str(CHECK_CODEGRAPH), "--project", str(project), "--json"])
        missing_payload = json.loads(missing.stdout)
        assert missing_payload["project_exists"] is True
        assert missing_payload["initialized"] is False
        assert missing_payload["initialization_status"] == "未初始化"

        (project / ".codegraph").mkdir()
        initialized = run([PYTHON, str(CHECK_CODEGRAPH), "--project", str(project), "--json"])
        initialized_payload = json.loads(initialized.stdout)
        assert initialized_payload["initialized"] is True
        assert initialized_payload["initialization_status"] == "已初始化"


def test_aggregate_skill_hits_quantifies_required_actual_and_misfires() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callbacks = Path(temp)
        (callbacks / "callback-1.md").write_text(
            """技能路由台账：
- 必选 skill：humanizer-zh、xhs-publish-assistant
技能命中回传：
- 已加载并使用：humanizer-zh
- 来源窗口要求但未使用：xhs-publish-assistant
- 临时发现应补用：cheat-on-content
- 误召/无效加载：story-deslop
- 影响产出的 skill：humanizer-zh
""",
            encoding="utf-8",
        )
        result = run([PYTHON, str(AGGREGATE_SKILL_HITS), str(callbacks), "--json"])
        payload = json.loads(result.stdout)
        assert payload["files_scanned"] == 1
        assert payload["required_skill_count"] == 2
        assert payload["loaded_required_skill_count"] == 1
        assert payload["declared_unused_required_skill_count"] == 1
        assert payload["missing_required_skill_count"] == 0
        assert payload["misfire_skill_count"] == 1
        assert payload["hit_rate"] == 0.5


def test_callback_must_start_with_forwardable_prefix() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callback = Path(temp) / "callback.md"
        callback.write_text(
            """说明：这只是一个最终总结。

压缩回调：
- 当前状态：完成
- 本轮变化：已更新台账
- 证据链接/文件/命令：git status
- 需要决策：无
- 下一回流对象：总控

技能命中回传：
- 已加载并使用：agent-role-orchestrator
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：agent-role-orchestrator

规则沉淀：
- 可复用优化沉淀：无
""",
            encoding="utf-8",
        )
        result = run([PYTHON, str(VALIDATE_LOOP), "--callback", str(callback)], check=False)
        assert result.returncode != 0
        assert "callback must start with <codex_delegation> or 压缩回调" in result.stdout


def test_render_prompt_rejects_ceo_direct_technical_execution_without_small_or_override() -> None:
    result = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "编写验收脚本",
            "--source-role",
            "总控",
        ],
        check=False,
    )
    assert result.returncode != 0
    assert "总控不能直接派发技术执行角色" in result.stderr


def test_render_prompt_allows_ceo_direct_small_development_dispatch() -> None:
    result = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "修改一个低风险单文件文案",
            "--source-role",
            "总控",
            "--task-size",
            "small",
        ]
    )
    assert "任务分发决策：" in result.stdout
    assert "任务规模：small" in result.stdout
    assert "建议路径：总控直派开发" in result.stdout
    assert "单一、短、小、可验证" in result.stdout
    assert "一旦出现架构判断、跨文件整合或风险升级，回流架构 / CTO" in result.stdout


def test_render_prompt_outputs_ceo_dispatch_decision_by_task_size() -> None:
    tiny = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "总控",
            "--objective",
            "顺手修正一个 README 错别字",
            "--task-size",
            "tiny",
        ]
    )
    assert "任务分发决策：" in tiny.stdout
    assert "任务规模：tiny" in tiny.stdout
    assert "建议路径：总控自办" in tiny.stdout
    assert "只允许低风险、局部、可验证的小改动" in tiny.stdout

    large = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "总控",
            "--objective",
            "启动一个涉及前后端、QA 和发布门禁的新功能",
            "--task-size",
            "large",
        ]
    )
    assert "任务规模：large" in large.stdout
    assert "建议路径：启动完整角色团队" in large.stdout
    assert "总控 -> 架构/内容主编 -> 执行角色" in large.stdout
    assert "测试/QA/安全/DBA/运维等门禁" in large.stdout


def test_render_prompt_rejects_ceo_direct_content_execution() -> None:
    result = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "小红书",
            "--objective",
            "准备发布包",
            "--source-role",
            "总控",
        ],
        check=False,
    )
    assert result.returncode != 0
    assert "总控不能直接派发内容执行角色" in result.stderr


def test_render_prompt_allows_ceo_to_owner_layer_and_explicit_override() -> None:
    owner = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "架构",
            "--objective",
            "拆解验收脚本需求",
            "--source-role",
            "总控",
            "--loop-depth",
            "L1",
        ]
    )
    assert "Loop 深度（可折叠路由）：" in owner.stdout
    assert "本次深度：L1" in owner.stdout
    assert "总控 / CEO 只直接对接负责人层" in owner.stdout

    override = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "用户明确要求直接生成开发窗口",
            "--source-role",
            "总控",
            "--allow-ceo-direct-dispatch",
            "--override-reason",
            "用户明确要求绕过架构",
        ]
    )
    assert "用户明确要求绕过架构" in override.stdout


def test_render_prompt_auto_compacts_l1_owner_prompt() -> None:
    compact = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "内容主编",
            "--objective",
            "判断公众号和小红书内容任务是否需要拆下游",
            "--source-role",
            "总控",
            "--loop-depth",
            "L1",
        ]
    )
    full_same_role = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "内容主编",
            "--objective",
            "判断公众号和小红书内容任务是否需要拆下游",
            "--source-role",
            "总控",
            "--loop-depth",
            "L1",
            "--profile",
            "full",
        ]
    )
    assert "Token Budget Profile：" in compact.stdout
    assert "profile：compact" in compact.stdout
    assert "策略：只保留闭环必需字段" in compact.stdout
    assert len(compact.stdout) < len(full_same_role.stdout)
    assert "模型建议：" in compact.stdout
    assert "负责人交互边界：" in compact.stdout
    assert "技能路由台账" in compact.stdout
    assert "技能命中回传：" in compact.stdout
    assert "压缩回调：" in compact.stdout
    assert "技术方案（架构/CTO 处理复杂技术需求必填" not in compact.stdout
    assert "CodeGraph 状态（新本地代码项目必填" not in compact.stdout
    assert "开源/可借鉴方案扫描" not in compact.stdout


def test_render_prompt_full_profile_keeps_deep_sections() -> None:
    full = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "架构",
            "--objective",
            "设计高风险技术改造并拆下游",
            "--source-role",
            "总控",
            "--loop-depth",
            "L3",
            "--profile",
            "full",
            "--new-code-project",
        ]
    )
    assert "Token Budget Profile：" in full.stdout
    assert "profile：full" in full.stdout
    assert "技术方案（架构/CTO 处理复杂技术需求必填" in full.stdout
    assert "CodeGraph 状态（新本地代码项目必填" in full.stdout
    assert "开源/可借鉴方案扫描" in full.stdout


def test_render_prompt_routes_development_lead_and_subagents() -> None:
    dev = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "实现一组长任务拆分",
            "--source-role",
            "架构",
        ]
    )
    assert "model：gpt-5.6-terra" in dev.stdout
    assert "thinking：high" in dev.stdout
    assert "开发负责人 / Dev Lead" in dev.stdout
    assert "开发执行 subagent" in dev.stdout
    assert "gpt-5.4-mini + high" in dev.stdout
    assert "gpt-5.6-terra + high" in dev.stdout
    assert "gpt-5.6-sol + xhigh" in dev.stdout
    assert "只执行单一、短、小、可验证的代码任务" in dev.stdout
    assert "窗口内一次性 subagent" in dev.stdout
    assert "不写入 .codex/role-windows.md" in dev.stdout
    assert "任务结束后关闭，不作为角色窗口复用" in dev.stdout

    bounded = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "修改两个边界清楚且已有测试的业务文件",
            "--source-role",
            "架构",
            "--executor-tier",
            "bounded",
        ]
    )
    assert "model：gpt-5.6-luna" in bounded.stdout
    assert "thinking：high" in bounded.stdout
    assert "一次性 subagent" in bounded.stdout


def test_render_prompt_rejects_unsafe_parallel_worker_fanout() -> None:
    rejected = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "并行实现三个模块",
            "--source-role",
            "架构",
            "--execution-profile",
            "parallel",
            "--worker-count",
            "3",
        ],
        check=False,
    )
    assert rejected.returncode != 0
    assert "disjoint-scope" in rejected.stderr
    assert "independent-validation" in rejected.stderr

    accepted = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "并行实现三个互不重叠的适配器",
            "--source-role",
            "架构",
            "--execution-profile",
            "parallel",
            "--worker-count",
            "3",
            "--disjoint-scope",
            "每个 worker 仅修改一个独立适配器目录",
            "--independent-validation",
            "每个适配器都有独立单测命令",
        ]
    )
    assert "execution-profile：parallel" in accepted.stdout
    assert "worker-count：3" in accepted.stdout
    assert "默认串行" not in accepted.stdout


def test_render_prompt_uses_spark_only_for_confirmed_short_executor() -> None:
    spark = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "实现一个已有独立测试的适配器",
            "--source-role",
            "架构",
            "--executor-tier",
            "bounded",
            "--prefer-spark",
            "--spark-available",
        ]
    )
    assert "model：gpt-5.3-codex-spark" in spark.stdout
    assert "thinking：high" in spark.stdout
    assert "Spark Opportunity Lane" in spark.stdout
    assert "选择结果：使用 Spark 独立额度" in spark.stdout
    assert "必须显式运行验证命令" in spark.stdout

    fallback = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "实现一个已有独立测试的适配器",
            "--source-role",
            "架构",
            "--executor-tier",
            "bounded",
            "--prefer-spark",
        ]
    )
    assert "model：gpt-5.6-luna" in fallback.stdout
    assert "选择结果：Spark 未确认可用，回退稳定路由" in fallback.stdout

    rejected = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "担任长期开发负责人",
            "--source-role",
            "架构",
            "--prefer-spark",
            "--spark-available",
        ],
        check=False,
    )
    assert rejected.returncode != 0
    assert "mechanical or bounded" in rejected.stderr


def test_render_prompt_compact_profile_stays_within_budget() -> None:
    compact = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "修复一个有明确回归测试的边界错误",
            "--source-role",
            "架构",
            "--profile",
            "compact",
        ]
    )
    assert len(compact.stdout.splitlines()) <= 90
    assert len(compact.stdout.encode("utf-8")) <= 6000


def test_render_prompt_routes_qa_default_and_critical_models() -> None:
    ordinary = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "QA",
            "--objective",
            "普通验收",
            "--source-role",
            "架构",
        ]
    )
    assert "model：gpt-5.6-terra" in ordinary.stdout
    assert "thinking：high" in ordinary.stdout

    critical = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "QA",
            "--objective",
            "关键 PR 对抗式审查",
            "--source-role",
            "架构",
            "--risk",
            "critical",
        ]
    )
    assert "model：gpt-5.6-sol" in critical.stdout
    assert "thinking：xhigh" in critical.stdout
    assert "技术方案（架构/CTO 处理复杂技术需求必填" not in critical.stdout
    assert "CodeGraph 状态（新本地代码项目必填" not in critical.stdout
    assert "开源/可借鉴方案扫描" not in critical.stdout


def test_render_prompt_extreme_cto_uses_supported_xhigh() -> None:
    extreme = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "架构",
            "--objective",
            "收敛信息高度冲突的不可逆技术决策",
            "--source-role",
            "总控",
            "--risk",
            "extreme",
        ]
    )
    assert "model：gpt-5.6-sol" in extreme.stdout
    assert "thinking：xhigh" in extreme.stdout
    assert "thinking：max" not in extreme.stdout


def test_orchestrator_entry_files_stay_within_token_budget() -> None:
    skill_text = ORCHESTRATOR_SKILL.read_text(encoding="utf-8")
    role_cards_text = ROLE_CARDS.read_text(encoding="utf-8")
    assert len(skill_text.splitlines()) <= 350
    assert len(skill_text.encode("utf-8")) <= 30000
    assert len(role_cards_text.splitlines()) <= 180
    assert len(role_cards_text.encode("utf-8")) <= 18000


def test_readme_stays_scannable_and_current() -> None:
    text = README.read_text(encoding="utf-8")
    assert len(text.splitlines()) <= 260
    assert len(text.encode("utf-8")) <= 20000
    for heading in (
        "## 30 秒上手",
        "## 角色与任务流",
        "## Fail-Closed Tool Layer",
        "## 稳定模型路由与 Spark 机会通道",
        "## 能力路由",
        "## 仓库与维护",
    ):
        assert heading in text
    assert "docs/technical-highlights.md" in text


def test_native_browser_routing_prefers_plugins_and_keeps_deterministic_fallbacks() -> None:
    readme = README.read_text(encoding="utf-8")
    browser_doc = BROWSER_AUTOMATION_DOC.read_text(encoding="utf-8")
    router = BROWSER_ROUTER.read_text(encoding="utf-8")
    playwright = PLAYWRIGHT_SKILL.read_text(encoding="utf-8")
    comments = XHS_COMMENT_RESEARCH.read_text(encoding="utf-8")
    publisher = XHS_AUTOMATION_PUBLISHER.read_text(encoding="utf-8")

    assert "browser-automation-router" in readme
    assert "docs/browser-automation.md" in readme
    assert "2026-06-11" in browser_doc
    assert "OpenAI does not publish a stable numeric" in router
    assert "existing Chrome profile" in router
    assert "deterministic terminal or CI automation" in playwright
    assert "Do not load repository-maintained JavaScript snippets" in comments
    assert not XHS_CHROME_SNIPPETS.exists()
    assert "native Chrome surface" in publisher
    assert "deterministic Xiaohongshu batch/export fallback" in publisher

    highlights = TECHNICAL_HIGHLIGHTS.read_text(encoding="utf-8")
    for heading in (
        "## CEO-First 与负责人分层",
        "## 可折叠的 Multi-Window Loop",
        "## Fail-Closed Tool Layer",
        "## Token-Aware Prompt Architecture",
        "## 稳定模型路由与 Spark 机会通道",
        "## 可量化的 Skill Routing",
    ):
        assert heading in highlights


def test_render_prompt_routes_owner_ops_dba_and_mechanical_work() -> None:
    ceo = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "总控",
            "--objective",
            "跨角色结果验收",
        ]
    )
    assert "model：gpt-5.6-terra" in ceo.stdout
    assert "thinking：high" in ceo.stdout

    cto = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "架构",
            "--objective",
            "实盘架构方案",
        ]
    )
    assert "model：gpt-5.6-sol" in cto.stdout
    assert "thinking：high" in cto.stdout

    ops = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "运维",
            "--objective",
            "生产恢复",
            "--risk",
            "critical",
        ]
    )
    assert "model：gpt-5.6-sol" in ops.stdout
    assert "thinking：xhigh" in ops.stdout

    dba = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "DBA",
            "--objective",
            "索引空间分析",
        ]
    )
    assert "model：gpt-5.6-terra" in dba.stdout
    assert "thinking：high" in dba.stdout

    knowledge = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "知识库",
            "--objective",
            "机械整理索引",
            "--risk",
            "mechanical",
        ]
    )
    assert "model：gpt-5.4-mini" in knowledge.stdout
    assert "thinking：medium" in knowledge.stdout


def test_render_prompt_includes_readonly_x_mcp_for_content_roles() -> None:
    editor = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "内容主编",
            "--objective",
            "研究爆款选题和对标账号",
            "--source-role",
            "总控",
        ]
    )
    assert "X MCP 内容研究源" in editor.stdout
    assert "只读、需授权" in editor.stdout
    assert "爆款内容研究、热点扫描、选题池、对标账号" in editor.stdout
    assert "禁止发帖、发布 Article、关注/取关、点赞、转发、私信、账号设置" in editor.stdout


def test_render_prompt_includes_content_tone_gate() -> None:
    editor = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "内容主编",
            "--objective",
            "准备正式对外内容",
            "--source-role",
            "总控",
        ]
    )
    assert "反老登味 / 反 AI 味内容闸门" in editor.stdout
    assert "说教、爹味、上位者口吻" in editor.stdout
    assert "模板化、空泛排比、万能套话" in editor.stdout
    assert "不改变事实、数据、价格、日期、来源、授权边界" in editor.stdout
    assert "正式对外内容必须先过这道闸门" in editor.stdout


def test_render_prompt_includes_xhs_automation_publish_gate() -> None:
    xhs = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "小红书",
            "--objective",
            "处理小红书自动发布卡点",
            "--source-role",
            "内容主编",
            "--risk",
            "critical",
        ]
    )
    assert "$browser-automation-router" in xhs.stdout
    assert "现有登录态、Chrome tab/profile/extension" in xhs.stdout
    assert "Codex Desktop 2026-06-11" in xhs.stdout
    assert "$xhs-automation-publisher" in xhs.stdout
    assert "脚本降级默认先用 --preview" in xhs.stdout
    assert "publish_pipeline.py 默认会自动点击发布" in xhs.stdout
    assert "click-publish、post-comment-to-feed、respond-comment、note-upvote、note-bookmark" in xhs.stdout
    assert "必须二次明确授权" in xhs.stdout


def test_render_prompt_includes_ui_preview_route_options() -> None:
    ui = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "UI/PPT",
            "--objective",
            "根据预览图实现高保真前端视觉效果",
            "--source-role",
            "架构",
            "--task-size",
            "medium",
        ]
    )
    assert "$ui-implementation-workflow" in ui.stdout
    assert "UI 工程闭环" in ui.stdout
    assert "medium+：最多 3 份参考" in ui.stdout
    assert "UI implementation plan" in ui.stdout
    assert "1440/768/390" in ui.stdout
    assert "修复后重截" in ui.stdout
    assert "动态换源" in ui.stdout
    assert "每轮只替换对应的一份参考" in ui.stdout
    assert "medium+ 默认最多换源 2 轮" in ui.stdout
    assert "预览图实现路线选择" in ui.stdout
    assert "不要默认拿 CSS 硬干" in ui.stdout
    assert "先给出 2-4 条实现路线" in ui.stdout
    assert "CSS/组件复刻" in ui.stdout
    assert "图片切片/生成资产" in ui.stdout
    assert "Canvas/SVG" in ui.stdout
    assert "Three.js/WebGL" in ui.stdout
    assert "Lottie/视频" in ui.stdout
    assert "截图对比" in ui.stdout


def test_render_prompt_keeps_tiny_ui_reference_budget_compact() -> None:
    ui = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "UI/PPT",
            "--objective",
            "修正一个按钮的对齐问题",
            "--source-role",
            "架构",
            "--task-size",
            "tiny",
        ]
    )
    assert "tiny：不做外部灵感搜索" in ui.stdout
    assert "tiny 不做外部换源" in ui.stdout
    assert "medium+：最多 3 份参考" not in ui.stdout
    assert "medium+ 默认最多换源 2 轮" not in ui.stdout


def test_ui_implementation_workflow_is_bounded_and_visual() -> None:
    workflow = UI_WORKFLOW.read_text(encoding="utf-8")
    catalog = UI_SOURCE_CATALOG.read_text(encoding="utf-8")

    for needle in (
        "marketing",
        "dashboard",
        "tiny",
        "small",
        "medium+",
        "Do not modify code until the plan is explicit",
        "Semantic Tokens",
        "real data and interactions",
        "$browser-automation-router",
        "1440px",
        "768px",
        "390px",
        "Fix visible defects and capture the affected widths again",
        "Dynamic Reference Switching",
        "reference ledger",
        "Replace one role per iteration",
        "small` allows one switch round",
        "medium+` allows two switch rounds",
    ):
        assert needle in workflow

    for needle in (
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
        "stack/license check",
    ):
        assert needle in catalog

    assert len(workflow.splitlines()) <= 180
    assert len(catalog.splitlines()) <= 180


def test_render_prompt_requires_fail_closed_source_callback() -> None:
    architect = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "架构",
            "--objective",
            "验收技术闭环并回调总控",
            "--source-role",
            "总控",
            "--source-thread",
            "thread-ceo",
            "--loop-depth",
            "L2",
        ]
    )
    assert "完成、阻塞或需要发起方决策时，必须同时完成两件事" in architect.stdout
    assert "更新 .codex/role-windows.md 并提交" in architect.stdout
    assert "向来源 thread 主动发送压缩回调" in architect.stdout
    assert "仅完成第 1 项不算闭环" in architect.stdout
    assert "当前窗口没有发送工具" in architect.stdout
    assert "<codex_delegation>" in architect.stdout
    assert "压缩回调" in architect.stdout


def test_role_system_validator() -> None:
    result = run([PYTHON, str(VALIDATE_ROLE_SYSTEM)])
    assert "Role system validation passed" in result.stdout


def main() -> int:
    tests = [
        test_project_role_file_bootstrap,
        test_existing_agents_file_is_preserved,
        test_role_ledger_rejects_duplicate_threads_and_bad_status,
        test_check_codegraph_reports_state_without_guessing,
        test_aggregate_skill_hits_quantifies_required_actual_and_misfires,
        test_callback_must_start_with_forwardable_prefix,
        test_render_prompt_rejects_ceo_direct_technical_execution_without_small_or_override,
        test_render_prompt_allows_ceo_direct_small_development_dispatch,
        test_render_prompt_outputs_ceo_dispatch_decision_by_task_size,
        test_render_prompt_rejects_ceo_direct_content_execution,
        test_render_prompt_allows_ceo_to_owner_layer_and_explicit_override,
        test_render_prompt_auto_compacts_l1_owner_prompt,
        test_render_prompt_full_profile_keeps_deep_sections,
        test_render_prompt_routes_development_lead_and_subagents,
        test_render_prompt_rejects_unsafe_parallel_worker_fanout,
        test_render_prompt_uses_spark_only_for_confirmed_short_executor,
        test_render_prompt_compact_profile_stays_within_budget,
        test_render_prompt_routes_qa_default_and_critical_models,
        test_render_prompt_extreme_cto_uses_supported_xhigh,
        test_orchestrator_entry_files_stay_within_token_budget,
        test_readme_stays_scannable_and_current,
        test_native_browser_routing_prefers_plugins_and_keeps_deterministic_fallbacks,
        test_render_prompt_routes_owner_ops_dba_and_mechanical_work,
        test_render_prompt_includes_readonly_x_mcp_for_content_roles,
        test_render_prompt_includes_content_tone_gate,
        test_render_prompt_includes_xhs_automation_publish_gate,
        test_render_prompt_includes_ui_preview_route_options,
        test_render_prompt_keeps_tiny_ui_reference_budget_compact,
        test_ui_implementation_workflow_is_bounded_and_visual,
        test_render_prompt_requires_fail_closed_source_callback,
        test_role_system_validator,
    ]
    for test in tests:
        test()
        print(f"PASS {test.__name__}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
