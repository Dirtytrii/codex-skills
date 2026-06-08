# Codex Skills

个人沉淀的 Codex skills 公共仓库。

这个仓库用于保存可公开复用的技能目录，方便在不同 Codex 环境、远程 Hermes 服务器和新机器之间同步。每个 skill 都应是一个可以独立复制到 `${CODEX_HOME:-$HOME/.codex}/skills/` 的目录。

推荐先阅读 [角色分工与推荐使用方式](docs/role-usage.md)：本地 Codex 主要承接架构、开发、UI/PPT、视频、安全、测试和 QA；服务器侧 Hermes agent 优先承接运维只读诊断、部署检查和发布验证。

## 快速使用

推荐把这个仓库当成“角色 + skill 工具箱”使用：

| 场景 | 推荐入口 | 运行环境 |
| --- | --- | --- |
| 新需求、需求拆分、多窗口协作 | `$agent-role-orchestrator`，先走 `架构` | Codex 本地窗口 |
| gstack 产品/架构/工程/设计/QA 方法论审查 | `$gstack` 路由到具体 `$gstack-*` 子方法 | Codex 本地窗口 |
| 代码实现、文档修改、测试执行 | `开发` 角色提示词 | Codex 本地窗口 |
| UI、网页 PPT、社交卡、公众号封面 | `UI/PPT`，按任务路由到 `design-taste-frontend` / `guizang-ppt-skill` / `guizang-social-card-skill` | Codex 本地窗口 |
| 部署检查、发布验证、日志/cron/服务诊断 | Hermes-owned 运维 skills | 服务器侧 Hermes agent 优先 |
| 测试用例、测试报告、证据包 | `$test-case-report-builder`，由 `测试` 角色承接 | Codex 本地窗口 |
| Review readiness、验收缺口、阻塞风险 | `QA` 角色 | Codex 本地窗口 |
| 授权安全审计 | `authorized-blackbox-web-security` 或 Codex Security 系列 | Codex 本地窗口，必要时低影响远端验证 |

常用调用示例：

```text
使用 $agent-role-orchestrator，先按架构角色梳理这个需求，并判断是否需要开发/UI/测试/运维窗口。
```

```text
使用 $guizang-social-card-skill，把这篇文章做成一套小红书 3:4 图文。
```

```text
给 Hermes 运维 agent 一个部署后只读验证提示词，使用 post-deployment-readonly-verification 的边界。
```

## Skills

完整机器可读清单在 [registry/skills.json](registry/skills.json)。当前 active skills 共 50 个，按使用方式分组如下：

| 分组 | 代表 skills | 来源 | 主要角色 |
| --- | --- | --- | --- |
| 角色编排 | `agent-role-orchestrator` | local | 架构 / 全角色 |
| gstack 方法论路由 | `gstack`，以及 `gstack-office-hours`、`gstack-spec`、`gstack-autoplan`、`gstack-plan-*` | external-github / adapted | 架构 |
| gstack 执行与复盘 | `gstack-investigate`、`gstack-review`、`gstack-ship`、`gstack-health`、`gstack-devex-review`、`gstack-careful`、`gstack-guard`、`gstack-freeze`、`gstack-unfreeze`、`gstack-learn`、`gstack-retro` | external-github / adapted | 开发 / QA / 架构 |
| gstack 设计 | `gstack-design-consultation`、`gstack-design-shotgun`、`gstack-design-html`、`gstack-design-review` | external-github / adapted | UI/PPT |
| gstack QA / 安全 / 发布门禁 | `gstack-qa-only`、`gstack-qa`、`gstack-canary`、`gstack-cso`、`gstack-setup-deploy`、`gstack-land-and-deploy` | external-github / adapted | QA / 安全 / 运维 |
| UI/PPT 生产 | `design-taste-frontend`、`guizang-ppt-skill`、`guizang-social-card-skill`、`playwright` | external-github | UI/PPT |
| 视频/视觉资产 | `hatch-pet` | local | UI/PPT / 视频 |
| 安全审计 | `authorized-blackbox-web-security`，以及 Codex Security 插件 skills | local / plugin | 安全 |
| 测试资产 | `test-case-report-builder`、`pdf`、`playwright` | local / external | 测试 |
| Hermes 运维 | `application-problem-diagnosis-workflow`、`package-update-check-and-plan`、`pre-deployment-readonly-checklist`、`post-deployment-readonly-verification`、`hermes-*`、`proxy-dependent-python-service-diagnosis`、`python-project-deployment-troubleshooting` | hermes | 运维 / QA |

