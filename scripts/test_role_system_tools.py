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
ROUTING_GUIDE = ROOT / "docs" / "routing-token-and-evaluation.md"
BROWSER_AUTOMATION_DOC = ROOT / "docs" / "browser-automation.md"
ENSURE = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "ensure_project_role_files.py"
RENDER_PROMPT = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "render_role_prompt.py"
PREPARE_ROLE_WINDOW = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "prepare_role_window.py"
BUNDLED_PREPARE_ROLE_WINDOW = (
    ROOT
    / "plugins"
    / "codex-skills-core"
    / "skills"
    / "agent-role-orchestrator"
    / "scripts"
    / "prepare_role_window.py"
)
VALIDATE_LOOP = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "validate_role_loop.py"
CHECK_CODEGRAPH = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "check_codegraph.py"
AGGREGATE_SKILL_HITS = ROOT / "skills" / "agent-role-orchestrator" / "scripts" / "aggregate_skill_hits.py"
EVALUATE_SKILL_ROUTING = ROOT / "scripts" / "evaluate_skill_routing.py"
SKILL_ROUTING_CASES = ROOT / "evals" / "skill-routing-cases.jsonl"
VALIDATE_ROLE_SYSTEM = ROOT / "scripts" / "validate_role_system.py"
ORCHESTRATOR_SKILL = ROOT / "skills" / "agent-role-orchestrator" / "SKILL.md"
ROLE_CARDS = ROOT / "skills" / "agent-role-orchestrator" / "references" / "role-cards.md"
PLANNING_CONTRACT = ROOT / "skills" / "agent-role-orchestrator" / "references" / "planning-contract.md"
BROWSER_ROUTER = ROOT / "skills" / "browser-automation-router" / "SKILL.md"
PLAYWRIGHT_SKILL = ROOT / "skills" / "playwright" / "SKILL.md"
XHS_COMMENT_RESEARCH = ROOT / "skills" / "xhs-comment-research" / "SKILL.md"
XHS_CHROME_SNIPPETS = ROOT / "skills" / "xhs-comment-research" / "references" / "chrome-snippets.md"
XHS_AUTOMATION_PUBLISHER = ROOT / "skills" / "xhs-automation-publisher" / "SKILL.md"
UI_WORKFLOW = ROOT / "skills" / "ui-implementation-workflow" / "SKILL.md"
UI_SOURCE_CATALOG = UI_WORKFLOW.parent / "references" / "source-catalog.md"
UI_VISUAL_DIRECTION = UI_WORKFLOW.parent / "references" / "visual-direction.md"
UI_VISUAL_REVIEW_SIGNALS = UI_WORKFLOW.parent / "references" / "visual-review-signals.md"
DESIGN_TASTE_ADAPTER = ROOT / "skills" / "design-taste-frontend" / "SKILL.md"
PLUGIN_REGISTRY = ROOT / "registry" / "plugin-packages.json"


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


def write_plugin_config(path: Path, enabled_plugins: set[str]) -> None:
    blocks = []
    for plugin in sorted(enabled_plugins):
        blocks.append(
            f'[plugins."{plugin}@dirtytrii-codex-skills"]\n'
            "enabled = true\n"
        )
    path.write_text("\n".join(blocks), encoding="utf-8")


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


def test_prepare_role_window_fails_closed_when_role_plugin_is_disabled() -> None:
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "config.toml"
        write_plugin_config(config, {"codex-skills-core"})
        result = run(
            [
                PYTHON,
                str(PREPARE_ROLE_WINDOW),
                "--role",
                "开发",
                "--objective",
                "实现订单筛选",
                "--source-role",
                "架构",
                "--required-skill",
                "gstack",
                "--plugin-registry",
                str(PLUGIN_REGISTRY),
                "--codex-config",
                str(config),
            ],
            check=False,
        )
        assert result.returncode != 0
        assert "prepare_role_window blocked" in result.stderr
        assert "codex-skills-engineering" in result.stderr
        assert (
            "codex plugin add "
            "codex-skills-engineering@dirtytrii-codex-skills"
        ) in result.stderr
        assert "【给 开发 窗口的" not in result.stdout


