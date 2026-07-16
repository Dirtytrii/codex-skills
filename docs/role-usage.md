# 角色分工与推荐使用方式

这份文档说明本仓库的结构、角色边界和推荐运行环境。核心原则是：`总控 / CEO` 作为默认入口判断目标、优先级、模型预算和角色路线；`架构 / CTO` 负责技术交付闭环，为新本地代码项目启动 CodeGraph、扫描开源/可借鉴方案并拆分开发/UI/测试/QA 等边界；`内容主编` 负责公众号、小红书、视频和视觉资产协作；`开发` 等执行角色按白名单落地，`知识库` / `技能维护` / `DBA` 可作为独立角色单独唤起，`运维` 优先交给服务器侧 Hermes agent 做只读诊断和受控操作。

## 仓库结构

```text
.
├── skills/                 # 可复制安装的 skill 目录，公开仓库保持扁平结构
├── registry/skills.json    # skill 元数据：来源、维护归属、角色消费关系
├── registry/plugin-packages.json # core/domain 包归属、依赖与安装策略
├── plugins/                # 由 canonical skills/ 生成的插件 bundle
├── .agents/plugins/marketplace.json # 仓库级插件 marketplace
├── docs/
│   ├── add-skill.md
│   ├── publication-checklist.md
│   ├── plugin-packaging.md
│   ├── routing-token-and-evaluation.md
│   ├── role-usage.md
│   └── source-policy.md
├── scripts/
│   ├── validate_public_skills.py
│   ├── validate_plugins.py
│   ├── validate_role_system.py
│   ├── test_plugin_packages.py
│   └── test_role_system_tools.py
├── skills/agent-role-orchestrator/scripts/
│   ├── aggregate_skill_hits.py
│   ├── check_codegraph.py
│   ├── ensure_project_role_files.py
│   ├── render_role_prompt.py
│   └── validate_role_loop.py
└── README.md
```

`skills/` 目录故意保持扁平：`skills/<skill-name>/SKILL.md`，并且是唯一人工维护源。`plugins/*/skills/` 由 `sync_plugin_bundles.py` 生成，不得直接编辑。Hermes 服务器上的 `devops/`、`system/`、`migration/` 等分类可以作为来源信息，但同步到公开仓库时不作为 canonical 路径。

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
| `总控` / `CEO` | Codex 本地窗口 | 默认入口、目标澄清、优先级、模型预算、角色路由、顶层台账、最终验收 | `agent-role-orchestrator`, `gstack-office-hours`, `gstack-plan-ceo-review`, `startup-pressure-test` |
| `架构` / `CTO` | Codex 本地窗口 | 技术方案、多方案技术选型、新项目 CodeGraph 启动、开源/可借鉴方案扫描、管理开发/UI/测试/QA/安全/DBA/运维闭环 | `agent-role-orchestrator`, `gstack`, `gstack-spec`, `gstack-autoplan`, `gstack-plan-*` |
| `开发负责人 / Dev Lead` | Codex 本地窗口 | 按第一性原理拆解任务、管理开发执行 subagent、整合代码、测试、提交 | 由项目技术栈决定，可辅助用 `gstack-investigate`, `gstack-review`, `gstack-ship`, `gstack-health`, `gstack-careful`, `gstack-guard`, `browser-automation-router`, `playwright`, `pdf` |
| `UI/PPT` / `UI/Frontend` | Codex 本地窗口 | UI 体验、视觉改造、前端视觉保真、参考到实现闭环、预览图实现路线选择、网页 PPT、社交卡、公众号封面、小红书图文视觉、演示材料、照片到玩具资产规划 | `ui-implementation-workflow`（内置按需视觉方向），`gstack-design-*`, `guizang-ppt-skill`, `xhs-visual-director`, `guizang-social-card-skill`, `photo-to-cute-3d-toy`, `browser-automation-router`；`design-taste-frontend` 仅兼容旧调用，CI/回归按需用 `playwright` |
| `视频` | Codex 本地窗口 | 宣传视频脚本、分镜、素材和渲染计划 | `hatch-pet` 或视频插件/工具链 |
| `内容主编` | Codex 本地窗口 | 内容域上层协调，管理公众号发布、小红书、视频和 UI/PPT 视觉资产协作 | `agent-role-orchestrator`, `humanizer-zh`, `story-deslop`, 内容平台相关 skills |
| `公众号发布` | Codex 本地窗口 | 公众号技术选题初稿、文章排版、草稿、预览、素材检查和授权发布自动化 | `wechat-ai-app-ops`, `wechat-tech-writer`, `wechat-article-formatter`, `humanizer-zh`；需要封面/社交卡时交给 `UI/PPT` 或 `guizang-social-card-skill` |
| `小红书` | Codex 本地窗口 | 小红书/Rednote 笔记、评论研究、图文视觉、标题标签、内容实验、发布复制包和授权发布自动化 | `cheat-on-content`, `xhs-comment-research`, `xhs-visual-director`, `humanizer-zh`, `xhs-publish-assistant`, `browser-automation-router`, `xhs-automation-publisher`, `guizang-social-card-skill`；最终发布必须明确授权 |
| `运维` | 服务器侧 Hermes agent 优先 | 部署检查、发布验证、日志/cron/服务诊断 | Hermes-owned 运维 skills；`gstack-setup-deploy` / `gstack-land-and-deploy` / `gstack-canary` 只作规划和门禁辅助；数据库实例主因转 `DBA` |
| `DBA` | Codex 本地窗口，按权限收集数据库证据 | 数据库容量、临时空间、binlog/WAL、长事务、锁、备份恢复、分区/归档和高风险清理方案 | `agent-role-orchestrator` 角色卡；默认只读，kill/purge/DDL/resize/restore/cleanup 等动作必须二次授权 |
| `安全` | Codex 本地窗口，必要时低影响远端验证 | 授权安全审计、仓库/PR 安全扫描、黑盒报告 | `gstack-cso`, `authorized-blackbox-web-security` 和 Codex Security 系列 |
| `测试` | Codex 本地窗口 | 测试用例、测试报告、证据包、独立压力/负载/性能/并发验证 | `test-case-report-builder`, `browser-automation-router`；CI/回归按需用 `playwright` |
| `QA` | Codex 本地窗口 | 对抗式审查、Review readiness、验收缺口、阻塞风险验证 | `gstack-qa-only`, `gstack-qa`, `gstack-canary`, `gstack-review`, `browser-automation-router`，CI/回归按需用 `playwright`，必要时使用 Hermes 只读验证 skill |
| `文档/交付` | Codex 本地窗口 | 交付清单、验收材料、演示脚本、变更确认、操作指南和交接文档 | `delivery-document-package`, `gstack-document-generate`, `gstack-document-release`, `gstack-learn`, `gstack-retro` |
| `知识库` | Codex 本地窗口 | 个人知识库/Obsidian vault 的目录、索引、标签、MOC 和链接整理 | `agent-role-orchestrator` 角色卡 |
| `技能维护` | Codex 本地窗口 | skill 命中率复盘、触发描述调优、registry/README/docs/source-policy 维护、角色卡拆合建议 | `agent-role-orchestrator` 角色卡 |

