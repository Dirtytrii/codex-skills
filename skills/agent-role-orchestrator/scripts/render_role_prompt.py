#!/usr/bin/env python3
"""Render a fail-closed role-window prompt for agent-role-orchestrator."""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path


CANONICAL_ROLES = {
    "ceo": "总控",
    "总控": "总控",
    "cto": "架构",
    "架构": "架构",
    "开发": "开发",
    "ui": "UI/PPT",
    "ui/ppt": "UI/PPT",
    "ui/frontend": "UI/PPT",
    "UI/PPT": "UI/PPT",
    "UI/Frontend": "UI/PPT",
    "测试": "测试",
    "qa": "QA",
    "QA": "QA",
    "安全": "安全",
    "dba": "DBA",
    "DBA": "DBA",
    "运维": "运维",
    "内容主编": "内容主编",
    "公众号发布": "公众号发布",
    "小红书": "小红书",
    "视频": "视频",
    "知识库": "知识库",
    "技能维护": "技能维护",
    "文档/交付": "文档/交付",
    "文档": "文档/交付",
}

ROLE_TREE_POSITION = {
    "总控": "总控 / CEO",
    "架构": "总控 / CEO -> 架构 / CTO",
    "开发": "总控 / CEO -> 架构 / CTO -> 开发",
    "UI/PPT": "总控 / CEO -> 架构 / CTO 或 内容主编 -> UI/PPT / UI/Frontend",
    "测试": "总控 / CEO -> 架构 / CTO -> 测试",
    "QA": "总控 / CEO -> 架构 / CTO -> QA",
    "安全": "总控 / CEO -> 架构 / CTO -> 安全",
    "DBA": "总控 / CEO -> 架构 / CTO -> DBA",
    "运维": "总控 / CEO -> 架构 / CTO -> 运维",
    "内容主编": "总控 / CEO -> 内容主编",
    "公众号发布": "总控 / CEO -> 内容主编 -> 公众号发布",
    "小红书": "总控 / CEO -> 内容主编 -> 小红书",
    "视频": "总控 / CEO -> 内容主编 -> 视频",
    "知识库": "总控 / CEO -> 知识库",
    "技能维护": "总控 / CEO -> 技能维护",
    "文档/交付": "总控 / CEO -> 文档/交付",
}

TECHNICAL_ROLES = {"架构", "开发", "UI/PPT", "测试", "QA", "安全", "DBA", "运维"}
CONTENT_ROLES = {"内容主编", "公众号发布", "小红书", "视频"}
PUBLIC_COPY_ROLES = CONTENT_ROLES | {"UI/PPT"}
BROWSER_ROLES = {"UI/PPT", "测试", "QA", "小红书"}
TECHNICAL_EXECUTION_ROLES = {"开发", "UI/PPT", "测试", "QA", "安全", "DBA", "运维"}
CONTENT_EXECUTION_ROLES = {"公众号发布", "小红书", "视频"}
OWNER_LAYER_ROLES = {"架构", "内容主编", "知识库", "技能维护", "文档/交付"}
ONE_SHOT_EXECUTOR_TIERS = {"mechanical", "bounded", "semantic"}


@dataclass(frozen=True)
class ModelRoute:
    model: str
    thinking: str
    escalation: str


@dataclass(frozen=True)
class TaskControls:
    risk: str
    loop_depth: str
    promotions: tuple[str, ...]


def canonical_role(raw: str) -> str:
    role = CANONICAL_ROLES.get(raw, CANONICAL_ROLES.get(raw.lower()))
    if not role:
        choices = "、".join(sorted(set(CANONICAL_ROLES.values())))
        raise ValueError(f"unknown role {raw!r}; choose one of: {choices}")
    return role


def effective_task_controls(args: argparse.Namespace) -> TaskControls:
    risk = args.risk
    loop_depth = args.loop_depth
    promotions: list[str] = []

    if (args.task_size == "critical" or loop_depth == "L3") and risk not in {
        "critical",
        "extreme",
    }:
        risk = "critical"
        promotions.append("critical 任务或 L3 门禁将 risk 提升为 critical")

    if args.executor_tier == "high-risk" and risk not in {"critical", "extreme"}:
        risk = "critical"
        promotions.append("high-risk executor tier 实际为 Dev Lead 高风险自办并提升 risk 至 critical")

    if risk in {"critical", "extreme"} and loop_depth != "L3":
        loop_depth = "L3"
        promotions.append("critical/extreme risk 至少使用 L3")
    elif args.task_size == "large" and loop_depth in {"L0", "L1"}:
        loop_depth = "L2"
        promotions.append("large 任务至少使用 L2")

    return TaskControls(risk=risk, loop_depth=loop_depth, promotions=tuple(promotions))


def task_controls_guidance(args: argparse.Namespace, controls: TaskControls) -> str:
    lines = [f"- 有效控制：risk={controls.risk}；loop={controls.loop_depth}"]
    if controls.promotions:
        lines.append(f"- 输入控制：risk={args.risk}；loop={args.loop_depth}")
        lines.append(f"- 自动提升：{'；'.join(controls.promotions)}")
    return "任务控制：\n" + "\n".join(lines) + "\n"


def model_route(role: str, risk: str, executor_tier: str = "owner") -> ModelRoute:
    if role == "总控":
        if risk in {"critical", "extreme"}:
            return ModelRoute("gpt-5.6-sol", "xhigh", "只用于资金、上线、生产恢复或跨角色最终 go/no-go；其余情况回到 Terra + high。")
        return ModelRoute("gpt-5.6-terra", "high", "资金、上线、生产恢复或跨角色最终 go/no-go 升级到 gpt-5.6-sol + xhigh。")
    if role == "架构":
        if risk == "extreme":
            return ModelRoute("gpt-5.6-sol", "xhigh", "仅限极难、信息高度冲突且 high 无法收敛的问题；不再虚构高于 xhigh 的思考档位。")
        if risk in {"critical", "extreme"}:
            return ModelRoute("gpt-5.6-sol", "xhigh", "实盘架构、事故根因、DB/并发/安全或不可逆方案使用 xhigh。")
        return ModelRoute("gpt-5.6-sol", "high", "实盘架构、事故根因、DB/并发/安全或不可逆方案升级到 xhigh。")
    if role == "开发":
        if executor_tier == "mechanical":
            return ModelRoute("gpt-5.6-luna", "high", "仅限单文件、规格和测试明确、无业务判断的一次性机械实现。")
        if executor_tier == "bounded":
            return ModelRoute("gpt-5.6-luna", "high", "仅限边界清楚、可独立验证的一次性执行任务；跨文件集成或范围漂移回流 Dev Lead。")
        if executor_tier == "semantic":
            return ModelRoute("gpt-5.6-terra", "high", "适合有限业务语义理解；跨模块整合、纠偏和提交仍由 Dev Lead 负责。")
        if executor_tier == "high-risk":
            return ModelRoute("gpt-5.6-sol", "xhigh", "高风险实现不得下放给廉价 executor，由 Dev Lead 亲自完成。")
        if risk in {"critical", "extreme"}:
            return ModelRoute("gpt-5.6-sol", "xhigh", "live exit、资金安全、PnL/fee、并发或重复失败返工由 Dev Lead 亲自处理，不交给廉价 subagent。")
        return ModelRoute("gpt-5.6-terra", "high", "live exit、资金安全、PnL/fee、并发或重复失败返工升级到 gpt-5.6-sol + xhigh。")
    if role == "QA":
        if risk in {"critical", "extreme"}:
            return ModelRoute("gpt-5.6-sol", "xhigh", "关键 PR、对抗式审查、发布门禁或生产风险需要 Sol xhigh。")
        return ModelRoute("gpt-5.6-terra", "high", "关键 PR、对抗式审查、发布门禁或生产风险升级到 gpt-5.6-sol + xhigh。")
    if role in {"运维", "DBA"}:
        if risk in {"critical", "extreme"}:
            return ModelRoute("gpt-5.6-sol", "xhigh", "真正部署、restart、rollback、生产故障、DDL、清理、恢复或数据风险需要 Sol xhigh。")
        return ModelRoute("gpt-5.6-terra", "high", "只读采证、容量、锁或空间分析用 Terra；部署/恢复/DDL/数据风险升级到 gpt-5.6-sol + xhigh。")
    if role in {"技能维护", "文档/交付", "知识库"}:
        if risk == "mechanical":
            return ModelRoute("gpt-5.6-luna", "medium", "仅限已确认范围内的索引、排版、搬运或 registry 机械同步；一旦需要判断，回到 Terra + high。")
        return ModelRoute("gpt-5.6-terra", "high", "策略结论、收益判断、知识结构或跨角色治理使用 Terra；纯索引、排版、搬运可降级到 gpt-5.6-luna + medium。")
    if role in CONTENT_ROLES:
        if risk == "critical":
            return ModelRoute("gpt-5.6-sol", "xhigh", "高风险公开定位、声明、合规或跨平台策略需要 Sol xhigh。")
        return ModelRoute("gpt-5.6-terra", "high", "高风险公开定位、声明、合规或跨平台策略升级到 gpt-5.6-sol + xhigh。")
    if risk == "mechanical":
        return ModelRoute("gpt-5.6-luna", "high", "仅限单文件、测试明确、无业务语义判断的机械执行。")
    if risk in {"critical", "extreme"}:
        return ModelRoute("gpt-5.6-sol", "xhigh", "高风险实现、不可逆操作或最终技术判断升级到 Sol xhigh。")
    return ModelRoute("gpt-5.6-terra", "high", "涉及高风险决策或跨角色协调时升级到 gpt-5.6-sol + xhigh。")


