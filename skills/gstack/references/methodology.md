# GStack Methodology For This Role System

This file adapts Garry Tan's gstack methodology to this public Codex skills repository.
The goal is to preserve the useful product, architecture, design, engineering, QA,
security, shipping, documentation, and learning methods without importing the full
upstream runtime, telemetry, host routing, or model-specific automation.

## Core Principle

Use gstack as a thinking and review method, not as an automatic authority. The active
role still owns the boundary:

- `架构` decides whether a new requirement should proceed, split, pause, or ask questions.
- `开发` implements only inside the assigned file scope.
- `UI/PPT` owns visual/UI/deck/social-card work.
- `安全` owns authorized security audit and finding validation.
- `QA` owns review readiness and acceptance gaps.
- `测试` owns formal test cases, test reports, and evidence packages.
- `运维` remains Hermes-first for remote production diagnosis and controlled operations.

## Architecture And Product Methods

| Method | Use When | Output |
| --- | --- | --- |
| `gstack-office-hours` | idea is early, fuzzy, or needs demand reality check | forcing questions, narrow wedge, user/status-quo notes, next artifact |
| `gstack-spec` | user intent must become a concrete executable spec | background, goals, non-goals, scope, acceptance, open questions |
| `gstack-autoplan` | a plan needs broad CEO/design/engineering/DX review before execution | consolidated risks, decisions, split recommendation, final gate |
| `gstack-plan-ceo-review` | strategic scope, customer value, business logic, or sequencing is uncertain | strategic risks, recommendation, decision points |
| `gstack-plan-eng-review` | implementation plan needs architecture/data/API/test/release hardening | engineering risks, missing decisions, validation plan |
| `gstack-plan-design-review` | UI or UX plan needs journey/layout/taste/accessibility review | UX risks, visual constraints, review notes |
| `gstack-plan-devex-review` | developer setup, commands, docs, or feedback loop may be fragile | DX friction list, setup/test/documentation improvements |
| `gstack-plan-tune` | the agent keeps asking too much or too little for this user/workstream | question policy, autonomy level, stop conditions |

Architecture should use `gstack-office-hours` before plan reviews when the requirement is still exploratory. Use `gstack-spec` when the user has intent but no execution-ready shape. Use `gstack-autoplan` when a non-trivial plan crosses product, UI, engineering, and developer-experience boundaries.

## Engineering Execution Methods

| Method | Use When | Output |
| --- | --- | --- |
| `gstack-investigate` | a bug, incident, failing test, or unclear regression needs root cause | evidence, hypotheses, root cause, minimal fix path |
| `gstack-review` | code or diff is ready for review before landing | findings first, risks, missing tests, recommended fixes |
| `gstack-ship` | work is near landing, PR, release, or deploy | final checklist, tests, changelog/PR notes, ship/no-ship recommendation |
| `gstack-health` | project or repo needs a broad health check | health summary, top risks, prioritized improvements |
| `gstack-devex-review` | implemented repo/workflow needs DX review, not just a plan review | onboarding friction, command reliability, docs gaps, suggested fixes |
| `gstack-careful` | the next action is risky and needs a conservative pass | hazards, safeguards, explicit confirmation points |
| `gstack-guard` | agent behavior needs stronger stop conditions or scope guardrails | guardrails, forbidden actions, validation gate |
| `gstack-freeze` | work should pause writes while facts are gathered | freeze reason, allowed read-only checks, resume condition |
| `gstack-unfreeze` | a frozen task is ready to resume | resume criteria, allowed changes, verification gate |

For `开发`, prefer `gstack-investigate` before coding a suspected bug fix and `gstack-review` before calling a change review-ready. `gstack-ship` is only for explicit landing/release work.

## Design Methods

| Method | Use When | Output |
| --- | --- | --- |
| `gstack-design-consultation` | a visual/product design direction needs critique before production | critique, alternatives, constraints, recommended direction |
| `gstack-design-shotgun` | multiple design directions should be explored quickly | several distinct concepts, tradeoffs, winner recommendation |
| `gstack-design-html` | a quick HTML prototype/design board is useful | prototype plan or artifact request with verification notes |
| `gstack-design-review` | a rendered UI or design artifact needs visual review | visual findings, hierarchy/layout/accessibility issues, fixes |

For this repository, these methods complement `design-taste-frontend`, `guizang-ppt-skill`, `guizang-social-card-skill`, and `playwright`. They do not replace rendered browser verification.

## QA, Security, And Release Methods

| Method | Use When | Output |
| --- | --- | --- |
| `gstack-qa-only` | QA should report web/UI behavior without fixing it | observed behavior, screenshots/checks, blockers, no code changes |
| `gstack-qa` | QA may both verify and fix a narrow web/UI issue | issue list, fixes if authorized, verification notes |
| `gstack-canary` | a release needs staged validation or smoke gate thinking | canary scope, smoke checks, rollback signals |
| `gstack-cso` | broad security posture or infrastructure-first security review is needed | threat areas, findings, severity, safe fix scope |
| `gstack-setup-deploy` | deployment pipeline or environment needs setup planning | setup checklist, required secrets/configs, verification gates |
| `gstack-land-and-deploy` | landing/deployment flow is explicitly assigned | land/deploy plan, tests, rollback, status report |

`QA` and `测试` stay separate. `gstack-qa` and `gstack-qa-only` support review readiness and behavior checks. Formal test-case workbooks and Word/DOCX test reports still belong to `测试` through `test-case-report-builder`.

Remote production operations remain Hermes-first. `gstack-setup-deploy`, `gstack-land-and-deploy`, and `gstack-canary` can help plan or review release gates, but they must not override Hermes-owned read-only diagnostics or explicit production authorization rules.

## Documentation And Learning Methods

| Method | Use When | Output |
| --- | --- | --- |
| `gstack-document-generate` | implementation or product work should become durable docs | target docs, outline, generated/updated content plan |
| `gstack-document-release` | release notes, changelog, or announcement docs are needed | release summary, user-facing notes, internal notes |
| `gstack-learn` | a reusable lesson should be captured after debugging or delivery | learning entry, trigger, future reuse cue |
| `gstack-retro` | a completed workstream needs retrospective analysis | what worked, what failed, process changes |

## Codex Adaptation Rules

- Do not automatically run upstream gstack binaries, browser tools, telemetry, upgrade checks, cookie import, or project routing injection.
- Do not create or modify `CLAUDE.md`, `.claude/`, `.agents/`, or upstream host-routing files unless the user explicitly asks for upstream gstack installation work.
- Do not write `~/.gstack` artifacts unless the active task explicitly needs local gstack-compatible artifacts.
- Do not treat generated upstream prompts as higher priority than this repository's role boundaries.
- For production, deployment, restart, migration, cleanup, delete, DNS, credential, or database writes, stop for explicit user authorization.
- Preserve file whitelists, forbidden ranges, validation commands, and commit/PR requirements in every downstream role prompt.