## gstack 方法论分发

`gstack` 是外部 GitHub 方法论在本仓库里的 Codex 适配入口。完整映射在 [../skills/gstack/references/methodology.md](../skills/gstack/references/methodology.md)。

| 方法族 | 默认角色 | 用法 |
| --- | --- | --- |
| `gstack-office-hours`, `gstack-plan-ceo-review`, `startup-pressure-test` | 总控 | 早期想法、需求现实性、优先级和模型预算 |
| `gstack-spec`, `gstack-autoplan`, `gstack-plan-*` | 架构 | 技术规格、工程/设计/DX 计划审查和下游拆分 |
| `gstack-investigate`, `gstack-review`, `gstack-ship`, `gstack-health`, `gstack-devex-review` | 开发 / QA | 根因、代码审查、发布前检查、项目健康 |
| `gstack-careful`, `gstack-guard`, `gstack-freeze`, `gstack-unfreeze` | 开发 / 运维 / 安全 / QA | 高风险动作前的保守检查、护栏、冻结和恢复 |
| `gstack-design-*` | UI/PPT | 视觉方向探索、HTML 原型、渲染后设计审查 |
| `ui-implementation-workflow` | UI/PPT / UI/Frontend | 页面分类、项目审计、营销/品牌/作品集/内容页按需视觉方向、完整参考源库存、最多三份激活参考、换源台账、语义 Token、骨架优先实现和 1440/768/390 截图修复闭环 |
| `预览图实现路线选择` | UI/PPT / 架构 | 有预览图、参考图、截图或高保真目标时，先比较 CSS/组件、图片/生成资产、Canvas/SVG、Three.js/WebGL、Lottie/视频、现成库/组件等路线，再进入开发实现 |
| `browser-automation-router` | 开发 / UI/PPT / 测试 / QA / 小红书 / 内容主编 | 原生 Browser、Chrome 登录态、Playwright 和平台脚本的 fail-closed 路由；最低能力门槛为 Codex Desktop `2026-06-11` 发布版本且当前任务可见对应插件 |
| `photo-to-cute-3d-toy` | UI/PPT / 视频 / 架构 | 照片参考到可爱 3D 玩具/GLB 路线、提示词包和交付清单 |
| `wechat-ai-app-ops` | 公众号发布 / 内容主编 / UI/PPT | 公众号 AI 应用文章、周刊连续性、图文排版、草稿箱 API 和本地交接 |
| `wechat-tech-writer`, `wechat-article-formatter` | 公众号发布 | 技术选题搜索/初稿和 Markdown 到微信公众号 HTML 排版 |
| X MCP 内容研究源 | 内容主编 / 小红书 / 公众号发布 / 视频 | 爆款内容研究、热点扫描、选题池、对标账号和公开讨论脉络；只读、需授权，官方文档：https://docs.x.com/tools/mcp |
| `反老登味 / 反 AI 味内容闸门` | 内容主编 / 小红书 / 公众号发布 / 视频 / UI/PPT | 正式对外中文内容交付前的语气闸门：去说教、爹味、上位者口吻、模板化排比和万能套话，同时不改事实、数据、价格、日期、来源和授权边界 |
| `humanizer-zh` | 小红书 / 公众号发布 / UI/PPT / 视频 | 中文 AI 写作去痕、人味化润色和发布前文案校准；不负责事实补充或发布动作 |
| `story-deslop` | 内容主编 / 公众号发布 / 小红书 / 视频 | 中文网文、叙事正文、剧情片段和对话场景的去 AI 味；不作为公众号或小红书营销文案的默认润色工具 |
| `cheat-on-content` | 小红书 / 内容主编 | 社交内容的选题打分、盲预测、发布后复盘、rubric 迭代和内容实验状态；不负责生成图文资产或最终发布 |
| `xhs-visual-director` | UI/PPT / 小红书 / 内容主编 | 小红书新图文视觉、封面重做、完整视觉改版、风格判断、统一视觉母版和图像提示词；发布动作仍归平台发布角色 |
| `guizang-social-card-skill` | UI/PPT / 小红书 / 公众号发布 | 小红书小型/旧流程社交卡和公众号封面素材生产；发布动作仍归平台发布角色 |
| `xhs-publish-assistant` | 小红书 | 小红书发布前复制包整理：标题、正文、标签、配图目录、标签数量和图片尺寸检查；不打开浏览器，不点击发布 |
| `xhs-automation-publisher` | 小红书 / 内容主编 | 小红书批量预览填充、内容数据导出、搜索/详情读取和确定性 Python/CDP 降级；交互式登录态优先走原生 Chrome，点击发布和互动动作二次授权 |
| `xhs-comment-research` | 小红书 / 内容主编 | 通过原生 Chrome 登录态读取和分析小红书评论，不再加载仓库维护的 JS selector 片段 |
| `gstack-qa-only`, `gstack-qa`, `gstack-canary` | QA | Web/UI 行为验证、窄范围修复闭环、发布门禁 |
| `gstack-cso` | 安全 | 基础设施优先的安全态势审查 |
| `gstack-setup-deploy`, `gstack-land-and-deploy` | 运维 / 架构 | 部署规划和发布门禁；远程生产事实仍交给 Hermes |
| `gstack-document-*`, `gstack-learn`, `gstack-retro`, `delivery-document-package` | 总控 / 架构 / 开发 / QA / 文档/交付 | 文档、发布说明、交付材料、经验沉淀、复盘 |

