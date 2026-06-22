---
name: agent-role-orchestrator
description: Create concise role-specific Codex window prompts and current-window handoffs with an architecture-first gateway and role-window registry. Use when the user asks for an architecture/development/UI-PPT/UI-Frontend/video/ops/security/testing/QA/document-delivery/WeChat Official Account publishing/Xiaohongshu/personal knowledge-base window, says to inherit/reset/continue the current role, asks for the next-window prompt, wants a requirement routed through architecture before deciding whether to open other role windows, wants existing roles reused instead of recreated, wants testing test-case/report prompts, wants delivery-document prompts for requirements/contracts/acceptance/docs, wants content publishing roles, wants personal knowledge-base organization, or wants security-audit prompts that delegate to the appropriate security skill.
---

# Agent Role Orchestrator

## Purpose

Turn fuzzy collaboration intent into a real role-window handoff or copy-paste prompt, with a clear role, context, boundaries, validation plan, and reporting contract.

Use this skill to:
- bootstrap a new role window, usually `架构` first;
- summarize the current thread so a next window can inherit a role;
- let `架构` decide whether to open `开发`, `UI/PPT` / `UI/Frontend`, `视频`, `公众号发布`, `小红书`, `运维`, `安全`, `测试`, `QA`, `文档/交付`, or `知识库` windows;
- remember whether each role has already been established and reuse it by default;
- rewrite a project-specific role prompt into a reusable role template.
- route `安全` work to the right existing security skill by default.
- route `测试` test-case/report work to the test artifact skill by default.
- require role windows to actively report terminal task state back to the task's source window.
- bootstrap CodeGraph for new local code projects when available.

## Architecture-First Rule

For one new requirement, default to one `架构` window first. Do not directly split the requirement into several role windows just because the user names possible roles.

Only output multiple downstream role prompts when one of these is true:
- the user says `架构已经决定`, `按这个架构拆`, or provides an accepted architecture split;
- the current thread is already acting as `架构` and has enough evidence to choose downstream roles;
- the user explicitly overrides the gateway and asks to bypass `架构`.

When the user asks for `开发`, `UI/PPT`, `视频`, `公众号发布`, `小红书`, `运维`, `安全`, `测试`, `QA`, `文档/交付`, or `知识库` prompts without an architecture decision, either produce a `架构` prompt first or clearly mark the downstream prompt as `待架构确认`.

## Complex Requirement Technical Options Rule

For a non-trivial new requirement, `架构` must produce a technical options brief before opening implementation windows. Non-trivial includes multi-screen or multi-scene products, uncertain asset pipelines, visual-fidelity targets, multi-role work, integration choices, deployment choices, or any request where the wrong route could waste significant time.

The brief should present as many credible routes as useful, normally 3 to 5 when plausible instead of only 1 or 2. For each route, record:
- what the route is;
- fit to the user's goal;
- tradeoffs, cost, speed, quality ceiling, and rollback path;
- required assets, tools, permissions, and external dependencies;
- main risks and validation plan.

Then name a recommended route, or mark the decision as `待用户/架构确认`. Do not dispatch implementation work until a route is accepted or `架构` explicitly selects one with rationale. If one route is clearly dominant, still name the rejected alternatives briefly and explain why they are not selected.

For frontend or visual product work, the options brief must cover the UX/UI route, asset-production route, implementation route, and QA/visual-acceptance route.

## Frontend/UI Role Routing Rule

Do not use `开发` as a catch-all just because the workspace contains code. Route by the dominant risk.

When a request is a pure frontend project, UI-heavy page, visual-fidelity pass, interaction/motion design, design-system decision, generated-asset composition, 2D/2.5D/3D scene layout, or "make it match the preview" task, prefer `UI/PPT` as the primary downstream role. In these cases `UI/PPT` may be addressed as `UI/Frontend`.

