# 角色分工与推荐使用方式

这份文档说明本仓库的结构、角色边界和推荐运行环境。核心原则是：`架构` 先判断需求和拆分边界，`开发` 等执行角色按白名单落地，`公众号发布` / `小红书` 可作为独立内容发布角色单独唤起，`运维` 优先交给服务器侧 Hermes agent 做只读诊断和受控操作。

## 仓库结构

```text
.
├── skills/                 # 可复制安装的 skill 目录，公开仓库保持扁平结构
├── registry/skills.json    # skill 元数据：来源、维护归属、角色消费关系
├── docs/
│   ├── add-skill.md
│   ├── publication-checklist.md
│   ├── role-usage.md
│   └── source-policy.md
├── scripts/
│   └── validate_public_skills.py
└── README.md
```

`skills/` 目录故意保持扁平：`skills/<skill-name>/SKILL.md`。Hermes 服务器上的 `devops/`、`system/`、`migration/` 等分类可以作为来源信息，但同步到公开仓库时不作为安装路径，避免破坏 Codex 的直接复制安装方式。

## 来源和维护归属

| 来源 | registry 标记 | 谁维护 | 推荐改动方式 |
| --- | --- | --- | --- |
| 本地沉淀 | `origin_type=local` | 本仓库主维护 | 可按实际使用反馈直接优化 |
| 外部 GitHub | `origin_type=external-github` | 上游为主，本仓库适配 | 保留上游来源，谨慎改核心逻辑 |
| Hermes 沉淀 | `origin_type=hermes` | 服务器侧 Hermes 工作流 | 先脱敏泛化，再同步进公开仓库 |

`maintenance` 用来说明维护方式：

- `local-owned`: 本仓库直接维护。
- `vendored-upstream`: 尽量贴近上游。
- `vendored-adapted`: 外部来源但做了 Codex/Hermes 适配。
- `hermes-owned`: Hermes 运维现场经验沉淀，本仓库接收脱敏同步。

## 角色分工

| 角色 | 推荐运行环境 | 核心职责 | 默认 skill |
| --- | --- | --- | --- |
| `架构` | Codex 本地窗口 | 需求澄清、架构判断、拆分角色、维护角色台账 | `agent-role-orchestrator`, `gstack`, `gstack-office-hours`, `gstack-spec`, `gstack-autoplan`, `gstack-plan-*`, `startup-pressure-test` |
| `开发` | Codex 本地窗口 | 按架构提示词实现代码、测试、提交 | 由项目技术栈决定，可辅助用 `gstack-investigate`, `gstack-review`, `gstack-ship`, `gstack-health`, `gstack-careful`, `gstack-guard`, `playwright`, `pdf` |
| `UI/PPT` | Codex 本地窗口 | UI 体验、视觉改造、网页 PPT、社交卡、公众号封面、演示材料 | `gstack-design-*`, `design-taste-frontend`, `guizang-ppt-skill`, `guizang-social-card-skill`, `playwright` |
| `视频` | Codex 本地窗口 | 宣传视频脚本、分镜、素材和渲染计划 | `hatch-pet` 或视频插件/工具链 |
| `公众号发布` | Codex 本地窗口 | 公众号文章排版、草稿、预览、素材检查和授权发布自动化 | `wechat-ai-app-ops`, `humanizer-zh`；需要封面/社交卡时交给 `UI/PPT` 或 `guizang-social-card-skill` |
| `小红书` | Codex 本地窗口 | 小红书/Rednote 笔记、图文组图、标题标签、草稿和授权发布自动化 | `humanizer-zh`, `guizang-social-card-skill`, `playwright`；最终发布必须明确授权 |
| `运维` | 服务器侧 Hermes agent 优先 | 部署检查、发布验证、日志/cron/服务诊断 | Hermes-owned 运维 skills；`gstack-setup-deploy` / `gstack-land-and-deploy` / `gstack-canary` 只作规划和门禁辅助 |
| `安全` | Codex 本地窗口，必要时低影响远端验证 | 授权安全审计、仓库/PR 安全扫描、黑盒报告 | `gstack-cso`, `authorized-blackbox-web-security` 和 Codex Security 系列 |
| `测试` | Codex 本地窗口 | 测试用例、测试报告、证据包 | `test-case-report-builder`, `playwright` |
| `QA` | Codex 本地窗口 | Review readiness、验收缺口、阻塞风险验证 | `gstack-qa-only`, `gstack-qa`, `gstack-canary`, `gstack-review`, `playwright`，必要时使用 Hermes 只读验证 skill |

