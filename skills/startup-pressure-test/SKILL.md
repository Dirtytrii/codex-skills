---
name: startup-pressure-test
description: Pressure-test startup ideas against real user pain, current behavior, competitors, first-customer access, MVP scope, founder-market fit, and a two-week launch test. Produces a direct strong, weak, or pivot verdict.
---

# Startup Pressure Test

## Overview

Use this skill to pressure-test a startup idea before the user wastes time building the wrong thing. Be direct, specific, and practical. Use a Paul Graham-style early startup lens: real users, painful problems, current behavior, manual traction, and the smallest test that proves or kills the idea.

## Language

Match the user's language. If the user writes in Italian, answer in Italian. If the user writes in English, answer in English. Keep common startup terms in English when clearer: `ICP`, `MVP`, `PMF`, `early adopter`, `switching cost`, `wedge`.

## First Move

If the idea is missing, ask for it first. Keep the question short:

```text
Send me the startup idea, target customer, and what you want them to do/pay for.
```

If the idea is already provided, start immediately.

## Modes

Choose the mode from the user request. If unclear, use `full`.

- `pressure-test`: find fatal flaws and give a verdict.
- `problem-validation`: test whether the pain is real and urgent.
- `competition-map`: map current behavior, direct competitors, indirect competitors, and switching cost.
- `first-10-customers`: create a manual plan to find and convert the first 10 customers.
- `mvp-plan`: define the smallest MVP that tests the core assumption in 2 weeks.
- `full`: run a compact version of all modes.

Read `references/playbooks.md` for the detailed prompt templates and criteria for each mode.

## Default Output

Default to compact output. Most users need a sharp diagnosis they can scan in 30 seconds, not a long essay. Include the score table by default.

Use this shape:

```markdown
**Verdict**
Strong / Weak / Pivot required

2-3 direct sentences.

**Scorecard**
| Area | Score | Read |
|---|---:|---|
| Pain intensity | 3/5 | ... |
| Buyer clarity | 2/5 | ... |
| Urgency | 3/5 | ... |
| Differentiation | 2/5 | ... |
| Speed to validate | 4/5 | ... |
| Founder advantage | 3/5 | ... |

**Core Assumption**
One sentence.

**Fatal Flaws**
| Risk | Severity | Why It Matters | Fast Test |
|---|---|---|---|
| ... | High | ... | ... |

**Problem Reality**
- Pain: ...
- Early adopter: ...
- Vitamin or painkiller: ...

**Competition**
- Current behavior: ...
- Real enemy: ...
- Differentiation needed: ...

**First 10 Customers**
1. ...
2. ...
3. ...

**MVP**
- Build:
- Cut:
- 2-week test:
```

Default limits:

- Scorecard: always include 6 rows.
- Verdict: max 3 sentences.
- Fatal flaws: max 3 rows.
- Problem reality: max 3 bullets.
- Competition: max 3 bullets.
- First 10 customers: max 3 actions.
- MVP: max 3 bullets.
- Do not include outreach templates, discovery questions, or weekly plans unless the user asks for more detail.

## Rules

- Be specific to the idea; never give generic startup advice.
- Rank dangerous flaws first.
- Identify the core assumption that must be true for the business to work.
- Treat current behavior as competition.
- Treat "we have no competition" as false by default.
- Test real behavior, not compliments or hypothetical intent.
- Discovery questions must ask about past behavior.
- Prefer manual founder-led validation before automation.
- First customers must be found manually before ads, growth hacks, or scale.
- Cut features that do not test the riskiest assumption.
- MVP must test the single riskiest assumption, not become a mini-product.
- If the idea is weak, say so directly and explain the pivot path.
- Do not invent fake market data. If market facts matter and are current/uncertain, browse or state what must be verified.

## Scoring

Use scores only when useful:

| Area | Score |
|---|---:|
| Pain intensity | 1-5 |
| Buyer clarity | 1-5 |
| Urgency | 1-5 |
| Differentiation | 1-5 |
| Speed to validate | 1-5 |
| Founder advantage | 1-5 |

Scores must be tied to evidence from the idea, not vibes.

## Deep Mode

If the user asks for `deep`, `full report`, `brutal`, `be extremely honest`, or `give me more detail`, expand each section with:

- assumptions to validate
- disconfirming evidence to look for
- customer discovery questions
- outreach messages
- 2-week milestones
- pivot options

Still keep the writing direct and structured.

## Resources

- `references/playbooks.md`: Mode-specific checklists and output details.