def lines_or_default(values: list[str], default: str) -> str:
    if not values:
        return f"- {default}"
    return "\n".join(f"- {value}" for value in values)


def csv_or_default(values: list[str], default: str) -> str:
    return "、".join(values) if values else default


def route_check_value(value: bool) -> str:
    return "是" if value else "待确认"


def task_dispatch_decision(role: str, args: argparse.Namespace) -> str:
    size = args.task_size
    if role == "总控":
        routes = {
            "tiny": (
                "总控自办",
                "只允许低风险、局部、可验证的小改动；如果出现跨文件设计、测试脚本、验收脚本、生产/账号/数据风险或不确定需求，立即升级到负责人层。",
            ),
            "small": (
                "总控可直派开发",
                "仅限单一、短、小、可验证的低风险开发任务；内容执行仍默认交给内容主编，技术复杂度上升时回流架构 / CTO。",
            ),
            "medium": (
                "总控 -> 负责人层",
                "交给架构 / CTO 或内容主编判断方案、范围和是否需要拆下游；总控只看结果、风险、决策点和验收建议。",
            ),
            "large": (
                "启动完整角色团队",
                "按总控 -> 架构/内容主编 -> 执行角色 -> 负责人层 -> 总控闭环推进，并按需加入测试/QA/安全/DBA/运维等门禁。",
            ),
            "critical": (
                "启动 L3 高风险门禁团队",
                "必须走负责人层和独立门禁；涉及生产、账号、数据库、安全、发布、关键 PR 或公开高风险声明时不得自办或直派执行。",
            ),
        }
        route, rule = routes[size]
        return f"""任务分发决策：
- 任务规模：{size}
- 建议路径：{route}
- 执行规则：{rule}
"""

    if args.source_role == "总控" and role == "开发" and size == "small":
        return """任务分发决策：
- 任务规模：small
- 建议路径：总控直派开发
- 执行规则：仅处理单一、短、小、可验证的低风险开发任务；一旦出现架构判断、跨文件整合或风险升级，回流架构 / CTO。
"""

    if args.source_role == "总控" and role in TECHNICAL_EXECUTION_ROLES:
        return f"""任务分发决策：
- 任务规模：{size}
- 建议路径：默认应先回到架构 / CTO
- 执行规则：除 small 开发直派或用户明确 override 外，总控不直接派发技术执行角色。
"""

    if args.source_role == "总控" and role in CONTENT_EXECUTION_ROLES:
        return f"""任务分发决策：
- 任务规模：{size}
- 建议路径：默认应先回到内容主编
- 执行规则：除用户明确 override 外，总控不直接派发内容执行角色。
"""

    return f"""任务分发决策：
- 任务规模：{size}
- 建议路径：继承来源窗口的角色分发决策
- 执行规则：保持当前角色边界；范围扩大或风险升级时回流来源窗口。
"""


def implicit_planning_contract(
    role: str, args: argparse.Namespace, profile: str
) -> str:
    """Render the smallest role-specific planning contract without a new role or command."""
    if role == "总控":
        if args.task_size == "tiny":
            return """隐性规划契约：
- 模式：route-only；只确认目标、成功条件和停止线，不得启动全库审计或技术规划。
"""
        mode = "outcome-brief" if args.task_size == "small" else "owner-contract"
        if profile == "compact":
            return f"""隐性规划契约：
- 模式：{mode}；总控只判断价值、成功标准、非目标、负责人、预算与风险，不做代码库侦察、不写技术实施步骤。
"""
        return f"""隐性规划契约：
- 模式：{mode}
- 总控只判断任务价值、成功标准、非目标、负责人、预算与风险；不做代码库侦察、不写技术实施步骤。
- 将技术理解与规格交给架构 / CTO；将内容方案交给内容主编。总控最终验收结果、风险和 go/no-go。
- 完整仓库或多类别审计必须由目标显式要求；不得仅因任务较大就自动 fan-out。
"""

    if role == "架构":
        mode = (
            "technical-brief"
            if args.task_size in {"tiny", "small"}
            else "implementation-spec"
        )
        if profile == "compact":
            return f"""隐性规划契约：
- 模式：{mode}；先读仓库事实并复核关键证据，再给范围、取舍、验证和 STOP 条件；默认不亲自实现。
"""
        return f"""隐性规划契约：
- 模式：{mode}
- Recon：读取仓库事实、约定、意图文档和真实构建/测试命令；只调查本任务需要的范围。
- Vet：亲自复核准备写入规格的关键证据，去掉误报、重复项和已有决策明确接受的取舍。
- Spec：给出目标/非目标、现状证据、方案取舍、范围、依赖、验证、风险与 STOP 条件；规格是执行契约，不是最终产品。
- 架构默认不亲自实现；完整仓库或多类别审计仅在目标显式要求时启动，不按 task-size 自动扩张。
"""

    if role == "开发":
        if args.executor_tier in ONE_SHOT_EXECUTOR_TIERS:
            return """隐性规划契约：
- 模式：execute-only；先运行漂移检查，只执行任务卡范围与验证；触发 STOP 条件时立即回报，不得重新做全库规划或自行改架构。
"""
        delegation_policy = getattr(args, "delegation_effective_policy", "optional")
        mode = (
            "task-card"
            if args.task_size in {"tiny", "small"}
            else "executor-contract"
        )
        if profile == "compact":
            if delegation_policy == "forbidden":
                return f"""隐性规划契约：
- 模式：{mode}；任务卡只用于 Dev Lead 自己分步、验证和跨压缩接续，本卡禁止派给 subagent；Dev Lead 负责实现、复验和提交。
"""
            return f"""隐性规划契约：
- 模式：{mode}；仅在下放时生成零上下文执行卡，写清范围、验证、预期结果和 STOP 条件；Dev Lead 仍负责集成、复验和提交。
"""
        if delegation_policy == "forbidden":
            return f"""隐性规划契约：
- 模式：{mode}
- Dev Lead 先核对 CTO 规格与代码现状；只补实现所需细节，不重复做全库审计。
- 任务卡用于 Dev Lead 自己分步、验证和跨压缩接续，不代表派发；本任务禁止创建开发执行 subagent。
- 内联只保留承载决策的短片段，其余使用文件、符号、提交或测试句柄；长耗时本身不改变 delegation policy。
- Dev Lead 亲自实现、复验和提交。
"""
        return f"""隐性规划契约：
- 模式：{mode}
- Dev Lead 先核对 CTO 规格与代码现状；只补实现所需细节，不重复做全库审计。
- 每个 subagent 获得一张零上下文执行卡：计划基线 commit、目标/非目标、现状证据、文件白名单/禁止范围、顺序步骤、每步验证命令与预期结果、测试和 STOP 条件。
- 内联只保留承载决策的短片段，其余使用文件、符号、提交或测试句柄；同一契约复用，不在窗口间反复改写。
- Dev Lead 仍负责集成、复验和提交；执行器报告不能替代亲自读取 diff 与重跑验收。
"""

    if role == "QA":
        return """隐性规划契约：
- 模式：evidence-review；默认只审查当前变更及直接影响面，复核验收证据并尝试证伪；不生成开发实施计划、不替实现者修代码。
"""

    return ""


