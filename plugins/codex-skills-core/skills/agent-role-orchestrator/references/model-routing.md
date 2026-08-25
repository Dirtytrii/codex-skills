# Model Routing

Read this file only when selecting, overriding, or auditing a role model. These are recommendations, not proof that a model is available in the current product surface.

## Durable Windows

| Role | Default | Escalate |
| --- | --- | --- |
| 总控 / CEO | `gpt-5.6-terra` + `high` | Funds, launch, production recovery, or final cross-role go/no-go: Sol/xhigh. |
| 架构 / CTO | `gpt-5.6-sol` + `high` | Live architecture, incident root cause, DB/concurrency/security, irreversible design: xhigh. |
| 开发负责人 | `gpt-5.6-terra` + `high` | Funds, ledger, PnL/fee, concurrency, repeated failed correction: Sol/xhigh. |
| QA | `gpt-5.6-terra` + `high` | Critical PR, adversarial release gate, production readiness: Sol/xhigh. |
| 运维 / DBA | `gpt-5.6-terra` + `high` | Deploy/restart/rollback/incident, DDL/cleanup/recovery/data risk: Sol/xhigh. |
| 内容主编 / 知识库 / 技能维护 / 文档 | `gpt-5.6-terra` + `high` | High-risk public claims or cross-role irreversible decisions: Sol/xhigh. |

Automatic routes intentionally stop at `xhigh`. Some current Codex surfaces may expose `Max` or `Ultra` for eligible models/accounts; never auto-select them. Use one only after explicit user choice, current-surface availability confirmation, and a representative eval showing that the added cost improves the target task.

## Reasoning Effort Eval Gate

`high` is the current operational baseline, not proof that every task needs it. Before lowering a durable default, compare the current route with one lower supported reasoning level on the same representative tasks and prompt contract.

Record completion correctness, required validation, tool calls, retries, correction loops, output tokens, and latency when available. Change the default only when the lower level preserves completion and safety across the representative set; keep `xhigh` for the explicit escalation conditions above. Do not raise or lower reasoning from intuition alone.

## One-Shot Development Executors

| Tier | Model | Boundary |
| --- | --- | --- |
| `mechanical` | `gpt-5.6-luna` + `high` | One deterministic file/change, complete spec, explicit test. |
| `bounded` | `gpt-5.6-luna` + `high` | Narrow semantic task with clear file ownership and independent validation. |
| `semantic` | `gpt-5.6-terra` + `high` | Limited business semantics or a few related files; Dev Lead still integrates. |
| `high-risk` | `gpt-5.6-sol` + `xhigh` | Not delegated to a cheap worker; Dev Lead owns it directly. |

Use `--executor-tier mechanical|bounded|semantic|high-risk`. The worker is an in-window one-shot subagent, not a durable role thread.

This matrix uses Luna as the stable cost-sensitive lane. OpenAI describes it for high-volume, cost-sensitive workloads; product-surface availability and membership-credit accounting are separate concerns and must be checked at runtime. Source: [GPT-5.6 Luna](https://developers.openai.com/api/docs/models/gpt-5.6-luna).

## Delegation Contract

Use `--delegation-policy auto|forbidden|optional|required` on development cards:

- `forbidden`: Dev Lead implements directly. Task-specific “no subagent”, critical/extreme risk, and `high-risk` tier override generic cost-saving advice.
- `optional`: a serial Dev Lead may delegate only when it can isolate one short leaf task with an exact write scope, validation, and STOP gate. If it does not delegate, report why.
- `required`: at least one eligible one-shot executor must be used. Explicit mechanical/bounded/semantic tiers and any parallel profile require this policy; fail closed if no eligible leaf exists.
- `auto`: resolves to the three rules above and prints the effective policy in the prompt.

Long-running means the work is likely to cross the current interaction/context boundary or includes slow staged validation. It triggers task cards, checkpoints, commits, or compressed handoff; duration alone never makes work delegable or parallel.

Generating a card does not create a worker. The Dev Lead must explicitly create the one-shot subagent with the recommended model/thinking when the runtime supports overrides. Every development callback reports whether delegation happened, actual model/thinking, task-card or evidence handle, retries/rework, and Dev Lead revalidation. Model availability is checked at execution time; substitutions are recorded rather than silently assumed.

## Spark Opportunity Lane

`gpt-5.3-codex-spark` is an opportunistic preview lane alongside the stable tiers. OpenAI currently describes it as a text-only, 128K, real-time coding model with a separate preview rate limit that may change with demand; credit rates are not final. Source: [Introducing GPT-5.3-Codex-Spark](https://openai.com/index/introducing-gpt-5-3-codex-spark/).

Select it only when all are true:

- the task is a `mechanical` or `bounded` one-shot development executor;
- current Spark availability/quota is explicitly confirmed;
- scope is short, text-only, and independently verifiable;
- the task card names the validation command and requires its result.

Use `--prefer-spark --spark-available`. Without confirmed availability, the generator falls back to Luna. Spark is forbidden for owner, semantic integration, high-risk, critical, architecture, final QA, and long-context work.

## Parallel Profile

Default: `serial`, one worker.

Parallel work is allowed only when each task has disjoint file/surface ownership, no shared evolving state, and independent validation. Two workers are the normal ceiling. Three to five workers require an explicit profile and are justified only by genuinely independent work, not by task size or duration alone. Parallel always requires `--delegation-policy required`.

```bash
python scripts/prepare_role_window.py \
  --role 开发 \
  --objective "实现三个独立适配器" \
  --source-role 架构 \
  --delegation-policy required \
  --execution-profile parallel \
  --worker-count 3 \
  --disjoint-scope "每个 worker 一个独立目录" \
  --independent-validation "每个目录有独立测试命令"
```

Fail closed when scope overlaps, workers need shared evolving state, validation is only global, or the Dev Lead cannot review/integrate every result.

## Fallback

If the recommended model is unavailable, record the actual model and reason. Prefer reducing scope or upgrading ownership over silently substituting a weaker durable owner. User model choices always take precedence.
