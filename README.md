# Codex Skills

一套可安装、可验证、可跨项目继承的 **role-based agent workflow**。它不是 prompt 合集：`agent-role-orchestrator` 先让 `总控 / CEO` 判断目标、范围、风险和预算，再由 `架构 / CTO`、`内容主编` 或其他负责人组织执行角色闭环。

核心设计亮点：CEO-first 入口、可折叠多窗口 Loop、来源窗口主动回调、Fail-Closed Tool Layer、按需 skill 路由、模型与 Token 预算、可量化的技能命中率，以及可复用优化沉淀。

详细资料：[技术亮点与设计取舍](docs/technical-highlights.md) · [插件拆包与安装](docs/plugin-packaging.md) · [跨机器安装与更新](docs/plugin-update-guide.md) · [路由、Token 与 Skill 评估](docs/routing-token-and-evaluation.md) · [角色与运行规则](docs/role-usage.md) · [机器可读 skill 清单](registry/skills.json) · [来源治理](docs/source-policy.md) · [新增 skill](docs/add-skill.md)

## 30 秒上手

推荐把仓库注册为插件 marketplace。`core` 是唯一默认包，其余领域包按当前任务启用：

```bash
codex plugin marketplace add Dirtytrii/codex-skills --ref main
codex plugin add codex-skills-core@dirtytrii-codex-skills
codex plugin add codex-skills-engineering@dirtytrii-codex-skills
```

也可以在 Codex 桌面的 Plugins 面板添加该 marketplace，并按任务安装领域包。CLI 安装显式执行 `plugin add codex-skills-core`，不要只依赖 marketplace 的默认安装标记。若只做总控分流、浏览器能力选择或项目压力测试，保持默认 `core` 即可；其他机器的日常刷新见[跨机器安装与更新](docs/plugin-update-guide.md)。

| 包 | 安装策略 | 适用任务 |
| --- | --- | --- |
| `codex-skills-core` | 默认 | 总控/角色路由、浏览器路由、项目压力测试 |
| `codex-skills-engineering` | 按需 | 架构、开发、测试、QA、工程发布 |
| `codex-skills-operations` | 按需 | 运维诊断、安全、部署前后门禁、恢复规划 |
| `codex-skills-content` | 按需 | 内容研究、写作、公众号、小红书与发布准备 |
| `codex-skills-visual-delivery` | 按需 | UI、视觉资产、PPT、PDF 与交付文档 |

内容配图、UI 文案等跨域任务先审计组合；未超预算时可以同时启用多个 domain，超出时拆成带压缩交接的阶段任务。不要把所有包长期常驻；可同时检查预估目录开销和旧平铺安装重复项：

```bash
python scripts/audit_plugin_context.py --plugin codex-skills-content --scan-user-roots --strict
```

插件机制不可用时，仍可从 canonical `skills/` 复制所需目录到 `$HOME/.agents/skills`；这是兼容路径，不再推荐一次安装全部。目录必须整体复制，不能只拿 `SKILL.md`。安装后在新任务中使用：

```text
使用 $agent-role-orchestrator，先按总控角色梳理这个需求，并选择最小安全 Loop、负责人和模型预算。
```

也可以单独唤起：`架构`、`内容主编`、`开发`、`UI/PPT`、`测试`、`QA`、`安全`、`DBA`、`运维`、`公众号发布`、`小红书`、`视频`、`知识库`、`技能维护`、`文档/交付`。

## 角色与任务流

体系分成三层：

| 层次 | 职责 | 事实来源 |
| --- | --- | --- |
| 角色编排 | 入口分流、任务规模、模型预算、台账、回调、最终验收 | `agent-role-orchestrator` |
| 能力执行 | 技术、内容、视觉、测试、运维等角色按需加载 skill | `skills/*` |
| 治理继承 | 来源、公开边界、registry、校验、跨机器同步 | `registry/skills.json`、`docs/*`、`scripts/*` |

