---
name: agent-role-orchestrator
description: Create concise role-specific Codex window prompts and current-window handoffs with a CEO-first gateway, CTO technical loop, content editor branch, model routing defaults, and role-window registry. Use when the user asks for 总控/CEO, 架构/CTO, development, UI-PPT/UI-Frontend, content editor, video, ops, DBA, security, testing, QA, document-delivery, WeChat Official Account publishing, Xiaohongshu, personal knowledge-base, skill-maintenance, inherited/continued role windows, next-window prompts, role reuse, testing reports, content publishing roles, skill hit-rate/statistics/curation, or security-audit prompts that delegate to the appropriate security skill.
---

# Agent Role Orchestrator

## Purpose

Turn fuzzy collaboration intent into a real role-window handoff or copy-paste prompt, with a clear role, context, boundaries, validation plan, and reporting contract.

Use this skill to:
- bootstrap a new role window, usually `总控` / `CEO` first;
- summarize the current thread so a next window can inherit a role;
- let `总控` decide whether to route work to `架构` / `CTO`, `内容主编`, `知识库`, `技能维护`, or a direct specialist role;
- let `架构` / `CTO` manage the technical role tree: `开发`, `UI/PPT` / `UI/Frontend`, `测试`, `QA`, `安全`, `DBA`, and `运维`;
- let `内容主编` manage the content role tree: `公众号发布`, `小红书`, `视频`, and `UI/PPT` visual-asset collaboration;
- remember whether each role has already been established and reuse it by default;
- rewrite a project-specific role prompt into a reusable role template.
- route `安全` work to the right existing security skill by default.
- route `测试` test-case/report work to the test artifact skill by default.
- route independent stress, load, performance, and concurrency validation to the `测试` role by default.
- require `开发` windows to use first-principles engineering during implementation, investigation, and corrections.
- require `QA` windows to use adversarial review to falsify readiness, not only confirm happy paths.
- require role windows to actively report terminal task state back to the task's source window.
- measure skill routing with a lightweight candidate/required/actual/effective hit ledger.
- keep loop callbacks token-efficient by passing deltas, evidence links, and decisions instead of full transcripts.
- require CEO, architecture, multi-role, dispatch, callback, and registry work to read this skill plus the project role-window ledger before creating or continuing role windows.
- apply model/thinking routing defaults when creating or continuing role windows.
- use the fail-closed tool layer for mechanical fields, prompt templates, ledger checks, callback checks, and skill-hit metrics when scripts are available.
- route cross-role skill curation, registry updates, README/docs structure, and hit-rate retrospectives to `技能维护` by default.
- bootstrap CodeGraph for new local code projects when available.

## Fail-Closed Tool Layer Rule

Markdown owns principles, role boundaries, and judgment. Scripts own mechanical fields, enums, templates, ledgers, callback completeness, and metrics.

When this skill's `scripts/` directory is available:
- use `scripts/ensure_project_role_files.py --project <path>` to inspect whether `AGENTS.md` and `.codex/role-windows.md` need bootstrapping; add `--write` only when project file writes are allowed;
- use `scripts/render_role_prompt.py` to generate non-trivial role prompts instead of hand-typing required sections from memory;
- use `scripts/validate_role_loop.py` before dispatching or accepting non-trivial prompts, callbacks, or `.codex/role-windows.md` updates;
- use `scripts/check_codegraph.py --project <path>` to produce the CodeGraph status block instead of guessing whether CodeGraph is initialized;
- use `scripts/aggregate_skill_hits.py <callbacks-or-ledgers>` to calculate skill hit-rate, missing required skills, misfires, and discovered should-use skills from artifacts;
- if validation fails, do not create/continue/dispatch/close the role loop until the missing field is fixed or explicitly marked `待确认` with a reason;
- do not let the script decide the architecture/content/business judgment. Fill the judgment fields after the script creates the structure.

Useful commands:

```bash
python skills/agent-role-orchestrator/scripts/ensure_project_role_files.py \
  --project /path/to/project
```

```bash
python skills/agent-role-orchestrator/scripts/render_role_prompt.py \
  --role 开发 \
  --objective "实现订单列表筛选修复" \
  --source-role 架构 \
  --source-thread thread-123 \
  --task-size small \
  --profile auto \
  --required-skill gstack-investigate \
  --validation "npm test"
```

```bash
python skills/agent-role-orchestrator/scripts/validate_role_loop.py \
  --project /path/to/project \
  --prompt /path/to/prompt.md \
  --callback /path/to/callback.md
```

```bash
python skills/agent-role-orchestrator/scripts/check_codegraph.py \
  --project /path/to/project
```

```bash
python skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py \
  /path/to/callbacks-or-ledgers
```

## CEO-First Role Hierarchy Rule

For one new requirement, default to one `总控` / `CEO` window first. Do not directly split the requirement into several role windows just because the user names possible roles.

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
└─ 技能维护
```

Only output multiple downstream role prompts when one of these is true:
- the user says `总控已经决定`, `架构已经决定`, `内容主编已经决定`, `按这个拆`, or provides an accepted role split;
- the current thread is already acting as `总控` and has enough evidence to choose downstream roles;
- the current thread is already acting as `架构` / `CTO` and the split stays inside the technical role tree;
- the current thread is already acting as `内容主编` and the split stays inside the content role tree;
- the user explicitly overrides the gateway and asks to bypass `总控`.

When the user asks for `开发`, `UI/PPT`, `视频`, `公众号发布`, `小红书`, `运维`, `DBA`, `安全`, `测试`, `QA`, `文档/交付`, `知识库`, or `技能维护` prompts without a source-window decision, either produce a `总控` prompt first or clearly mark the downstream prompt as `待总控确认`. If the user explicitly asks for `架构` / `CTO`, produce the technical architecture prompt directly and mark the source as the user.

## Loop Depth And Owner-Layer Routing Rule

The role tree is a collapsible organization structure, not a mandatory long chain for every task. `总控` must choose the smallest loop depth that can safely close the task:

| Depth | Route | Use When |
| --- | --- | --- |
| `L0` | `用户 -> 执行角色` | The user explicitly asks for a specific execution role and the task is small, low-risk, and does not need CEO/owner coordination. |
| `L1` | `总控 -> 负责人层` | The task needs route judgment, outcome framing, or owner-level risk review, but not direct multi-role execution yet. |
| `L2` | `总控 -> 架构/内容主编 -> 执行角色 -> 架构/内容主编 -> 总控` | Normal multi-role technical or content work. |
| `L3` | `总控 -> 架构/内容主编 -> 执行角色 + independent gates -> 架构/内容主编 -> 总控` | Critical PRs, releases, production, accounts, security, database risk, public claims, or adversarial acceptance. |

Rules:
- `总控` / `CEO` interacts directly with owner-layer roles: `架构` / `CTO`, `内容主编`, `知识库`, `技能维护`, and when useful `文档/交付`.
- Technical execution roles (`开发`, `UI/PPT`, `测试`, `QA`, `安全`, `DBA`, `运维`) are dispatched and accepted by `架构` / `CTO` by default.
- Content execution roles (`公众号发布`, `小红书`, `视频`) are dispatched and accepted by `内容主编` by default.
- `总控` tracks project-level outcome, risks, tradeoffs, decisions, priority, model budget, and final acceptance; it does not chase implementation details with execution roles.
- Direct `总控 -> 开发` dispatch is allowed for `small` development tasks only: a single, short, small, low-risk, verifiable change. If architecture judgment, cross-file integration, UI direction, tests/acceptance scripts, production/account/data/security risk, or repeated correction appears, route back to `架构` / `CTO`.
- Direct `总控 -> 其他执行角色` dispatch is allowed only when the user explicitly requests the bypass. Mark it as an override, record the reason, and keep the source as `用户明确 override`, not the normal CEO path.

## CEO Task Dispatch Decision Rule

Before acting or creating downstream prompts, `总控` must output a `任务分发决策` with task size, recommended path, and boundary. This makes "CEO self-handles" a deliberate choice instead of drift into implementation.

| Size | Default Path | Boundary |
| --- | --- | --- |
| `tiny` | `总控自办` | Only low-risk, local, verifiable changes. Stop and route to owner layer if design, cross-file work, test/acceptance scripts, production/account/data risk, or uncertainty appears. |
| `small` | `总控直派开发` | Only one short, small, verifiable low-risk development task. Callback goes to `总控`; escalation goes to `架构` / `CTO`. |
| `medium` | `总控 -> 负责人层` | Owner-level judgment is needed, but a full team may not be needed yet. |
| `large` | `完整角色团队` | `总控 -> 架构/内容主编 -> 执行角色 -> 负责人层 -> 总控`, with validation and callbacks. |
| `critical` | `L3 高风险门禁团队` | Releases, production, accounts, security, DBA, critical PRs, public high-risk claims, or anything needing independent gates. |

Generated prompts should use `scripts/render_role_prompt.py --task-size tiny|small|medium|large|critical`. Default to `medium` when unknown. A `tiny` self-handled task may include a small code or docs edit, but it must not grow silently; if the work expands, record the expansion and re-route.

## CEO And Architecture Entry Guard Rule

For CEO, architecture, multi-role, dispatch, callback, or role-window registry tasks, the active window must use this skill before creating, continuing, dispatching, or retiring any role window. Do not rely on chat memory alone.

Required preflight:
- read the installed `agent-role-orchestrator/SKILL.md`, usually under `${CODEX_HOME:-$HOME/.codex}/skills/agent-role-orchestrator/SKILL.md` or Windows `%USERPROFILE%\.codex\skills\agent-role-orchestrator\SKILL.md`;
- read the project `.codex/role-windows.md` when a project path is known and the file exists;
- if `.codex/role-windows.md` does not exist, say it is absent and either create it when project writes are allowed or keep an inline `待确认` registry;
- if the project ledger cannot be read, do not create, continue, or dispatch role windows until the missing state is confirmed or marked as `待确认` with a clear reason.

When project file writes are allowed, prefer `scripts/ensure_project_role_files.py --project <path> --write` to create or refresh the managed `AGENTS.md` entry-rule block and initial `.codex/role-windows.md` table. Without `--write`, the script is dry-run only.

When maintaining a project-level `AGENTS.md` or `.codex/role-windows.md`, add this reusable entry rule near the top unless the project explicitly forbids it:

```text
总控/架构/多角色/派发/回调/台账类任务必须先使用 agent-role-orchestrator。
执行前必须读取：
- 已安装的 agent-role-orchestrator/SKILL.md（通常位于 `${CODEX_HOME:-$HOME/.codex}/skills/agent-role-orchestrator/SKILL.md` 或 Windows `%USERPROFILE%\.codex\skills\agent-role-orchestrator\SKILL.md`）
- .codex/role-windows.md

