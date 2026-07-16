# Tool And Skill Routing

Read only the section relevant to the selected role. Script output provides structure; role judgment remains with the owner.

## Fail-Closed Scripts

| Need | Tool |
| --- | --- |
| Create/check `AGENTS.md` and `.codex/role-windows.md` | `ensure_project_role_files.py` |
| Check required plugins and generate a role prompt | `prepare_role_window.py` |
| Render a prompt after plugin preflight | `render_role_prompt.py` |
| Validate ledger, prompt, or callback | `validate_role_loop.py` |
| Inspect CodeGraph state | `check_codegraph.py` |
| Aggregate required/actual/misfire skill use | `aggregate_skill_hits.py` |

## Technical Routing

- Architecture/product/engineering/design/release method selection: `$gstack` and its focused methods.
- UI/Frontend implementation: load `$ui-implementation-workflow`; classify, bound active references, keep the complete source inventory and switch ledger, extract design rules, build skeleton-first, then repair 1440/768/390 screenshots and replace only the failed reference role when needed. Load its visual-direction reference only for expressive marketing/brand/portfolio/content work; do not run `$design-taste-frontend` as a second workflow. Ignore inherited aesthetic preferences and record fresh explicit screenshot feedback in `.codex/ui-visual-review-signals.md` as raw evidence.
- Browser interaction: load `$browser-automation-router`; use the in-app Browser for public/local visual work, Chrome for an approved existing login/profile, and `$playwright` only for deterministic CLI/CI runs or an explicit fallback.
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