本仓库不内置上游 gstack 的浏览器/设计二进制运行时，也不自动开启遥测、cookie 导入或 host routing 注入。需要上游完整运行时能力时，单独按上游仓库安装，不把这些运行时文件混入本公开 skills 仓库。

## 推荐协作流

### 新需求

1. 先开或继承 `总控` 窗口，除非用户明确要求直接进入某个专业角色。
2. `总控` 读取项目上下文，判断需求类型、风险、模型预算、是否需要多角色，并先选择任务规模和 loop 深度：`tiny` 可自办，`small` 可直派 `开发`，`medium` 走负责人层，`large` 启动完整角色团队，`critical` 启动 L3 门禁。生成器随后统一计算有效控制值：`large` 至少为 L2，`critical`、critical/extreme risk 或显式 L3 统一进入 L3；模型、Spark 资格和 Token Profile 都使用这一结果。
3. 一旦进入总控管理流，原则是总控只直接对接负责人层：`架构 / CTO`、`内容主编`、`知识库`、`技能维护`，必要时 `文档/交付`；只有 `tiny` 低风险局部小改动可以总控自办，只有 `small` 单一、短、小、可验证的低风险开发任务可以总控直派 `开发`。
4. 总控/架构/多角色/派发/回调/台账类任务必须先读取已安装的 `agent-role-orchestrator/SKILL.md` 和项目 `.codex/role-windows.md`；若台账缺失或不可读，状态写 `待确认`，不要编造线程 ID。项目允许写入时，优先用 `ensure_project_role_files.py --write` 创建或刷新 `AGENTS.md` 托管规则块和初始台账模板。
5. 技术复杂需求交给 `架构 / CTO` 输出 3-5 个可行技术路线的选型简报，再进入下游实施。
6. 新本地代码项目由 `架构 / CTO` 默认先用 `check_codegraph.py --project <path>` 检查 CodeGraph；未初始化时在允许写入的前提下初始化并重查，未安装时提示安装，或在环境允许且安装方式明确时做用户级静默安装。
7. 技术需求确认到足以描述问题后，`架构 / CTO` 先做有边界的开源/可借鉴方案扫描；若网络不可用、用户禁用或上下文敏感，要写明跳过原因。
8. 内容任务由 `内容主编` 判断是否拆给 `公众号发布`、`小红书`、`视频` 或 `UI/PPT` 视觉资产协作。
9. `总控`、`架构`、`内容主编` 只在必要时输出下游提示词，并写清模型建议、文件范围、禁止范围、验证和回调；脚本可用时优先用 `render_role_prompt.py` 生成骨架。
10. 已建立过的角色默认走 `继承` / `接续`，不要重复新建窗口；`.codex/role-windows.md` 中已有线程 ID 时必须复用。
11. 下游角色完成、阻塞或需要发起方决策时，用 `压缩回调` 默认回调任务发起窗口；不无条件回报给 `总控` 或 `架构`。
12. 完成、阻塞或需要发起方决策时，必须同时完成两件事：更新 `.codex/role-windows.md` 并提交；向来源 thread 主动发送 `压缩回调`。仅完成第 1 项不算闭环。
13. 当前窗口没有发送工具时，最终输出必须以 `<codex_delegation>` 或 `压缩回调` 开头，供系统/用户转发。
14. 每次派发、回调、阻塞、完成、误开或纠偏后，更新 `.codex/role-windows.md` 的最新结果、下一步和循环状态。
15. 只有明确需要并行时才开 `开发1号`、`开发2号` 这类编号角色。