若未读取，不允许创建、继续或派发角色窗口；状态未知一律写“待确认”。
```

## Model Routing Rule

When thread tools are available, `总控` and `架构` should set model and thinking explicitly when creating or continuing role windows. Existing windows should be reused first; sending a follow-up with a new model/thinking only affects future replies in that window.

Default model routes:
- `总控` / `CEO`: `gpt-5.5` + `xhigh`.
- `架构` / `CTO`: `gpt-5.5` + `xhigh`.
- `开发负责人` / `Dev Lead` (`开发` window): `gpt-5.5` + `xhigh`; it owns task breakdown, integration, correction, and final commit.
- `开发执行 subagent`: `gpt-5.3-codex-spark` + `xhigh`; it is an in-window one-shot subagent, not a persistent role window, and only executes a single, short, small, verifiable coding task from a written task card.
- `QA`: ordinary acceptance checks use `gpt-5.5` + `medium`; critical PR, adversarial review, release gate, or final risk review uses `gpt-5.5` + `xhigh`.
- `技能维护` and `文档/交付`: `gpt-5.3-codex-spark` + `high`, or `gpt-5.4-mini` for small docs/registry edits.
- `内容主编`, `公众号发布`, `小红书`, and `视频`: default to `gpt-5.3-codex-spark` + `high`; escalate to `gpt-5.5` + `xhigh` only for high-risk positioning, public claims, compliance, or cross-platform strategy.

For long or compact-prone development tasks, do not make `gpt-5.3-codex-spark` the long-running owner. Keep ownership in the `开发负责人` / `Dev Lead` window and delegate only bounded execution slices to Spark subagents. These are in-window one-shot subagents, not reusable role windows: do not write them into `.codex/role-windows.md`, do not assign them persistent thread ids, and close them after the task ends. The Dev Lead must write the task card first: goal, allowed files, forbidden scope, validation command, expected output, and callback target. Spark subagents must not own architecture decisions, cross-file integration, correction strategy, final verification, or commits unless the Dev Lead explicitly narrows that responsibility.

If thread tools are unavailable or the output is copy-paste only, include this block in the prompt:

```text
模型建议：
- model：
- thinking：
- 升级/降级条件：
```

## Complex Requirement Technical Options Rule

For a non-trivial technical requirement, `架构` / `CTO` must produce a technical options brief before opening implementation windows. `总控` decides whether a new requirement belongs to this technical path. Non-trivial includes multi-screen or multi-scene products, uncertain asset pipelines, visual-fidelity targets, multi-role work, integration choices, deployment choices, or any request where the wrong route could waste significant time.

The brief should present as many credible routes as useful, normally 3 to 5 when plausible instead of only 1 or 2. For each route, record:
- what the route is;
- fit to the user's goal;
- tradeoffs, cost, speed, quality ceiling, and rollback path;
- required assets, tools, permissions, and external dependencies;
- main risks and validation plan.

Then name a recommended route, or mark the decision as `待用户/总控/架构确认`. Do not dispatch implementation work until a route is accepted or `架构` explicitly selects one with rationale. If one route is clearly dominant, still name the rejected alternatives briefly and explain why they are not selected.

For frontend or visual product work, the options brief must cover the UX/UI route, asset-production route, implementation route, and QA/visual-acceptance route.

## Frontend/UI Role Routing Rule

Do not use `开发` as a catch-all just because the workspace contains code. Route by the dominant risk.

When a request is a pure frontend project, UI-heavy page, visual-fidelity pass, interaction/motion design, design-system decision, generated-asset composition, 2D/2.5D/3D scene layout, or "make it match the preview" task, prefer `UI/PPT` as the primary downstream role. In these cases `UI/PPT` may be addressed as `UI/Frontend`.

Use `开发` for implementation plumbing, data models, build/test scripts, asset gates, browser-state bugs, and code execution under an accepted visual/technical spec. When both visual direction and code are needed, split them: `UI/Frontend` owns the visual route, target composition, screenshot acceptance, and responsive behavior; `开发` implements the scoped code changes from that spec; `QA` or `架构` verifies. For content visuals, `UI/PPT` can also be coordinated by `内容主编`.

### UI Preview Implementation Route Rule

When `UI/PPT` / `UI/Frontend` receives a preview image, reference screenshot, mockup, or visual-fidelity target, it must not default to CSS-only reconstruction. Before assigning implementation or editing code, it should give a short `预览图实现路线选择`, normally 2 to 4 plausible routes.

Consider at least these routes when relevant:
- CSS/组件复刻；
- 图片切片/生成资产；
- Canvas/SVG；
- Three.js/WebGL；
- Lottie/视频；
- 现成库/组件；
- 手工或生成式视觉资产。

Choose based on interaction needs, responsive behavior, maintainability, performance, accessibility, animation complexity, fidelity ceiling, and future content replacement cost. If the preview depends on complex illustration, texture, 3D, particles, or animation that AI/code cannot reliably recreate with CSS, prefer an asset-based or rendering-specialist path instead of fragile CSS stacking. In short: 不要默认拿 CSS 硬干.

The UI role should output the recommended route, rejected routes, required assets/tools, and acceptance method. Implementation should start only after the route is selected by `UI/PPT`, `架构`, or the user. Validation should include screenshot comparison, layout/pixel checks, or visual QA evidence when feasible.

## Development First-Principles Rule

`开发` usually acts as `开发负责人` / `Dev Lead`, not merely a long-running Spark executor. It must use first-principles engineering throughout development, not only when correcting defects. Before implementing, investigating, correcting, or returning to rework, reduce the task to:
- user goal and acceptance signal;
- observed facts from files, tests, logs, UI, or docs;
- constraints, invariants, ownership boundaries, and forbidden scope;
- smallest falsifiable hypothesis for the change;
- minimal change that should satisfy the hypothesis;
- validation evidence that can disprove or confirm the result.

When subagents are available and the work is long, compact-prone, or parallelizable, the Dev Lead should split execution into narrow task cards and send only those cards to `开发执行 subagent` workers. Each subagent task must be single-purpose, short, small, and verifiable, with disjoint write scope when multiple subagents run in parallel. Treat every execution subagent as an in-window one-shot worker: it is not a new role window, it is not recorded as a reusable `.codex/role-windows.md` role, and it is closed after the task returns. The Dev Lead remains responsible for reviewing diffs, integrating results, rerunning final validation, correcting failed assumptions, committing, and reporting back to `架构` / `CTO`.

When a correction is requested, do not stack patches on top of a failed assumption. Name the failed assumption or violated invariant first, then make the smallest verifiable fix.

## QA Adversarial Review Rule

`QA` must use adversarial review by default. Its job is to try to falsify readiness, not merely confirm that the happy path works.

Adversarial review should challenge:
- hidden assumptions and overclaimed status;
- counterexamples, edge cases, and regression surfaces;
- permission, data-boundary, concurrency, rollback, and failure-mode risks;
- missing tests, weak evidence, and checks that could pass while the user goal still fails;
- mismatch between acceptance criteria, implementation behavior, and user-visible outcome.

QA findings should still be evidence-based and ordered by severity. If no blocker is found, QA should say what it tried to falsify and what residual risk remains.

## Open-Source Reference Scan Rule

After `架构` / `CTO` has confirmed a technical requirement enough to describe the problem, it should perform a bounded online scan for open-source or public reference solutions before locking the design or splitting downstream role work, when network access is available and the work is not explicitly offline, private, or confidential.

Keep the scan small and decision-oriented:
- search for existing GitHub repos, libraries, product docs, demos, architecture notes, issue threads, and prior-art implementations that resemble the requirement;
- inspect about 3 to 5 plausible candidates or use a short time box, then stop and synthesize;
- record fit, gaps, license/attribution concerns, maintenance activity, security/privacy risks, and what should or should not be borrowed;
- do not blindly copy code, prompts, UI, wording, or architecture; convert useful findings into constraints, options, and validation checks;
- if no useful reference is found, say so and proceed from first principles;
- if the scan is skipped because the user forbids web access, the network is unavailable, or the context is sensitive/offline, state the reason explicitly.

Include the result in the technical architecture summary or downstream prompt:

```text
【开源/可借鉴方案扫描】
- 检索关键词：
- 候选方案：
- 可借鉴点：
- 不采用/风险：
- 对下游工作的约束：
```

## New Project CodeGraph Bootstrap Rule

For a new local code project or a newly opened repository, default to bootstrapping CodeGraph before deeper architecture, impact analysis, or downstream development prompts, when a project path is known and file writes are allowed.

Required behavior:
- when scripts are available, start with `scripts/check_codegraph.py --project <path>` and copy its status block into the architecture summary or prompt;
- if the script reports `未初始化` and writes are allowed, rerun with `--init` or run the project-level initialization from the repo root, such as `codegraph init -i`, then re-check with `check_codegraph.py`;
- if MCP CodeGraph tools are available, their `codegraph_status` may be used as additional evidence, but do not replace the project-local status block;
- if CodeGraph is not installed or the tool is unavailable, either prompt the user with the install action or perform a silent user-level install only when the environment provides a known non-destructive installer and policy allows it;
- do not claim CodeGraph is ready until a fresh script or MCP status check confirms it;
- if initialization writes a local index such as `.codegraph/`, keep it local and ignore it unless the project explicitly tracks that directory;
- skip and state the reason when the task is read-only, the project path is unknown, the repo is not code-oriented, the user forbids writes/install, or initialization repeatedly fails.

After bootstrapping, include the status in the architecture summary:

```text
【CodeGraph 状态】
- 项目：
- 工具可用性：
- 初始化状态：
- 索引路径/忽略策略：
- 建议动作：
- 跳过或失败原因：
```

## Role-Window Registry Rule

Treat role windows as persistent per project/workstream.

Default lifecycle:
- first time a role is needed: establish the real role window when thread tools are available; otherwise create the role prompt and mark it as pending establishment;
- after a role is established: continue or send to that same-role window by default;
- when the same role needs fresh context, output an inheritance/continuation prompt for the existing role;
- create numbered parallel roles only when the user, `总控`, `架构`, or `内容主编` explicitly asks for them, such as `开发1号`, `开发2号`, `UI/PPT1号`;
- if existing-role state is unknown, ask for or reconstruct the role registry before generating same-role prompts.

Maintain this registry in `总控` / `架构` handoffs when possible:

```text
【角色窗口台账】
| 角色 | 状态 | thread id | 来源窗口 | 当前职责 | 下一步 | 循环状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 总控 | 待确认 | 待确认 | 用户 | 入口分流、模型预算、最终验收 | 待确认 | 待总控分流 |
| 架构 | 待确认 | 待确认 | 总控 | CTO 技术拆解和技术角色闭环 | 待确认 | 待架构拆解 |
| 内容主编 | 待确认 | 待确认 | 总控 | 内容域分流和平台角色闭环 | 待确认 | 待内容主编拆解 |
```

Use `新建` only for first establishment or explicit parallel instances. Use `继承` / `接续` for resets, context refreshes, and ongoing work in an existing role.

### Project Registry File

For project-scoped work with a known local project path, persist the role-window registry in the project whenever file writes are allowed. Use `.codex/role-windows.md` at the project root by default and treat it as the source of truth for role routing.

Before creating or continuing a role window:
- read `.codex/role-windows.md` first if a project path is known;
- merge it with current conversation evidence and thread/tool evidence;
- prefer existing established role windows over creating duplicates; if a role has a thread id, reuse/continue that thread instead of creating a new one;
- when thread tools are available and project registry writes are allowed, default to establishing or continuing the real role window instead of only outputting a prompt;
- if the canonical role already has an established thread id, continue or send to that thread;
- if the canonical role is not established, create/open the role window with the canonical title and record the thread id;
- create numbered parallel windows only when the user, `总控`, `架构`, or `内容主编` explicitly chooses parallel work;
- output a copy-paste prompt instead only when the user asks for prompt-only output, thread tools are unavailable, or `总控`, `架构`, or `内容主编` decides the real window should not be established yet;
- mark uncertain items as `待确认` instead of inventing thread ids or status.

After every dispatch, callback, continuation, completion, block, retirement, or correction, update `.codex/role-windows.md` with:
- role name and lifecycle status: `未建立`, `已建立`, `接续中`, `已关闭`, `误开/废弃`, or `待确认`;
- known thread id or `待确认`;
- source window;
- current responsibility and forbidden responsibility;
- last known handoff/QA/development result;
- next recommended action;
- loop state and latest callback target.

Recommended `.codex/role-windows.md` format is the fixed Markdown table above plus:

```text
## 压缩交接卡
- 最近摘要：
- 关键决策：
- 当前证据：
- 下一步：
- 新窗口接续提示：
```

If a role was opened incorrectly, do not erase it silently. Record `误开/废弃/纠偏`, why it was wrong, and which canonical role/thread supersedes it.

Do not write the registry file when the user explicitly forbids file edits, when no project path is known, or when producing a reusable role template. In those cases, include the registry inline in the response and say it was not persisted.

## Source-Window Callback Rule

Role-window communication is source-directed, not `总控`- or architecture-directed by default.

When window `A` assigns, delegates, or hands off a task to window `B`:
- name `A` as the task source and callback target in `B`'s prompt, including role name and thread id when known;
- require `B` to actively notify `A` when the task is complete, blocked, or needs a decision from `A`;
- use thread tools to send that callback when available; if direct thread messaging is unavailable, require `B` to output a copy-paste-ready callback message addressed to `A`;
- do not tell every downstream role to report to `总控` or `架构` unless that role is actually the source window, the designated coordinator, or the user explicitly says so;
- if `B` delegates a subtask to `C`, `B` becomes the source for `C` while still remaining responsible for reporting its own task state back to `A`.

Completion is fail-closed. When a role window is complete, blocked, or needs a source-window decision, it must do both:
1. update `.codex/role-windows.md` and commit the ledger update when project writes are allowed and the project is a git repo;
2. actively send a `压缩回调` to the source thread.

Only doing item 1 is not a closed loop. If the current window has no sending tool, the final output must start with `<codex_delegation>` or `压缩回调` so the system or user can forward it. If the project is not a git repo, writes are forbidden, or committing is impossible, say that in the callback with the replacement evidence.

This callback rule is separate from user-facing final reports. A downstream window may summarize for the user, but it must still close the loop with its task source.

## Context Budget And Compact Handoff Rule

Long-running role windows must avoid depending on the full chat transcript. The durable state source is the project ledger, commits/PRs, evidence files, and compact callbacks.

Required behavior:
- after every dispatch, callback, block, completion, or correction, update `.codex/role-windows.md` when project writes are allowed;
- after every completion, block, or source-decision request, update `.codex/role-windows.md`, commit it when possible, and send the source thread a `压缩回调`; do not count the loop closed until both ledger and callback are done;
- for long-running work, keep `.codex/role-windows.md`'s `压缩交接卡` current with latest summary, decisions, evidence handles, next action, and the prompt needed for a new window to continue;
- do not paste full transcripts, long logs, or large code blocks into callbacks. Use file paths, commit hashes, PR links, commands, screenshots, or short evidence excerpts;
- if remote compact fails with a context-window error, stop relying on the old conversation. Start or continue from `.codex/role-windows.md`, the latest compact callback, PR/commit state, and source files;
- if one workstream spans multiple PRs, several role loops, or repeated back-and-forth, create or continue the canonical role window with a fresh generated prompt instead of carrying all history in one window.

Add this section to role prompts:

```text
上下文预算：
- 不搬运完整聊天记录、长日志或大段源码；默认只传状态增量、证据句柄、决策需求和下一回流对象。
- 每次派发、回调、阻塞、完成或纠偏后，更新 .codex/role-windows.md；长任务同时刷新“压缩交接卡”；完成/阻塞/需决策时还必须提交台账并向来源 thread 主动发送压缩回调。
- 当上下文接近过长、compact 失败、或任务跨越多个闭环时，先用台账、提交、PR、文件证据和压缩交接卡接续，不要求新窗口读取完整旧线程。
```

## Skill Routing Measurement Rule

When `总控`, `架构`, or `内容主编` creates or updates a non-trivial role prompt, include a lightweight skill routing ledger. `总控` owns the aggregate route, model budget, and final hit-rate view; `架构` owns the technical subtree ledger; `内容主编` owns the content subtree ledger. Downstream roles own reporting what they actually loaded and whether it affected the work.

Use four hit levels:
- `候选命中`: the task may need this skill.
- `必选命中`: the source/coordinator marks this skill as required for the role.
- `实际命中`: the downstream role actually loaded and used the skill.
- `有效命中`: the skill changed scope, output, validation, safety, or decision quality.

Minimum metrics:
- `技能路由命中率 = 实际命中的必选 skill 数 / 来源窗口标记的必选 skill 数`.
- `误召率 = 加载但最终无效的 skill 数 / 总加载 skill 数`.
- `漏召数 = 任务结束后发现本该使用但没有使用的 skill 数`.

When callback files, PR notes, or ledger snapshots exist, run `scripts/aggregate_skill_hits.py <path>` instead of calculating from memory. Use the script output as the source of truth for hit rate, missing required skills, misfires, and discovered should-use skills.

Add this ledger to `总控`, `架构`, `内容主编`, and multi-role split prompts:

```text
技能路由台账：
- 候选 skill：
- 必选 skill：
- 可选 skill：
- 跳过 skill 及原因：
- 预期加载角色：
```

Require downstream roles to callback with:

```text
技能命中回传：
- 已加载并使用：
- 来源窗口要求但未使用：
- 临时发现应补用：
- 误召/无效加载：
- 影响产出的 skill：
```

If the ledger reveals recurring misses, noisy triggers, stale descriptions, overlapping skills, or registry drift, route maintenance to `技能维护` unless the current role has explicit authorization to make a narrow self-edit.

## Loop Token Compression Rule

Loop engineering must save tokens instead of multiplying them. Each callback should pass only state deltas and evidence handles, not the full transcript or all intermediate reasoning.

If there is no direct send tool, the final answer that carries a callback must start with `<codex_delegation>` or `压缩回调`. Extra prose before the callback makes forwarding unreliable and should fail review.

Default callback shape:

```text
压缩回调：
- 当前状态：
- 本轮变化：
- 证据链接/文件/命令：
- 需要决策：
- 下一回流对象：
- 可复用优化沉淀：无 / 建议 / 已沉淀
```

Use full context only when the receiver cannot act without it. Prefer paths, commit hashes, screenshots, command summaries, PR links, and short acceptance notes over pasted logs. `总控`, `架构`, and `内容主编` should consume downstream/source summaries instead of rereading every transcript. `技能维护` should consume skill-hit summaries instead of raw task histories.

## Token Budget Profile Rule

Every non-trivial generated role prompt must choose the smallest safe Token Budget Profile. Use `scripts/render_role_prompt.py --profile auto` by default so the tool, not the model's memory, applies the routing table.

- `compact`: for L0/L1 small loops, owner-layer triage, mechanical follow-up, or focused execution. Keep only role identity, model route, source callback, allowed/forbidden scope, validation, skill routing ledger, compressed callback, skill-hit report, and reusable-optimization capture. Do not emit large placeholder sections for technical alternatives, CodeGraph, or open-source scans unless they are actually needed.
- `standard`: for normal L2 collaboration, architecture-owned work, new local code projects, or tasks where implementation scope must be explicit but risk is not critical.
- `full`: for L3, critical PR review, adversarial QA, security/DBA/operations gates, production or account-impacting actions, high-risk public claims, or any task whose receiver cannot act safely without deeper checks.

`auto` chooses `full` for `--risk critical` or `L3`, `standard` for `架构`, new code projects, or `L2`, and `compact` for the remaining L0/L1 prompts. A human may override with `--profile compact|standard|full`, but the prompt must state the chosen `Token Budget Profile` so reviewers can catch over-broad or under-specified delegation.

## Loop Engineering Rule

Treat role-window collaboration as a closed loop, not just parallel conversation.

Every non-trivial multi-window task must carry an explicit loop state. Use the smallest useful state set from:
- `待总控分流`
- `待架构拆解`
- `待内容主编拆解`
- `已派发`
- `执行中`
- `开发完成`
- `内容完成`
- `QA 未通过`
- `返工中`
- `QA 通过`
- `架构验收`
- `内容主编验收`
- `总控终验`
- `完成`
- `阻塞`

When `QA`, `架构`, `内容主编`, `总控`, or any source window sends work back, feedback must be structured enough to change the next iteration. Include:
- problem or gap;
- evidence, file path, screenshot, command output, or reproduction step;
- severity or acceptance impact;
- suggested return target: `总控` / `架构` / `内容主编` / `开发` / `UI/Frontend` / `QA` / another named role;
- decision needed, if any;
- next loop state.

At loop close, `总控` or the final coordinator must consider whether the result should update durable behavior. `架构` does this for technical loops and `内容主编` does this for content loops. If the same issue is likely to recur, record a proposed sedimentation target such as `SKILL.md`, `README.md`, role prompt template, QA checklist, validation command, or project docs. Do not edit those targets unless the user has authorized the edit or the current task explicitly asks for skill/workflow maintenance. For cross-role skill routing, registry, README/docs structure, hit-rate, or token-compression improvements, route the landing work to `技能维护`.

## Core Rule

Do not invent project state. Use only the current conversation, local files, git state, known memory, and user-provided facts. If a fact is missing, write `待确认` or make a small explicit assumption.

## Reusable Optimization Capture Rule

If using this skill reveals a reusable prompt gap, role-boundary improvement, validation habit, callback habit, skill routing miss, token-compression issue, or source-policy improvement, make it visible in the generated role prompt and in the callback/completion message under `可复用优化沉淀`.

Use this three-state wording:
- `无`: no reusable workflow change was discovered this round.
- `建议`: a reusable improvement was discovered, but it needs user approval or a separate maintenance task before editing.
- `已沉淀`: the current task explicitly authorizes skill/workflow maintenance and the improvement was already written to the named target.

Use this ownership split: the discovering role proposes; `总控` decides for global workflow changes; `架构` decides for technical-loop changes; `内容主编` decides for content-loop changes; `技能维护` lands cross-role edits such as registry, README/docs, hit metrics, trigger descriptions, split/merge/rename, or recurring miss fixes.

Update this skill directly only when the user has authorized self-editing or the current request asks for skill/workflow improvement. Otherwise, return the proposed target and rationale instead of silently editing.

Default edit targets:
- [SKILL.md](SKILL.md) for workflow, gateway, output-shape, or invocation rules;
- [references/role-cards.md](references/role-cards.md) for role-specific defaults.

After editing, validate the skill structure and summarize the change. Keep self-edits narrow; do not rewrite unrelated roles.

## Role Card Reference

For common role defaults, read [references/role-cards.md](references/role-cards.md) only when needed. Use it when the user names or implies a role such as:
- 总控 / CEO;
- 架构 / CTO;
- 开发 / backend / frontend;
- UI/PPT / slide deck;
- 内容主编 / content editor / editor-in-chief;
- 视频 / 宣传视频 / HyperFrames;
- 公众号发布 / 微信公众号 / WeChat Official Account article publishing;
- 小红书 / Rednote publishing / Xiaohongshu notes;
- 运维 / deployment / production verification;
- DBA / database administration / MySQL instance capacity / binlog / WAL / InnoDB / long transaction incident;
- 安全;
- 测试 / test cases / test report / stress testing / load testing / performance testing;
- QA / review / 验收.
- 文档/交付 / delivery docs / requirements / contract / acceptance / handoff.
- 知识库 / personal knowledge base / Obsidian vault / notes taxonomy.
- 技能维护 / Skill Curator / skill hit-rate / registry / README / source policy / trigger tuning.

For `安全`, always include the relevant downstream security skill in the generated prompt:
- public site, black-box, exposed JS/API, login protection, CORS, headers, or penetration-style report: `$authorized-blackbox-web-security`;
- repository-wide or scoped-path code security scan: `$codex-security:security-scan`;
- PR, branch, commit, or working-tree security review: `$codex-security:security-diff-scan`;
- deep repository scan: `$codex-security:deep-security-scan`;
- fix a validated or plausible security finding: `$codex-security:fix-finding`.

### Public Writing Gate

For roles that produce outward-facing Chinese copy (`公众号发布`, `小红书`, `UI/PPT` social/cover/landing copy, and `视频` public scripts/captions), load and apply `$humanizer-zh` before any final, preview-ready, publish-ready, or copy-paste-ready content output.

- Treat this as mandatory for formal public copy, not only when the draft obviously sounds AI-generated.
- Preserve facts, dates, prices, claims, attribution, source links, and approved structure. The anti-AI pass must not invent evidence or change the publishing decision.
- Use `$story-deslop` only when the public copy itself is narrative prose, story fragments, character dialogue, or fiction-like scenario writing. Normal WeChat/Xiaohongshu marketing or analysis copy still defaults to `$humanizer-zh`.
- Skip this gate only for rough outlines, internal notes, diagnostics, or non-public technical/docs output, and say it was not formal public copy.

#### Content Tone Gate

`内容主编` owns the `反老登味 / 反 AI 味内容闸门` for public-facing content. Before formal outward copy leaves the content domain, `内容主编`, `公众号发布`, `小红书`, `视频`, and `UI/PPT` public copy must check:

- 反老登味：avoid 说教、爹味、上位者口吻、油腻成功学、年龄/资历压人、替读者下判断.
- 反 AI 味：avoid 模板化、空泛排比、万能套话、机械转折、过度总结、没有个人判断.
- Keep real experience, concrete details, natural spoken rhythm, platform voice, and the reader's actual situation.
- Do not change facts, data, prices, dates, source attribution, authorization boundaries, publishing status, endorsements, or effect claims.
- `$humanizer-zh` is still required for final formal Chinese copy; the tone gate defines taste and risk boundaries instead of replacing that skill.

### X MCP Content Research Source

`X MCP` is an optional, read-only, user-authorized content research source for `内容主编`, `小红书`, `公众号发布`, and `视频`. Use it for viral-content research, trend scanning, topic pools, benchmark accounts, public discussion timelines, and cross-platform signal gathering.

Boundaries:
- Default coordinator: `内容主编`. Platform roles should usually inherit the editor's findings; they may call X MCP directly only when assigned.
- Official docs: https://docs.x.com/tools/mcp. X MCP connects through `https://api.x.com/mcp` via `xurl mcp`; Docs MCP at `https://docs.x.com/mcp` is for X API documentation lookup.
- Default allowed use: read/search posts, users, user timelines, trends/news, public discussions, and public source context that the authorized account can access.
- Default forbidden use: posting, publishing Articles, following/unfollowing, liking, reposting, DMs, account settings, bookmark mutation, engagement manipulation, or any write action.
- Secrets and OAuth: require the user's X Developer app and OAuth flow when real access is needed; never write `CLIENT_ID`, `CLIENT_SECRET`, tokens, cookies, or account-specific state into this repo.
- Interpretation: X data is a trend and benchmark signal, not direct proof that a Xiaohongshu or WeChat piece will perform. Pair it with platform-local skills such as `$cheat-on-content`, `$xhs-comment-research`, and `$humanizer-zh` before final content.