def validate_source_route(role: str, args: argparse.Namespace) -> None:
    source_role = args.source_role or ""
    if source_role != "总控":
        return
    if role in OWNER_LAYER_ROLES:
        return
    if role in TECHNICAL_EXECUTION_ROLES:
        if role == "开发" and args.task_size == "small":
            return
        if not args.allow_ceo_direct_dispatch:
            raise ValueError("总控不能直接派发技术执行角色；请先派给 架构 / CTO，由架构拆给开发、UI/PPT、测试、QA、安全、DBA 或运维。")
        if not args.override_reason:
            raise ValueError("总控直派技术执行角色必须提供 --override-reason，说明用户为何明确要求绕过 架构 / CTO。")
    if role in CONTENT_EXECUTION_ROLES:
        if not args.allow_ceo_direct_dispatch:
            raise ValueError("总控不能直接派发内容执行角色；请先派给 内容主编，由内容主编拆给公众号发布、小红书或视频。")
        if not args.override_reason:
            raise ValueError("总控直派内容执行角色必须提供 --override-reason，说明用户为何明确要求绕过 内容主编。")


def has_explicit_no_delegation(args: argparse.Namespace) -> bool:
    values = [args.objective, args.work_requirements or "", args.boundary or "", *(args.forbid or [])]
    normalized = "".join("".join(values).lower().split())
    return any(
        marker in normalized
        for marker in (
            "不派subagent",
            "不使用subagent",
            "禁止subagent",
            "禁止使用subagent",
            "禁止派发subagent",
            "不得派发subagent",
            "nosubagent",
            "donotusesubagent",
            "donotdelegate",
        )
    )


def effective_delegation_policy(
    role: str, args: argparse.Namespace, controls: TaskControls
) -> str:
    if role != "开发":
        return "forbidden"
    if args.delegation_policy != "auto":
        return args.delegation_policy
    if (
        has_explicit_no_delegation(args)
        or controls.risk in {"critical", "extreme"}
        or args.executor_tier == "high-risk"
    ):
        return "forbidden"
    if (
        args.execution_profile == "parallel"
        or args.executor_tier in ONE_SHOT_EXECUTOR_TIERS
    ):
        return "required"
    return "optional"


def validate_parent_leaf(args: argparse.Namespace, controls: TaskControls) -> None:
    if args.parent_risk == "normal":
        if args.leaf_kind or args.leaf_safety:
            raise ValueError("leaf isolation evidence requires an explicit high-risk parent")
        return
    if (args.executor_tier != "mechanical" or controls.risk != "mechanical"
            or args.task_size not in {"tiny", "small"} or controls.loop_depth == "L3"):
        raise ValueError("high-risk parent permits only a small mechanical asset leaf; implementation risk cannot be downgraded")
    required = (args.project, args.leaf_kind, args.leaf_safety, args.context, args.source_thread,
                args.allow, args.read_first, args.validation, args.exit_condition)
    placeholders = {"待确认", "todo", "tbd", "unknown", "none"}
    def concrete(value: object) -> bool:
        if isinstance(value, list):
            return bool(value) and all(concrete(item) for item in value)
        return isinstance(value, str) and bool(value.strip()) and value.strip().lower() not in placeholders
    if not all(concrete(value) for value in required):
        raise ValueError("high-risk parent leaf requires kind, isolation evidence, baseline, owner, allowlist, reads, validation and STOP")
    project = Path(args.project).resolve()
    if not project.is_dir():
        raise ValueError("high-risk parent leaf requires an existing project")
    for raw in args.allow:
        path = Path(raw)
        if path.is_absolute():
            if not args.project:
                raise ValueError("absolute leaf allowlist requires --project")
            try:
                path = path.resolve().relative_to(Path(args.project).resolve())
            except ValueError as exc:
                raise ValueError("leaf file must stay within project") from exc
        relative = path.as_posix()
        if ".." in path.parts or any(char in relative for char in "*?[]"):
            raise ValueError("leaf allowlist requires exact, non-traversing file paths")
        try:
            relative = (project / path).resolve().relative_to(project).as_posix()
        except ValueError as exc:
            raise ValueError("leaf file must stay within project, including symlinks") from exc
        prefixes = ("docs/",) if args.leaf_kind == "documentation" else ("tests/fixtures/", "test/fixtures/")
        suffixes = {".md", ".rst", ".txt"} if args.leaf_kind == "documentation" else {".json", ".csv", ".txt"}
        if (not relative.startswith(prefixes) or Path(relative).suffix.lower() not in suffixes
                or (project / path).is_dir()):
            raise ValueError("high-risk parent leaf is limited to documentation or non-executable test fixtures")


def validate_delegation_contract(
    role: str, args: argparse.Namespace, controls: TaskControls
) -> None:
    policy = effective_delegation_policy(role, args, controls)
    args.delegation_effective_policy = policy
    validate_parent_leaf(args, controls)

    if role != "开发":
        if args.executor_tier != "owner":
            raise ValueError("--executor-tier is only supported for 开发")
        if args.delegation_policy not in {"auto", "forbidden"}:
            raise ValueError("non-development roles only support delegation-policy auto or forbidden")
        return

    one_shot_executor = args.executor_tier in ONE_SHOT_EXECUTOR_TIERS
    high_risk = controls.risk in {"critical", "extreme"} or args.executor_tier == "high-risk"

    if has_explicit_no_delegation(args) and policy != "forbidden":
        raise ValueError("task requirements explicitly forbid subagents; use --delegation-policy forbidden")
    if high_risk and policy != "forbidden":
        raise ValueError("critical/extreme or high-risk development must use delegation-policy forbidden")
    if controls.risk in {"critical", "extreme"} and one_shot_executor:
        raise ValueError("critical/extreme development cannot use a cheap one-shot executor tier")
    if one_shot_executor and policy != "required":
        raise ValueError("mechanical/bounded/semantic executor tiers require delegation-policy required")
    if policy == "forbidden" and (
        one_shot_executor or args.execution_profile == "parallel"
    ):
        raise ValueError("delegation-policy forbidden requires owner/high-risk tier and serial execution")
    if policy == "optional" and (
        one_shot_executor or args.execution_profile == "parallel"
    ):
        raise ValueError("delegation-policy optional is only valid for a serial Dev Lead owner")
    if policy == "required" and args.executor_tier == "high-risk":
        raise ValueError("high-risk development is owner work and cannot require delegation")
    if args.execution_profile == "parallel" and policy != "required":
        raise ValueError("parallel execution-profile requires delegation-policy required")


