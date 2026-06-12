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

- `架构`: `gstack`、`gstack-office-hours`、`gstack-spec`、`gstack-autoplan`、`gstack-plan-*`、`startup-pressure-test`
- `开发`: `gstack-investigate`、`gstack-review`、`gstack-ship`、`gstack-health`、`gstack-devex-review`、`gstack-careful`、`gstack-guard`
- `UI/PPT`: `design-taste-frontend`、`guizang-ppt-skill`、`guizang-social-card-skill`、`playwright`
- `公众号发布`: `wechat-ai-app-ops` 承接公众号 AI 应用文章、周刊连续性、草稿箱 API 和本地交接；文案人味化可复用 `humanizer-zh`，视觉资产可复用 `guizang-social-card-skill`
- `小红书`: 预留的小红书/Rednote 笔记和授权发布角色；内容实验和增长判断可复用 `cheat-on-content`，标题、正文和 caption 人味化可复用 `humanizer-zh`，图文资产可复用 `guizang-social-card-skill`
- `运维`: Hermes-owned 的部署前检查、部署后验证、Hermes cron、Python 服务和代理诊断类 skill
- `测试`: `test-case-report-builder`、`playwright`
- `QA`: `gstack-qa-only`、`gstack-qa`、`gstack-canary`、`gstack-review`、`playwright`，可按需使用 Hermes-owned 只读验证 skill，但默认不负责测试用例/测试报告资产
- `安全`: `gstack-cso`、`authorized-blackbox-web-security`

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

### gstack 适配规则

`gstack` 和 `gstack-*` 来自 `https://github.com/garrytan/gstack`，在本仓库中使用 `origin_type=external-github` 和 `maintenance=vendored-adapted`。

本仓库只沉淀 Codex 角色体系需要的方法论入口：

- 保留 product / architecture / design / engineering / QA / security / ship / docs / retro 的方法划分。
- 使用 `skills/gstack/references/methodology.md` 做共享方法图谱。
- 每个 `gstack-*` 子 skill 是薄适配入口，负责触发、边界和输出口径。

不要默认提交：

- 上游浏览器或设计二进制运行时。
- `node_modules`、浏览器下载缓存、构建产物。
- 上游 telemetry、cookie import、host routing 自动注入配置。
- `CLAUDE.md` / `.claude/` / `.agents/` 自动改写逻辑，除非用户明确要做上游 gstack 安装/迁移。

## Hermes Skill 同步规则

Hermes 同步进来的 skill 默认是运维现场经验沉淀，不等于可以直接公开原始版本。进入仓库前必须先完成脱敏和泛化。

可以公开：

- 只读诊断流程。
- 部署前检查、部署后验证、健康检查、日志摘要、cron 输出诊断。
- 使用占位符表达的命令计划和报告格式。

不能公开：

- 真实服务器路径、内网/公网 IP、域名、账号、数据库连接串、token、cookie、JWT、私钥、`.env` 内容。
- 原始生产日志、客户数据、订单数据、个人信息。
- 项目专属名称、交易/收益/业务策略细节。
- 默认会执行写操作、重启、清理、迁移、删除、回滚的流程。

写操作处理规则：

- 修复、重启、清理、迁移、删除、回滚只能放在 `Optional user-approved actions` 或类似“需用户确认后执行”的章节。
- 默认 workflow 必须保持只读。
- `registry/skills.json` 中运维原创类使用 `origin_type=hermes` 和 `maintenance=hermes-owned`。
- 公开仓库的安装结构保持 `skills/<skill-name>/` 扁平目录；Hermes 本地分类路径不要作为公开路径写入。