Use `开发` for implementation plumbing, data models, build/test scripts, asset gates, browser-state bugs, and code execution under an accepted visual/technical spec. When both visual direction and code are needed, split them: `UI/Frontend` owns the visual route, target composition, screenshot acceptance, and responsive behavior; `开发` implements the scoped code changes from that spec; `QA` or `架构` verifies.

## Open-Source Reference Scan Rule

After `架构` has confirmed the requirement enough to describe the problem, it should perform a bounded online scan for open-source or public reference solutions before locking the design or splitting downstream role work, when network access is available and the work is not explicitly offline, private, or confidential.

Keep the scan small and decision-oriented:
- search for existing GitHub repos, libraries, product docs, demos, architecture notes, issue threads, and prior-art implementations that resemble the requirement;
- inspect about 3 to 5 plausible candidates or use a short time box, then stop and synthesize;
- record fit, gaps, license/attribution concerns, maintenance activity, security/privacy risks, and what should or should not be borrowed;
- do not blindly copy code, prompts, UI, wording, or architecture; convert useful findings into constraints, options, and validation checks;
- if no useful reference is found, say so and proceed from first principles;
- if the scan is skipped because the user forbids web access, the network is unavailable, or the context is sensitive/offline, state the reason explicitly.

Include the result in the architecture summary or downstream prompt:

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
- start with `codegraph_status` if the CodeGraph tools are available;
- if the project is not initialized, run the project-level initialization from the repo root, such as `codegraph init -i`, then re-check status;
- if CodeGraph is not installed or the tool is unavailable, either prompt the user with the install action or perform a silent user-level install only when the environment provides a known non-destructive installer and policy allows it;
- do not claim CodeGraph is ready until a fresh status check confirms it;
- if initialization writes a local index such as `.codegraph/`, keep it local and ignore it unless the project explicitly tracks that directory;
- skip and state the reason when the task is read-only, the project path is unknown, the repo is not code-oriented, the user forbids writes/install, or initialization repeatedly fails.

After bootstrapping, include the status in the architecture summary:

```text
【CodeGraph 状态】
- 可用性：
- 初始化状态：
- 索引路径/忽略策略：
- 跳过或失败原因：
```

## Role-Window Registry Rule

Treat role windows as persistent per project/workstream.

Default lifecycle:
- first time a role is needed: establish the real role window when thread tools are available; otherwise create the role prompt and mark it as pending establishment;
- after a role is established: continue or send to that same-role window by default;
- when the same role needs fresh context, output an inheritance/continuation prompt for the existing role;
- create numbered parallel roles only when the user or `架构` explicitly asks for them, such as `开发1号`, `开发2号`, `UI/PPT1号`;
- if existing-role state is unknown, ask for or reconstruct the role registry before generating same-role prompts.

Maintain this registry in architecture handoffs when possible:

```text
【角色窗口台账】
- 架构：已建立 / 未建立 / 待确认
- 开发：已建立 / 未建立 / 待确认；实例：开发1号、开发2号...
- UI/PPT（UI/Frontend）：已建立 / 未建立 / 待确认
- 视频：已建立 / 未建立 / 待确认
- 公众号发布：已建立 / 未建立 / 待确认
- 小红书：已建立 / 未建立 / 待确认
- 运维：已建立 / 未建立 / 待确认
- 安全：已建立 / 未建立 / 待确认
- 测试：已建立 / 未建立 / 待确认
- QA：已建立 / 未建立 / 待确认
- 文档/交付：已建立 / 未建立 / 待确认
- 知识库：已建立 / 未建立 / 待确认
```

Use `新建` only for first establishment or explicit parallel instances. Use `继承` / `接续` for resets, context refreshes, and ongoing work in an existing role.

### Project Registry File

For project-scoped work with a known local project path, persist the role-window registry in the project whenever file writes are allowed. Use `.codex/role-windows.md` at the project root by default.