```text
总控 / CEO
├─ 架构 / CTO
│  ├─ 开发、UI/PPT、测试、QA、安全、DBA、运维
├─ 内容主编
│  ├─ 公众号发布、小红书、视频、UI/PPT 视觉协作
├─ 知识库
├─ 技能维护
└─ 文档/交付
```

`总控只直接对接负责人层`。技术执行默认由 `架构 / CTO` 派发和验收，内容执行默认由 `内容主编` 派发和验收；总控负责项目结果、范围、优先级、风险和最终 go/no-go，不默认写代码、测试脚本或验收脚本。

Loop 深度按任务折叠，而不是默认走最长链路：

| 深度 | 链路 | 适用 |
| --- | --- | --- |
| `L0` | 用户 -> 执行角色 | 明确、低风险的小任务 |
| `L1` | 总控 -> 负责人层 | 只需路线、风险或结果判断 |
| `L2` | 总控 -> 负责人 -> 执行 -> 负责人 -> 总控 | 普通复杂交付 |
| `L3` | L2 + 独立门禁 | 关键 PR、发布、生产、账号、安全、数据库或公开声明 |

总控在行动前输出 `任务分发决策`：`tiny` 可自办，`small` 可直派一个短小开发任务，`medium` 交负责人判断，`large` 启动完整团队，`critical` 进入 L3 门禁。

生成器会先统一输入值，再选择模型与 Prompt：

| 输入 | 负责决定 | 关键规则 |
| --- | --- | --- |
| `task-size` | 默认组织路径 | `large` 至少 L2；`critical` 进入 L3 |
| `risk` | 风险和模型余量 | critical/extreme 进入 L3 与高风险路由 |
| `loop-depth` | 角色链路深度 | 显式 L3 会把普通风险提升为 critical |
| `profile` | Prompt 字段量 | 默认 `auto`；不应拿 compact 删减高风险门禁 |

因此 large 默认得到 L2 + standard，critical 默认得到 critical risk + L3 + full。模型、Spark 资格、Loop 和 Profile 使用同一组 effective controls，不会各自猜测。完整推导、命令和指标解释见 [路由、Token 与 Skill 评估指南](docs/routing-token-and-evaluation.md)。

多窗口闭环遵循来源窗口：A 派 B，B 回 A；B 再派 C，C 回 B。完成、阻塞或需要决策时必须同时更新并提交 `.codex/role-windows.md`，并向来源 thread 主动发送压缩回调；`仅完成台账更新不算闭环`。没有发送工具时，以 `<codex_delegation>` 或 `压缩回调` 开头供转发。

## Fail-Closed Tool Layer

Markdown 管原则和角色边界，脚本管固定字段、枚举、模板、状态和统计。校验失败时不继续派发或关闭 Loop。

| 脚本 | 作用 |
| --- | --- |
| `ensure_project_role_files.py` | 检查或创建 `AGENTS.md` 与 `.codex/role-windows.md` 托管规则 |
| `render_role_prompt.py` | 按角色、风险、来源、范围、模型和 Token 档位生成 prompt |
| `validate_role_loop.py` | 校验台账、prompt、回调和技能命中字段 |
| `check_codegraph.py` | 检查新代码项目的 CodeGraph 可用性和初始化状态 |
| `aggregate_skill_hits.py` | 仅从含路由声明或技能回调的文件聚合自报命中、漏召、有效使用、真实误召和不一致回传 |
| `evaluate_skill_routing.py` | 对实际选择做离线评分，覆盖应命中与无需 Skill 的负样本 |
| `audit_skill_catalog.py` | 递归检查 Skill 目录、描述预算和隐式调用策略 |

角色运行脚本位于 `skills/agent-role-orchestrator/scripts/`；目录审计和路由评估属于仓库级 PR 工具，位于 `scripts/`。典型用法：

```bash
python skills/agent-role-orchestrator/scripts/ensure_project_role_files.py --project /path/to/project --write
python skills/agent-role-orchestrator/scripts/render_role_prompt.py --role 开发 --objective "修复订单筛选" --source-role 架构 --profile auto --validation "pytest"
python skills/agent-role-orchestrator/scripts/validate_role_loop.py --prompt /path/to/prompt.md --callback /path/to/callback.md
python scripts/evaluate_skill_routing.py --validate-only --strict
```