def test_prepare_role_window_generates_only_after_required_plugins_are_enabled() -> None:
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "config.toml"
        write_plugin_config(
            config,
            {"codex-skills-core", "codex-skills-engineering"},
        )
        result = run(
            [
                PYTHON,
                str(PREPARE_ROLE_WINDOW),
                "--role",
                "开发",
                "--objective",
                "实现订单筛选",
                "--source-role",
                "架构",
                "--required-skill",
                "gstack",
                "--plugin-registry",
                str(PLUGIN_REGISTRY),
                "--codex-config",
                str(config),
            ]
        )
        assert "插件前置检查：" in result.stdout
        assert "状态：通过" in result.stdout
        assert "codex-skills-core、codex-skills-engineering" in result.stdout
        assert "【给 开发 窗口的" in result.stdout


def test_prepare_role_window_required_skill_can_add_cross_domain_plugin() -> None:
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "config.toml"
        write_plugin_config(
            config,
            {"codex-skills-core", "codex-skills-content"},
        )
        result = run(
            [
                PYTHON,
                str(PREPARE_ROLE_WINDOW),
                "--role",
                "内容主编",
                "--objective",
                "准备公众号文章和配图",
                "--source-role",
                "总控",
                "--required-skill",
                "ui-implementation-workflow",
                "--plugin-registry",
                str(PLUGIN_REGISTRY),
                "--codex-config",
                str(config),
            ],
            check=False,
        )
        assert result.returncode != 0
        assert "codex-skills-visual-delivery" in result.stderr
        assert "【给 内容主编 窗口的" not in result.stdout


def test_prepare_role_window_rejects_unmapped_required_skill() -> None:
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "config.toml"
        write_plugin_config(config, {"codex-skills-core"})
        result = run(
            [
                PYTHON,
                str(PREPARE_ROLE_WINDOW),
                "--role",
                "总控",
                "--objective",
                "路由任务",
                "--required-skill",
                "unknown-private-skill",
                "--plugin-registry",
                str(PLUGIN_REGISTRY),
                "--codex-config",
                str(config),
            ],
            check=False,
        )
        assert result.returncode != 0
        assert "required skill is not mapped" in result.stderr
        assert "unknown-private-skill" in result.stderr


def test_bundled_prepare_role_window_discovers_bundled_registry() -> None:
    with tempfile.TemporaryDirectory() as temp:
        config = Path(temp) / "config.toml"
        write_plugin_config(config, {"codex-skills-core"})
        result = run(
            [
                PYTHON,
                str(BUNDLED_PREPARE_ROLE_WINDOW),
                "--role",
                "总控",
                "--objective",
                "判断任务路由",
                "--codex-config",
                str(config),
            ]
        )
        assert "插件前置检查：" in result.stdout
        assert "codex-skills-core" in result.stdout
        assert "【给 总控 窗口的" in result.stdout