def default_forbidden(role: str, task_size: str = "medium") -> str:
    defaults = "未授权的生产环境、账号设置、凭据、发布动作、数据库写操作、无关重构"
    if role == "总控":
        if task_size == "tiny":
            return defaults + "、跨文件代码实现、测试脚本、验收脚本、自动化验证脚本、需要架构判断或多人协作的任务"
        return defaults + "、代码实现、测试脚本、验收脚本、自动化验证脚本、直接指挥技术或内容执行角色"
    return defaults


def loop_depth_explanation(depth: str, override_reason: str | None) -> str:
    override = f"\n- 本次 override：{override_reason}" if override_reason else ""
    return f"""Loop 深度（可折叠路由）：
- 本次深度：{depth}
- L0：用户明确指定执行角色，直接执行一个低风险小任务；来源是用户，不是总控。
- L1：总控只对接负责人层（架构 / CTO、内容主编、知识库、技能维护、文档/交付），负责人给出方案、风险、验收建议或是否需要拆下游。
- L2：负责人拆给执行角色，执行角色回调负责人，负责人收敛后回总控。
- L3：高风险闭环，在 L2 基础上加入测试、QA、安全、DBA、运维等独立复核或门禁。
- 选择原则：能 L0/L1 解决就不要升级到 L2/L3；一旦进入总控管理流，总控不直接指挥执行层。{override}
"""


def role_execution_guidance(
    role: str, args: argparse.Namespace, route: ModelRoute
) -> str:
    if role != "开发":
        return ""
    policy = args.delegation_effective_policy
    if args.executor_tier in ONE_SHOT_EXECUTOR_TIERS:
        return f"""开发执行 subagent 规则：
- 本窗口是负责人已派发的一次性 executor，使用 {route.model} + {route.thinking}；delegation-policy：required（已派发）。
- 只执行一张单一、短小、边界明确且可独立验证的任务卡；先做基线漂移检查，命中 STOP 条件立即回报。
- 必须遵守文件白名单、禁止范围、验收命令和退出条件；不得承担架构判断、跨文件整合、纠偏策略、最终验证或提交。
- 完成后回传 diff/验证证据并关闭；不写入 .codex/role-windows.md，不作为角色窗口复用。
"""

    common = f"""开发负责人 / Dev Lead 执行规则：
- 本窗口是开发负责人 / Dev Lead，使用 {route.model} + {route.thinking}，负责拆解、集成、纠偏、最终验证和提交。
- delegation-policy：{policy}
"""
    if policy == "forbidden":
        return common + """- 本任务禁止派发开发执行 subagent；Dev Lead 亲自完成实现。具体任务要求和高风险门禁优先于任何通用降本建议。
- “耗时长”只触发任务卡、检查点、提交或压缩交接，不构成派发或并行理由。
- live/资金/并发/账本、PnL/fee、高风险实现或重复失败返工不得下放。
"""
    if policy == "required":
        return common + """- 必须派发至少一个单一、短小、边界明确且可独立验证的一次性 executor；无合格叶子任务立即回流。
- 路由：mechanical/bounded = gpt-5.6-luna + high；semantic = gpt-5.6-terra + high。
- 生成任务卡不等于已派发；创建 subagent 时必须显式传入 model/thinking，替代时回传实际模型和原因。
- 任务卡带基线、白名单、禁止范围、验收、预期结果和 STOP；Dev Lead 负责整合、复验、提交。
- 耗时长本身不是派发或并行理由。
"""
    return common + """- Dev Lead 可自行判断是否派发；仅可下放单一、短小、边界明确且可独立验证的叶子任务，未派发回传原因。
- 路由：mechanical/bounded = gpt-5.6-luna + high；semantic = gpt-5.6-terra + high。
- 生成任务卡不等于已派发；创建 subagent 时显式传入 model/thinking，替代时回传实际模型和原因。
- 任务卡带基线、白名单、禁止范围、验收和 STOP；Dev Lead 负责整合、复验、提交。
- 耗时长只触发任务卡、检查点、提交或压缩交接，不自动触发 subagent；live/资金/并发/账本、PnL/fee 不得下放。
"""


def executor_usage_guidance(role: str, args: argparse.Namespace) -> str:
    if role != "开发":
        return ""
    policy = args.delegation_effective_policy
    return f"""执行器使用回传（开发必填）：
- delegation-policy：{policy}
- 回传：是否派发、实际 model/thinking、任务卡/证据、重试/返工、Dev Lead 复验；optional 未派发写原因，forbidden 写“策略禁止”。
"""


def execution_profile_guidance(role: str, args: argparse.Namespace) -> str:
    if role != "开发":
        return ""
    if args.execution_profile == "serial":
        policy = args.delegation_effective_policy
        if policy == "forbidden":
            detail = "串行由 Dev Lead 亲自执行；禁止创建 worker。"
        elif policy == "required":
            detail = "串行使用一个一次性 worker；Dev Lead 等待结果后整合和复验。"
        else:
            detail = "默认串行；只有满足派发资格时才可选择一个一次性 worker。"
        return f"""执行拓扑：
- execution-profile：serial
- worker-count：1
- {detail}
"""
    return f"""执行拓扑：
- execution-profile：parallel
- worker-count：{args.worker_count}
- 范围互斥证据：{args.disjoint_scope}
- 独立验证证据：{args.independent_validation}
- 2-5 个 worker 仅用于显式并行 profile；每个 worker 都是任务结束即关闭的一次性 subagent。
"""


def validate_execution_profile(role: str, args: argparse.Namespace) -> None:
    if args.executor_tier in ONE_SHOT_EXECUTOR_TIERS and args.execution_profile != "serial":
        raise ValueError("one-shot executor must use serial execution; only Dev Lead may fan out")
    if args.execution_profile == "serial":
        if args.worker_count != 1:
            raise ValueError("serial execution-profile requires --worker-count 1")
        return
    if role != "开发":
        raise ValueError("parallel execution-profile is only supported for 开发 / Dev Lead")
    if args.worker_count < 2 or args.worker_count > 5:
        raise ValueError("parallel execution-profile requires --worker-count between 2 and 5")
    missing = []
    if not args.disjoint_scope:
        missing.append("--disjoint-scope")
    if not args.independent_validation:
        missing.append("--independent-validation")
    if missing:
        raise ValueError("parallel execution-profile requires " + " and ".join(missing))


def validate_spark_opportunity(
    role: str, args: argparse.Namespace, controls: TaskControls
) -> None:
    if args.spark_available and not args.prefer_spark:
        raise ValueError("--spark-available requires --prefer-spark")
    if not args.prefer_spark:
        return
    if role != "开发" or args.executor_tier not in {"mechanical", "bounded"}:
        raise ValueError("Spark Opportunity Lane only supports 开发 mechanical or bounded one-shot executors")
    if controls.risk in {"critical", "extreme"}:
        raise ValueError("Spark Opportunity Lane does not support critical or extreme risk")


def selected_model_route(
    role: str, args: argparse.Namespace, controls: TaskControls
) -> ModelRoute:
    if args.prefer_spark and args.spark_available:
        return ModelRoute(
            "gpt-5.3-codex-spark",
            "high",
            "仅用于短小、文本型、范围明确且可独立验证的一次性编码任务；不可用、排队或范围增长时回退稳定路由。",
        )
    return model_route(role, controls.risk, args.executor_tier)


def spark_opportunity_guidance(
    role: str, args: argparse.Namespace, controls: TaskControls
) -> str:
    if role != "开发" or not args.prefer_spark:
        return ""
    fallback = model_route(role, controls.risk, args.executor_tier)
    selection = (
        "使用 Spark 独立额度"
        if args.spark_available
        else f"Spark 未确认可用，回退稳定路由 {fallback.model} + {fallback.thinking}"
    )
    return f"""Spark Opportunity Lane：
- 选择结果：{selection}
- 适用边界：仅限 mechanical/bounded、文本型、短小且可独立验证的一次性开发 executor。
- 预览约束：research preview、128K、text-only；独立限额和可用性可能随需求调整。
- 验证门禁：Spark 默认工作方式轻量，任务卡必须显式运行验证命令并回传结果。
"""


