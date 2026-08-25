# Implicit Planning Contract

Use this reference only when designing or auditing owner-to-executor planning. Normal role prompts already receive the minimum contract from `render_role_prompt.py`; users do not need a slash command, a new role, or a separate public skill.

## Core Rule

Put judgment where it compounds, then hand bounded execution to the smallest reliable model. Plan once, reuse the same evidence handles, and keep ownership with the durable role.

The plan is an execution contract, not the final product. Delivery still requires implementation, independent verification where applicable, integration, callback, and final owner acceptance.

## Role Mapping

| Role | Planning responsibility | Must not absorb |
| --- | --- | --- |
| `总控 / CEO` | Decide value, success criteria, non-goals, owner, budget, risk, and planning depth. | Codebase recon, technical steps, implementation, or diff review. |
| `架构 / CTO` | Run scoped Recon and Vet, compare routes, and produce the technical implementation spec. | Routine implementation or automatic whole-repo audit. |
| `开发负责人 / Dev Lead` | Check the spec against current code, compile one-shot executor cards, integrate, re-run verification, and commit. | Repeating the whole audit or giving final integration ownership to a cheap worker. |
| `开发执行 subagent` | Run drift check, execute one bounded card, verify, and report. | Architecture changes, scope growth, integration, final validation, or commit ownership. |
| `QA` | Review the current delivery/change and direct impact surface, try to falsify readiness, and report evidence. | Writing the implementation plan or silently repairing code. |

## Automatic Depth

| Task size | Minimum planning output |
| --- | --- |
| `tiny` | Route-only: objective, success condition, and stop line. No repository audit. |
| `small` | Outcome/task brief: narrow scope, validation, and escalation condition. |
| `medium` | Owner contract: goals, non-goals, evidence, scope, validation, risk, and callback. |
| `large` | Implementation spec plus, when delegation is permitted, bounded executor cards and integration order. |
| `critical` | Large contract plus independent gates, rollback/failure conditions, unresolved risk, and go/no-go owner. |

Task size does not authorize a full repository or nine-category audit. Broad audit, roadmap discovery, or branch-wide improvement review must be explicit in the objective.

## Scoped Recon And Vet

CTO planning uses two evidence passes:

1. `Recon`: read only the relevant repository structure, conventions, intent/decision docs, current implementation, and exact build/test/lint commands.
2. `Vet`: personally re-open every load-bearing location before it enters the spec; remove duplicates, wrong attributions, and behavior already accepted by an ADR or explicit decision.

Do not make every worker repeat Recon. Store paths, symbols, commits, tests, and short load-bearing excerpts once, then reuse those handles.

## Zero-Context Executor Card

A one-shot executor card contains only what a worker with no chat history needs:

- objective and why it matters;
- planned-at commit and drift-check command;
- current-state evidence and applicable local convention;
- exact in-scope files and explicit out-of-scope files/actions;
- ordered steps, each with a verification command and expected result;
- required tests and done criteria;
- task-specific STOP conditions;
- fixed completion report and callback target.

Inline short code only when it carries a decision or when an isolated worker cannot read an uncommitted artifact. Prefer file/symbol/test handles over large excerpts.

## Drift And STOP Gates

Before editing, compare the planned-at commit with current `HEAD` for in-scope paths. Stop and return to Dev Lead when:

- relevant code no longer matches the planned state;
- a required step needs an out-of-scope file or architectural decision;
- the named validation command is unavailable or fails twice after a reasonable local correction;
- a load-bearing assumption is false;
- risk grows beyond the assigned executor tier.

The worker reports the observation; it does not improvise around the gate.

## Artifact And Token Policy

- Do not create a persistent plan file for routine `tiny` or `small` work.
- For multi-session `large` or `critical` work, reuse the project's existing planning location; when none exists, `.codex/plans/` is the default local artifact directory.
- Reuse one contract across CTO, Dev Lead, executor, and QA. Pass deltas and evidence handles instead of rewriting the full plan in every callback.
- Treat long-running work as a continuity concern: use checkpoints, commits, and compressed handoff when it may cross the current context or includes slow staged validation. Duration alone does not authorize a subagent.
- Default to serial execution. Parallel workers require disjoint write scope, no shared evolving state, independent validation, and an explicit `required` delegation policy.
- Load `gstack-spec` only for fuzzy intent, and `gstack-autoplan` or plan-review adapters only when the stated cross-domain review actually needs them.

## Upstream Method Note

This contract adapts planning ideas from [shadcn/improve](https://github.com/shadcn/improve) (MIT): capable-model codebase understanding and specification, self-contained executor plans, verification gates, drift checks, and STOP conditions. This repository does not vendor its slash-command workflow, automatic multi-category audit, executor runtime, or `plans/` backlog behavior.