def test_aggregate_skill_hits_quantifies_required_actual_and_misfires() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callbacks = Path(temp)
        (callbacks / "callback-1.md").write_text(
            """技能路由台账：
- 必选 skill：humanizer-zh、xhs-publish-assistant
技能命中回传：
- 已加载并使用：humanizer-zh、story-deslop
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
        assert payload["misfire_not_loaded_skill_count"] == 0
        assert payload["hit_rate"] == 0.5
        assert payload["routing_declaration_coverage"] == 1.0
        assert payload["skill_callback_completeness"] == 1.0
        assert payload["effective_use_rate"] == 0.5
        assert payload["misfire_rate"] == 0.5


def test_aggregate_skill_hits_ignores_ordinary_notes_in_denominators() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callbacks = Path(temp)
        for index in range(9):
            (callbacks / f"note-{index}.md").write_text(
                f"# 普通记录 {index}\n\n这里没有技能路由或回调。\n",
                encoding="utf-8",
            )
        (callbacks / "callback.md").write_text(
            """技能路由台账：
- 必选 skill：humanizer-zh
技能命中回传：
- 已加载并使用：humanizer-zh
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：humanizer-zh
""",
            encoding="utf-8",
        )

        result = run([PYTHON, str(AGGREGATE_SKILL_HITS), str(callbacks), "--json"])
        payload = json.loads(result.stdout)
        assert payload["files_discovered"] == 10
        assert payload["files_scanned"] == 1
        assert payload["ignored_file_count"] == 9
        assert payload["routing_declaration_coverage"] == 1.0
        assert payload["skill_callback_completeness"] == 1.0


def test_aggregate_skill_hits_separates_misfires_that_were_not_loaded() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callback = Path(temp) / "callback.md"
        callback.write_text(
            """技能命中回传：
- 已加载并使用：humanizer-zh
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：story-deslop
- 影响产出的 skill：humanizer-zh
""",
            encoding="utf-8",
        )

        result = run([PYTHON, str(AGGREGATE_SKILL_HITS), str(callback), "--json"])
        payload = json.loads(result.stdout)
        assert payload["misfire_skill_count"] == 0
        assert payload["misfire_not_loaded_skill_count"] == 1
        assert payload["misfire_rate"] == 0.0
        assert payload["files"][0]["misfire_not_loaded_skills"] == ["story-deslop"]


def test_aggregate_skill_hits_does_not_claim_success_without_requirements() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callback = Path(temp) / "callback.md"
        callback.write_text(
            """技能命中回传：
- 已加载并使用：humanizer-zh
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：humanizer-zh
""",
            encoding="utf-8",
        )
        result = run([PYTHON, str(AGGREGATE_SKILL_HITS), str(callback), "--json"])
        payload = json.loads(result.stdout)
        assert payload["hit_rate"] is None
        assert payload["routing_declaration_coverage"] == 0.0
        assert payload["skill_callback_completeness"] == 1.0


def test_skill_routing_eval_scores_observed_decisions_independently() -> None:
    validation = run(
        [PYTHON, str(EVALUATE_SKILL_ROUTING), "--validate-only", "--strict"]
    )
    assert json.loads(validation.stdout)["case_count"] >= 18

    with tempfile.TemporaryDirectory() as temp:
        observed = Path(temp) / "observed.jsonl"
        cases = [
            json.loads(line)
            for line in SKILL_ROUTING_CASES.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
        observed.write_text(
            "\n".join(
                json.dumps(
                    {"id": case["id"], "selected_skills": case["required_skills"]},
                    ensure_ascii=False,
                )
                for case in cases
            )
            + "\n",
            encoding="utf-8",
        )
        result = run(
            [
                PYTHON,
                str(EVALUATE_SKILL_ROUTING),
                "--observed",
                str(observed),
                "--strict",
            ]
        )
        payload = json.loads(result.stdout)
        assert payload["unevaluated_case_count"] == 0
        assert payload["case_pass_rate"] == 1.0
        assert payload["required_skill_recall"] == 1.0
        assert payload["negative_case_count"] >= 3
        assert payload["evaluated_negative_case_count"] >= 3
        assert payload["negative_case_pass_rate"] == 1.0

        first_negative = next(
            case
            for case in cases
            if not case["required_skills"] and not case["allowed_skills"]
        )
        observed.write_text(
            json.dumps(
                {"id": first_negative["id"], "selected_skills": ["humanizer-zh"]},
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )
        negative = run(
            [PYTHON, str(EVALUATE_SKILL_ROUTING), "--observed", str(observed)]
        )
        negative_payload = json.loads(negative.stdout)
        assert negative_payload["evaluated_negative_case_count"] == 1
        assert negative_payload["negative_case_pass_rate"] == 0.0
        assert negative_payload["results"][0]["unexpected_skills"] == ["humanizer-zh"]


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


def test_callback_without_required_skills_is_not_reported_as_full_hit() -> None:
    with tempfile.TemporaryDirectory() as temp:
        callback = Path(temp) / "callback.md"
        callback.write_text(
            """压缩回调：
- 当前状态：完成
- 本轮变化：完成只读检查
- 证据链接/文件/命令：git status
- 需要决策：无
- 下一回流对象：总控
技能命中回传：
- 已加载并使用：无
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：无
规则沉淀：
- 可复用优化沉淀：无
""",
            encoding="utf-8",
        )
        result = run([PYTHON, str(VALIDATE_LOOP), "--callback", str(callback), "--json"])
        payload = json.loads(result.stdout)
        assert payload[0]["metrics"]["required_skill_count"] == 0
        assert payload[0]["metrics"]["skill_hit_rate"] is None


def test_non_visual_standard_and_full_prompts_stay_within_budget() -> None:
    sources = {
        "总控": "用户",
        "架构": "总控",
        "开发": "架构",
        "QA": "架构",
        "内容主编": "总控",
        "技能维护": "总控",
    }
    for role, source in sources.items():
        standard = run(
            [
                PYTHON,
                str(RENDER_PROMPT),
                "--role",
                role,
                "--objective",
                "验证提示词体积",
                "--source-role",
                source,
                "--profile",
                "standard",
            ]
        )
        full = run(
            [
                PYTHON,
                str(RENDER_PROMPT),
                "--role",
                role,
                "--objective",
                "验证提示词体积",
                "--source-role",
                source,
                "--profile",
                "full",
            ]
        )
        assert len(standard.stdout) <= 3200
        assert len(full.stdout) <= 3400
        assert len(standard.stdout) < len(full.stdout)
        assert "独立门禁与失败回退（full 必填）" not in standard.stdout
        assert "独立门禁与失败回退（full 必填）" in full.stdout


def test_standard_generated_prompt_passes_fail_closed_validator() -> None:
    with tempfile.TemporaryDirectory() as temp:
        prompt = Path(temp) / "standard-prompt.md"
        run(
            [
                PYTHON,
                str(RENDER_PROMPT),
                "--role",
                "开发",
                "--objective",
                "验证标准档提示词",
                "--source-role",
                "架构",
                "--source-thread",
                "thread-cto",
                "--profile",
                "standard",
                "--output",
                str(prompt),
            ]
        )
        result = run([PYTHON, str(VALIDATE_LOOP), "--prompt", str(prompt)])
        assert "[PASS]" in result.stdout


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


def test_render_prompt_layers_implicit_planning_contract_across_owners() -> None:
    ceo = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "总控",
            "--objective",
            "判断一个跨前后端需求是否值得启动",
            "--task-size",
            "large",
        ]
    )
    assert "隐性规划契约：" in ceo.stdout
    assert "模式：owner-contract" in ceo.stdout
    assert "价值、成功标准、非目标、负责人、预算与风险" in ceo.stdout
    assert "不做代码库侦察、不写技术实施步骤" in ceo.stdout

    cto = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "架构",
            "--objective",
            "理解代码库并形成可执行技术规格",
            "--source-role",
            "总控",
            "--task-size",
            "large",
        ]
    )
    assert "模式：implementation-spec" in cto.stdout
    assert "Recon：读取仓库事实" in cto.stdout
    assert "Vet：亲自复核" in cto.stdout
    assert "规格是执行契约，不是最终产品" in cto.stdout
    assert "默认不亲自实现" in cto.stdout

    dev_lead = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "把技术规格拆成可验证的执行任务",
            "--source-role",
            "架构",
            "--task-size",
            "large",
        ]
    )
    assert "模式：executor-contract" in dev_lead.stdout
    assert "零上下文执行卡" in dev_lead.stdout
    assert "计划基线 commit" in dev_lead.stdout
    assert "每步验证命令与预期结果" in dev_lead.stdout
    assert "Dev Lead 仍负责集成、复验和提交" in dev_lead.stdout


def test_render_prompt_keeps_executor_contract_short_and_fail_closed() -> None:
    tiny_ceo = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "总控",
            "--objective",
            "判断是否顺手修正文档错字",
            "--task-size",
            "tiny",
        ]
    )
    assert "模式：route-only" in tiny_ceo.stdout
    assert "不得启动全库审计" in tiny_ceo.stdout
    assert "持久规格文件" not in tiny_ceo.stdout

    executor = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "按任务卡修改一个确定文件",
            "--source-role",
            "开发",
            "--task-size",
            "small",
            "--executor-tier",
            "mechanical",
        ]
    )
    assert "模式：execute-only" in executor.stdout
    assert "先运行漂移检查" in executor.stdout
    assert "触发 STOP 条件时立即回报" in executor.stdout
    assert "不得重新做全库规划" in executor.stdout


def test_render_prompt_maps_qa_to_evidence_review_not_planning() -> None:
    qa = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "QA",
            "--objective",
            "审查当前分支是否达到发布条件",
            "--source-role",
            "架构",
            "--task-size",
            "medium",
        ]
    )
    assert "隐性规划契约：" in qa.stdout
    assert "模式：evidence-review" in qa.stdout
    assert "只审查当前变更及直接影响面" in qa.stdout
    assert "不生成开发实施计划" in qa.stdout


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
    assert "总控只对接负责人/治理层" in owner.stdout

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
    assert "独立门禁与失败回退（full 必填）" in full.stdout
    assert "不得由实现者自证通过" in full.stdout
    assert "失败/回滚条件与执行责任人" in full.stdout


def test_render_prompt_auto_profile_uses_task_size_and_risk() -> None:
    def render(task_size: str, *extra: str) -> str:
        result = run(
            [
                PYTHON,
                str(RENDER_PROMPT),
                "--role",
                "开发",
                "--objective",
                "按范围实现并验证",
                "--source-role",
                "架构",
                "--task-size",
                task_size,
                *extra,
            ]
        )
        return result.stdout

    assert "profile：compact" in render("tiny")
    assert "profile：compact" in render("small")
    assert "profile：compact" in render("medium")
    standard = render("large")
    assert "profile：standard" in standard
    assert "有效控制：risk=normal；loop=L2" in standard
    assert "独立门禁与失败回退（full 必填）" not in standard
    critical = render("critical")
    assert "profile：full" in critical
    assert "model：gpt-5.6-sol" in critical
    assert "thinking：xhigh" in critical
    assert "有效控制：risk=critical；loop=L3" in critical
    assert "独立门禁与失败回退（full 必填）" in critical
    extreme = render("medium", "--risk", "extreme")
    assert "profile：full" in extreme
    assert "model：gpt-5.6-sol" in extreme
    assert "有效控制：risk=extreme；loop=L3" in extreme

    critical_risk = render("medium", "--risk", "critical")
    assert "profile：full" in critical_risk
    assert "有效控制：risk=critical；loop=L3" in critical_risk

    deep_loop = render("medium", "--loop-depth", "L3")
    assert "profile：full" in deep_loop
    assert "model：gpt-5.6-sol" in deep_loop
    assert "有效控制：risk=critical；loop=L3" in deep_loop

    explicit = render("critical", "--profile", "compact")
    assert "profile：compact" in explicit
    assert "独立门禁与失败回退（full 必填）" not in explicit


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

    critical_task = run(
        [
            PYTHON,
            str(RENDER_PROMPT),
            "--role",
            "开发",
            "--objective",
            "处理资金账本",
            "--source-role",
            "架构",
            "--task-size",
            "critical",
            "--executor-tier",
            "bounded",
            "--prefer-spark",
            "--spark-available",
        ],
        check=False,
    )
    assert critical_task.returncode != 0
    assert "does not support critical or extreme risk" in critical_task.stderr


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
    planning_contract_text = PLANNING_CONTRACT.read_text(encoding="utf-8")
    assert len(skill_text.splitlines()) <= 350
    assert len(skill_text.encode("utf-8")) <= 30000
    assert len(role_cards_text.splitlines()) <= 180
    assert len(role_cards_text.encode("utf-8")) <= 18000
    assert len(planning_contract_text.splitlines()) <= 140
    assert len(planning_contract_text.encode("utf-8")) <= 14000
    assert "Task size does not authorize a full repository" in planning_contract_text
    assert "Zero-Context Executor Card" in planning_contract_text
    assert "shadcn/improve" in planning_contract_text


def test_readme_stays_scannable_and_current() -> None:
    text = README.read_text(encoding="utf-8")
    routing_guide = ROUTING_GUIDE.read_text(encoding="utf-8")
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
    assert "docs/routing-token-and-evaluation.md" in text
    assert "隐性规划契约" in text
    assert "零上下文执行卡" in text
    assert len(routing_guide.splitlines()) <= 220
    assert len(routing_guide.encode("utf-8")) <= 12000
    for needle in (
        "Effective Controls",
        "effective risk",
        "effective loop",
        "三层 Skill 评估",
        "negative_case_pass_rate",
        "misfire_not_loaded_skill_count",
        "runtime runner",
    ):
        assert needle in routing_guide


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
    assert "deterministic terminal or CI browser automation" in playwright
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
    assert "references/visual-direction.md" in ui.stdout
    assert "design-taste-frontend 只作兼容入口" in ui.stdout
    assert "不继承旧审美偏好" in ui.stdout
    assert ".codex/ui-visual-review-signals.md" in ui.stdout
    assert "raw 证据" in ui.stdout
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
    visual_direction = UI_VISUAL_DIRECTION.read_text(encoding="utf-8")
    review_signals = UI_VISUAL_REVIEW_SIGNALS.read_text(encoding="utf-8")
    adapter = DESIGN_TASTE_ADAPTER.read_text(encoding="utf-8")

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
        "no inherited aesthetic preference",
        "references/visual-direction.md",
        "references/visual-review-signals.md",
        ".codex/ui-visual-review-signals.md",
        "raw review evidence only",
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

    for needle in (
        "Visual Direction Brief",
        "design variance",
        "motion intensity",
        "visual density",
        "Do not force image generation",
        "Do not create a new blanket ban",
        "no persistent aesthetic preference",
        "visual-review-signals.md",
    ):
        assert needle in visual_direction

    for needle in (
        "no inherited aesthetic preference",
        "workflow: ui-implementation-workflow-v2",
        "status: raw",
        ".codex/ui-visual-review-signals.md",
        "Do not infer preference from silence",
        "do not automatically convert them into global defaults",
    ):
        assert needle in review_signals

    for needle in (
        "$ui-implementation-workflow",
        "references/visual-direction.md",
        "no inherited aesthetic preference",
        "Do not run a second audit",
        "persistent preference automatically",
    ):
        assert needle in adapter

    assert len(workflow.splitlines()) <= 180
    assert len(catalog.splitlines()) <= 180
    assert len(visual_direction.splitlines()) <= 220
    assert len(review_signals.splitlines()) <= 100
    assert len(adapter.splitlines()) <= 80


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
        test_prepare_role_window_fails_closed_when_role_plugin_is_disabled,
        test_prepare_role_window_generates_only_after_required_plugins_are_enabled,
        test_prepare_role_window_required_skill_can_add_cross_domain_plugin,
        test_prepare_role_window_rejects_unmapped_required_skill,
        test_bundled_prepare_role_window_discovers_bundled_registry,
        test_aggregate_skill_hits_quantifies_required_actual_and_misfires,
        test_aggregate_skill_hits_ignores_ordinary_notes_in_denominators,
        test_aggregate_skill_hits_separates_misfires_that_were_not_loaded,
        test_aggregate_skill_hits_does_not_claim_success_without_requirements,
        test_skill_routing_eval_scores_observed_decisions_independently,
        test_callback_must_start_with_forwardable_prefix,
        test_callback_without_required_skills_is_not_reported_as_full_hit,
        test_non_visual_standard_and_full_prompts_stay_within_budget,
        test_standard_generated_prompt_passes_fail_closed_validator,
        test_render_prompt_rejects_ceo_direct_technical_execution_without_small_or_override,
        test_render_prompt_allows_ceo_direct_small_development_dispatch,
        test_render_prompt_outputs_ceo_dispatch_decision_by_task_size,
        test_render_prompt_layers_implicit_planning_contract_across_owners,
        test_render_prompt_keeps_executor_contract_short_and_fail_closed,
        test_render_prompt_maps_qa_to_evidence_review_not_planning,
        test_render_prompt_rejects_ceo_direct_content_execution,
        test_render_prompt_allows_ceo_to_owner_layer_and_explicit_override,
        test_render_prompt_auto_compacts_l1_owner_prompt,
        test_render_prompt_full_profile_keeps_deep_sections,
        test_render_prompt_auto_profile_uses_task_size_and_risk,
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
