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
TECHNICAL_EXECUTION_ROLES = {"开发", "UI/PPT", "测试", "QA", "安全", "DBA", "运维"}
CONTENT_EXECUTION_ROLES = {"公众号发布", "小红书", "视频"}
OWNER_LAYER_ROLES = {"架构", "内容主编", "知识库", "技能维护", "文档/交付"}


@dataclass(frozen=True)
class ModelRoute:
    model: str
    thinking: str
    escalation: str


def canonical_role(raw: str) -> str:
    role = CANONICAL_ROLES.get(raw, CANONICAL_ROLES.get(raw.lower()))
    if not role:
        choices = "、".join(sorted(set(CANONICAL_ROLES.values())))
        raise ValueError(f"unknown role {raw!r}; choose one of: {choices}")
    return role


def model_route(role: str, risk: str) -> ModelRoute:
    if role in {"总控", "架构"}:
        return ModelRoute("gpt-5.5", "xhigh", "降级仅限低风险摘要或已确认的机械同步。")
    if role == "开发":
        return ModelRoute("gpt-5.5", "xhigh", "开发执行 subagent 默认使用 gpt-5.3-codex-spark + xhigh；复杂架构决策或跨系统高风险变更回流架构/总控。")
    if role == "QA":
        if risk == "critical":
            return ModelRoute("gpt-5.5", "xhigh", "普通验收可降级到 gpt-5.5 + medium。")
        return ModelRoute("gpt-5.5", "medium", "关键 PR、对抗式审查、发布门禁升级到 gpt-5.5 + xhigh。")
    if role in {"技能维护", "文档/交付", "知识库"}:
        return ModelRoute("gpt-5.3-codex-spark", "high", "小型文档/registry 机械编辑可降级到 gpt-5.4-mini。")
    if role in CONTENT_ROLES:
        return ModelRoute("gpt-5.3-codex-spark", "high", "高风险公开定位、声明、合规或跨平台策略升级到 gpt-5.5 + xhigh。")
    return ModelRoute("gpt-5.3-codex-spark", "high", "涉及高风险决策或跨角色协调时回流总控/架构。")


def lines_or_default(values: list[str], default: str) -> str:
    if not values:
        return f"- {default}"
    return "\n".join(f"- {value}" for value in values)


def csv_or_default(values: list[str], default: str) -> str:
    return "、".join(values) if values else default


def route_check_value(value: bool) -> str:
    return "是" if value else "待确认"


def validate_source_route(role: str, args: argparse.Namespace) -> None:
    source_role = args.source_role or ""
    if source_role != "总控":
        return
    if role in OWNER_LAYER_ROLES:
        return
    if role in TECHNICAL_EXECUTION_ROLES:
        if not args.allow_ceo_direct_dispatch:
            raise ValueError("总控不能直接派发技术执行角色；请先派给 架构 / CTO，由架构拆给开发、UI/PPT、测试、QA、安全、DBA 或运维。")
        if not args.override_reason:
            raise ValueError("总控直派技术执行角色必须提供 --override-reason，说明用户为何明确要求绕过 架构 / CTO。")
    if role in CONTENT_EXECUTION_ROLES:
        if not args.allow_ceo_direct_dispatch:
            raise ValueError("总控不能直接派发内容执行角色；请先派给 内容主编，由内容主编拆给公众号发布、小红书或视频。")
        if not args.override_reason:
            raise ValueError("总控直派内容执行角色必须提供 --override-reason，说明用户为何明确要求绕过 内容主编。")


def default_forbidden(role: str) -> str:
    defaults = "未授权的生产环境、账号设置、凭据、发布动作、数据库写操作、无关重构"
    if role == "总控":
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


def role_execution_guidance(role: str) -> str:
    if role != "开发":
        return ""
    return """开发负责人 / Dev Lead 执行规则：
- 本窗口默认是开发负责人 / Dev Lead，使用 gpt-5.5 + xhigh，负责拆解、集成、纠偏、最终提交。
- 需要并行或长任务时，先拆成任务卡，再把单一、短、小、可验证的代码任务交给开发执行 subagent。
- 开发执行 subagent 是窗口内一次性 subagent，不是新的角色窗口；不写入 .codex/role-windows.md，不作为后续任务复用。
- 开发执行 subagent 默认模型：gpt-5.3-codex-spark + xhigh；只执行单一、短、小、可验证的代码任务；任务结束后关闭，不作为角色窗口复用。
- subagent 必须带文件白名单、禁止范围、验收命令和退出条件；不要让 subagent 承担架构判断、跨文件整合或最终提交。
"""


