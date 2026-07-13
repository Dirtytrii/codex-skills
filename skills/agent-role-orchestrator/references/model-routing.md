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

No route uses `max`; the highest supported recommendation is `xhigh`.

## One-Shot Development Executors

| Tier | Model | Boundary |
| --- | --- | --- |
| `mechanical` | `gpt-5.4-mini` + `high` | One deterministic file/change, complete spec, explicit test. |
| `bounded` | `gpt-5.6-luna` + `high` | Narrow semantic task with clear file ownership and independent validation. |
| `semantic` | `gpt-5.6-terra` + `high` | Limited business semantics or a few related files; Dev Lead still integrates. |
| `high-risk` | `gpt-5.6-sol` + `xhigh` | Not delegated to a cheap worker; Dev Lead owns it directly. |

Use `--executor-tier mechanical|bounded|semantic|high-risk`. The worker is an in-window one-shot subagent, not a durable role thread.

## Spark Opportunity Lane

`gpt-5.3-codex-spark` is an opportunistic preview lane alongside the stable tiers. OpenAI currently describes it as a text-only, 128K, real-time coding model with a separate preview rate limit that may change with demand; credit rates are not final. Source: [Introducing GPT-5.3-Codex-Spark](https://openai.com/index/introducing-gpt-5-3-codex-spark/).

Select it only when all are true:

- the task is a `mechanical` or `bounded` one-shot development executor;
- current Spark availability/quota is explicitly confirmed;
- scope is short, text-only, and independently verifiable;
- the task card names the validation command and requires its result.

Use `--prefer-spark --spark-available`. Without confirmed availability, the generator falls back to Mini/Luna. Spark is forbidden for owner, semantic integration, high-risk, critical, architecture, final QA, and long-context work.

## Parallel Profile

Default: `serial`, one worker.

Parallel work is allowed only when each task has disjoint file/surface ownership and independent validation. Two workers are the normal ceiling. Three to five workers require an explicit profile and are justified only by genuinely independent work, not by task size alone.

```bash
python scripts/render_role_prompt.py \
  --role 开发 \
  --objective "实现三个独立适配器" \
  --source-role 架构 \
  --execution-profile parallel \
  --worker-count 3 \
  --disjoint-scope "每个 worker 一个独立目录" \
  --independent-validation "每个目录有独立测试命令"
```

Fail closed when scope overlaps, workers need shared evolving state, validation is only global, or the Dev Lead cannot review/integrate every result.

## Fallback

If the recommended model is unavailable, record the actual model and reason. Prefer reducing scope or upgrading ownership over silently substituting a weaker durable owner. User model choices always take precedence.