Before creating or continuing a role window:
- read `.codex/role-windows.md` if it exists;
- merge it with current conversation evidence and thread/tool evidence;
- prefer existing established role windows over creating duplicates;
- when thread tools are available and project registry writes are allowed, default to establishing or continuing the real role window instead of only outputting a prompt;
- if the canonical role already has an established thread id, continue or send to that thread;
- if the canonical role is not established, create/open the role window with the canonical title and record the thread id;
- create numbered parallel windows only when the user or `架构` explicitly chooses parallel work;
- output a copy-paste prompt instead only when the user asks for prompt-only output, thread tools are unavailable, or `架构` decides the real window should not be established yet;
- mark uncertain items as `待确认` instead of inventing thread ids or status.

After a role is created, manually opened by the user, continued, retired, or discovered to be misplaced, update `.codex/role-windows.md` with:
- role name and lifecycle status: `未建立`, `已建立`, `接续中`, `已关闭`, `误开/废弃`, or `待确认`;
- known thread id or `待确认`;
- project path or scope;
- current responsibility and forbidden responsibility;
- last known handoff/QA/development result;
- next recommended action.

Do not write the registry file when the user explicitly forbids file edits, when no project path is known, or when producing a reusable role template. In those cases, include the registry inline in the response and say it was not persisted.

## Source-Window Callback Rule

Role-window communication is source-directed, not architecture-directed by default.

When window `A` assigns, delegates, or hands off a task to window `B`:
- name `A` as the task source and callback target in `B`'s prompt, including role name and thread id when known;
- require `B` to actively notify `A` when the task is complete, blocked, or needs a decision from `A`;
- use thread tools to send that callback when available; if direct thread messaging is unavailable, require `B` to output a copy-paste-ready callback message addressed to `A`;
- do not tell every downstream role to report to `架构` unless `架构` is actually the source window, the designated coordinator, or the user explicitly says so;
- if `B` delegates a subtask to `C`, `B` becomes the source for `C` while still remaining responsible for reporting its own task state back to `A`.

This callback rule is separate from user-facing final reports. A downstream window may summarize for the user, but it must still close the loop with its task source.

## Loop Engineering Rule

Treat role-window collaboration as a closed loop, not just parallel conversation.

Every non-trivial multi-window task must carry an explicit loop state. Use the smallest useful state set from:
- `待拆解`
- `已派发`
- `执行中`
- `开发完成`
- `QA 未通过`
- `返工中`
- `QA 通过`
- `架构终验`
- `完成`
- `阻塞`

When `QA`, `架构`, or any source window sends work back, feedback must be structured enough to change the next iteration. Include:
- problem or gap;
- evidence, file path, screenshot, command output, or reproduction step;
- severity or acceptance impact;
- suggested return target: `架构` / `开发` / `UI/Frontend` / `QA` / another named role;
- decision needed, if any;
- next loop state.

At loop close, `架构` or the final coordinator must consider whether the result should update durable behavior. If the same issue is likely to recur, record a proposed sedimentation target such as `SKILL.md`, `README.md`, role prompt template, QA checklist, validation command, or project docs. Do not edit those targets unless the user has authorized the edit or the current task explicitly asks for skill/workflow maintenance.

## Core Rule

Do not invent project state. Use only the current conversation, local files, git state, known memory, and user-provided facts. If a fact is missing, write `待确认` or make a small explicit assumption.

## Self-Improvement Rule

If using this skill reveals a reusable prompt gap or role-boundary improvement, update this skill directly when the user has authorized self-editing or the current request asks for skill improvement.

Default edit targets:
- [SKILL.md](SKILL.md) for workflow, gateway, output-shape, or invocation rules;
- [references/role-cards.md](references/role-cards.md) for role-specific defaults.

After editing, validate the skill structure and summarize the change. Keep self-edits narrow; do not rewrite unrelated roles.

## Role Card Reference

For common role defaults, read [references/role-cards.md](references/role-cards.md) only when needed. Use it when the user names or implies a role such as:
- 架构;
- 开发 / backend / frontend;
- UI/PPT / slide deck;
- 视频 / 宣传视频 / HyperFrames;
- 公众号发布 / 微信公众号 / WeChat Official Account article publishing;
- 小红书 / Rednote publishing / Xiaohongshu notes;
- 运维 / deployment / production verification;
- 安全;
- 测试 / test cases / test report;
- QA / review / 验收.
- 文档/交付 / delivery docs / requirements / contract / acceptance / handoff.
- 知识库 / personal knowledge base / Obsidian vault / notes taxonomy.

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