For role tools sourced from external GitHub skills or Hermes-owned operational skills, name them as dependencies instead of treating them as local role logic:
- `总控` CEO/product pressure, role route, and model-budget review: `$gstack-office-hours`, `$gstack-plan-ceo-review`, `$startup-pressure-test`;
- `架构` gstack method routing / plan lock-in before technical downstream windows: `$gstack`;
- `架构` executable requirement/spec shaping: `$gstack-spec`;
- `架构` full product/design/engineering/DX plan review for technical delivery: `$gstack-autoplan`;
- `架构` focused technical plan reviews: `$gstack-plan-eng-review`, `$gstack-plan-design-review`, `$gstack-plan-devex-review`, `$gstack-plan-tune`;
- `开发` bug/root-cause investigation and implementation review: `$gstack-investigate`, `$gstack-review`;
- `开发` final landing or release readiness when explicitly assigned: `$gstack-ship`, `$gstack-health`, `$gstack-devex-review`;
- risky work guardrails for `开发`, `运维`, `安全`, or `QA`: `$gstack-careful`, `$gstack-guard`, `$gstack-freeze`, `$gstack-unfreeze`;
- `UI/PPT` landing/redesign/frontend taste work: `$design-taste-frontend`;
- `UI/PPT` gstack design critique and exploration: `$gstack-design-consultation`, `$gstack-design-shotgun`, `$gstack-design-html`, `$gstack-design-review`, `$gstack-plan-design-review`;
- `UI/PPT` web PPT / Swiss deck / magazine deck work: `$guizang-ppt-skill`;
- `UI/PPT` Xiaohongshu/Rednote new carousel visuals, cover redesigns, and full visual rewrites: `$xhs-visual-director`;
- `UI/PPT` small Xiaohongshu/Rednote social-card edits, legacy carousel packages, or WeChat cover pairs: `$guizang-social-card-skill`;
- `UI/PPT` photo-reference cute 3D toy concepts, toy-character prompt packs, and GLB route planning: `$photo-to-cute-3d-toy`;
- `UI/PPT` final public-facing Chinese cover/card/landing copy: `$humanizer-zh` before final export or handoff;
- `内容主编` content route planning across WeChat, Xiaohongshu, video, and visual assets: use the same content role tools below and enforce approval gates;
- `公众号发布` WeChat Official Account AI application article operations, draft-box updates, weekly continuity, and publishing handoff: `$wechat-ai-app-ops`;
- `公众号发布` first-pass technical topic research and Chinese WeChat tech drafts: `$wechat-tech-writer`;
- `公众号发布` Markdown-to-WeChat HTML formatting and template polish: `$wechat-article-formatter`;
- `公众号发布` final Chinese copy humanization, anti-AI texture, and voice polish before preview or draft handoff: `$humanizer-zh`;
- `公众号发布` cover image pairs and inline article visuals when needed: `$guizang-social-card-skill`;
- `小红书` Xiaohongshu/Rednote note packaging, carousel assets, captions, tags, content experiments, comment research, and publishing automation: use `$cheat-on-content` for topic scoring, blind prediction, benchmark learning, post-publish retro, and rubric evolution; use `$xhs-comment-research` for comment collection/analysis when the user asks to use comment data; use `$xhs-visual-director` for new carousel visuals, cover redesigns, full visual rewrites, style judgment, visual master, and image prompts; use `$humanizer-zh` for title/caption/body copy humanization before final packaging; use `$xhs-publish-assistant` for copy-ready publish bundles; use `$guizang-social-card-skill` only for legacy/small social-card production when needed; then apply explicit user authorization gates before posting;
- `视频` final public-facing Chinese scripts, voiceover, and captions: `$humanizer-zh` before final output;
- narrative/story/dialogue public prose in any content role: `$story-deslop` only for those narrative passages;
- browser UI verification, rendered frontend checks, and E2E-like flows: `$playwright`;
- `安全` broad infrastructure-first posture review: `$gstack-cso`;
- `QA` web/UI behavior verification and release gates: `$gstack-qa-only`, `$gstack-qa`, `$gstack-canary`;
- `文档/交付` docs, release notes, learnings, and retrospectives: `$gstack-document-generate`, `$gstack-document-release`, `$gstack-learn`, `$gstack-retro`;
- `文档/交付` client-facing delivery packages, acceptance forms, delivery checklists, demo scripts, and handoff notes: `$delivery-document-package`;
- `测试` test cases, Excel workbook, Word/DOCX test report, or formal testing artifact package: `$test-case-report-builder`.
- `测试` independent stress/load/performance/concurrency validation: use native project test commands or appropriate tools, preserve exact evidence, and keep environment-impacting work behind explicit safety approval.
- `运维` application incident diagnosis: `$application-problem-diagnosis-workflow`;
- `运维` package/update planning before deployment: `$package-update-check-and-plan`;
- `运维` pre-deployment read-only checks: `$pre-deployment-readonly-checklist`;
- `运维` post-deployment read-only verification: `$post-deployment-readonly-verification`;
- `运维` Hermes cron empty-output diagnosis: `$hermes-cron-empty-output-diagnosis`;
- `运维` Hermes cron interpreter-wrapper diagnosis: `$hermes-python-script-wrapper-for-shell-cron`;
- `运维` proxy-dependent Python service diagnosis: `$proxy-dependent-python-service-diagnosis`;
- `运维` Python deployment troubleshooting: `$python-project-deployment-troubleshooting`.
- `运维` deploy/canary planning support only when it does not replace Hermes read-only production evidence: `$gstack-setup-deploy`, `$gstack-land-and-deploy`, `$gstack-canary`.
- `DBA` MySQL/Postgres instance-side capacity, binlog/WAL, InnoDB/transaction, lock, temp-space, backup/restore, partitioning, and data-retention incidents: keep the first pass read-only; separate evidence collection from actions such as kill, purge, DDL, resize, backup restore, or data cleanup; route from `运维` to `DBA` when the dominant risk is database-engine state rather than app/service state.

