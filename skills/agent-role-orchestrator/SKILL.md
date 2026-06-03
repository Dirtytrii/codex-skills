---
name: agent-role-orchestrator
description: Create concise role-specific Codex window prompts and current-window handoffs with an architecture-first gateway and role-window registry. Use when the user asks for an architecture/development/UI-PPT/video/ops/security/testing/QA window, says to inherit/reset/continue the current role, asks for the next-window prompt, wants a requirement routed through architecture before deciding whether to open other role windows, wants existing roles reused instead of recreated, wants testing test-case/report prompts, or wants security-audit prompts that delegate to the appropriate security skill.
---

# Agent Role Orchestrator

## Purpose

Turn fuzzy collaboration intent into a copy-paste prompt for the next Codex window, with a clear role, context, boundaries, validation plan, and reporting contract.

Use this skill to:
- bootstrap a new role window, usually `架构` first;
- summarize the current thread so a next window can inherit a role;
- let `架构` decide whether to open `开发`, `UI/PPT`, `视频`, `运维`, `安全`, `测试`, or `QA` windows;
- remember whether each role has already been established and reuse it by default;
- rewrite a project-specific role prompt into a reusable role template.
- route `安全` work to the right existing security skill by default.
- route `测试` test-case/report work to the test artifact skill by default.

## Architecture-First Rule

For one new requirement, default to one `架构` window first. Do not directly split the requirement into several role windows just because the user names possible roles.

Only output multiple downstream role prompts when one of these is true:
- the user says `架构已经决定`, `按这个架构拆`, or provides an accepted architecture split;
- the current thread is already acting as `架构` and has enough evidence to choose downstream roles;
- the user explicitly overrides the gateway and asks to bypass `架构`.

When the user asks for `开发`, `UI/PPT`, `视频`, `运维`, `安全`, `测试`, or `QA` prompts without an architecture decision, either produce a `架构` prompt first or clearly mark the downstream prompt as `待架构确认`.

## Role-Window Registry Rule

Treat role windows as persistent per project/workstream.

Default lifecycle:
- first time a role is needed: create the role prompt and mark it as established;
- after a role is established: do not create another same-role window by default;
- when the same role needs fresh context, output an inheritance/continuation prompt for the existing role;
- create numbered parallel roles only when the user or `架构` explicitly asks for them, such as `开发1号`, `开发2号`, `UI/PPT1号`;
- if existing-role state is unknown, ask for or reconstruct the role registry before generating same-role prompts.

Maintain this registry in architecture handoffs when possible:

```text
【角色窗口台账】
- 架构：已建立 / 未建立 / 待确认
- 开发：已建立 / 未建立 / 待确认；实例：开发1号、开发2号...
- UI/PPT：已建立 / 未建立 / 待确认
- 视频：已建立 / 未建立 / 待确认
- 运维：已建立 / 未建立 / 待确认
- 安全：已建立 / 未建立 / 待确认
- 测试：已建立 / 未建立 / 待确认
- QA：已建立 / 未建立 / 待确认
```

Use `新建` only for first establishment or explicit parallel instances. Use `继承` / `接续` for resets, context refreshes, and ongoing work in an existing role.

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
- 运维 / deployment / production verification;
- 安全;
- 测试 / test cases / test report;
- QA / review / 验收.

For `安全`, always include the relevant downstream security skill in the generated prompt:
- public site, black-box, exposed JS/API, login protection, CORS, headers, or penetration-style report: `$authorized-blackbox-web-security`;
- repository-wide or scoped-path code security scan: `$codex-security:security-scan`;
- PR, branch, commit, or working-tree security review: `$codex-security:security-diff-scan`;
- deep repository scan: `$codex-security:deep-security-scan`;
- fix a validated or plausible security finding: `$codex-security:fix-finding`.

For role tools sourced from external GitHub skills, name them as dependencies instead of treating them as local role logic:
- `UI/PPT` landing/redesign/frontend taste work: `$design-taste-frontend`;
- `UI/PPT` web PPT / Swiss deck / magazine deck work: `$guizang-ppt-skill`;
- browser UI verification, rendered frontend checks, and E2E-like flows: `$playwright`;
- `测试` test cases, Excel workbook, Word/DOCX test report, or formal testing artifact package: `$test-case-report-builder`.

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
- relevant docs named by the user;
- relevant changed files or recent test output.

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

提交/PR 要求：
...

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
使用 $agent-role-orchestrator，给我视频窗口。
```

```text
使用 $agent-role-orchestrator，给我测试窗口。
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
- existing role windows are inherited/continued by default instead of recreated;
- numbered parallel roles appear only when explicitly requested or selected by `架构`;
- downstream role prompts include file scope, forbidden scope, validation, and commit/report expectations by default.
- `安全` prompts explicitly invoke the appropriate security skill instead of duplicating that workflow.
- `测试` prompts for test cases or test reports explicitly invoke `$test-case-report-builder`.
- `QA` prompts stay focused on review readiness, acceptance risk, and blocker verification; they do not own test-case/report authoring by default.
- role prompts distinguish external GitHub skills from local-owned skills when that affects maintenance or self-editing.

## Common Defaults

Use these defaults unless the user says otherwise:
- `架构` clarifies requirements, maintains the role-window registry, and decides whether downstream windows are needed; it does not code or commit.
- `开发` implements within a narrow file scope, runs tests, and commits when asked or when workspace instructions require it.
- `UI/PPT` and `视频` produce visible artifacts and perform visual verification.
- `测试` uses `$test-case-report-builder` for test case and test report artifacts.
- `QA` checks review/release readiness, blockers, and acceptance risk.
- `运维` investigates read-only first and avoids restarts, migrations, deletes, or production writes without explicit authorization.
- `安全` delegates to the matching security skill first, uses low-impact checks by default, and distinguishes evidence from suspicion.