For role tools sourced from external GitHub skills or Hermes-owned operational skills, name them as dependencies instead of treating them as local role logic:
- `架构` gstack method routing / plan lock-in before downstream windows: `$gstack`;
- `架构` early idea and demand reality check: `$gstack-office-hours`;
- `架构` executable requirement/spec shaping: `$gstack-spec`;
- `架构` full product/design/engineering/DX plan review: `$gstack-autoplan`;
- `架构` focused plan reviews: `$gstack-plan-ceo-review`, `$gstack-plan-eng-review`, `$gstack-plan-design-review`, `$gstack-plan-devex-review`, `$gstack-plan-tune`;
- `开发` bug/root-cause investigation and implementation review: `$gstack-investigate`, `$gstack-review`;
- `开发` final landing or release readiness when explicitly assigned: `$gstack-ship`, `$gstack-health`, `$gstack-devex-review`;
- risky work guardrails for `开发`, `运维`, `安全`, or `QA`: `$gstack-careful`, `$gstack-guard`, `$gstack-freeze`, `$gstack-unfreeze`;
- `UI/PPT` landing/redesign/frontend taste work: `$design-taste-frontend`;
- `UI/PPT` gstack design critique and exploration: `$gstack-design-consultation`, `$gstack-design-shotgun`, `$gstack-design-html`, `$gstack-design-review`, `$gstack-plan-design-review`;
- `UI/PPT` web PPT / Swiss deck / magazine deck work: `$guizang-ppt-skill`;
- `UI/PPT` Xiaohongshu/Rednote carousel images, social cards, or WeChat cover pairs: `$guizang-social-card-skill`;
- `UI/PPT` photo-reference cute 3D toy concepts, toy-character prompt packs, and GLB route planning: `$photo-to-cute-3d-toy`;
- `UI/PPT` final public-facing Chinese cover/card/landing copy: `$humanizer-zh` before final export or handoff;
- `公众号发布` WeChat Official Account AI application article operations, draft-box updates, weekly continuity, and publishing handoff: `$wechat-ai-app-ops`;
- `公众号发布` first-pass technical topic research and Chinese WeChat tech drafts: `$wechat-tech-writer`;
- `公众号发布` Markdown-to-WeChat HTML formatting and template polish: `$wechat-article-formatter`;
- `公众号发布` final Chinese copy humanization, anti-AI texture, and voice polish before preview or draft handoff: `$humanizer-zh`;
- `公众号发布` cover image pairs and inline article visuals when needed: `$guizang-social-card-skill`;
- `小红书` Xiaohongshu/Rednote note packaging, carousel assets, captions, tags, content experiments, comment research, and publishing automation: use `$cheat-on-content` for topic scoring, blind prediction, benchmark learning, post-publish retro, and rubric evolution; use `$xhs-comment-research` for comment collection/analysis when the user asks to use comment data; use `$humanizer-zh` for title/caption/body copy humanization before final packaging; use `$xhs-publish-assistant` for copy-ready publish bundles; use `$guizang-social-card-skill` for carousel/social-card production when needed; then apply explicit user authorization gates before posting;
- `视频` final public-facing Chinese scripts, voiceover, and captions: `$humanizer-zh` before final output;
- narrative/story/dialogue public prose in any content role: `$story-deslop` only for those narrative passages;
- browser UI verification, rendered frontend checks, and E2E-like flows: `$playwright`;
- `安全` broad infrastructure-first posture review: `$gstack-cso`;
- `QA` web/UI behavior verification and release gates: `$gstack-qa-only`, `$gstack-qa`, `$gstack-canary`;
- `文档/交付` docs, release notes, learnings, and retrospectives: `$gstack-document-generate`, `$gstack-document-release`, `$gstack-learn`, `$gstack-retro`;
- `文档/交付` client-facing delivery packages, acceptance forms, delivery checklists, demo scripts, and handoff notes: `$delivery-document-package`;
- `测试` test cases, Excel workbook, Word/DOCX test report, or formal testing artifact package: `$test-case-report-builder`.
- `运维` application incident diagnosis: `$application-problem-diagnosis-workflow`;
- `运维` package/update planning before deployment: `$package-update-check-and-plan`;
- `运维` pre-deployment read-only checks: `$pre-deployment-readonly-checklist`;
- `运维` post-deployment read-only verification: `$post-deployment-readonly-verification`;
- `运维` Hermes cron empty-output diagnosis: `$hermes-cron-empty-output-diagnosis`;
- `运维` Hermes cron interpreter-wrapper diagnosis: `$hermes-python-script-wrapper-for-shell-cron`;
- `运维` proxy-dependent Python service diagnosis: `$proxy-dependent-python-service-diagnosis`;
- `运维` Python deployment troubleshooting: `$python-project-deployment-troubleshooting`.
- `运维` deploy/canary planning support only when it does not replace Hermes read-only production evidence: `$gstack-setup-deploy`, `$gstack-land-and-deploy`, `$gstack-canary`.