生成后先看 `任务控制`、`模型建议` 和 `Token Budget Profile` 是否一致。统计时区分三层：目录审计只证明 Skill 可发现；回调聚合只反映角色自报；路由评分需要外部提供实际 `selected_skills`，当前脚本不会自动运行 Codex。无需 Skill 的负样本也必须保持空选择，用来发现过度加载。

新本地代码项目由架构先运行 `check_codegraph.py`，技术方案确认后再做有边界的开源/可借鉴方案扫描。项目台账有 thread id 就复用，状态不明写 `待确认`，不能靠聊天记忆编造。

## 稳定模型路由与 Spark 机会通道

长期 owner 使用稳定路由：

| 角色 | 默认 | 升级条件 |
| --- | --- | --- |
| `总控 / CEO` | `gpt-5.6-terra` + `high` | 资金、上线、生产恢复、跨角色最终 go/no-go：Sol/xhigh |
| `架构 / CTO` | `gpt-5.6-sol` + `high` | 实盘架构、事故根因、DB/并发/安全、不可逆方案：xhigh |
| `开发负责人 / Dev Lead` | `gpt-5.6-terra` + `high` | 资金、账本、PnL/fee、并发、重复返工：Sol/xhigh |
| `QA`、`运维`、`DBA`、内容与治理 owner | `gpt-5.6-terra` + `high` | 关键门禁、生产/数据风险、高风险公开声明：Sol/xhigh |

`开发执行 subagent` 是当前开发窗口内一次性 worker，不写入角色台账、不长期复用：

| Executor tier | 模型 | 边界 |
| --- | --- | --- |
| `mechanical` | `gpt-5.4-mini` + `high` | 单文件、规格和测试明确、无业务判断 |
| `bounded` | `gpt-5.6-luna` + `high` | 边界清楚、有限语义、可独立验证 |
| `semantic` | `gpt-5.6-terra` + `high` | 跨少量相关文件，需要业务语义 |
| `high-risk` | `gpt-5.6-sol` + `xhigh` | 由 Dev Lead 亲自处理，不下放廉价 executor |

`Spark Opportunity Lane` 不是稳定第五级。Spark 当前可用且独立预览额度有剩余时，mechanical/bounded executor 可用 `gpt-5.3-codex-spark` + `high`；通过 `--prefer-spark --spark-available` 显式启用，未确认可用时回退 Mini/Luna。它不承担 owner、跨文件集成、最终 QA、critical/high-risk 或长上下文任务，并且任务卡必须显式运行验证命令。

默认串行。并行必须有互斥范围和独立验证；3-5 个 worker 只能显式使用 `--execution-profile parallel --worker-count N --disjoint-scope ... --independent-validation ...`，不会因为“任务很大”自动扩散。

Token Budget Profile 控制 prompt 体积：`compact` 用于 tiny/small 和普通 medium 小闭环，`standard` 用于 large、L2、架构或新项目，`full` 用于 critical、L3 与高风险门禁，并额外要求独立复核、失败回退和 go/no-go 决策方。显式 `--profile` 优先于自动路由。上下文预算只传状态增量、证据句柄、决策和下一回流对象；长任务依靠台账、提交、PR 和压缩交接卡接续。

## 能力路由

角色只加载当前任务需要的能力，不把所有 skill 塞进一个超级 prompt：