Loop 深度：

| 深度 | 链路 | 适用 |
| --- | --- | --- |
| `L0` | 用户 -> 执行角色 | 用户明确指定角色、低风险小任务 |
| `L1` | 总控 -> 负责人层 | 需要目标、路线、风险判断，但暂不需要多角色执行 |
| `L2` | 总控 -> 负责人 -> 执行角色 -> 负责人 -> 总控 | 普通复杂任务 |
| `L3` | L2 + 独立门禁 | 关键 PR、发布、生产、账号、安全、DBA、公开声明等高风险任务 |

任务规模：

| 规模 | 默认路径 | 边界 |
| --- | --- | --- |
| `tiny` | 总控自办 | 低风险、局部、可验证的小改动；出现跨文件设计、测试脚本、验收脚本或风险升级时转负责人层 |
| `small` | 总控直派 `开发` | 单一、短、小、可验证的低风险开发任务；出现架构判断、跨文件整合或风险升级时回流 `架构 / CTO` |
| `medium` | 总控 -> 负责人层 | 需要目标、路线、风险判断，但暂不需要完整团队 |
| `large` | 完整角色团队 | 负责人拆给执行角色并回流总控 |
| `critical` | L3 门禁团队 | 关键 PR、发布、生产、账号、安全、DBA、公开声明等高风险任务 |

总控不默认写代码、测试脚本、验收脚本或自动化验证脚本；超过 `tiny` 自办和 `small` 直派开发边界的产物交给 `开发` 或 `测试`，由 `架构` / `QA` 复核证据。

有效路由速查：

| 输入示例 | effective controls | auto profile | 预期行为 |
| --- | --- | --- | --- |
| `medium + normal + L1` | `normal + L1` | `compact` | 负责人或普通开发小闭环 |
| `large + normal + L1` | `normal + L2` | `standard` | 负责人拆执行并收敛 |
| `critical + normal + L1` | `critical + L3` | `full` | 高风险模型与独立门禁 |
| `medium + normal + L3` | `critical + L3` | `full` | 显式深链路同步提升风险 |

`--profile` 只控制 Prompt 字段量，不负责降低风险、模型或 Loop。默认始终使用 `--profile auto`；critical/L3 不应用显式 compact/standard 删除门禁字段。完整推导和指标格式见 [路由、Token 与 Skill 评估指南](routing-token-and-evaluation.md)。

### 路由前检查

`总控`、`架构`、`内容主编` 每次派发前必须自检：

- 是否读取 agent-role-orchestrator？
- 是否读取 `.codex/role-windows.md`？
- 是否复用已有角色线程？
- 是否选择最小可行 loop 深度？
- 是否输出任务分发决策？
- 总控是否只对接负责人层？
- 是否写清模型建议/覆盖？
- 是否写清 source-window callback？
- 是否写清允许/禁止范围？
- 是否写清验证与提交要求？
- 是否包含技能路由台账？
- 是否需要更新 `.codex/role-windows.md`？

### Fail-Closed 工具层

`agent-role-orchestrator` 的规则分两层：Markdown 负责原则和角色边界；脚本负责台账、模板、字段、枚举、统计和校验。

生成角色提示词：

```bash
python skills/agent-role-orchestrator/scripts/ensure_project_role_files.py \
  --project /path/to/project \
  --write
```

```bash
python skills/agent-role-orchestrator/scripts/render_role_prompt.py \
  --role 开发 \
  --objective "实现订单列表筛选修复" \
  --source-role 架构 \
  --source-thread thread-123 \
  --task-size small \
  --profile auto \
  --required-skill gstack-investigate \
  --validation "npm test"
```

校验台账、提示词或回调：

```bash
python skills/agent-role-orchestrator/scripts/validate_role_loop.py \
  --project /path/to/project \
  --prompt /path/to/prompt.md \
  --callback /path/to/callback.md
```

检查 CodeGraph 状态：

```bash
python skills/agent-role-orchestrator/scripts/check_codegraph.py \
  --project /path/to/project
```

聚合技能命中率：

```bash
python skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py \
  /path/to/callbacks-or-ledgers \
  --json
```