## gstack 方法论分发

`gstack` 是外部 GitHub 方法论在本仓库里的 Codex 适配入口。完整映射在 [../skills/gstack/references/methodology.md](../skills/gstack/references/methodology.md)。

| 方法族 | 默认角色 | 用法 |
| --- | --- | --- |
| `gstack-office-hours`, `gstack-spec` | 架构 | 早期想法、需求澄清、可执行规格 |
| `gstack-autoplan`, `gstack-plan-*` | 架构 | CEO/设计/工程/DX 的计划审查和下游拆分 |
| `gstack-investigate`, `gstack-review`, `gstack-ship`, `gstack-health`, `gstack-devex-review` | 开发 / QA | 根因、代码审查、发布前检查、项目健康 |
| `gstack-careful`, `gstack-guard`, `gstack-freeze`, `gstack-unfreeze` | 开发 / 运维 / 安全 / QA | 高风险动作前的保守检查、护栏、冻结和恢复 |
| `gstack-design-*` | UI/PPT | 视觉方向探索、HTML 原型、渲染后设计审查 |
| `wechat-ai-app-ops` | 公众号发布 / 架构 / UI/PPT | 公众号 AI 应用文章、周刊连续性、图文排版、草稿箱 API 和本地交接 |
| `humanizer-zh` | 小红书 / 公众号发布 | 中文 AI 写作去痕、人味化润色和发布前文案校准；不负责事实补充或发布动作 |
| `guizang-social-card-skill` | UI/PPT / 小红书 / 公众号发布 | 小红书图文、社交卡和公众号封面素材生产；发布动作仍归平台发布角色 |
| `gstack-qa-only`, `gstack-qa`, `gstack-canary` | QA | Web/UI 行为验证、窄范围修复闭环、发布门禁 |
| `gstack-cso` | 安全 | 基础设施优先的安全态势审查 |
| `gstack-setup-deploy`, `gstack-land-and-deploy` | 运维 / 架构 | 部署规划和发布门禁；远程生产事实仍交给 Hermes |
| `gstack-document-*`, `gstack-learn`, `gstack-retro` | 架构 / 开发 / QA | 文档、发布说明、经验沉淀、复盘 |

本仓库不内置上游 gstack 的浏览器/设计二进制运行时，也不自动开启遥测、cookie 导入或 host routing 注入。需要上游完整运行时能力时，单独按上游仓库安装，不把这些运行时文件混入本公开 skills 仓库。

## 推荐协作流

### 新需求

1. 先开或继承 `架构` 窗口。
2. `架构` 读取项目上下文，判断需求类型、风险和是否需要多角色。
3. `架构` 只在必要时输出 `开发`、`UI/PPT`、`视频`、`公众号发布`、`小红书`、`测试`、`QA`、`安全`、`运维` 等下游提示词。
4. 已建立过的角色默认走 `继承` / `接续`，不要重复新建窗口。
5. 只有明确需要并行时才开 `开发1号`、`开发2号` 这类编号角色。

### 开发团队

推荐用 Codex 本地窗口承接：

- 架构拆分后的代码实现。
- 前端/UI/PPT/社交卡/视频产物。
- 公众号文章和小红书笔记的草稿、预览、发布包和明确授权后的发布自动化。
- 仓库测试、QA、Review 准备。
- 安全代码审计和低影响黑盒报告。

开发窗口必须带上：

- 文件白名单。
- 禁止范围。
- 验证命令。
- 提交/PR 要求。
- 完成后回传格式。

这些字段由 `agent-role-orchestrator` 默认生成，不需要用户每次单独提醒。

### 运维团队

推荐交给服务器侧 Hermes agent 承接，Codex 本地窗口负责写提示词、收集回传、判断下一步。

适合 Hermes 的任务：

