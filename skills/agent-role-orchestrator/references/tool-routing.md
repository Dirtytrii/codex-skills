# Tool And Skill Routing

Read only the section relevant to the selected role. Script output provides structure; role judgment remains with the owner.

## Fail-Closed Scripts

| Need | Tool |
| --- | --- |
| Create/check `AGENTS.md` and `.codex/role-windows.md` | `ensure_project_role_files.py` |
| Generate a role prompt | `render_role_prompt.py` |
| Validate ledger, prompt, or callback | `validate_role_loop.py` |
| Inspect CodeGraph state | `check_codegraph.py` |
| Aggregate required/actual/misfire skill use | `aggregate_skill_hits.py` |

## Technical Routing

- Architecture/product/engineering/design/release method selection: `$gstack` and its focused methods.
- Bug or incident diagnosis: systematic debugging or the installed diagnosis workflow before fixing.
- Implementation: TDD where applicable, then verification before completion.
- UI with a visual reference: UI route selection before code; use rendered visual QA.
- Security: route by intent to the installed security scan, review, threat model, finding validation, or fix skill. Keep authorization explicit.
- Test assets/reports: `$test-case-report-builder`.
- Deployment: pre-deployment read-only evidence, then separately authorized execution and post-deployment verification.

## Content Routing

For public writing or publishing, read `content-routing.md`. Typical required skills include `$humanizer-zh`, platform-specific WeChat/Xiaohongshu skills, visual asset skills, and authorized browser automation.

## Knowledge And Delivery

- Knowledge-base role: use the user's vault/project conventions and place durable knowledge before editing.
- Document/delivery role: use the artifact-specific document, presentation, spreadsheet, or PDF skill when the output format requires it.
- Skill maintenance: use skill-authoring guidance, update registry/docs/tests, validate, sync local installation, and open a PR.

## Skill Ledger

Owner layer records candidate, required, optional, and skipped skills. Execution reports actual use, required-but-unused, newly discovered, misfires, and output-impacting skills. Aggregate artifacts with `aggregate_skill_hits.py`; do not tune routes from one anecdote.