校验路由评估集，并用实际选择记录评分：

```bash
python scripts/evaluate_skill_routing.py --validate-only --strict
python scripts/evaluate_skill_routing.py --observed /path/to/observed.jsonl --strict
```

`observed.jsonl` 每行只记录 case id 和这次实际选择的 Skill；无需 Skill 的 case 必须传空数组：

```json
{"id":"no-skill-arithmetic","selected_skills":[]}
{"id":"role-window-routing","selected_skills":["agent-role-orchestrator"]}
```

`--strict` 会在 case 未观测、评分失败或观测格式错误时返回非零。它不会自动启动 Codex；应由真实任务、外部 runner 或人工审计先产出 `selected_skills`。

校验失败时不要派发、继续或关闭 loop；先补齐缺失字段，或把不确定状态明确写成 `待确认` 并说明原因。

`.codex/role-windows.md` 推荐使用固定表格：

```markdown
| 角色 | 状态 | thread id | 来源窗口 | 当前职责 | 下一步 | 循环状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 总控 | 待确认 | 待确认 | 用户 | 入口分流、模型预算、最终验收 | 待确认 | 待总控分流 |
| 架构 | 待确认 | 待确认 | 总控 | CTO 技术拆解和技术角色闭环 | 待确认 | 待架构拆解 |
| 内容主编 | 待确认 | 待确认 | 总控 | 内容域分流和平台角色闭环 | 待确认 | 待内容主编拆解 |
```

表格后保留 `压缩交接卡`：最近摘要、关键决策、当前证据、下一步、新窗口接续提示。长任务和多轮返工都从这里接续，不要求新窗口读取完整旧线程。

### 技能命中和 Token 压缩

- `总控` 为全局多角色任务维护轻量 `技能路由台账`；`架构` 维护技术子树台账；`内容主编` 维护内容子树台账。
- 下游角色完成、阻塞或需要决策时，用 `技能命中回传` 说明已加载并使用、来源窗口要求但未使用、临时发现应补用、误召/无效加载和真正影响产出的 skill。
- 来源窗口验收时必须检查 `技能命中回传`；缺失时退回补 callback，不算闭环完成。
- 多窗口 loop 默认用 `压缩回调`，只传当前状态、本轮变化、证据链接/文件/命令、需要决策、下一回流对象和可复用优化沉淀状态。
- 负责人层关闭技术或内容子树前，必须确认 `.codex/role-windows.md` 已更新并提交，且来源 thread 已收到压缩回调；如果没有发送工具，回调输出必须以 `<codex_delegation>` 或 `压缩回调` 开头。
- 当上下文接近过长、remote compact 失败、或同一任务跨多个 PR/闭环时，优先开新窗口或接续既有角色窗口；输入只用 `.codex/role-windows.md`、压缩交接卡、提交/PR、文件证据和必要短摘要。
- 生成下游提示词时使用 Token Budget Profile：`compact` 给 tiny/small 和普通 medium 小闭环；`standard` 给 large、L2、架构或新代码项目；`full` 给 critical、L3、关键 PR、对抗审查、高风险公开声明、生产/数据/安全闭环，并增加独立复核、失败回退和 go/no-go 字段。`render_role_prompt.py --profile auto` 是默认入口，显式 `--profile` 覆盖自动分级。
- `agent-role-orchestrator/SKILL.md` 只加载稳定闭环契约；角色边界、模型分级、工具路由、内容平台规则按需读取 `references/role-cards.md`、`model-routing.md`、`tool-routing.md`、`content-routing.md`，避免无关角色说明进入每个窗口上下文。PR 校验会限制入口文件行数和字节数。
- 有回调文件或台账快照时，用 `aggregate_skill_hits.py` 聚合自报命中、声明覆盖、回调完整和有效使用率；只有含路由声明或技能回调的 eligible 文件进入分母，普通 Markdown 会被忽略。没有必选声明时命中率是 `null`，不是 0% 或 100%；回传为误召却未声明已加载的 skill 必须作为数据不一致单列。
- 用 `evaluate_skill_routing.py` 对代表性输入和实际 `selected_skills` 做离线评分，并同时覆盖“应该命中”和“不应加载任何 skill”的负样本。重点同时看 `required_skill_recall`、`negative_case_pass_rate`、`unexpected_skills` 和 `unevaluated_case_count`，不要只追一个命中率。
- `总控` 负责本次任务的全局路由判断和聚合视图；`架构` 与 `内容主编` 负责各自子树。长期的漏召、误召、触发描述过期、registry 漂移、README 说明混乱或跨角色 token 过重，转给 `技能维护`。
- `技能维护` 只沉淀可公开复用的 skill 体系改进，不接收项目私有 `.codex/role-windows.md`、本机 memory、账号登录态或生产细节。

### 模型路由默认值

`总控` 或 `架构` 创建新窗口、接续已有窗口时，应尽量显式写清 model 和 thinking。已开窗口可以在后续消息里覆盖 model/thinking，但只影响之后的回复。