- 部署前只读检查：`pre-deployment-readonly-checklist`
- 部署后只读验证：`post-deployment-readonly-verification`
- 应用故障诊断：`application-problem-diagnosis-workflow`
- 部署包检查和更新计划：`package-update-check-and-plan`
- Hermes cron 空输出诊断：`hermes-cron-empty-output-diagnosis`
- Hermes cron 脚本解释器问题：`hermes-python-script-wrapper-for-shell-cron`
- 代理依赖型 Python 服务诊断：`proxy-dependent-python-service-diagnosis`
- Python 部署问题诊断：`python-project-deployment-troubleshooting`

Hermes 默认只读。重启、清理、迁移、删除、回滚、配置修改、数据库写操作都必须进入“待授权动作”，不能作为默认 workflow 执行。

### 内容发布团队

`公众号发布` 和 `小红书` 是独立内容发布角色：

- 可以由 `架构` 分流，也可以通过 `$agent-role-orchestrator` 单独唤起。
- `公众号发布` 默认使用 `wechat-ai-app-ops` 处理 AI 应用公众号文章、周刊连续性、图文排版和草稿箱 API。
- `小红书` 和 `公众号发布` 可使用 `humanizer-zh` 做标题、正文、caption 的人味化和去 AI 痕迹处理，但不得借此新增事实、数据、价格、背书或发布时间。
- 默认只做草稿、预览、发布包、素材检查和自动化步骤准备。
- 最终发布、群发、删除、账号设置、凭据变更等动作必须有用户明确授权。
- 视觉资产生产仍可交给 `UI/PPT`，特别是公众号封面、小红书图文组图和社交卡。
- 平台账号、登录态、token、cookie 和后台权限不随本仓库同步，必须在目标机器或目标账号环境单独配置。

### 测试和 QA

`测试` 和 `QA` 不合并：

- `测试` 负责正式测试资产，例如 Excel 测试用例、Word/DOCX 测试报告、测试证据包。
- `QA` 负责变更是否可验收、是否可 Review、是否存在 blocker、是否缺少关键验证。

如果一个任务同时需要测试报告和 Review readiness，先让 `架构` 拆成 `测试` 与 `QA` 两个提示词，避免职责混在一起。

## 安装建议

Codex 本地开发机可以安装全部 active skills：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for d in skills/*; do
  [ -d "$d" ] || continue
  rsync -a "$d/" "${CODEX_HOME:-$HOME/.codex}/skills/$(basename "$d")/"
done
```

服务器侧 Hermes agent 建议按需安装运维子集：

```bash
for name in \
  application-problem-diagnosis-workflow \
  package-update-check-and-plan \
  pre-deployment-readonly-checklist \
  post-deployment-readonly-verification \
  hermes-cron-empty-output-diagnosis \
  hermes-python-script-wrapper-for-shell-cron \
  proxy-dependent-python-service-diagnosis \
  python-project-deployment-troubleshooting
do
  rsync -a "skills/$name/" "${CODEX_HOME:-$HOME/.codex}/skills/$name/"
done
```

如果服务器 agent 不使用 Codex 的 `${CODEX_HOME}` 目录结构，保持 `SKILL.md` 内容不变，按服务器 agent 的 skill 目录规范复制即可。

## 公开同步流程

1. 本地或 Hermes 先只读盘点候选 skill。
2. 判断来源：`local`、`external-github`、`hermes`。
3. 对 Hermes 内容先脱敏，移除真实路径、IP、域名、账号、日志原文、密钥和项目专属信息。
4. 放入 `skills/<skill-name>/`。
5. 更新 `registry/skills.json`、`README.md` 和必要 docs。
6. 运行 `python3 scripts/validate_public_skills.py`。
7. 做敏感信息扫描。
8. 中文提交并推送。

## 使用口诀

- 新需求先过 `架构`。
- 代码和产物交给 Codex。
- 远程生产事实交给 Hermes 只读查。
- 公众号和小红书默认先草稿/预览，最终发布必须显式授权。
- 测试报告归 `测试`。
- 验收阻塞归 `QA`。
- 外部 skill 记来源，Hermes skill 先脱敏。