## Workflow

### 1. Classify The Request

Choose exactly one main mode:

- `ceo-gateway`: user has a new requirement that should first go through `总控`.
- `technical-architecture`: user explicitly asks for `架构` / `CTO` or the current route is already technical.
- `content-editorial`: user explicitly asks for `内容主编` or the current route is already content-led.
- `role-bootstrap`: user wants a first-time role prompt or an explicitly numbered parallel role.
- `handoff-summary`: user wants the current state summarized so an existing role can inherit/continue/reset.
- `multi-agent-split`: `总控`, `架构`, `内容主编`, or the user has already decided several windows are needed.
- `role-template`: user wants a reusable role prompt with project-specific details removed.

If unclear, ask at most 3 short questions. If a reasonable assumption is safe, state the assumption and proceed.

### 2. Gather Minimal Context

Prefer precise evidence over broad rediscovery:
- current user objective and latest request;
- repo/project path, if any;
- active role and desired role autonomy;
- files, docs, screenshots, URLs, test outputs, terminal state, or git state that matter;
- work already completed, work not completed, blockers, and known risks;
- user constraints such as commit language, PR expectations, no-go paths, production safety, or read-only boundaries.

For local repos, inspect before writing prompts when the answer depends on current state:
- `git status --short --branch`;
- CodeGraph status/init when this is a new local code project or newly opened repository;
- relevant docs named by the user;
- relevant changed files or recent test output.