| 角色 | 默认模型 |
| --- | --- |
| `总控 / CEO` | `gpt-5.6-terra` + `high`；资金、上线、生产恢复、跨角色最终 go/no-go 升 `gpt-5.6-sol` + `xhigh` |
| `架构 / CTO` | `gpt-5.6-sol` + `high`；实盘架构、事故根因、DB/并发/安全、不可逆方案升 `xhigh`；自动路由不选 Max/Ultra |
| `开发负责人 / Dev Lead` | `gpt-5.6-terra` + `high`；live exit、资金安全、PnL/fee、并发、重复失败返工升 `gpt-5.6-sol` + `xhigh` |
| `开发执行 subagent` | 窗口内一次性 worker。纯机械单文件：`gpt-5.4-mini` + `high`；边界清楚、可独立验证的有限语义任务：`gpt-5.6-luna` + `high`；跨文件业务语义：`gpt-5.6-terra` + `high`；live/资金/并发/账本不下放，由 Dev Lead 用 Sol + xhigh 处理 |
| `Spark Opportunity Lane` | Spark 当前可用且独立预览额度有剩余时，mechanical/bounded 一次性开发 executor 可用 `gpt-5.3-codex-spark` + `high`；未确认可用时回退 Mini/Luna，不承担 owner、集成、最终 QA 或高风险任务 |
| `QA` | 普通验收：`gpt-5.6-terra` + `high`；关键 PR / 对抗式审查 / 发布门禁：`gpt-5.6-sol` + `xhigh` |
| `运维` / `DBA` | 只读采证、容量、锁、空间分析：`gpt-5.6-terra` + `high`；部署、restart、rollback、生产故障、DDL、清理、恢复、数据风险：`gpt-5.6-sol` + `xhigh` |
| `知识库` / `技能维护` / `文档/交付` | 默认 `gpt-5.6-terra` + `high`；纯索引、排版、搬运、registry 机械同步：`gpt-5.4-mini` + `medium` |
| `UI/PPT` / `内容主编` / 内容执行角色 | 默认 `gpt-5.6-terra` + `high`；机械 HTML/资产整理：`gpt-5.4-mini` + `high`；公开高风险定位、声明或合规：`gpt-5.6-sol` + `xhigh` |

部分 Codex 界面可能为符合条件的模型或账号提供 Max/Ultra。它们不进入本体系的自动默认值；只有用户明确选择、当前界面确认可用，并通过代表性 eval 证明额外成本有效时才使用。

### 开发团队

推荐用 Codex 本地窗口承接：

- `架构 / CTO` 拆分后的代码实现。
- `开发` 默认是 `开发负责人 / Dev Lead`：用 `gpt-5.6-terra` + `high` 拆解任务、整合结果、纠偏、最终验证和提交；live exit、资金安全、PnL/fee、并发或重复失败返工升 `gpt-5.6-sol` + `xhigh`。
- `开发执行 subagent` 是当前开发负责人窗口内的一次性 worker：纯机械单文件用 `gpt-5.4-mini` + `high`；边界清楚、可独立验证的有限语义任务用 `gpt-5.6-luna` + `high`；跨文件业务语义用 `gpt-5.6-terra` + `high`。不写入 `.codex/role-windows.md`，任务结束后关闭，不作为角色窗口复用。
- 不要让低成本 subagent 独立承担长任务负责人、架构判断、跨文件整合、最终提交或完整上下文恢复；live/资金/并发/账本工作必须由 Dev Lead 使用 `gpt-5.6-sol` + `xhigh` 处理。
- 开发全过程默认遵循第一性原理：先还原目标、事实、约束/不变量、最小可证伪假设、最小改动和验证证据，再动手实现。
- 长任务或容易 compact 的任务先由 Dev Lead 写任务卡，包含目标、文件白名单、禁止范围、验证命令、预期输出和回调对象，再派发给开发执行 subagent。
- 默认串行；普通并行最多 2 个 worker，且必须声明互斥范围和独立验证。3-5 个 worker 只允许显式 `parallel` profile，并通过 `--worker-count`、`--disjoint-scope` 和 `--independent-validation` fail-closed 校验。
- Spark 是独立额度机会通道，不是稳定第五级：仅在当前可用性已确认时，用 `--prefer-spark --spark-available` 把 mechanical/bounded 一次性 executor 路由到 Spark/high；否则回退 Mini/Luna。Spark 任务必须显式给出验证命令，不承担 owner、跨文件集成、最终 QA、critical/high-risk 或长上下文任务。
- 前端/UI/PPT/社交卡/视频产物；纯前端或视觉保真任务默认先由 `UI/PPT` / `UI/Frontend` 加载 `ui-implementation-workflow`：选择单一页面类型，审计现有组件/Token/相邻页面。营销、品牌、作品集或内容页在现有系统不足时按需读取内置 `references/visual-direction.md`；后台、表单、列表和配置页不加载。`design-taste-frontend` 仅把旧调用转入这一 reference，不再启动第二套流程。旧审美偏好停用；用户或指定审核者对实际截图的明确反馈从空白基线写入 `.codex/ui-visual-review-signals.md`，先作为 raw 审核证据，不自动成为长期或跨项目偏好。完整记录参考站但每轮只激活 `small` 最多 1 份、`medium+` 最多 3 份职责互斥参考，先输出 UI implementation plan，再按结构 -> 数据/交互 -> 响应式 -> 字体/颜色 -> 装饰 -> 动效实现，最后在 1440/768/390 截图、修复并重截。效果不满意时只替换失败职责位；有预览图时再比较 CSS/组件、资产、Canvas/SVG、Three.js/WebGL、Lottie/视频或成熟库。
- 公众号文章和小红书笔记的草稿、预览、发布包和明确授权后的发布自动化。
- 交付文档包和个人知识库整理。
- 仓库测试、QA、Review 准备。
- 安全代码审计和低影响黑盒报告。