def ui_preview_route_guidance(role: str) -> str:
    if role != "UI/PPT":
        return ""
    return """预览图实现路线选择：
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


def effective_token_profile(role: str, args: argparse.Namespace) -> str:
    if args.profile != "auto":
        return args.profile
    if args.risk == "critical" or args.loop_depth == "L3":
        return "full"
    if role == "架构" or args.new_code_project or args.loop_depth == "L2":
        return "standard"
    return "compact"


def token_profile_strategy(profile: str) -> str:
    strategies = {
        "compact": "只保留闭环必需字段；省略深层技术方案、CodeGraph 和开源扫描占位，适合 L0/L1 小闭环。",
        "standard": "保留常规路由、验证、技能台账和必要技术/内容门禁，适合 L2 普通协作。",
        "full": "保留完整深层检查、CodeGraph、开源扫描和门禁字段，适合 L3、高风险、关键 PR 或新代码项目。",
    }
    return strategies[profile]


def build_compact_prompt(
    *,
    args: argparse.Namespace,
    role: str,
    route: ModelRoute,
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

{role_execution_guidance(role)}
{ui_preview_route_guidance(role)}
{content_research_guidance(role)}
{content_tone_gate(role)}
角色树位置（总控/架构/内容主编/执行角色）：
{ROLE_TREE_POSITION[role]}

{loop_depth_explanation(args.loop_depth, args.override_reason)}
负责人交互边界：
- 总控 / CEO 只直接对接负责人层或治理角色；技术执行默认由架构 / CTO 派发，内容执行默认由内容主编派发。
- 总控不编写代码、测试脚本、验收脚本或自动化验证脚本；需要产物时交给对应负责人拆下游。

目标：
{args.objective}

请先阅读/检查：
{lines_or_default(read_first, "agent-role-orchestrator/SKILL.md；项目 .codex/role-windows.md（若存在）；与目标直接相关的项目文件")}

允许修改：
{lines_or_default(allowed, "待确认；未确认前只读")}

禁止修改：
{lines_or_default(forbidden, default_forbidden(role))}

实现/工作要求：
{args.work_requirements or "只处理本轮目标；不搬运完整旧聊天、长日志或大段源码；不确定信息写待确认。"}

验证：
{lines_or_default(validation, "说明无法验证的原因；可验证项必须给出命令、文件、截图或人工检查步骤")}

闭环状态：
- 当前状态：{args.loop_state}
- 上一轮反馈：{args.previous_feedback or "无 / 待确认"}
- 本轮退出条件：{args.exit_condition or "完成目标、阻塞并说明证据、或需要来源窗口决策"}

上下文预算：
- 默认只传状态增量、证据句柄、决策需求和下一回流对象。
- compact 档不输出大段候选方案占位；需要深层设计、CodeGraph 或开源扫描时升级到 standard/full。
- 当上下文接近过长或 compact 失败时，用台账、提交、PR、文件证据和压缩交接卡接续。

闭环完成条件：
- 完成、阻塞或需要发起方决策时，必须同时完成两件事：1. 更新 .codex/role-windows.md 并提交；2. 向来源 thread 主动发送压缩回调。
- 仅完成第 1 项不算闭环；来源 thread 未收到回调时，负责人层仍应视为待回流。
- 如果当前窗口没有发送工具，最终输出必须以 <codex_delegation> 或“压缩回调”开头，供系统/用户转发。

路由前检查（总控、架构、内容主编和多角色派发必填）：
- 是否读取 agent-role-orchestrator：{route_check_value(args.read_orchestrator)}
- 是否读取 .codex/role-windows.md：{route_check_value(args.read_ledger)}
- 是否复用已有角色线程：{args.reuse_thread or "待确认"}
- 是否写清 source-window callback：是
- 是否写清允许/禁止范围：是
- 是否写清验证与提交要求：是
- 是否包含技能路由台账：是
- 是否需要更新 .codex/role-windows.md：{args.update_ledger or "待确认"}

技能路由台账（总控、架构、内容主编和多角色拆分必填；单一执行角色可写“不适用/继承来源台账”）：
- 候选 skill：{csv_or_default(candidate_skills, "待确认")}
- 必选 skill：{csv_or_default(required_skills, "无 / 待确认")}
- 可选 skill：{csv_or_default(optional_skills, "无 / 待确认")}
- 跳过 skill 及原因：{csv_or_default(skipped_skills, "无")}
- 预期加载角色：{role}

提交/PR 要求：
{args.commit_requirements or "遵循项目 AGENTS.md；未要求提交时先回报变更和验证证据。"}

回调/通知规则：
- 本任务发起方：{callback_target}。
- 完成、阻塞或需要发起方决策时，主动通知发起方窗口；不要只等待用户转述。
- 如无法直接发送到发起方窗口，请输出一段可复制的“给发起方的回调消息”，且最终输出必须以 <codex_delegation> 或“压缩回调”开头。

结构化反馈格式（返工/验收失败/需要决策时必填）：
- 问题/缺口：
- 证据/复现：
- 影响等级：
- 建议回流对象：
- 需要决策：
- 下一闭环状态：

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
- 具体问题或优化：
- 目标位置：skill / README / 角色提示词 / QA 清单 / 验证命令 / registry / source policy / 项目文档 / 待确认
- 已执行变更或建议后续：

完成后请回传：
{args.return_requirements or "压缩回调、验证证据、技能命中回传、规则沉淀状态。"}

角色底线：
{args.boundary or "守住角色边界；不越权发布、写生产、改凭据、编造证据或扩大范围。"}
"""