For `technical-architecture`, after the requirement is clear enough to describe, apply the Open-Source Reference Scan Rule before finalizing technical architecture decisions or downstream role prompts.

### 3. Normalize The Role

Every role prompt must state:
- identity: what role the new window is playing;
- responsibility: what the role owns;
- non-responsibility: what the role must not do;
- first actions: what to read/check before acting;
- execution style: implement, review, plan, design, summarize, or only draft prompts;
- collaboration rule: when to ask the user, when to proceed.

Use strong boundaries. A role prompt that says "do everything" is a failed prompt.

Use concise role names in user-facing prompts:
- `总控`, not `CEO 总调度与全局编排角色`;
- `架构`, not `架构总览与需求编排角色`;
- `开发`, not `开发 agent`;
- `UI/PPT`, not a long UI design and PPT production title;
- `内容主编`, not a long content strategy and publishing coordinator title;
- `视频`, not a long promo-video production title.
- `公众号发布`, not a long WeChat article automation title.
- `小红书`, not a long Rednote publishing operator title.
- `知识库`, not a long personal knowledge-base curator title.

### 4. Define Agent Boundaries

For each agent/window, include:
- objective;
- allowed files or surfaces;
- forbidden files or surfaces;
- input docs/context to read first;
- output artifacts;
- validation commands or manual verification;
- commit/PR expectations;
- final report format.
- source-window callback target and the rule for actively notifying it.
- loop state, structured feedback expectations, and whether durable rule sedimentation should be considered at the end.