def ui_preview_route_guidance(role: str, args: argparse.Namespace) -> str:
    if role != "UI/PPT":
        return ""
    if args.task_size == "tiny":
        reference_budget = "tiny：不做外部灵感搜索，复用项目现有组件、Token 和相邻页面，只验证受影响视口。"
        switch_budget = "tiny 不做外部换源，只修正项目内模式。"
    elif args.task_size == "small":
        reference_budget = "small：项目内没有可用模式时最多补 1 份外部参考。"
        switch_budget = "small 最多换源 1 轮。"
    else:
        reference_budget = "medium+：最多 3 份参考，且职责互斥：布局、配色/字体、组件/动效各 1 份。"
        switch_budget = "medium+ 默认最多换源 2 轮。"
    return f"""UI 工程闭环（先加载 $ui-implementation-workflow）：
- 页面分类：先在 marketing、brand、portfolio、content、auth、dashboard、list、detail、form、settings、mobile 中选一个主类型；后台/表单/数据页禁止套营销 Hero 和炫技动效。
- 视觉方向：仅 marketing、brand、portfolio、content 且现有系统不足时读取 ui-implementation-workflow/references/visual-direction.md；design-taste-frontend 只作兼容入口，不再运行第二套 UI 流程。
- 审核信号重置：不继承旧审美偏好；用户或指定审核者对实际截图的明确反馈写入 .codex/ui-visual-review-signals.md，先保留为 raw 证据，不自动形成长期或跨项目偏好。
- 项目审计：先读现有技术栈、组件库、共享布局、Token、资产和相邻页面；{reference_budget}
- 先分析后编码：代码修改前输出 UI implementation plan，包含布局层级、字体、语义色、间距/圆角/阴影、交互状态、动效、响应式、借鉴与拒绝项。
- Token 与顺序：优先复用现有 Token；按结构 -> 数据/交互 -> 响应式 -> 字体/颜色 -> 装饰 -> 动效实现，禁止先做粒子背景再补业务流程。
- 截图闭环：加载 $browser-automation-router，在 1440/768/390 三个宽度检查溢出、截断、对齐、间距、控件高度、横向滚动和动效可读性；修复后重截受影响宽度，不得只看代码推测。
- 动态换源：完整网站目录只作库存，不一次性加载；效果不达标时先归因到布局、视觉、组件或动效，每轮只替换对应的一份参考并记录失败原因；{switch_budget}超限回报决策，不无限浏览。

预览图实现路线选择：
- 有预览图、参考图、截图或视觉保真目标时，不要默认拿 CSS 硬干；先给出 2-4 条实现路线并说明取舍。
- 候选路线至少考虑：CSS/组件复刻、图片切片/生成资产、Canvas/SVG、Three.js/WebGL、Lottie/视频、现成库/组件、手工或生成式视觉资产。
- 选择依据：交互需求、响应式要求、可维护性、加载性能、可访问性、动效复杂度、还原精度、后续内容替换成本。
- 如果预览图是复杂插画、纹理、3D、粒子、复杂动效或 AI 难以稳定复刻的视觉，优先考虑资产化或专用渲染路线，不要用大量脆弱 CSS 堆效果。
- 进入开发前输出推荐路线、拒绝路线、需要的资产/工具、验收方式；实现后用截图对比、像素/布局检查或视觉 QA 证据验证。
"""


def content_research_guidance(role: str) -> str:
    if role not in CONTENT_ROLES:
        return ""
    return """X MCP 内容研究源（可选、只读、需授权）：
- 适用：爆款内容研究、热点扫描、选题池、对标账号、跨平台讨论脉络。
- 默认由内容主编统筹调用；公众号发布、小红书、视频可继承内容主编结论，或在被明确指派时使用。
- 官方文档：https://docs.x.com/tools/mcp；X MCP 通过 https://api.x.com/mcp + xurl mcp 连接，Docs MCP 可用于查询 X API 文档。
- 默认只读：搜索 posts、用户、用户时间线、trends/news 和公开讨论；需要 X Developer app 与 OAuth 授权，不把 CLIENT_ID/CLIENT_SECRET 写入 repo。
- 禁止发帖、发布 Article、关注/取关、点赞、转发、私信、账号设置；任何写操作都需要用户单独明确授权。
"""


def content_tone_gate(role: str) -> str:
    if role not in PUBLIC_COPY_ROLES:
        return ""
    return """反老登味 / 反 AI 味内容闸门：
- 正式对外内容必须先过这道闸门，再交付预览、发布包、复制文本、封面/社交卡文案或视频脚本。
- 反老登味：避免说教、爹味、上位者口吻、油腻成功学、年龄/资历压人、替读者下判断。
- 反 AI 味：避免模板化、空泛排比、万能套话、机械转折、过度总结、没有个人判断。
- 改写原则：保留真实经验、具体细节、自然口语、平台语感和读者处境。
- 安全边界：不改变事实、数据、价格、日期、来源、授权边界；不新增背书、效果承诺或发布状态。
- 执行方式：内容主编负责定义口径并验收；公众号发布、小红书、视频和含公开中文文案的 UI/PPT 产物执行；最终正式中文文案仍需加载并使用 $humanizer-zh。
"""


def browser_automation_guidance(role: str) -> str:
    if role not in BROWSER_ROLES:
        return ""
    return """浏览器自动化路由：
- 先加载 $browser-automation-router；公开页、localhost 和视觉验收优先应用内 Browser，需要现有登录态、Chrome tab/profile/extension 时优先原生 Chrome 插件。
- 仅在 CI、可复现回归、trace、无人值守批处理或原生插件不可用时使用 $playwright 或平台脚本；不默认维护临时 JavaScript、cookie 导入或 profile-path 启动逻辑。
- 原生路由最低能力门槛为 Codex Desktop 2026-06-11 发布版本且当前任务实际可见对应插件；缺失时 fail closed 到明确降级方案。
"""


def xhs_automation_publish_gate(role: str) -> str:
    if role != "小红书":
        return ""
    return """小红书自动化发布门禁：
- 自动化登录、创作者中心交互填充和发布卡点排查先走 $browser-automation-router 的原生 Chrome 登录态；批量填充、内容数据导出、搜索详情读取或原生插件降级时使用 $xhs-automation-publisher。
- 原生 Chrome 默认只填充并让用户复核；脚本降级默认先用 --preview 或 cdp_publish.py fill。publish_pipeline.py 默认会自动点击发布，缺少 --preview 时视为高风险动作。
- click-publish、post-comment-to-feed、respond-comment、note-upvote、note-bookmark 等发布/互动命令必须二次明确授权；不得把评论、点赞收藏、切号、清理账号 Profile 当作普通发布步骤。
- 本地 cookie、登录二维码、账号配置、Chrome profile 路径和真实账号状态不得写入仓库或回调正文。
"""


def effective_token_profile(
    role: str, args: argparse.Namespace, controls: TaskControls
) -> str:
    if args.profile != "auto":
        return args.profile
    if (
        args.task_size == "critical"
        or controls.risk in {"critical", "extreme"}
        or controls.loop_depth == "L3"
    ):
        return "full"
    if (
        args.task_size == "large"
        or role == "架构"
        or args.new_code_project
        or controls.loop_depth == "L2"
    ):
        return "standard"
    return "compact"


def token_profile_strategy(profile: str) -> str:
    strategies = {
        "compact": "只保留闭环必需字段；省略深层技术方案、CodeGraph 和开源扫描占位，适合 L0/L1 小闭环。",
        "standard": "保留常规路由、验证、技能台账和必要技术/内容门禁，适合 L2 普通协作。",
        "full": "保留完整深层检查、CodeGraph、开源扫描和门禁字段，适合 L3、高风险、关键 PR 或新代码项目。",
    }
    return strategies[profile]


