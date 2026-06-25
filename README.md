# Codex Skills

个人沉淀的 Codex skill 体系。它不是普通 prompt collection，而是一套可跨机器继承的 **role-based agent workflow**：用 `agent-role-orchestrator` 先做架构分流，再让开发、UI、内容发布、运维、DBA、安全、测试、QA、文档/交付、知识库等角色按边界工作。

这个仓库适合两类人或 agent：

- 想快速安装并复用这套 Codex skills。
- 想理解这套多窗口、角色化、可沉淀的协作模型，并在自己的项目中继续维护。

更细的角色边界见 [docs/role-usage.md](docs/role-usage.md)，来源治理见 [docs/source-policy.md](docs/source-policy.md)，机器可读清单见 [registry/skills.json](registry/skills.json)。

## 快速上手

```bash
git clone git@github.com:Dirtytrii/codex-skills.git
cd codex-skills
python3 scripts/validate_public_skills.py
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for d in skills/*; do
  [ -d "$d" ] || continue
  rsync -a --delete "$d/" "${CODEX_HOME:-$HOME/.codex}/skills/$(basename "$d")/"
done
```

Windows 没有 `rsync` 时，可以按目录复制 `skills/<skill-name>/` 到 `%USERPROFILE%\.codex\skills\`；需要包含 `SKILL.md`、`references/`、`scripts/`、`assets/` 等整个目录。

安装后最常用入口：

```text
使用 $agent-role-orchestrator，先按架构角色梳理这个需求，并判断是否需要开发/UI/公众号发布/小红书/测试/DBA/运维窗口。
```

常用单独唤起：

```text
使用 $agent-role-orchestrator，给我公众号发布窗口。
使用 $agent-role-orchestrator，给我小红书窗口。
使用 $agent-role-orchestrator，给我 DBA 窗口。
```

## 这套体系解决什么

传统 prompt collection 的问题是：每个 prompt 都能回答，但很难组织复杂工作，也很难把一次项目里的经验变成下一次默认行为。本仓库把 skill 组织成三个层次：

| 层次 | 作用 | 代表内容 |
| --- | --- | --- |
| 角色编排 | 先判断需求、拆分窗口、维护回调和闭环状态 | `agent-role-orchestrator` |
| 方法与工具 | 给不同角色装上合适的方法论或操作能力 | `gstack-*`、`wechat-*`、`cheat-on-content`、`test-case-report-builder` 等 |
| 治理与继承 | 说明来源、边界、安装、公开同步和敏感信息规则 | `registry/skills.json`、`docs/*`、校验脚本 |

核心默认行为：

- 新需求先过 `架构`，复杂需求先给多方案技术选型。
- 新本地代码项目默认检查或初始化 CodeGraph。
- 需求确认后，`架构` 先做有边界的开源/可借鉴方案扫描。
- 已建立角色默认继承/接续，不重复开新窗口。
- 下游完成、阻塞或需要决策时，回调任务发起窗口，不默认都回架构。
- 闭环结束要写 `可复用优化沉淀：无 / 建议 / 已沉淀`。

## 技术亮点

### 1. Architecture-first Gateway

`agent-role-orchestrator` 是入口控制器。它先澄清需求、判断风险、拆角色、给文件范围和验收标准，再决定是否派给开发、UI、内容发布、运维、DBA、安全、测试、QA 或文档角色。

### 2. Multi-Window / Role-Based Loop Engineering

这套设计把多个 Codex 窗口当作长期角色，而不是一次性聊天。每个角色只承接自己的职责，反馈进入下一轮闭环。

```text
用户目标
→ 架构澄清 / 选型 / 派发
→ 角色窗口执行
→ QA 或发起窗口验收
→ 结构化反馈
→ 返工或决策
→ 架构终验
→ 可复用优化沉淀
```

关键点：

- `架构` 是 controller，不是所有任务的执行者。
- `开发`、`UI`、`内容发布`、`DBA`、`运维`、`测试`、`QA` 分离职责。
- `QA` 是 evaluator，不默认写测试报告，也不替开发修问题。
- 回调按任务来源流动：A 派 B，B 完成后回 A；如果 B 再派 C，C 回 B。
- 反馈必须包含问题、证据、影响等级、回流对象、决策需求和下一闭环状态。

### 3. Skill as Capability Routing

角色不会把所有能力塞进一个超级提示词，而是按任务加载对应 skill：

| 任务类型 | 默认路由 |
| --- | --- |
| 架构/规格/计划审查 | `agent-role-orchestrator` + `gstack-*` |
| 代码实现、调查、评审 | 开发角色 + `gstack-investigate/review/ship/health` |
| UI、网页 PPT、社交卡、封面 | UI/PPT 角色 + `design-taste-frontend`、`guizang-*` |
| 公众号发布 | `wechat-ai-app-ops`、`wechat-tech-writer`、`wechat-article-formatter` |
| 小红书发布与内容实验 | `cheat-on-content`、`xhs-publish-assistant`、`xhs-comment-research` |
| 中文正式对外文案 | `humanizer-zh`，叙事类再按需用 `story-deslop` |
| 运维只读诊断 | Hermes-owned 运维 skills |
| 数据库实例风险 | DBA 角色卡，危险动作二次授权 |
| 测试资产和压测验证 | `test-case-report-builder`、`playwright` |
| 安全审计 | `authorized-blackbox-web-security` 或 Codex Security 系列 |

### 4. Source and Safety Governance

仓库区分三种来源：

| 来源 | 含义 | 维护方式 |
| --- | --- | --- |
| `local` | 本地长期使用沉淀 | 可直接按反馈优化 |
| `external-github` | 外部 GitHub skill 或方法论 | 保留 provenance，谨慎适配 |
| `hermes` | 服务器侧运维经验沉淀 | 先脱敏泛化，再公开同步 |

公开仓库不同步：token、密钥、登录态、浏览器 cookie、生产日志、服务器真实路径、本机 memory、私有自动化任务和插件运行时。

## 角色速查

| 角色 | 什么时候用 | 默认边界 |
| --- | --- | --- |
| `架构` | 新需求、复杂拆分、多窗口协作 | 澄清需求、选型、开源参考扫描、派发角色 |
| `开发` | 代码实现、修复、项目内测试 | 按架构范围改代码并验证 |
| `UI/PPT` / `UI/Frontend` | 视觉、前端体验、网页 PPT、社交卡 | 负责视觉方向和视觉验证 |
| `视频` | 宣传视频、分镜、动效素材 | 产出脚本、分镜和渲染计划 |
| `公众号发布` | 微信公众号文章、草稿、预览、发布准备 | 默认草稿/预览，最终发布需授权 |
| `小红书` | 小红书笔记、图文、标题标签、发布复制包 | 默认发布包，最终发布需授权 |
| `文档/交付` | 交付清单、验收表、演示脚本、交接文档 | 不替代 QA、开发事实或法律/税务意见 |
| `知识库` | Obsidian/个人笔记整理 | 不删除、不公开、不改写成专业建议 |
| `运维` | 部署检查、日志、cron、服务诊断 | Hermes 优先，只读优先，写操作授权 |
| `DBA` | 容量、锁、binlog/WAL、长事务、备份恢复 | 只读诊断优先，危险动作二次授权 |
| `安全` | 授权安全审计、仓库/PR 扫描、黑盒报告 | 低影响验证，委派安全专项 skill |
| `测试` | 测试用例、测试报告、证据包、压测验证 | 不实现功能，不伪造测试结果 |
| `QA` | Review readiness、验收缺口、阻塞风险 | 不默认写测试报告或替开发修复 |

## 仓库结构

```text
.
├── skills/                 # 可复制安装的 skill 目录，保持 skills/<name>/SKILL.md 扁平结构
├── registry/skills.json    # active skills、来源、维护归属、角色消费关系
├── docs/
│   ├── add-skill.md        # 新增 skill 流程
│   ├── publication-checklist.md
│   ├── role-usage.md       # 完整角色分工和推荐运行环境
│   └── source-policy.md    # local / external / hermes 来源治理
├── scripts/
│   └── validate_public_skills.py
└── README.md
```

## 维护方式

常规维护流程：

1. 本机使用中发现可复用改进。
2. 优先沉淀到对应 skill；角色编排类改进通常在 `agent-role-orchestrator`。
3. 可公开复用的部分同步到本仓库，项目私有状态不进仓库。
4. 更新 `registry/skills.json` 和必要 docs。
5. 运行 `python3 scripts/validate_public_skills.py`。
6. 做公开发布检查，提交中文 commit，并开 PR。

更详细的新增/同步规则见 [docs/add-skill.md](docs/add-skill.md) 和 [docs/publication-checklist.md](docs/publication-checklist.md)。