When splitting agents, avoid overlap. If overlap is unavoidable, name the shared files and the coordination rule.

These boundary items are defaults. Do not make the user spell out "文件白名单、禁止范围、验证命令、提交要求"; include them automatically whenever a role may modify files.

### 5. Output A Forwardable Prompt

Default to Chinese when the user writes in Chinese. Make the prompt directly copyable.

Prefer generating the skeleton with `scripts/render_role_prompt.py` when available, then fill project-specific judgment fields. Before using the prompt for a non-trivial role dispatch, run `scripts/validate_role_loop.py --prompt <file>` or manually check the same required markers when no file exists.

Use this structure:

```text
【给 <角色名> 窗口的提示词】

你现在担任：
...

背景：
...

模型建议：
- model：
- thinking：
- 升级/降级条件：

Token Budget Profile：
- profile：compact / standard / full
- 策略：

角色树位置（总控/架构/内容主编/执行角色）：
...

Loop 深度（可折叠路由）：
- 本次深度：L0 / L1 / L2 / L3
- L0：用户明确指定执行角色，直接执行一个低风险小任务；来源是用户，不是总控。
- L1：总控只对接负责人层（架构 / CTO、内容主编、知识库、技能维护、文档/交付），负责人给出方案、风险、验收建议或是否需要拆下游。
- L2：负责人拆给执行角色，执行角色回调负责人，负责人收敛后回总控。
- L3：高风险闭环，在 L2 基础上加入测试、QA、安全、DBA、运维等独立复核或门禁。
- 选择原则：能 L0/L1 解决就不要升级到 L2/L3；一旦进入总控管理流，总控不直接指挥执行层。

任务分发决策：
- 任务规模：tiny / small / medium / large / critical
- 建议路径：
- 执行规则：

负责人交互边界：
- 总控 / CEO 只直接对接负责人层或治理角色：架构 / CTO、内容主编、知识库、技能维护、文档/交付，或用户明确指定的例外。
- 技术执行角色（开发、UI/PPT、测试、QA、安全、DBA、运维）默认由架构 / CTO 派发、验收和回流；总控只接收架构汇总的项目结果、风险、决策点和最终验收建议。
- 内容执行角色（公众号发布、小红书、视频）默认由内容主编派发、验收和回流；总控只接收内容主编汇总的内容结果、发布风险、授权点和最终验收建议。
- 总控不编写或修改代码、测试脚本、验收脚本、自动化验证脚本；需要这类产物时，交给开发或测试实现，由架构/QA 复核证据。

技术方案（架构/CTO 处理复杂技术需求必填；已选定则写明选型）：
- 方案 A：
- 方案 B：
- 方案 C：
- 推荐：
- 待确认：

目标：
...

请先阅读/检查：
...

允许修改：
...

禁止修改：
...

实现/工作要求：
...

验证：
...

闭环状态：
- 当前状态：
- 上一轮反馈：
- 本轮退出条件：

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
- 项目：
- 工具可用性：
- 初始化状态：
- 索引路径/忽略策略：
- 建议动作：
- 跳过或失败原因：

路由前检查（总控、架构、内容主编和多角色派发必填）：
- 是否读取 agent-role-orchestrator：
- 是否读取 .codex/role-windows.md：
- 是否复用已有角色线程：
- 是否写清模型建议/覆盖：
- 是否写清 source-window callback：
- 是否写清允许/禁止范围：
- 是否写清验证与提交要求：
- 是否包含技能路由台账：
- 是否需要更新 .codex/role-windows.md：

技能路由台账（总控、架构、内容主编和多角色拆分必填；单一执行角色可写“不适用/继承来源台账”）：
- 候选 skill：
- 必选 skill：
- 可选 skill：
- 跳过 skill 及原因：
- 预期加载角色：

开源/可借鉴方案扫描（架构/CTO 技术窗口必填；非架构窗口仅在被明确指派时填写）：
- 检索关键词：
- 候选方案：
- 可借鉴点：
- 不采用/风险：
- 对下游工作的约束：

提交/PR 要求：
...

回调/通知规则：
- 本任务发起方：<角色名 + thread id，未知则写待确认>。
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
...

角色底线：
...
```