开发窗口必须带上：

- 文件白名单。
- 禁止范围。
- 验证命令。
- 提交/PR 要求。
- 回调/通知规则。
- `技能命中回传` 字段。
- `压缩回调` 字段。
- 可复用优化沉淀三态：`无` / `建议` / `已沉淀`。
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

数据库实例主因要从 `运维` 分流到 `DBA`：例如 datadir/tmp/binlog/WAL 容量、InnoDB/事务/锁、长 COMMIT/rollback、备份恢复、DDL、分区归档或高风险清理。`DBA` 的第一轮仍然只读；kill、purge、DDL、resize、restore、cleanup 等动作必须拿到发起方或用户的二次授权。

### 内容发布团队

`公众号发布` 和 `小红书` 是独立内容发布角色：

- 可以由 `总控` 分流到 `内容主编`，再由 `内容主编` 拆给平台角色；也可以通过 `$agent-role-orchestrator` 单独唤起具体平台角色。
- `公众号发布` 默认使用 `wechat-ai-app-ops` 处理 AI 应用公众号文章、周刊连续性、图文排版和草稿箱 API。
- `公众号发布` 需要技术选题搜索和初稿时可使用 `wechat-tech-writer`；需要 Markdown 到微信 HTML 排版时可使用 `wechat-article-formatter`。
- X MCP 内容研究源可用于爆款内容研究、热点扫描、选题池、对标账号和公开讨论脉络；默认由 `内容主编` 统筹，平台角色继承结论或在被明确指派时只读使用。官方文档：https://docs.x.com/tools/mcp
- X MCP 默认禁止发帖、发布 Article、关注/取关、点赞、转发、私信、账号设置、书签变更和任何互动/写操作；真实访问需要 X Developer app、OAuth 和本机 `xurl mcp`，不得把 `CLIENT_ID`、`CLIENT_SECRET`、token、cookie 或账号状态写入仓库。
- `小红书` 在需要选题评分、对标账号学习、盲预测、发布后复盘或增长判断时使用 `cheat-on-content`；没有 `.cheat-state.json` 的内容项目应先初始化该 workflow。
- `小红书` 在需要读取、总结、分类评论区或从评论派生选题/回复策略时使用 `xhs-comment-research`，先由 `browser-automation-router` 选择原生 Chrome 登录态，且不读取 cookie、token、local storage 或浏览器 profile 文件。
- `小红书` 新建图文视觉、封面重做或完整视觉改版时默认使用 `xhs-visual-director`，先输出风格判断、统一视觉母版、视觉确认图和最终图片/提示词记录。
- `小红书` 需要登录检查、浏览器预览填充或发布卡点排查时，先用 `browser-automation-router` 选择原生 Chrome；批量预览、内容数据导出、搜索/详情读取或原生插件不可用时，再使用 `xhs-automation-publisher` 的 Python/CDP 命令。脚本默认先用 `--preview` 或 `cdp_publish.py fill`，因为 `publish_pipeline.py` 缺少 `--preview` 会点击发布。
- `xhs-automation-publisher` 的 `click-publish`、评论/回复、点赞收藏、切号、清 cookie、删除 profile 等动作必须对目标账号和具体动作二次授权；cookie、二维码、真实账号名、Chrome profile 路径和账号状态不得写入仓库。
- `内容主编` 负责 `反老登味 / 反 AI 味内容闸门`：正式对外文案不得有说教、爹味、上位者口吻、油腻成功学、年龄/资历压人、替读者下判断，也不得有模板化、空泛排比、万能套话、机械转折、过度总结和没有个人判断的 AI 味。
- `小红书`、`公众号发布`、社交卡/封面/落地页文案和视频脚本只要输出正式对外中文内容，就必须先使用 `humanizer-zh` 做人味化和去 AI 痕迹处理，但不得借此新增事实、数据、价格、背书或发布时间。
- `story-deslop` 只在内容本身是小说、叙事正文、剧情片段或对话场景时按需使用；普通公众号文章和小红书笔记仍默认走 `humanizer-zh`，避免被改成网文腔。
- `公众号发布` 在交给用户最终发布前提醒默认保留 `原创`、`赞赏`、`留言`，留言优先使用“留言自动精选公开”；不要声称脚本已开启只能在发布面板手动确认的选项。
- `小红书` 在用户说“输出发布格式”“准备发布”“二次编辑发布格式”时使用 `xhs-publish-assistant`，只输出可复制标题、正文、标签、配图目录和发布前检查，不接管平台页面；发布标题必须检查 20 字以内。
- 默认只做草稿、预览、发布包、素材检查和自动化步骤准备。
- 最终发布、群发、删除、账号设置、凭据变更等动作必须有用户明确授权。
- 视觉资产生产仍可交给 `UI/PPT`，特别是公众号封面、小红书图文组图和社交卡；小红书新视觉默认走 `xhs-visual-director`，小型旧流程社交卡可走 `guizang-social-card-skill`。
- 平台账号、登录态、token、cookie 和后台权限不随本仓库同步，必须在目标机器或目标账号环境单独配置。

