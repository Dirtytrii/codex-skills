# Skill 来源治理

这个仓库同时保存本地沉淀 skill、外部 GitHub skill 以及后续 Hermes 同步进来的 skill。来源必须在 `registry/skills.json` 中显式标注。

## origin_type

- `local`: 本地工作流中沉淀出来的 skill，可以按使用反馈直接维护。
- `external-github`: 从 GitHub 外部仓库引入的 skill，应记录上游来源，保留许可证/README/provenance。
- `hermes`: Hermes 服务器沉淀后同步进来的 skill。
- `upstream-adapted`: 兼容旧清单的历史值，后续新增不要再用，改用 `external-github` 加 `maintenance`。

## maintenance

- `local-owned`: 本仓库主维护，可直接按使用经验修改。
- `vendored-upstream`: 尽量贴近上游，只做必要同步和兼容调整。
- `vendored-adapted`: 来自外部，但为了 Codex/Hermes 使用做了本地适配；修改时要保留来源说明。
- `hermes-owned`: 由 Hermes 工作流主维护，本仓库接收同步。

## 角色消费关系

`consumed_by_roles` 记录哪些角色默认会调用该 skill。例如：

- `UI/PPT`: `design-taste-frontend`、`guizang-ppt-skill`、`playwright`
- `QA`: `test-case-report-builder`、`playwright`
- `安全`: `authorized-blackbox-web-security`

角色消费不代表原创归属。外部 skill 可以作为角色默认工具，但仍必须保持外部来源标记。

## 外部 GitHub Skill 修改规则

可以改：

- Codex/Hermes 调用说明。
- 本仓库安装路径、包装脚本、轻量适配文档。
- 明确不会改变上游语义的错别字或兼容性说明。

谨慎改：

- 核心流程、模板、脚本逻辑。
- 许可证、上游 README、provenance。

必须记录：

- `upstream_url`，如果暂时未知就填 `null`，不要编造。
- `maintenance`。
- 改动原因和验证结果。