| 任务 | 推荐入口 |
| --- | --- |
| 技术规划、实现、评审、发布 | `架构 / CTO` + `gstack-*`，执行角色按任务加载调查、Review、QA、Ship 方法 |
| 浏览器交互与登录态复用 | `browser-automation-router`：应用内 Browser 处理公开页/localhost，Chrome 插件复用现有登录态；Playwright 留给 CI/回归 |
| UI、网页 PPT、社交卡 | `UI/PPT` + [`ui-implementation-workflow`](skills/ui-implementation-workflow/SKILL.md)：统一页面分类、按需视觉方向、预览图实现路线选择、参考台账与失败维度动态换源、设计规则/Token、骨架优先和 1440/768/390 截图闭环；旧审美偏好停用，实际截图反馈从新基线记录为原始审核信号；`design-taste-frontend` 仅保留为旧名称兼容入口 |
| 公众号 | `wechat-ai-app-ops`、`wechat-tech-writer`、`wechat-article-formatter` |
| 小红书 | `xhs-visual-director`、`xhs-publish-assistant`、`xhs-automation-publisher`、`xhs-comment-research`、`cheat-on-content` |
| 中文正式对外文案 | `social-text-websense-gate` + `反老登味 / 反 AI 味内容闸门` + `humanizer-zh`；叙事按需用 `story-deslop` |
| 测试与安全 | `test-case-report-builder`、`playwright`、`authorized-blackbox-web-security` 或 Codex Security 系列 |
| 运维与数据库 | 只读诊断 skills + 运维/DBA 角色；写操作和危险动作单独授权 |
| 知识、交付、技能治理 | 知识库、文档/交付、技能维护角色按边界处理 |

浏览器能力从 Codex Desktop `2026-06-11` 发布版本起作为最低能力门槛，并且必须在当前任务中实际检测到 Browser/Chrome 插件；完整路由和旧版降级见 [docs/browser-automation.md](docs/browser-automation.md)。

内容分支保留三道明确门禁：

- **X MCP 内容研究源**：由内容主编统筹爆款、热点、选题和对标账号研究；默认只读，官方文档为 https://docs.x.com/tools/mcp，写操作另行授权。
- **内容语气闸门**：正式对外中文先去掉说教、爹味、模板化和 AI 味，再用 `humanizer-zh`；不改变事实、数据、来源、授权或发布状态。
- **小红书自动化发布门禁**：`xhs-automation-publisher` 默认预览/填充；发布、评论、点赞、收藏、切号等动作必须二次确认，cookie 与账号状态不进仓库。

skill 命中通过回调量化：负责人声明候选/必选/可选/跳过，下游回传实际使用、漏召、误召和产出影响。长期触发漂移、README/docs 混乱和跨角色 Token 过重由 `技能维护` 收敛，不让总控或架构长期背负。

## 仓库与维护

```text
skills/                         可安装 skill；每个目录包含 SKILL.md 及按需 references/scripts/assets
registry/skills.json            active skill、来源、维护归属和角色消费关系
registry/plugin-packages.json   core/domain 唯一归属、依赖和默认安装策略
plugins/                        从 skills/ 生成的 Codex 插件 bundle；禁止直接维护
.agents/plugins/marketplace.json 仓库级插件 marketplace
docs/technical-highlights.md    角色编排、Loop、Token 和 Fail-Closed 的设计取舍
docs/plugin-packaging.md        插件安装、拆包边界、迁移和上下文审计
docs/plugin-update-guide.md     跨机器安装、缓存刷新、新任务验证和回滚
docs/routing-token-and-evaluation.md  路由推导、模型/Profile、指标和评估输入格式
docs/role-usage.md              完整角色边界、模型、回调和平台运行规则
docs/source-policy.md           local / external-github / hermes 来源治理
scripts/validate_public_skills.py 公开 skill 总校验入口
scripts/validate_role_system.py    角色体系、README 和工具契约校验
```

仓库只同步可公开复用内容，不提交 token、密钥、cookie、登录态、生产日志、服务器真实路径、本机 memory、项目私有台账或插件运行时。

常规维护：从实际使用发现问题，优先沉淀到对应 skill；跨角色规则交给 `技能维护`；同步 registry/docs；运行：

```bash
python scripts/test_role_system_tools.py
python scripts/test_plugin_packages.py
python scripts/sync_plugin_bundles.py --check
python scripts/validate_plugins.py
python scripts/validate_role_system.py
python scripts/validate_public_skills.py
git diff --check
```

提交保持小颗粒、中文说明，并通过 PR 合并。完整流程见 [docs/publication-checklist.md](docs/publication-checklist.md)。