def prompt_codegraph_policy(role: str, args: argparse.Namespace) -> str:
    effective = getattr(args, "codegraph_effective_policy", None)
    if effective:
        return effective
    if args.codegraph_policy != "auto":
        return args.codegraph_policy
    if role == "架构" or args.new_code_project:
        return "check"
    return "skip"


def codegraph_planning_section(role: str, args: argparse.Namespace) -> str:
    policy = prompt_codegraph_policy(role, args)
    status = getattr(args, "codegraph_status", None)
    if status is None:
        status = {
            "tool_available": False,
            "tool_path": "未检查",
            "initialization_status": "未检查",
            "freshness_status": "未检查",
            "index_path": "未检查",
            "index_ignored_by_gitignore": False,
            "file_count": None,
            "node_count": None,
            "edge_count": None,
            "pending_changes": None,
            "worktree_mismatch": None,
            "ready": False,
            "recommendation": "请改用 prepare_role_window.py 执行前置检查。",
            "skip_or_failure_reason": "底层渲染器不执行环境探测。",
        }

    if policy == "skip":
        gate = "已按策略跳过"
    elif status["ready"]:
        gate = "通过" if policy in {"required", "init", "sync"} else "只读检查通过"
    else:
        gate = "未通过" if policy in {"required", "init", "sync"} else "只读检查未就绪"

    availability = "可用" if status["tool_available"] else "不可用/未检查"
    ignored = "是" if status["index_ignored_by_gitignore"] else "否/未配置"
    return f"""CodeGraph 状态（新本地代码项目必填；不适用时写明原因）：
- CodeGraph policy：{policy}
- 门禁结果：{gate}
- 可用性与初始化状态：工具{availability}（{status['tool_path']}）；{status['initialization_status']}；新鲜度={status['freshness_status']}
- 索引路径/忽略策略：{status['index_path']}；.gitignore 忽略={ignored}
- 索引摘要：files={status['file_count']}；nodes={status['node_count']}；edges={status['edge_count']}；pending={status['pending_changes']}；worktreeMismatch={status['worktree_mismatch']}
- 建议动作：{status['recommendation']}
- 跳过或失败原因：{status['skip_or_failure_reason']}
"""


def architecture_planning_sections(role: str, args: argparse.Namespace) -> str:
    sections: list[str] = []
    if role == "架构":
        sections.append("""技术方案（架构/CTO 处理复杂技术需求必填；已选定则写明选型）：
- 状态：必填
- 候选方案与取舍：待确认
- 推荐与约束：待确认
""")
    if role == "架构" or args.new_code_project or args.codegraph_policy != "auto":
        sections.append(codegraph_planning_section(role, args))
    if role == "架构":
        sections.append("""开源/可借鉴方案扫描：
- 检索关键词与候选方案：待确认
- 可借鉴点、不采用风险、下游约束：待确认
""")
    return "\n".join(sections)


def full_profile_gate(profile: str, callback_target: str, controls: TaskControls) -> str:
    if profile != "full" and controls.loop_depth != "L3":
        return ""
    label = "full" if profile == "full" else "L3"
    return f"""独立门禁与失败回退（{label} 必填）：
- 独立复核角色与证据：待确认；不得由实现者自证通过
- 失败/回滚条件与执行责任人：待确认
- 未解决风险、剩余不确定性与影响范围：待确认
- 最终 go/no-go 决策方：{callback_target}
"""


def build_compact_prompt(
    *,
    args: argparse.Namespace,
    role: str,
    route: ModelRoute,
    controls: TaskControls,
    callback_target: str,
    project: str,
    read_first: list[str],
    allowed: list[str],
    forbidden: list[str],
    validation: list[str],
    candidate_skills: list[str],
    required_skills: list[str],
    optional_skills: list[str],
    skipped_skills: list[str],
    profile: str,
) -> str:
    return f"""【给 {role} 窗口的 compact 提示词】
角色：{role}；项目：{project}；方式：{args.mode}；来源窗口：{callback_target}
上下文：{args.context or "待确认"}

模型建议：
- model：{route.model}
- thinking：{route.thinking}
- 条件：{route.escalation}
Token Budget Profile：
- profile：{profile}
- 策略：{token_profile_strategy(profile)}
{role_execution_guidance(role, args, route)}{execution_profile_guidance(role, args)}{executor_usage_guidance(role, args)}{spark_opportunity_guidance(role, args, controls)}{ui_preview_route_guidance(role, args)}{browser_automation_guidance(role)}{content_research_guidance(role)}{content_tone_gate(role)}{xhs_automation_publish_gate(role)}
角色树位置：{ROLE_TREE_POSITION[role]}
{task_controls_guidance(args, controls)}
Loop 深度（可折叠路由）：
- 本次深度：{controls.loop_depth}；L0 直达，L1 负责人，L2 负责人拆执行，L3 增加独立门禁。
- 本次 override：{args.override_reason or "无"}
任务分发决策：
- {task_dispatch_decision(role, args).splitlines()[1].removeprefix("- ")}
- {task_dispatch_decision(role, args).splitlines()[2].removeprefix("- ")}
- {task_dispatch_decision(role, args).splitlines()[3].removeprefix("- ")}
{implicit_planning_contract(role, args, profile)}
{full_profile_gate(profile, callback_target, controls)}
{codegraph_planning_section(role, args) if prompt_codegraph_policy(role, args) != "skip" else ""}
负责人交互边界：
- 总控只对接负责人层；技术执行由 CTO 派发，内容执行由内容主编派发。

目标：{args.objective}
请先阅读/检查：
{lines_or_default(read_first, "agent-role-orchestrator/SKILL.md；.codex/role-windows.md；目标相关文件")}
允许修改：
{lines_or_default(allowed, "待确认；确认前只读")}
禁止修改：
{lines_or_default(forbidden, default_forbidden(role, args.task_size))}
实现/工作要求：{args.work_requirements or "只处理本轮目标；不搬运旧聊天、长日志或大段源码。"}
验证：
{lines_or_default(validation, "给出命令、文件、截图或无法验证的原因")}

闭环状态：当前={args.loop_state}；上一轮={args.previous_feedback or "无 / 待确认"}；退出={args.exit_condition or "完成、阻塞有证据、或需来源决策"}
上下文预算：只传增量与证据；过长时用台账、提交、PR 或压缩交接卡接续。
闭环完成条件：更新 .codex/role-windows.md 并提交，同时向来源 thread 发送压缩回调；仅更新台账不算闭环。
路由前检查：orchestrator={route_check_value(args.read_orchestrator)}；ledger={route_check_value(args.read_ledger)}；复用线程={args.reuse_thread or "待确认"}；更新台账={args.update_ledger or "待确认"}。
技能路由台账：
- 候选 skill：{csv_or_default(candidate_skills, "待确认")}
- 必选 skill：{csv_or_default(required_skills, "无 / 待确认")}
- 可选 skill：{csv_or_default(optional_skills, "无 / 待确认")}
- 跳过 skill 及原因：{csv_or_default(skipped_skills, "无")}
提交/PR 要求：{args.commit_requirements or "遵循 AGENTS.md；回报变更与验证证据。"}

回调/通知规则：本任务发起方：{callback_target}。完成、阻塞、需决策时主动通知；无发送工具时，以 <codex_delegation> 或“压缩回调”开头。
结构化反馈格式：问题/缺口；证据/复现；影响等级；建议回流对象；需要决策；下一闭环状态。
压缩回调：
- 当前状态：
- 本轮变化：
- 证据链接/文件/命令：
- 需要决策：
- 下一回流对象：
技能命中回传：
- 已加载并使用：
- 来源窗口要求但未使用：
- 临时发现应补用：
- 误召/无效加载：
- 影响产出的 skill：
规则沉淀：可复用优化沉淀=无 / 建议 / 已沉淀；写明目标位置和后续。
完成后请回传：{args.return_requirements or "压缩回调、验证证据、技能命中回传、规则沉淀状态。"}
角色底线：{args.boundary or "不越权、不编造证据、不扩大范围。"}
"""


