# Artifact Schema

Use this reference when designing the Excel workbook or Word report for the `test-case-report-builder` skill.

## Excel Workbook

Recommended sheets:

1. `概览`
   - Purpose: stakeholder snapshot.
   - Suggested blocks: generated time, scope, business test-case count, automated index count, executed case count, blocking defect count, status distribution, module summary, chart.

2. `测试用例`
   - Purpose: business/manual/acceptance test-case matrix.
   - Suggested columns: `用例编号`, `模块`, `层级`, `优先级`, `类型`, `用例标题`, `前置条件`, `测试步骤`, `预期结果`, `自动化覆盖`, `关联文件/接口`, `最近结果`, `备注`.
   - Use stable ids like `HS-TC-001` or `<PROJECT>-TC-001`.
   - Include both automated and still-manual release cases.

3. `自动化索引`
   - Purpose: parsed index of existing automated tests.
   - Suggested columns: `索引编号`, `模块`, `层级`, `测试套件`, `用例/方法`, `文件`, `行号`, `本次结果`.
   - Use stable ids like `AUTO-001`.

4. `执行记录`
   - Purpose: exact command evidence.
   - Suggested columns: `命令`, `层级`, `范围`, `文件/类数`, `用例数`, `通过`, `失败`, `跳过`, `耗时`, `结果`, `备注`.
   - Record environment workarounds here instead of hiding them in prose.

5. `风险与待办`
   - Purpose: release risk queue.
   - Suggested columns: `编号`, `领域`, `等级`, `说明`, `建议动作`, `状态`.

Formatting checklist:

- Freeze header rows.
- Apply filters/tables to matrix sheets.
- Wrap long cells and set deliberate column widths.
- Use validation lists for priority/status fields.
- Add one chart or KPI block on `概览` when there is status/module data.
- Render at least representative ranges from all sheets.

## Word Report

Recommended sections:

1. Title and metadata
   - Project, test time, scope, artifacts, conclusion.

2. Execution summary
   - Table of commands, layers, case counts, pass/fail/skip counts, duration, result.
   - Explain any fallback or temporary config.

3. Test asset summary
   - Workbook contents, business case count, automated index count, P0 count, status distribution.

4. Key passed paths
   - Short bullets grouped by domain: auth/security, core business, finance, inventory, shell/navigation, reports, deployment if applicable.

5. Risks and todos
   - Compact table; keep release blockers visible.

6. Release recommendation
   - Say whether local regression is sufficient for merge/handoff.
   - Explicitly separate local/mock/H2 evidence from production/public-domain evidence.

Verification checklist:

- DOCX opens structurally (`unzip -t`).
- Render with `render_docx.py` whenever `soffice` is available.
- If rendering cannot run because LibreOffice is unavailable, state that limitation and use another local preview only as a fallback.
- Ensure tables do not clip text and the first page is readable at a glance.
