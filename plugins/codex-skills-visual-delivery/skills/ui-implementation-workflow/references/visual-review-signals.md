# Visual Review Signals

Use this reference to restart visual-review learning after the UI workflow change. These records are raw review evidence, not an active aesthetic preference profile.

## Reset Boundary

- Start the revised workflow with no inherited aesthetic preference.
- Do not import defaults, prohibitions, scores, or taste judgments from the old `design-taste-frontend` workflow.
- Preserve old records when they exist, but do not use them for routing or design decisions.
- A record without `workflow: ui-implementation-workflow-v2` belongs to the old baseline.
- Brand guidelines, accessibility requirements, existing design tokens, and explicit task constraints are project evidence, not aesthetic preferences; continue to honor them.

## Project Record

When a user or designated reviewer gives explicit feedback on rendered UI, append a fresh entry to `.codex/ui-visual-review-signals.md`. If the file already contains old data, keep it and begin a new section headed `## ui-implementation-workflow-v2`.

```text
workflow: ui-implementation-workflow-v2
status: raw
task:
page/surface:
screenshot or artifact:
reviewer:
decision: accepted | rejected | mixed
accepted aspects:
rejected aspects:
reason in reviewer words:
scope: this surface | this project | candidate cross-project signal
recorded at:
```

Record only feedback that was actually stated or clearly tied to an acceptance decision. Do not infer preference from silence, a merged PR, lack of requested changes, or the agent's own taste.

## Use During The Reset Period

- Apply explicit feedback to the current task and affected surface.
- Keep future records as `raw`; do not automatically convert them into global defaults.
- Do not rank, score, or summarize a personal aesthetic profile.
- Do not reuse a raw signal across projects unless the user explicitly confirms that scope.
- When feedback conflicts, preserve both entries and ask for a decision only if the conflict blocks the current task.

If persistent preference routing is re-enabled later, synthesize only repeated explicit signals and ask the user to approve the proposed profile before it affects future work.