### 技能维护

`技能维护` 是 skill 体系的维护角色，不是普通产品开发角色：

- 适合处理 skill 命中率统计、触发描述调优、角色卡拆分/合并建议、`registry/skills.json`、README、source policy 和使用文档维护。
- 默认读取 `agent-role-orchestrator` 规则、相关 role cards、registry、README/docs 和来源治理说明，再根据 `技能路由台账` 与 `技能命中回传` 判断是否需要改 skill。
- 可维护 AGENTS.md / `.codex/role-windows.md` 顶部的可复用入口规则模板，但具体线程 ID、项目状态和私有台账只留在目标项目。
- 输出必须说明命中问题、改动文件、为什么是可复用改进、验证结果和 PR/commit 信息。
- 不替代 `总控`、`架构` 或 `内容主编` 做本次任务决策，不替代 `开发` 实现产品，不把项目私有状态同步进公开仓库。

### 文档/交付和知识库

- `文档/交付` 使用 `delivery-document-package` 维护客户交付包，包括交付清单、演示脚本、验收表、变更确认、操作指南和交接文档。
- `文档/交付` 不替代 `QA` 的验收风险判断、`测试` 的正式测试报告、`开发` 的实现事实，也不提供法律/税务最终意见。
- `知识库` 负责个人笔记库、Obsidian vault、索引/MOC、标签、链接和高风险笔记边界整理。
- `知识库` 默认不删除、不公开、不大规模移动/改写私人笔记；涉及医疗、投资、法律、税务或安全类笔记时，只做个人记录和待验证事项整理。

### 测试和 QA

`测试` 和 `QA` 不合并：

- `测试` 负责正式测试资产，例如 Excel 测试用例、Word/DOCX 测试报告、测试证据包。
- `测试` 在被指派时也负责独立压力/负载/性能/并发验证，但必须先确认目标环境、数据隔离、流量上限、停止条件、指标和证据保存方式。
- `QA` 负责变更是否可验收、是否可 Review、是否存在 blocker、是否缺少关键验证，并默认用对抗式审查主动寻找反例、边界、回归面、证据缺口和过度声明。

如果一个任务同时需要测试报告、压测证据和 Review readiness，先让 `总控` 或 `架构` 拆成 `测试` 与 `QA` 两个提示词，避免职责混在一起。

## 安装建议

Codex 本地开发机默认只安装 `codex-skills-core`。当前任务涉及哪个域，再启用对应插件；跨域任务可以组合启用，任务结束后无需让所有 domain 长期常驻。插件命令、包边界和旧平铺安装迁移见 [plugin-packaging.md](plugin-packaging.md)。

插件机制暂不可用时，只把当前任务需要的 canonical skill 整体复制到 `$HOME/.agents/skills`。不要默认复制全部，也不要同时保留同名插件 skill 和平铺 skill；先用 `audit_plugin_context.py --scan-user-roots` 检查重复项。

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
5. 更新 `registry/skills.json`、`registry/plugin-packages.json`、`README.md` 和必要 docs。
6. 运行 `python3 scripts/sync_plugin_bundles.py --write` 生成插件副本。
7. 运行 `python3 scripts/test_plugin_packages.py`、`python3 scripts/validate_plugins.py` 和 `python3 scripts/validate_public_skills.py`。
8. 做敏感信息扫描。
9. 中文提交并推送。

## 使用口诀

- 新需求先过 `总控`。
- 总控先选 loop 深度，不默认走最长链路。
- 总控只找负责人层，技术找架构，内容找主编。
- 技术复杂需求交给 `架构 / CTO` 看多条技术路线，选定路线再拆下游。
- 新本地代码项目由 `架构 / CTO` 先检查或初始化 CodeGraph，未安装则提示安装或在可行时静默安装。
- `架构 / CTO` 确认技术需求后，先做有边界的开源/可借鉴方案扫描，再决定是否拆给技术下游角色。
- 内容任务交给 `内容主编` 管平台、账号、文案、视觉资产和发布授权。
- 代码和产物交给 Codex。
- 远程生产事实交给 Hermes 只读查。
- 公众号和小红书默认先草稿/预览，最终发布必须显式授权。
- 测试报告归 `测试`。
- 验收阻塞归 `QA`。
- 外部 skill 记来源，Hermes skill 先脱敏。
