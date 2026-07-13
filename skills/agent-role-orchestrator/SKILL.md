---
name: agent-role-orchestrator
description: Create concise role-specific Codex prompts and handoffs with a CEO-first gateway, CTO technical loop, content editor branch, model routing, fail-closed callbacks, and role-window registry. Use for 总控/CEO, 架构/CTO, development, UI/PPT, content, ops, DBA, security, testing, QA, document delivery, knowledge-base, skill maintenance, inherited windows, role reuse, skill-hit statistics, or multi-window loop engineering.
---

# Agent Role Orchestrator

## Purpose

Turn a collaboration request into the smallest reliable role loop. Keep the main contract here; load only the reference file needed for the selected role or decision.

Default role tree:

```text
总控 / CEO
├─ 架构 / CTO
│  ├─ 开发
│  ├─ UI/PPT / UI/Frontend
│  ├─ 测试
│  ├─ QA
│  ├─ 安全
│  ├─ DBA
│  └─ 运维
├─ 内容主编
│  ├─ 公众号发布
│  ├─ 小红书
│  ├─ 视频
│  └─ UI/PPT 视觉资产协作
├─ 知识库
├─ 技能维护
└─ 文档/交付
```

Do not load every reference by default:

- role ownership: `references/role-cards.md`;
- current model tiers, executor tiers, and parallel policy: `references/model-routing.md`;
- script and skill routing: `references/tool-routing.md`;
- X MCP, public writing, Xiaohongshu, and content gates: `references/content-routing.md`.

## Fail-Closed Tool Layer Rule

Markdown owns principles and judgment. Scripts own enums, templates, ledgers, callback completeness, CodeGraph state, and metrics.

When `scripts/` is available:

- bootstrap/check project files with `ensure_project_role_files.py`;
- generate non-trivial prompts with `render_role_prompt.py` instead of hand-writing fixed fields;
- validate prompts, callbacks, and ledgers with `validate_role_loop.py`;
- inspect CodeGraph with `check_codegraph.py` instead of guessing;
- calculate hit rate with `aggregate_skill_hits.py` instead of chat memory.

If a required check fails, do not dispatch or close the loop. Fix it or record `待确认` with a reason. Scripts do not make architecture, product, or editorial judgment.

```bash
python skills/agent-role-orchestrator/scripts/ensure_project_role_files.py --project /path/to/project --write
python skills/agent-role-orchestrator/scripts/render_role_prompt.py --role 开发 --objective "修复筛选" --source-role 架构 --task-size small --profile auto
python skills/agent-role-orchestrator/scripts/validate_role_loop.py --project /path/to/project --prompt /path/to/prompt.md --callback /path/to/callback.md
python skills/agent-role-orchestrator/scripts/check_codegraph.py --project /path/to/project
python skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py /path/to/callbacks
```

## CEO-First Role Hierarchy Rule

One new requirement defaults to one `总控` / `CEO` window. `总控` owns outcome, scope, priority, budget, risk, and final go/no-go. It normally talks only to owner-layer roles: `架构` / `CTO`, `内容主编`, `知识库`, `技能维护`, and `文档/交付`.

Technical execution roles report to `架构` / `CTO`. Content execution roles report to `内容主编`. `总控` does not write implementation or acceptance scripts and does not directly manage execution details, except for the deliberate `tiny` or `small` routes below.

Reuse an existing role thread when its thread id is known. Unknown state is `待确认`; never invent a thread id.

## Loop Depth And Owner-Layer Routing Rule

Use the shallowest loop that can close safely:

| Depth | Route | Use |
| --- | --- | --- |
| `L0` | `用户 -> 执行角色` | Explicit, small, low-risk specialist task. |
| `L1` | `总控 -> 负责人层` | Route or owner judgment without downstream execution yet. |
| `L2` | `总控 -> 负责人 -> 执行 -> 负责人 -> 总控` | Normal multi-role work. |
| `L3` | L2 plus independent gates | Release, production, account, security, DB, critical PR, or high-risk public claims. |

负责人交互边界: `总控`只直接对接负责人层；负责人拆分、验收并压缩回流。Do not choose L2/L3 merely because multiple roles exist.

## CEO Task Dispatch Decision Rule

Before acting or dispatching, output `任务分发决策：` with size, path, and stop condition.