def build_executor_prompt(args: argparse.Namespace, route: ModelRoute, controls: TaskControls,
                          callback_target: str) -> str:
    """One-shot workers never inherit a durable window's closure or fanout contract."""
    return f"""【开发一次性执行卡】
- actor-kind：executor
- fanout-policy：forbidden
- ledger-write：forbidden
- commit-policy：forbidden
- 本任务发起方：{callback_target}
{f"父任务风险：{args.parent_risk}；leaf-kind：{args.leaf_kind}; owner-gates：retained" if args.parent_risk != "normal" else ""}
{f"叶子隔离证据：{args.leaf_safety}；父任务 L3 门禁与最终验收仍由负责人保留，本叶子完成不代表整体通过。" if args.parent_risk != "normal" else ""}
项目：{args.project or "待确认"}
模型建议：
- model：{route.model}
- thinking：{route.thinking}
{task_controls_guidance(args, controls)}
{role_execution_guidance("开发", args, route)}
{implicit_planning_contract("开发", args, "compact")}
{spark_opportunity_guidance("开发", args, controls)}
{codegraph_planning_section("开发", args) if prompt_codegraph_policy("开发", args) != "skip" else ""}
目标：{args.objective}
基线：{args.context or "以负责人任务卡的提交/文件证据为准；无法核实时 STOP"}
请先阅读/检查：
{lines_or_default(args.read_first, "仅负责人任务卡及白名单目标；缺失时 STOP")}
允许修改：
{lines_or_default(args.allow, "待确认；确认前只读并回报")}
禁止修改：
- 台账、Git 提交、创建角色窗口或再次派发 worker；架构判断、跨任务集成、最终验收。
{lines_or_default(args.forbid, default_forbidden("开发"))}
实现/工作要求：{args.work_requirements or "只完成本张卡；缺少范围或验证时 STOP"}
验证：
{lines_or_default(args.validation, "待确认；不得自报验证通过")}
STOP / 退出条件：{args.exit_condition or "完成指定验证即回报；漂移、范围扩大、验证失败或缺少授权立即停止"}
结果回传：完成/阻塞；diff；验证命令与结果；实际 model/thinking；重试/返工；未解决问题。
必选 skill：{csv_or_default(args.required_skill, "无")}
技能使用回传：已使用、未使用及原因；只报证据，不写共享台账。
负责人保留集成、最终复验、提交和来源窗口闭环；执行器回报后结束。
"""