For a handoff summary, prepend:

```text
【当前情况摘要】
- 交接方式：新建 / 继承 / 接续 / 重置
- 当前窗口角色：
- 项目/路径：
- 角色窗口台账：
- 最新目标：
- 已完成：
- 尚未完成：
- 关键文件/证据：
- 已运行验证：
- 风险/阻塞：
- 建议下一步：
```

For a multi-agent split, include a short table before the prompts:

```text
| 窗口 | 目标 | 允许范围 | 禁止范围 | 验收 |
| --- | --- | --- | --- | --- |
```

## Concise Invocation Examples

Prefer short examples when telling the user how to call the skill:

```text
使用 $agent-role-orchestrator，给我总控窗口。
```

```text
使用 $agent-role-orchestrator，接续当前总控。
```

```text
使用 $agent-role-orchestrator，给我架构窗口。
```

```text
使用 $agent-role-orchestrator，接续当前架构。
```

```text
使用 $agent-role-orchestrator，给我开发窗口。
```

```text
使用 $agent-role-orchestrator，接续开发。
```

```text
使用 $agent-role-orchestrator，给我开发1号、开发2号。
```

```text
使用 $agent-role-orchestrator，给我 UI/PPT 窗口。
```

```text
使用 $agent-role-orchestrator，给我 UI/Frontend 窗口。
```

```text
使用 $agent-role-orchestrator，给我内容主编窗口。
```

```text
使用 $agent-role-orchestrator，给我视频窗口。
```

```text
使用 $agent-role-orchestrator，给我公众号发布窗口。
```

```text
使用 $agent-role-orchestrator，给我小红书窗口。
```

```text
使用 $agent-role-orchestrator，给我 DBA 窗口。
```

```text
使用 $agent-role-orchestrator，给我测试窗口。
```

```text
使用 $agent-role-orchestrator，给我文档/交付窗口。
```

```text
使用 $agent-role-orchestrator，给我知识库窗口。
```

```text
使用 $agent-role-orchestrator，给我技能维护窗口。
```

## Quality Bar

