# Skill System Audit Dimensions

Load only the sections needed for the current finding. The deterministic audit establishes repository health; these questions support architecture judgment.

## 1. Trigger And Routing Quality

- Can a realistic user request discover the skill from its name and description?
- Does the description state both capability and trigger without listing unrelated domains?
- Does the skill overlap another public skill enough to create ambiguous routing?
- Do positive eval cases cover the intended trigger, and do negative cases expose over-routing?
- Is measured routing evidence available? If not, mark accuracy `not_evaluable`.
- Are callback hit, miss, and misfire fields complete enough for aggregation?

Prefer changing one owning description or route over copying trigger prose into several role prompts.

## 2. Role And Loop Boundaries

- Is there one durable owner for the outcome?
- Does the role own decisions while a skill owns reusable procedure?
- Is a new role actually necessary, or can an existing owner invoke the skill?
- Does the loop depth match task size and risk?
- Are total-control, owner, executor, QA, and callback responsibilities distinct?
- Does a script enforce repeated fields and enums that would be fragile in prose?

Keep project state in the project ledger. Shared skills contain reusable rules, templates, and validators.

## 3. Token And Context Cost

- Is the skill in Core because it is genuinely cross-domain, or merely convenient?
- Can detailed material move from `SKILL.md` into one scoped reference?
- Does the workflow repeatedly reread evidence that could be passed as a handle or short summary?
- Are multiple roles independently reconstructing the same context?
- Does the task need all enabled plugins, references, workers, and review layers?
- Can a deterministic script replace verbose prompt instructions or manual recounting?
- Does a long-running owner checkpoint decisions in commits, ledgers, PRs, or compressed handoffs before context pressure rises?

Count catalog characters as a stable guardrail, not an exact Token bill. Measure runtime selection separately.

## 4. Workflow Reliability

- Which failure mode does each instruction prevent?
- Is the requirement observable and testable?
- Could a missing field, invalid enum, duplicate ID, stale bundle, or skipped callback break the loop?
- Is fail-open behavior acceptable? If not, implement a validator or generator.
- Does the tool remain read-only by default and separate diagnosis from mutation?
- Are high-risk writes, publishing, production, and irreversible actions separately authorized?

Use Markdown for principles and ownership. Use scripts for schemas, fields, enums, aggregation, generation, and validation.

## 5. Packaging And Source Ownership

- Does every public skill belong to exactly one package?
- Is Core the only default package?
- Does each domain depend on Core without duplicating Core skills?
- Are canonical sources under `skills/`, with generated plugin copies byte-synchronized?
- Is provenance recorded as local, external GitHub, or Hermes-owned?
- Has an upstream adaptation preserved license and maintenance notes?
- Does the selected Core plus domain combination stay within the catalog target?

Never repair drift by editing `plugins/*/skills/` directly.

## 6. Lifecycle And Consolidation

- Is the skill still invoked, useful, and independently owned?
- Has its procedure been absorbed by another workflow?
- Is it a compatibility alias that should disable implicit invocation?
- Can two skills consolidate without broadening the surviving trigger beyond clarity?
- Does deprecation leave a migration route and remove stale registry/docs/package references?

Do not delete from one usage report. Look for repeated evidence, clear supersession, or structural duplication.

## 7. Documentation And Validation Drift

- Do README, role usage, technical highlights, source policy, registry, package registry, role cards, and generated bundles agree?
- Can a new machine install the required package and discover the skill in a new task?
- Do publication checks include the new deterministic validator?
- Are hard-coded counts and context metrics regenerated rather than guessed?
- Does the PR explain the causal problem, the chosen boundary, tests, and remaining limits?

Documentation should expose entry points and design intent. Put operational detail in one owning guide and link to it.

## Evidence Ladder

Use the strongest available evidence and label weaker levels:

1. Deterministic validator or reproducible test failure.
2. Observed runtime routing or recorded artifact.
3. Aggregated callbacks across several tasks.
4. Repeated user reports with concrete examples.
5. Single anecdote or model intuition.

Levels 4-5 can justify an experiment or eval case, not a claimed system-wide metric.