def build_prompt(args: argparse.Namespace) -> str:
    role = canonical_role(args.role)
    controls = effective_task_controls(args)
    if (
        args.codegraph_policy in {"required", "init", "sync"}
        and not hasattr(args, "codegraph_status")
    ):
        raise ValueError(
            "strict CodeGraph policies require prepare_role_window.py; "
            "render_role_prompt.py does not inspect or mutate the project"
        )
    validate_source_route(role, args)
    validate_delegation_contract(role, args, controls)
    validate_execution_profile(role, args)
    validate_spark_opportunity(role, args, controls)
    route = selected_model_route(role, args, controls)
    source_role = args.source_role or ("用户" if role in {"总控", "架构"} else "待确认")
    source_thread = args.source_thread or "待确认"
    project = args.project or "待确认"
    required_skills = args.required_skill or []
    optional_skills = args.optional_skill or []
    candidate_skills = args.candidate_skill or []
    skipped_skills = args.skipped_skill or []
    read_first = args.read_first or []
    allowed = args.allow or []
    forbidden = args.forbid or []
    validation = args.validation or []
    callback_target = f"{source_role} / thread id: {source_thread}"
    profile = effective_token_profile(role, args, controls)

    if args.executor_tier in ONE_SHOT_EXECUTOR_TIERS:
        return build_executor_prompt(args, route, controls, callback_target)

    if profile == "compact":
        return build_compact_prompt(
            args=args,
            role=role,
            route=route,
            controls=controls,
            callback_target=callback_target,
            project=project,
            read_first=read_first,
            allowed=allowed,
            forbidden=forbidden,
            validation=validation,
            candidate_skills=candidate_skills,
            required_skills=required_skills,
            optional_skills=optional_skills,
            skipped_skills=skipped_skills,
            profile=profile,
        )

    return f"""【给 {role} 窗口的提示词】

你现在担任：
{role}

背景：
- 项目/路径：{project}
- 交接方式：{args.mode}
- 来源窗口：{callback_target}
- 当前已知上下文：{args.context or "待确认"}

模型建议：
- model：{route.model}
- thinking：{route.thinking}
- 升级/降级条件：{route.escalation}

Token Budget Profile：
- profile：{profile}
- 策略：{token_profile_strategy(profile)}

{role_execution_guidance(role, args, route)}
{execution_profile_guidance(role, args)}
{executor_usage_guidance(role, args)}
{spark_opportunity_guidance(role, args, controls)}
{ui_preview_route_guidance(role, args)}
{browser_automation_guidance(role)}
{content_research_guidance(role)}
{content_tone_gate(role)}
{xhs_automation_publish_gate(role)}
角色树位置（总控/架构/内容主编/执行角色）：
{ROLE_TREE_POSITION[role]}

{task_controls_guidance(args, controls)}
{loop_depth_explanation(controls.loop_depth, args.override_reason)}
{task_dispatch_decision(role, args)}
{implicit_planning_contract(role, args, profile)}
负责人交互边界：
- 总控只对接负责人/治理层；技术执行由 CTO 负责，内容执行由内容主编负责。只有用户明确 override 时越级。
- 总控不编写代码、测试或验收脚本；由开发/测试实现，架构/QA 复核，总控只验收结果、风险和决策点。

{architecture_planning_sections(role, args)}
{full_profile_gate(profile, callback_target, controls)}

目标：
{args.objective}

请先阅读/检查：
{lines_or_default(read_first, "agent-role-orchestrator/SKILL.md；项目 .codex/role-windows.md（若存在）；与目标直接相关的项目文件")}

允许修改：
{lines_or_default(allowed, "待确认；未确认前只读")}

禁止修改：
{lines_or_default(forbidden, default_forbidden(role, args.task_size))}

实现/工作要求：
{args.work_requirements or "按角色边界推进；不确定信息写待确认；不要编造线程、事实、验证结果或发布状态。"}

验证：
{lines_or_default(validation, "说明无法验证的原因；可验证项必须给出命令、文件、截图或人工检查步骤")}

闭环状态：
- 当前状态：{args.loop_state}
- 上一轮反馈：{args.previous_feedback or "无 / 待确认"}
- 本轮退出条件：{args.exit_condition or "完成目标、阻塞并说明证据、或需要来源窗口决策"}

上下文预算：
- 只传状态增量、证据句柄、决策和下一回流对象；不搬运完整聊天、长日志或大段源码。
- 每次状态变化更新 .codex/role-windows.md；长任务用压缩交接卡、提交、PR 和文件证据接续。

闭环完成条件：
- 完成、阻塞或需要发起方决策时，必须同时完成两件事：1. 更新 .codex/role-windows.md 并提交；2. 向来源 thread 主动发送压缩回调。
- 仅完成第 1 项不算闭环；来源 thread 未收到回调时，负责人层仍应视为待回流。
- 如果当前窗口没有发送工具，最终输出必须以 <codex_delegation> 或“压缩回调”开头，供系统/用户转发。
- 如果项目不是 git 仓库、项目禁止写入或无法提交，必须在压缩回调中说明原因和替代证据。

路由前检查（总控、架构、内容主编和多角色派发必填）：
- orchestrator：{route_check_value(args.read_orchestrator)}；role-windows：{route_check_value(args.read_ledger)}；复用线程：{args.reuse_thread or "待确认"}
- 模型、来源回调、允许/禁止范围、验证/提交、技能台账：已写入本提示词
- 是否更新 .codex/role-windows.md：{args.update_ledger or "待确认"}

技能路由台账（总控、架构、内容主编和多角色拆分必填；单一执行角色可写“不适用/继承来源台账”）：
- 候选 skill：{csv_or_default(candidate_skills, "待确认")}
- 必选 skill：{csv_or_default(required_skills, "无 / 待确认")}
- 可选 skill：{csv_or_default(optional_skills, "无 / 待确认")}
- 跳过 skill 及原因：{csv_or_default(skipped_skills, "无")}
- 预期加载角色：{role}

提交/PR 要求：
{args.commit_requirements or "遵循项目 AGENTS.md；未要求提交时先回报变更和验证证据。"}

回调/通知规则：
- 本任务发起方：{callback_target}。完成、阻塞或需决策时执行上方闭环完成条件，不等待用户转述。

结构化反馈格式（返工/验收失败/需要决策时必填）：
- 问题/缺口；证据/复现；影响等级；建议回流对象；需要决策；下一闭环状态。

压缩回调：
- 当前状态：
- 本轮变化：
- 证据链接/文件/命令：
- 需要决策：
- 下一回流对象：

技能命中回传：
- 已加载并使用：
- 来源窗口要求但未使用：
- 临时发现应补用：
- 误召/无效加载：
- 影响产出的 skill：

规则沉淀：
- 可复用优化沉淀：无 / 建议 / 已沉淀
- 具体问题、目标位置、已执行变更或建议后续：

完成后请回传：
{args.return_requirements or "压缩回调、验证证据、技能命中回传、规则沉淀状态。"}

角色底线：
{args.boundary or "守住角色边界；不越权发布、写生产、改凭据、编造证据或扩大范围。"}
"""


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Render a copy-paste role prompt with mandatory loop, callback, skill-hit, and model-routing fields.",
    )
    parser.add_argument("--role", required=True, help="Canonical role or alias, e.g. 总控, 架构, 开发, QA, 内容主编.")
    parser.add_argument("--objective", required=True, help="Concrete task objective. Required to avoid blank prompts.")
    parser.add_argument("--project", help="Project path or scope.")
    parser.add_argument("--mode", default="新建", choices=["新建", "继承", "接续", "重置"])
    parser.add_argument("--loop-depth", default="L1", choices=["L0", "L1", "L2", "L3"], help="Collapsible routing depth. Effective controls promote large work to at least L2 and critical/extreme work to L3.")
    parser.add_argument("--profile", default="auto", choices=["auto", "compact", "standard", "full"], help="Token budget profile. auto chooses compact for tiny/small/ordinary medium work, standard for large/L2/architecture/new-code work, and full for critical/L3/high-risk gates.")
    parser.add_argument("--task-size", default="medium", choices=["tiny", "small", "medium", "large", "critical"], help="Task dispatch size. large promotes the effective loop to at least L2; critical promotes effective risk/loop to critical/L3.")
    parser.add_argument("--risk", default="normal", choices=["normal", "mechanical", "critical", "extreme"], help="Use mechanical only for fully scoped rote work. Critical/extreme risk promotes the effective loop to L3 and controls model/profile routing.")
    parser.add_argument("--executor-tier", default="owner", choices=["owner", "mechanical", "bounded", "semantic", "high-risk"], help="Development execution tier. bounded routes a one-shot executor to Luna; owner keeps the durable Dev Lead route.")
    parser.add_argument("--parent-risk", default="normal", choices=["normal", "critical", "extreme"], help="Parent risk for an isolated asset leaf; does not reduce this task's own --risk.")
    parser.add_argument("--leaf-kind", choices=["documentation", "test-fixture"], help="Pilot lane for non-implementation assets under a high-risk parent.")
    parser.add_argument("--leaf-safety", help="Owner-approved evidence of isolation from high-risk implementation and shared evolving state.")
    parser.add_argument(
        "--delegation-policy",
        default="auto",
        choices=["auto", "forbidden", "optional", "required"],
        help=(
            "Development subagent contract. auto resolves to forbidden for high-risk or explicit no-subagent work, "
            "required for one-shot/parallel execution, and optional for an ordinary serial Dev Lead."
        ),
    )
    parser.add_argument("--execution-profile", default="serial", choices=["serial", "parallel"], help="Development topology. Parallel is fail-closed and requires disjoint scope plus independent validation.")
    parser.add_argument("--worker-count", type=int, default=1, help="One-shot development workers. Default 1; explicit parallel profile permits 2-5.")
    parser.add_argument("--disjoint-scope", help="Evidence that parallel worker file/surface ownership does not overlap.")
    parser.add_argument("--independent-validation", help="Evidence that each parallel worker has an independent validation command or check.")
    parser.add_argument("--prefer-spark", action="store_true", help="Prefer the opportunistic Spark lane for a mechanical/bounded one-shot development executor.")
    parser.add_argument("--spark-available", action="store_true", help="Confirm Spark is currently available with usable preview quota; requires --prefer-spark.")
    parser.add_argument("--source-role", help="Source/callback role. Defaults to 用户 only for 总控/架构, otherwise 待确认.")
    parser.add_argument("--source-thread", help="Source thread id. Defaults to 待确认.")
    parser.add_argument("--context", help="Short known context.")
    parser.add_argument("--read-first", action="append", default=[], help="Required file/doc to read first. Repeatable.")
    parser.add_argument("--allow", action="append", default=[], help="Allowed file/surface. Repeatable.")
    parser.add_argument("--forbid", action="append", default=[], help="Forbidden file/surface/action. Repeatable.")
    parser.add_argument("--validation", action="append", default=[], help="Validation command or manual check. Repeatable.")
    parser.add_argument("--candidate-skill", action="append", default=[], help="Candidate skill. Repeatable.")
    parser.add_argument("--required-skill", action="append", default=[], help="Required skill. Repeatable.")
    parser.add_argument("--optional-skill", action="append", default=[], help="Optional skill. Repeatable.")
    parser.add_argument("--skipped-skill", action="append", default=[], help="Skipped skill with reason, e.g. skill: reason. Repeatable.")
    parser.add_argument("--loop-state", default="待确认")
    parser.add_argument("--previous-feedback")
    parser.add_argument("--exit-condition")
    parser.add_argument("--reuse-thread")
    parser.add_argument("--update-ledger")
    parser.add_argument("--work-requirements")
    parser.add_argument("--commit-requirements")
    parser.add_argument("--return-requirements")
    parser.add_argument("--boundary")
    parser.add_argument("--read-orchestrator", action="store_true", help="Mark orchestrator skill as read.")
    parser.add_argument("--read-ledger", action="store_true", help="Mark project role ledger as read.")
    parser.add_argument("--new-code-project", action="store_true", help="Require CodeGraph status fields.")
    parser.add_argument(
        "--codegraph-policy",
        default="auto",
        choices=["auto", "skip", "check", "required", "init", "sync"],
        help=(
            "CodeGraph preflight. auto performs a read-only check for architecture/new-code prompts; "
            "required fails unless the index is ready; init/sync are explicit write policies and only run through prepare_role_window.py."
        ),
    )
    parser.add_argument("--allow-ceo-direct-dispatch", action="store_true", help="Allow an explicit user override for 总控 -> execution-role direct dispatch.")
    parser.add_argument("--override-reason", help="Required when --allow-ceo-direct-dispatch bypasses 架构 / CTO or 内容主编.")
    parser.add_argument("--output", type=Path, help="Write prompt to file instead of stdout.")
    return parser


def parse_args(argv: list[str]) -> argparse.Namespace:
    return build_arg_parser().parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        prompt = build_prompt(args)
    except Exception as exc:  # noqa: BLE001
        print(f"render_role_prompt failed: {exc}", file=sys.stderr)
        return 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