Before finalizing, check:
- no project-specific facts remain in a reusable template unless the user requested them;
- every implementation role has a clear file whitelist and blacklist;
- every non-implementation role says whether it may edit files;
- validation is concrete, not just "test it";
- production or security roles default to read-only or low-impact investigation unless user authorizes changes;
- next-window prompts can stand alone without this conversation, while still marking uncertain facts as `待确认`;
- commit instructions match the user's known preference when available;
- a single new requirement goes through `总控` first unless explicitly bypassed;
- role prompts choose a `Loop 深度` (`L0`/`L1`/`L2`/`L3`) and do not force the longest chain when a shorter loop can close safely;
- `总控` prompts include a `任务分发决策` with task size and route: `tiny` self-handle, `small` direct to `开发`, `medium` owner layer, `large` full team, or `critical` L3 gates;
- `总控` interacts with owner-layer roles by default, not execution roles; technical execution goes through `架构` / `CTO`, content execution goes through `内容主编`;
- `总控` may self-handle only `tiny` low-risk local changes and may direct-dispatch only `small` development tasks to `开发`; it does not write test scripts, acceptance scripts, automation validation scripts, or technical verification helpers by default;
- `架构` is treated as `CTO` for technical delivery, not as the global CEO-style entrance;
- `内容主编` is treated as the content-domain coordinator for `公众号发布`, `小红书`, `视频`, and content visuals;
- non-trivial multi-window work carries a loop state and exit condition;
- QA or source-window feedback is structured with evidence, impact, return target, decision needs, and next state;
- final coordination reports reusable lessons as `无`, `建议`, or `已沉淀`, with target and rationale when applicable;
- complex technical requirements include a multi-option technical options brief from `架构` / `CTO` and an explicit route-selection gate before downstream implementation;
- pure frontend or visual-fidelity work routes visual ownership to `UI/PPT` / `UI/Frontend` by default, with `开发` used for scoped implementation rather than as a catch-all;
- UI/PPT preview/reference-image work includes `预览图实现路线选择` before implementation, rather than defaulting to CSS-only reconstruction;
- existing role windows are inherited/continued by default instead of recreated;
- numbered parallel roles appear only when explicitly requested or selected by `总控`, `架构`, or `内容主编`;
- new local code projects check or initialize CodeGraph before deeper architecture/development work, or include an explicit skip/failure reason.
- CEO, architecture, multi-role, dispatch, callback, and registry tasks read `agent-role-orchestrator/SKILL.md` and the project `.codex/role-windows.md` before creating or continuing role windows.
- `.codex/role-windows.md` is treated as the role routing source of truth; known thread ids are reused, unknown state is marked `待确认`, and misrouted windows are recorded as `误开/废弃/纠偏`.
- `总控`, `架构`, `内容主编`, and multi-role prompts include the `路由前检查` checklist.
- role prompts include a model/thinking recommendation or override when a new/continued window is being created.
- downstream role prompts include file scope, forbidden scope, validation, and commit/report expectations by default.
- downstream role prompts identify the source window and require active callback to that source when complete, blocked, or awaiting a decision.
- `总控`, `架构`, `内容主编`, and multi-role prompts include a `技能路由台账` with candidate/required/optional/skipped skills and expected loader roles.
- downstream role prompts include `技能命中回传` so required/actual/effective skill use can be measured.
- callbacks use `压缩回调` delta fields and avoid replaying full transcripts unless necessary.
- generated role prompts and completion/callback formats include `可复用优化沉淀：无 / 建议 / 已沉淀`.
- `架构` / `CTO` prompts require a bounded open-source/reference scan after technical requirements are confirmed, or include an explicit skip reason.
- `内容主编` prompts enforce public-writing gates and final-publish approval gates for content roles.
- `安全` prompts explicitly invoke the appropriate security skill instead of duplicating that workflow.
- `测试` prompts for test cases or test reports explicitly invoke `$test-case-report-builder`.
- `测试` prompts for stress/load/performance/concurrency validation specify environment, data isolation, traffic limits, stop conditions, metrics, and evidence capture.
- `开发` prompts require first-principles engineering for implementation, investigation, and correction: goal, facts, constraints/invariants, hypothesis, minimal change, and validation proof.
- `QA` prompts stay focused on review readiness, acceptance risk, and blocker verification; they do not own test-case/report authoring by default.
- `QA` prompts require adversarial review: counterexamples, hidden assumptions, edge cases, regression surfaces, evidence gaps, and residual risks.
- `文档/交付` prompts stay focused on requirements, quotes, contracts, acceptance records, handoff docs, change logs, and operator-facing documentation; they do not own code, QA signoff, legal advice, or tax advice.
- `总控` prompts choose CEO/product pressure methods and model budget; `架构` prompts use `$gstack` as a technical method router and choose `$gstack-spec`, `$gstack-autoplan`, or focused `$gstack-plan-*` reviews when useful.
- role prompts distinguish external GitHub skills from local-owned skills when that affects maintenance or self-editing.
- recurring skill misses, noisy triggers, registry drift, README/docs information architecture, and cross-role skill edits route to `技能维护`.

## Common Defaults

Use these defaults unless the user says otherwise:
- `总控` is the default first window. It clarifies goal, success signal, priority, task size, loop depth, role route, source-window callback, model/thinking plan, token budget, top-level registry, and final acceptance; it may self-handle `tiny` low-risk local changes and may direct-dispatch `small` development tasks to `开发`, but otherwise talks to owner-layer roles by default and does not write test/acceptance scripts, draft content, operate production, directly supervise execution roles, or own long-term skill curation.
- `架构` / `CTO` owns technical delivery under `总控` or an explicit user/source-window assignment: technical options, CodeGraph bootstrap, bounded open-source/reference scan, technical role split, and the `开发` / `UI/PPT` / `测试` / `QA` / `安全` / `DBA` / `运维` loop.
- `架构` uses `$gstack` for technical method routing: specs go to `$gstack-spec`; concrete plans go to `$gstack-autoplan` or focused `$gstack-plan-*` reviews.
- `开发` is the `开发负责人` / `Dev Lead` by default: it breaks down coding work, may delegate single, short, small, verifiable coding slices to `gpt-5.3-codex-spark` + `xhigh` subagents, integrates results, runs final tests, and commits when asked or when workspace instructions require it; it should not own UI/visual direction when the dominant risk is visual fidelity.
- `UI/PPT` (also `UI/Frontend` for frontend visual work) and `视频` produce visible artifacts and perform visual verification; when UI/PPT receives a preview/reference image, it first chooses a `预览图实现路线选择` across CSS/components, asset, Canvas/SVG, Three.js/WebGL, Lottie/video, or library routes; when output includes final public-facing Chinese copy, it runs `$humanizer-zh` before export or handoff.
- `内容主编` owns content-domain routing under `总控`: `公众号发布`, `小红书`, `视频`, and `UI/PPT` visual-asset collaboration; it enforces fact discipline, account boundaries, public-writing gates, and explicit publish approvals.
- `公众号发布` uses `$wechat-ai-app-ops`, runs `$humanizer-zh` before final preview/draft handoff, prepares and automates WeChat Official Account article drafts/previews by default, and requires explicit approval before final publish.
- `小红书` may use `$cheat-on-content` for social-content scoring, blind prediction, benchmark learning, and retro loops; it uses `$xhs-visual-director` for new carousel visuals, cover redesigns, and full visual rewrites, uses `$humanizer-zh` before final note/publish copy, uses `$xhs-publish-assistant` for copy-ready publish bundles, and requires explicit approval before final posting.
- `测试` uses `$test-case-report-builder` for test case and test report artifacts, and owns independent stress/load/performance/concurrency validation when assigned.
- `QA` checks review/release readiness, blockers, and acceptance risk through adversarial review that tries to falsify readiness with counterexamples, edge cases, regression surfaces, and evidence gaps.
- `文档/交付` maintains the project documentation package across phases: requirements, quotes, contracts/service agreements, acceptance sheets, delivery checklists, operation guides, change confirmations, and handoff notes; it does not write code or replace legal/tax review.
- `知识库` organizes an Obsidian-style personal notes vault: inventories note clusters, proposes taxonomy and link maps, maintains WikiLinks/MOC/index notes and shareable Markdown when assigned, and preserves the user's personal voice and high-stakes boundaries; it does not delete, publish, edit `.obsidian` config, or convert personal notes into medical/financial/legal advice without explicit approval.
- `技能维护` owns skill-hit retrospectives, trigger tuning, registry/README/docs/source-policy updates, role-card split/merge/rename suggestions, and reusable skill PRs; it does not implement product work or absorb project-specific role-window state.
- `运维` investigates read-only first and avoids restarts, migrations, deletes, or production writes without explicit authorization.
- `DBA` owns database-instance evidence and action plans for capacity, temp space, binlog/WAL, long transactions, locks, backups, schema/data retention, and risky database maintenance; it starts read-only and requires explicit second approval before kill, purge, DDL, resize, or data cleanup.
- `安全` delegates to the matching security skill first, uses low-impact checks by default, and distinguishes evidence from suspicion.
