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

## Bundled Reference Loader

Focused methods are stored at `references/skills/<name>/REFERENCE.md`. They are ordinary references, not independently discoverable skills.

- Choose one method from the tables below and read only that bundle.
- Resolve scripts, nested references, and assets relative to the selected bundle directory.
- Load another bundle only for an explicit handoff or a separate task phase.
- Record the method name in the skill ledger exactly as before; progressive loading changes discovery, not audit semantics.

### GStack methods

| Role or need | Bundled methods |
| --- | --- |
| CEO/product pressure | `gstack-office-hours`, `gstack-plan-ceo-review` |
| Specification and broad plan review | `gstack-spec`, `gstack-autoplan` |
| Focused plan review | `gstack-plan-eng-review`, `gstack-plan-design-review`, `gstack-plan-devex-review`, `gstack-plan-tune` |
| Investigation and implementation review | `gstack-investigate`, `gstack-review`, `gstack-health`, `gstack-devex-review` |
| Landing and release | `gstack-ship`, `gstack-canary`, `gstack-setup-deploy`, `gstack-land-and-deploy` |
| Risk containment | `gstack-careful`, `gstack-guard`, `gstack-freeze`, `gstack-unfreeze` |
| Design | `gstack-design-consultation`, `gstack-design-shotgun`, `gstack-design-html`, `gstack-design-review` |
| QA and security | `gstack-qa-only`, `gstack-qa`, `gstack-cso` |
| Documentation and learning | `gstack-document-generate`, `gstack-document-release`, `gstack-learn`, `gstack-retro` |

Keep `$gstack` as the public router. Once it chooses a focused method, load `references/skills/<method>/REFERENCE.md` here.

### Content and platform methods

| Need | Bundled reference |
| --- | --- |
| Separate raw model drafting from editor acceptance | `content-model-handoff` |
| Learn durable style rules from user edits | `content-style-calibration-loop` |
| Remove README/launch-event tone from social copy | `social-text-websense-gate` |
| WeChat AI application workflow and draft operations | `wechat-ai-app-ops` |
| First-pass WeChat technical research and drafting | `wechat-tech-writer` |
| Markdown-to-WeChat HTML formatting | `wechat-article-formatter` |
| Xiaohongshu comment research | `xhs-comment-research` |
| Xiaohongshu visual direction | `xhs-visual-director` |
| Copy-ready Xiaohongshu publish package | `xhs-publish-assistant` |
| Authorized Xiaohongshu browser automation | `xhs-automation-publisher` |
| Xiaohongshu short-video package | `xhs-short-video-workflow` |

### Operations and diagnosis methods

| Need | Bundled reference |
| --- | --- |
| Generic application incident evidence | `application-problem-diagnosis-workflow` |
| Uploaded package/update comparison | `package-update-check-and-plan` |
| Pre-deployment read-only gate | `pre-deployment-readonly-checklist` |
| Post-deployment read-only verification | `post-deployment-readonly-verification` |
| Hermes cron succeeds but output is empty | `hermes-cron-empty-output-diagnosis` |
| Hermes cron interpreter/wrapper mismatch | `hermes-python-script-wrapper-for-shell-cron` |
| Proxy-dependent Python behavior | `proxy-dependent-python-service-diagnosis` |
| Python deployment startup/dependency/readiness failures | `python-project-deployment-troubleshooting` |

## Technical Routing

- Architecture/product/engineering/design/release method selection: `$gstack`, then one focused bundled method.
- Bug or incident diagnosis: load the smallest matching bundled diagnosis workflow before fixing.
- Implementation: TDD where applicable, then verification before completion.
- UI with a visual reference: UI route selection before code; use rendered visual QA.
- Security: route by intent to the installed security scan, review, threat model, finding validation, or fix skill. Keep authorization explicit.
- Test assets/reports: `$test-case-report-builder`.
- Deployment: load the pre-deployment bundle for read-only evidence, keep execution separately authorized, then load post-deployment verification.

## Content Routing

For public writing or publishing, read `content-routing.md`, then load only the matching platform/content bundle. Standalone `$humanizer-zh` and visual asset skills remain separate when needed.

## Knowledge And Delivery

- Knowledge-base role: use the user's vault/project conventions and place durable knowledge before editing.
- Document/delivery role: use the artifact-specific document, presentation, spreadsheet, or PDF skill when the output format requires it.
- Skill maintenance: use skill-authoring guidance, update registry/docs/tests, validate, sync local installation, and open a PR.

## Skill Ledger

Owner layer records candidate, required, optional, and skipped skills. Execution reports actual use, required-but-unused, newly discovered, misfires, and output-impacting skills. Aggregate artifacts with `aggregate_skill_hits.py`; do not tune routes from one anecdote.