def build_prompt(args: argparse.Namespace) -> str:
    role = canonical_role(args.role)
    validate_source_route(role, args)
    route = model_route(role, args.risk)
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
    needs_technical = "必填" if role == "架构" else "不适用"
    needs_codegraph = "必填" if args.new_code_project or role == "架构" else "不适用"
    needs_scan = "必填" if role == "架构" else "不适用"
    profile = effective_token_profile(role, args)

    if profile == "compact":
        return build_compact_prompt(
            args=args,
            role=role,
            route=route,
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

{role_execution_guidance(role)}
{ui_preview_route_guidance(role)}
{content_research_guidance(role)}
{content_tone_gate(role)}
角色树位置（总控/架构/内容主编/执行角色）：
{ROLE_TREE_POSITION[role]}

{loop_depth_explanation(args.loop_depth, args.override_reason)}
负责人交互边界：
- 总控 / CEO 只直接对接负责人层或治理角色：架构 / CTO、内容主编、知识库、技能维护、文档/交付，或用户明确指定的例外。
- 技术执行角色（开发、UI/PPT、测试、QA、安全、DBA、运维）默认由架构 / CTO 派发、验收和回流；总控只接收架构汇总的项目结果、风险、决策点和最终验收建议。
- 内容执行角色（公众号发布、小红书、视频）默认由内容主编派发、验收和回流；总控只接收内容主编汇总的内容结果、发布风险、授权点和最终验收建议。
- 总控不编写或修改代码、测试脚本、验收脚本、自动化验证脚本；需要这类产物时，交给开发或测试实现，由架构/QA复核证据。

技术方案（架构/CTO 处理复杂技术需求必填；已选定则写明选型）：
- 状态：{needs_technical}
- 方案 A：待确认
- 方案 B：待确认
- 方案 C：待确认
- 推荐：待确认
- 待确认：待确认

目标：
{args.objective}

请先阅读/检查：
{lines_or_default(read_first, "agent-role-orchestrator/SKILL.md；项目 .codex/role-windows.md（若存在）；与目标直接相关的项目文件")}

允许修改：
{lines_or_default(allowed, "待确认；未确认前只读")}

禁止修改：
{lines_or_default(forbidden, default_forbidden(role))}

实现/工作要求：
{args.work_requirements or "按角色边界推进；不确定信息写待确认；不要编造线程、事实、验证结果或发布状态。"}

验证：
{lines_or_default(validation, "说明无法验证的原因；可验证项必须给出命令、文件、截图或人工检查步骤")}

闭环状态：
- 当前状态：{args.loop_state}
- 上一轮反馈：{args.previous_feedback or "无 / 待确认"}
- 本轮退出条件：{args.exit_condition or "完成目标、阻塞并说明证据、或需要来源窗口决策"}

上下文预算：
- 不搬运完整聊天记录、长日志或大段源码；默认只传状态增量、证据句柄、决策需求和下一回流对象。
- 每次派发、回调、阻塞、完成或纠偏后，更新 .codex/role-windows.md；长任务同时刷新“压缩交接卡”；项目允许写入且是 git 仓库时提交该台账更新。
- 当上下文接近过长、compact 失败、或任务跨越多个闭环时，先用台账、提交、PR、文件证据和压缩交接卡接续，不要求新窗口读取完整旧线程。

闭环完成条件：
- 完成、阻塞或需要发起方决策时，必须同时完成两件事：1. 更新 .codex/role-windows.md 并提交；2. 向来源 thread 主动发送压缩回调。
- 仅完成第 1 项不算闭环；来源 thread 未收到回调时，负责人层仍应视为待回流。
- 如果当前窗口没有发送工具，最终输出必须以 <codex_delegation> 或“压缩回调”开头，供系统/用户转发。
- 如果项目不是 git 仓库、项目禁止写入或无法提交，必须在压缩回调中说明原因和替代证据。

CodeGraph 状态（新本地代码项目必填；不适用时写明原因）：
- 可用性：{needs_codegraph}
- 初始化状态：待确认
- 索引路径/忽略策略：待确认
- 跳过或失败原因：待确认

路由前检查（总控、架构、内容主编和多角色派发必填）：
- 是否读取 agent-role-orchestrator：{route_check_value(args.read_orchestrator)}
- 是否读取 .codex/role-windows.md：{route_check_value(args.read_ledger)}
- 是否复用已有角色线程：{args.reuse_thread or "待确认"}
- 是否写清模型建议/覆盖：是
- 是否写清 source-window callback：是
- 是否写清允许/禁止范围：是
- 是否写清验证与提交要求：是
- 是否包含技能路由台账：是
- 是否需要更新 .codex/role-windows.md：{args.update_ledger or "待确认"}

技能路由台账（总控、架构、内容主编和多角色拆分必填；单一执行角色可写“不适用/继承来源台账”）：
- 候选 skill：{csv_or_default(candidate_skills, "待确认")}
- 必选 skill：{csv_or_default(required_skills, "无 / 待确认")}
- 可选 skill：{csv_or_default(optional_skills, "无 / 待确认")}
- 跳过 skill 及原因：{csv_or_default(skipped_skills, "无")}
- 预期加载角色：{role}

开源/可借鉴方案扫描（架构/CTO 技术窗口必填；非架构窗口仅在被明确指派时填写）：
- 状态：{needs_scan}
- 检索关键词：待确认
- 候选方案：待确认
- 可借鉴点：待确认
- 不采用/风险：待确认
- 对下游工作的约束：待确认

提交/PR 要求：
{args.commit_requirements or "遵循项目 AGENTS.md；未要求提交时先回报变更和验证证据。"}

回调/通知规则：
- 本任务发起方：{callback_target}。
- 完成、阻塞或需要发起方决策时，主动通知发起方窗口；不要只等待用户转述。
- 必须先更新 .codex/role-windows.md 并提交，再向来源 thread 主动发送压缩回调；仅完成台账更新不算闭环。
- 如无法直接发送到发起方窗口，请输出一段可复制的“给发起方的回调消息”，且最终输出必须以 <codex_delegation> 或“压缩回调”开头。

结构化反馈格式（返工/验收失败/需要决策时必填）：
- 问题/缺口：
- 证据/复现：
- 影响等级：
- 建议回流对象：
- 需要决策：
- 下一闭环状态：

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
- 具体问题或优化：
- 目标位置：skill / README / 角色提示词 / QA 清单 / 验证命令 / registry / source policy / 项目文档 / 待确认
- 已执行变更或建议后续：

完成后请回传：
{args.return_requirements or "压缩回调、验证证据、技能命中回传、规则沉淀状态。"}

角色底线：
{args.boundary or "守住角色边界；不越权发布、写生产、改凭据、编造证据或扩大范围。"}
"""


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render a copy-paste role prompt with mandatory loop, callback, skill-hit, and model-routing fields.",
    )
    parser.add_argument("--role", required=True, help="Canonical role or alias, e.g. 总控, 架构, 开发, QA, 内容主编.")
    parser.add_argument("--objective", required=True, help="Concrete task objective. Required to avoid blank prompts.")
    parser.add_argument("--project", help="Project path or scope.")
    parser.add_argument("--mode", default="新建", choices=["新建", "继承", "接续", "重置"])
    parser.add_argument("--loop-depth", default="L1", choices=["L0", "L1", "L2", "L3"], help="Collapsible routing depth. L0 direct user-to-executor; L1 owner layer; L2 owner-to-executor loop; L3 high-risk gated loop.")
    parser.add_argument("--profile", default="auto", choices=["auto", "compact", "standard", "full"], help="Token budget profile. auto chooses compact for L0/L1 owner/simple prompts, standard for L2/architecture/new-code prompts, and full for L3/critical prompts.")
    parser.add_argument("--risk", default="normal", choices=["normal", "critical"], help="Use critical for release gates, adversarial QA, compliance, or high-risk public claims.")
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
    parser.add_argument("--allow-ceo-direct-dispatch", action="store_true", help="Allow an explicit user override for 总控 -> execution-role direct dispatch.")
    parser.add_argument("--override-reason", help="Required when --allow-ceo-direct-dispatch bypasses 架构 / CTO or 内容主编.")
    parser.add_argument("--output", type=Path, help="Write prompt to file instead of stdout.")
    return parser.parse_args(argv)


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