gstack 的完整角色映射见 [skills/gstack/references/methodology.md](skills/gstack/references/methodology.md)。本仓库保留的是 Codex 角色体系适配版，不内置上游大体积运行时、浏览器二进制、遥测或 host routing 自动注入。

暂不公开：

- `chronicle`：和本机屏幕录制/记忆能力绑定，公开复用价值低，容易造成误用。
- `.backup-*`：历史备份目录，不进入公开仓库。

## 目录结构

```text
.
├── skills/                 # 可复制安装的 skill 目录
├── registry/skills.json    # skill 清单和状态
├── docs/
│   ├── add-skill.md        # 新增 skill 的流程
│   ├── publication-checklist.md
│   ├── role-usage.md       # 角色分工和推荐运行环境
│   └── source-policy.md    # local / external / hermes 来源治理
├── scripts/
│   └── validate_public_skills.py
└── README.md
```

`skills/` 保持扁平结构：`skills/<skill-name>/SKILL.md`。如果某个 skill 自带 `references/`、`assets/`、`scripts/`、模板或校验脚本，整目录一起复制；不要只复制 `SKILL.md`。例如 `gstack` 的共享方法论在 `skills/gstack/references/methodology.md`，各 `gstack-*` 子 skill 会引用它。

单个 skill 的推荐结构：

```text
skills/<skill-name>/
├── SKILL.md               # 必需，frontmatter 至少包含 name 和 description
├── references/            # 可选，长说明和细分规则
├── assets/                # 可选，模板、图片、静态资源
├── scripts/               # 可选，辅助脚本
└── README.md              # 可选，上游或本仓库说明
```

## 安装

复制单个 skill：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
rsync -a "skills/agent-role-orchestrator/" "${CODEX_HOME:-$HOME/.codex}/skills/agent-role-orchestrator/"
```

复制全部 active skills：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for d in skills/*; do
  [ -d "$d" ] || continue
  rsync -a "$d/" "${CODEX_HOME:-$HOME/.codex}/skills/$(basename "$d")/"
done
```

## Hermes 后续补充

Hermes 服务器有新的 skill 时，按这个流程加入：

1. 在 `skills/<skill-name>/` 下放完整 skill 目录；公开仓库保持扁平安装结构，Hermes 本地分类目录只记录在同步说明里。
2. 确保 `skills/<skill-name>/SKILL.md` frontmatter 至少包含 `name` 和 `description`。
3. 更新 `registry/skills.json`，填好 `origin_type`、`maintenance` 和 `consumed_by_roles`。
4. 运行：

```bash
python3 scripts/validate_public_skills.py
```

5. 按 `docs/publication-checklist.md` 做公开发布前检查。
6. 使用中文 commit message 提交。

## 公开发布原则

- 不提交 token、密钥、账号密码、生产域名凭据、内网地址、私有日志、截图原始敏感信息。
- 不提交 `.backup-*`、临时输出、生成图片缓存、运行时录屏、记忆文件。
- 第三方来源 skill 保留原始许可证、README 和 provenance。
- 外部 GitHub 来源 skill 使用 `origin_type=external-github` 标记；除兼容 Codex/Hermes 所需的适配外，不把它当成本地原创。
- 每个 skill 保持最小自洽：`SKILL.md` 必须能说明何时使用、怎么使用、边界和校验方式。

## 维护约定

- 新需求先过 `agent-role-orchestrator` 的 `架构` 角色。
- 已建立角色默认走继承/接续，不重复新建窗口。
- `架构` 在非平凡实施计划进入开发前，可使用 `gstack` 路由到 `gstack-office-hours`、`gstack-spec`、`gstack-autoplan` 或具体 `gstack-plan-*` 审查。
- `运维` 优先使用 Hermes-owned 的只读诊断/部署检查 skills；涉及写操作、重启、清理、迁移时必须先获得用户明确授权。
- 安全审计默认委派到安全专项 skill。
- `测试` 生成测试用例/测试报告默认使用 `test-case-report-builder`。
- `QA` 保持验收/Review 角色，默认不负责写测试用例和测试报告。
- 使用中发现可复用优化时，优先沉淀回对应 skill。