| Size | Default path | Boundary |
| --- | --- | --- |
| `tiny` | 总控自办 | Local, low-risk, verifiable. Stop on design, scripts, cross-file, production, account, or data risk. |
| `small` | 总控直派开发 | One short, narrow, low-risk code task; growth returns to CTO. |
| `medium` | 总控 -> 负责人层 | Owner judgment required. |
| `large` | 完整角色团队 | Owner splits execution and gates. |
| `critical` | L3 门禁团队 | Independent review required. |

Generate with `--task-size tiny|small|medium|large|critical`. Default unknown work to `medium`.

## Entry Guard And Registry Rule

For CEO, architecture, multi-role, dispatch, callback, or registry work:

1. Read this installed skill.
2. Read project `.codex/role-windows.md` when a project is known.
3. Run `ensure_project_role_files.py` when files may be missing; use `--write` only when writes are allowed.
4. Treat `.codex/role-windows.md` as the source of truth. Reuse known thread ids, record corrections, and never infer status from chat memory.

The ledger must track role, status, thread id, source window, responsibility, next step, and loop state. Update it after dispatch, callback, correction, blocking, and completion.

## Model Routing Rule

Load `references/model-routing.md` when selecting or overriding models. The stable defaults are:

- `总控`: `gpt-5.6-terra` + `high`;
- `架构`: `gpt-5.6-sol` + `high`;
- `开发负责人`, ordinary `QA`, `运维`, `DBA`, content owners, and durable support owners: `gpt-5.6-terra` + `high`;
- high-risk funds, ledger, concurrency, production, irreversible design, critical PR, or go/no-go: `gpt-5.6-sol` + `xhigh`;
- deterministic mechanical executor: `gpt-5.4-mini` + `high`;
- bounded one-shot executor: `gpt-5.6-luna` + `high`.

`gpt-5.3-codex-spark` is an optional `Spark Opportunity Lane`, not a durable fifth tier. During its research preview it may have a separate usage limit, but availability and rates may change. Use it only for a mechanical/bounded, text-only, short, independently verifiable one-shot development executor when current availability is explicitly confirmed; otherwise fall back to Mini/Luna. Spark never owns architecture, integration, final QA, high-risk work, or long context.

Never emit an unsupported `max` tier. User selection and actual model availability override these recommendations; record fallbacks explicitly.

For development, durable owner and executor are different:

- `开发负责人 / Dev Lead` owns decomposition, integration, correction, final validation, and commit.
- `开发执行 subagent` is an in-window one-shot worker. It handles one short, narrow, independently verifiable task, is not added to `.codex/role-windows.md`, and is not reused after completion.
- Default execution is serial. Two workers require disjoint scope and independent validation. Three to five workers require an explicit parallel profile and the same fail-closed evidence.
- High-risk implementation stays with Dev Lead on Sol/xhigh; do not send it to a low-cost executor.
- Spark tasks must include an explicit validation command because its lightweight default behavior may not run tests automatically.

## Token Budget Profile Rule

Generate with `--profile auto`; override only with evidence:

- `compact`: L0/L1, one execution task, or simple owner decision;
- `standard`: L2, architecture planning, or new-code setup;
- `full`: L3, critical gates, security/DB/ops risk, or complex irreversible work.

`compact` must contain the closure contract but omit unrelated CTO, CodeGraph, content, and platform placeholders. Do not paste full chat history, large logs, or large source blocks into role prompts.

## Technical And Quality Rules

### Architecture

For a complex requirement, `架构` first compares credible technical routes and checks whether a current open-source solution is reusable. For a new local code project, run `check_codegraph.py`; initialize when allowed or report the missing tool/status.

### Development

`开发负责人` and executors use first principles: restate invariants, inspect evidence, identify the smallest causal change, write or update tests where appropriate, and verify the integrated result. Repeated correction, unclear ownership, or scope growth returns to Dev Lead/CTO.

### QA

QA uses adversarial review: try to falsify readiness, inspect negative paths, boundary values, permissions, rollback, and regression risk. Ordinary QA uses Terra/high; critical release or production gates use Sol/xhigh. QA does not receive CTO-only planning placeholders.

### UI Preview Implementation Route Rule

When a preview image exists, `UI/PPT` must not `不要默认拿 CSS 硬干`. First compare CSS/components, image assets, Canvas/SVG, Three.js/WebGL, Lottie/video, proven libraries, or generated/manual assets. Record the selected route and visual verification evidence before development.