## Workflow

### 1. Classify The Request

Choose exactly one main mode:

- `architecture-gateway`: user has a new requirement that should first go through `架构`.
- `role-bootstrap`: user wants a first-time role prompt or an explicitly numbered parallel role.
- `handoff-summary`: user wants the current state summarized so an existing role can inherit/continue/reset.
- `multi-agent-split`: `架构` or the user has already decided several windows are needed.
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

For `architecture-gateway`, after the requirement is clear enough to describe, apply the Open-Source Reference Scan Rule before finalizing architecture decisions or downstream role prompts.

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
- `架构`, not `架构总览与需求编排角色`;
- `开发`, not `开发 agent`;
- `UI/PPT`, not a long UI design and PPT production title;
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

Use this structure:

```text
【给 <角色名> 窗口的提示词】

你现在担任：
...

背景：
...

技术方案（架构窗口处理复杂新需求必填；已选定则写明选型）：
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

CodeGraph 状态（新本地代码项目必填；不适用时写明原因）：
- 可用性：
- 初始化状态：
- 索引路径/忽略策略：
- 跳过或失败原因：

开源/可借鉴方案扫描（架构窗口必填；非架构窗口仅在被明确指派时填写）：
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
- 如无法直接发送到发起方窗口，请输出一段可复制的“给发起方的回调消息”。

结构化反馈格式（返工/验收失败/需要决策时必填）：
- 问题/缺口：
- 证据/复现：
- 影响等级：
- 建议回流对象：
- 需要决策：
- 下一闭环状态：

规则沉淀：
- 本轮是否暴露可复用流程问题：
- 建议沉淀位置：
- 是否需要另开 skill/README/清单更新：

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
使用 $agent-role-orchestrator，给我视频窗口。
```

```text
使用 $agent-role-orchestrator，给我公众号发布窗口。
```

