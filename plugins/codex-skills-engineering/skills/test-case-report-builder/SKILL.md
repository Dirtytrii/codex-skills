---
name: test-case-report-builder
description: Create or update project test-case assets and test reports. Use when Codex is asked to generate test cases in Excel, produce a Word/DOCX test report, summarize automated test execution, turn repository tests into a formal testing artifact, or沉淀/复用 a project testing documentation workflow.
---

# Test Case Report Builder

## Purpose

Build a reusable testing documentation package for a software project: an Excel workbook containing business test cases and automated-test indexes, plus a Word test report summarizing scope, execution evidence, risks, and release recommendations.

Use the repository's real modules, tests, docs, and commands. Do not invent a passing status for tests that were not run.

## Core Workflow

1. **Read project context first**
   - Check repo docs such as `README`, `docs/TESTING.*`, product/business docs, CI config, `package.json`, `pom.xml`, `playwright.config.*`, and existing test folders.
   - Inspect current git status. If unrelated dirty files exist, leave them untouched and mention them only if they affect the report.
   - Extract real modules from controllers/services/components/routes rather than relying only on top-level docs.

2. **Inventory existing tests**
   - Use `rg --files` and targeted `rg` for test files and test declarations.
   - Index test cases with at least: layer, module, suite/class, case title or method name, file, line, and current result.
   - Include unit, component, service, controller, integration, E2E, proxy/edge, and CI tests when present.

3. **Run evidence-producing commands**
   - Prefer project-native commands from scripts/docs, for example `npm run test:run`, `mvn test`, `npm run test:e2e`, `npm run lint`, or a repo-specific quality gate.
   - If a command fails because of environment setup rather than product behavior, record the exact blocker and use the least invasive fallback only when it preserves evidence integrity.
   - For E2E, do not kill user processes just to free a port. Use an alternate port, reuse an existing local server, or note the blocker.

4. **Design the Excel workbook**
   - Use the Spreadsheets skill and bundled workspace dependencies for `.xlsx` creation.
   - Include a workbook overview, business test-case matrix, automated-test index, execution records, and risks/todos unless the user requests a narrower artifact.
   - Include filters, frozen headers, readable widths, wrapped text, data validation for status/priority, and at least one visual summary when useful.
   - See `references/artifact-schema.md` for recommended sheets and columns.

5. **Design the Word report**
   - Use the Documents skill and bundled workspace dependencies for `.docx` creation.
   - Choose a formal internal test-report style; keep it concise enough for stakeholders to skim.
   - Cover: project/scope metadata, execution summary, test asset summary, key passed paths, risks/todos, release recommendation, and limitations.
   - If the report cites a workbook, use the actual relative path.

6. **Verify both artifacts**
   - For Excel: inspect key ranges, scan formula errors, render representative sheets/ranges, and export `.xlsx`.
   - For Word: run the Documents skill render flow with `render_docx.py`; if `soffice`/LibreOffice is missing, use a structural check plus any available OS preview fallback and explicitly disclose that the LibreOffice render gate was skipped.
   - Also run archive checks such as `unzip -t` for both `.xlsx` and `.docx`.

7. **Clean up and commit when appropriate**
   - Remove scratch builders, previews, and temporary configs unless the user asked to keep them.
   - If project instructions require commits, stage only the final artifacts and any intentional docs updates. Do not stage unrelated dirty files.
   - Use a detailed Chinese commit message when the repo/user instructions require it.

## Status Semantics

- `通过`: The relevant automated command or manual verification was actually completed successfully.
- `部分通过`: Some automated coverage exists, but important business/manual behavior remains outside the executed checks.
- `待执行`: The case is designed but not run in this pass, or requires deployment/manual data.
- `阻塞`: Execution could not proceed because of an environment, credential, dependency, or access blocker.

Never mark a case `通过` just because a related test file exists.

## Evidence Rules

- Preserve exact commands, counts, timestamps, durations, and error text in the report.
- Separate local mocked/H2/API-mock evidence from real deployment or production evidence.
- For public-surface/security findings, keep claims anchored in executed probes or existing validated tests; do not convert source-code inspection into public evidence.
- If a command was rerun with a temporary config, record why and what differed from the canonical command.

## Output Conventions

- Prefer project-local paths such as `docs/testing/<project>测试用例.xlsx` and `docs/testing/<project>测试报告.docx` unless the user specifies another location.
- Use Chinese deliverable names and report prose when the project/user context is Chinese.
- Keep final responses short: link the `.xlsx` and `.docx`, summarize commands/results, mention any skipped visual verification or environment workaround, and identify the commit if one was made.