## Content Routing Gates

Load `references/content-routing.md` only for public writing, platform research, or publishing work.

- `X MCP Content Research Source`: use [official X MCP docs](https://docs.x.com/tools/mcp) for authorized read-only trend, topic, benchmark-account, and public-discussion research. Writes need separate authorization.
- `Content Tone Gate`: 正式对外内容先过 `反老登味 / 反 AI 味内容闸门`, then use `$humanizer-zh` without changing facts.
- `Xiaohongshu Automation Publisher Gate`: use `$xhs-automation-publisher`; preview/fill first, and require explicit confirmation for publish or interaction actions.

## Source-Window Callback Rule

The source window is the role/thread that assigned this task, not always `架构` or `总控`. If B delegates to C, B is C's source while B still reports its own state to A.

Completion is fail-closed. On completed, blocked, or decision-needed state, do both:

1. update `.codex/role-windows.md` and commit when project policy permits;
2. actively send a compressed callback to the source thread.

`仅完成第 1 项不算闭环`. If no sending tool exists, final output starts with `<codex_delegation>` or `压缩回调` for forwarding.

Required callback shape:

```text
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
```

## Context Budget And Compact Handoff Rule

上下文预算 defaults to deltas and evidence handles. Before a long window approaches compaction, refresh the ledger and a compact handoff card containing objective, constraints, current state, decisions, artifacts/commits, validation, blockers, and next action. A new or resumed window reads artifacts instead of reconstructing the whole transcript.

## Skill Routing Measurement Rule

Owner layers declare candidate, required, optional, and skipped skills. Execution callbacks report actual use, omissions, misfires, and discovered should-use skills. Use `aggregate_skill_hits.py` for hit rate; do not count from memory.

Route a reusable cross-role improvement to `技能维护`. Project state stays in the project ledger; reusable trigger, prompt, validation, or routing behavior belongs in the shared skill repository and should be proposed through a PR.

## Role Card Reference

Read `references/role-cards.md`, then only the thematic reference required by the task. Important defaults:

- 总控: outcome and routing, not technical implementation;
- Act as `架构` / `CTO`: technical owner and execution-team manager;
- 开发: durable Dev Lead plus optional one-shot executors;
- 内容主编: editorial owner and platform-role manager;
- QA: independent adversarial gate;
- 技能维护: reusable rules, registry, docs, prompt scripts, and hit-rate governance.

## Workflow

1. Classify the request and source window.
2. Read ledger; bootstrap files if allowed.
3. Choose task size and smallest loop depth.
4. Choose owner/executor role, model route, and Token Budget Profile.
5. Load only the relevant reference file and required downstream skills.
6. Generate with `render_role_prompt.py`; use explicit `--executor-tier` and parallel arguments when applicable.
7. Validate before dispatch.
8. On terminal state, update ledger, send callback, aggregate skill hits when useful, and route reusable improvements.

Generated prompts must include:

```text
模型建议：
- model：...
- thinking：...

任务分发决策：
技能命中回传：
```

## Concise Invocation Examples

```bash
# Durable Dev Lead, serial by default
python scripts/render_role_prompt.py --role 开发 --objective "实现订单修复" --source-role 架构 --profile auto

# Bounded one-shot Luna executor
python scripts/render_role_prompt.py --role 开发 --objective "实现独立适配器" --source-role 架构 --executor-tier bounded --profile compact

# Same bounded task using confirmed Spark preview quota
python scripts/render_role_prompt.py --role 开发 --objective "实现独立适配器" --source-role 架构 --executor-tier bounded --prefer-spark --spark-available --validation "pytest tests/test_adapter.py"

# Explicit three-worker parallel execution
python scripts/render_role_prompt.py --role 开发 --objective "实现三个独立适配器" --source-role 架构 --execution-profile parallel --worker-count 3 --disjoint-scope "每人一个目录" --independent-validation "每个目录独立测试"
```

## Quality Bar

- smallest safe loop, narrowest role, smallest model, and shortest prompt that preserve reliability;
- no invented thread ids, validation, publication state, or model tier;
- no direct CEO drift into implementation;
- no worker fanout without disjoint scope and independent validation;
- no terminal state without ledger update plus source-thread callback;
- no reusable optimization left only in chat.