```text
使用 $agent-role-orchestrator，给我小红书窗口。
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

## Quality Bar

Before finalizing, check:
- no project-specific facts remain in a reusable template unless the user requested them;
- every implementation role has a clear file whitelist and blacklist;
- every non-implementation role says whether it may edit files;
- validation is concrete, not just "test it";
- production or security roles default to read-only or low-impact investigation unless user authorizes changes;
- next-window prompts can stand alone without this conversation, while still marking uncertain facts as `待确认`;
- commit instructions match the user's known preference when available;
- a single new requirement goes through `架构` first unless explicitly bypassed;
- non-trivial multi-window work carries a loop state and exit condition;
- QA or source-window feedback is structured with evidence, impact, return target, decision needs, and next state;
- final coordination considers whether reusable lessons should be sedimented into a skill, README, checklist, prompt template, validation command, or project docs;
- complex new requirements include a multi-option technical options brief and an explicit route-selection gate before downstream implementation;
- pure frontend or visual-fidelity work routes visual ownership to `UI/PPT` / `UI/Frontend` by default, with `开发` used for scoped implementation rather than as a catch-all;
- existing role windows are inherited/continued by default instead of recreated;
- numbered parallel roles appear only when explicitly requested or selected by `架构`;
- new local code projects check or initialize CodeGraph before deeper architecture/development work, or include an explicit skip/failure reason.
- downstream role prompts include file scope, forbidden scope, validation, and commit/report expectations by default.
- downstream role prompts identify the source window and require active callback to that source when complete, blocked, or awaiting a decision.
- `架构` prompts require a bounded open-source/reference scan after requirements are confirmed, or include an explicit skip reason.
- `安全` prompts explicitly invoke the appropriate security skill instead of duplicating that workflow.
- `测试` prompts for test cases or test reports explicitly invoke `$test-case-report-builder`.
- `QA` prompts stay focused on review readiness, acceptance risk, and blocker verification; they do not own test-case/report authoring by default.
- `文档/交付` prompts stay focused on requirements, quotes, contracts, acceptance records, handoff docs, change logs, and operator-facing documentation; they do not own code, QA signoff, legal advice, or tax advice.
- `架构` prompts use `$gstack` as a method router and choose `$gstack-office-hours`, `$gstack-spec`, `$gstack-autoplan`, or focused `$gstack-plan-*` reviews when useful.
- role prompts distinguish external GitHub skills from local-owned skills when that affects maintenance or self-editing.

## Common Defaults

Use these defaults unless the user says otherwise:
- `架构` clarifies requirements, writes a multi-option technical options brief for complex new requirements, bootstraps CodeGraph for new local code projects when available, performs a bounded open-source/reference scan when relevant and allowed, maintains the role-window registry, and decides whether downstream windows are needed; it does not code or commit.
- `架构` uses `$gstack` for method routing: early ideas go to `$gstack-office-hours` or `$gstack-spec`; concrete plans go to `$gstack-autoplan` or focused `$gstack-plan-*` reviews.
- `开发` implements within a narrow file scope, runs tests, and commits when asked or when workspace instructions require it; it should not own UI/visual direction when the dominant risk is visual fidelity.
- `UI/PPT` (also `UI/Frontend` for frontend visual work) and `视频` produce visible artifacts and perform visual verification; when their output includes final public-facing Chinese copy, they run `$humanizer-zh` before export or handoff.
- `公众号发布` uses `$wechat-ai-app-ops`, runs `$humanizer-zh` before final preview/draft handoff, prepares and automates WeChat Official Account article drafts/previews by default, and requires explicit approval before final publish.
- `小红书` may use `$cheat-on-content` for social-content scoring, blind prediction, benchmark learning, and retro loops; it uses `$humanizer-zh` before final note/publish copy, uses `$xhs-publish-assistant` for copy-ready publish bundles, and requires explicit approval before final posting.
- `测试` uses `$test-case-report-builder` for test case and test report artifacts.
- `QA` checks review/release readiness, blockers, and acceptance risk.
- `文档/交付` maintains the project documentation package across phases: requirements, quotes, contracts/service agreements, acceptance sheets, delivery checklists, operation guides, change confirmations, and handoff notes; it does not write code or replace legal/tax review.
- `知识库` organizes an Obsidian-style personal notes vault: inventories note clusters, proposes taxonomy and link maps, maintains WikiLinks/MOC/index notes and shareable Markdown when assigned, and preserves the user's personal voice and high-stakes boundaries; it does not delete, publish, edit `.obsidian` config, or convert personal notes into medical/financial/legal advice without explicit approval.
- `运维` investigates read-only first and avoids restarts, migrations, deletes, or production writes without explicit authorization.
- `安全` delegates to the matching security skill first, uses low-impact checks by default, and distinguishes evidence from suspicion.
