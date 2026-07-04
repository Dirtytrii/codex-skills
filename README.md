# Codex Skills

个人沉淀的 Codex skill 体系。它不是普通 prompt collection，而是一套可跨机器继承的 **role-based agent workflow**：用 `agent-role-orchestrator` 先由 `总控 / CEO` 做入口分流，再让 `架构 / CTO`、开发、UI、内容发布、运维、DBA、安全、测试、QA、文档/交付、知识库、技能维护等角色按边界工作。

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
使用 $agent-role-orchestrator，先按总控角色梳理这个需求，并判断是否需要架构/开发/UI/内容主编/公众号发布/小红书/测试/DBA/运维窗口。
```

常用单独唤起：

```text
使用 $agent-role-orchestrator，给我总控窗口。
使用 $agent-role-orchestrator，给我架构窗口。
使用 $agent-role-orchestrator，给我内容主编窗口。
使用 $agent-role-orchestrator，给我公众号发布窗口。
使用 $agent-role-orchestrator，给我小红书窗口。
使用 $agent-role-orchestrator，给我 DBA 窗口。
使用 $agent-role-orchestrator，给我技能维护窗口。
```

## 这套体系解决什么

传统 prompt collection 的问题是：每个 prompt 都能回答，但很难组织复杂工作，也很难把一次项目里的经验变成下一次默认行为。本仓库把 skill 组织成三个层次：

| 层次 | 作用 | 代表内容 |
| --- | --- | --- |
| 角色编排 | 先判断需求、拆分窗口、维护回调和闭环状态 | `agent-role-orchestrator` |
| 方法与工具 | 给不同角色装上合适的方法论或操作能力 | `gstack-*`、`wechat-*`、`cheat-on-content`、`test-case-report-builder` 等 |
| 治理与继承 | 说明来源、边界、安装、公开同步和敏感信息规则 | `registry/skills.json`、`docs/*`、校验脚本 |

核心默认行为：

- 新需求默认先过 `总控 / CEO`，由总控判断是否进入 `架构 / CTO`、`内容主编`、`知识库`、`技能维护` 或专业角色。
- 角色树是可折叠组织结构，不是每次强制最长链路；总控先选择 `L0`/`L1`/`L2`/`L3` loop 深度。
- 进入总控管理流后，总控只直接对接负责人层：`架构 / CTO`、`内容主编`、`知识库`、`技能维护` 和必要时 `文档/交付`。
- `架构 / CTO` 管技术交付闭环：开发、UI/Frontend、测试、QA、安全、DBA、运维。
- `内容主编` 管内容闭环：公众号发布、小红书、视频和 UI/PPT 视觉资产协作。
- 新本地代码项目默认检查或初始化 CodeGraph。
- 技术需求确认后，`架构 / CTO` 先做有边界的开源/可借鉴方案扫描。
- 有预览图/参考图的 UI 任务先由 `UI/PPT` 做 `预览图实现路线选择`，在 CSS/组件、图片/生成资产、Canvas/SVG、Three.js/WebGL、Lottie/视频、现成库之间选型，再进入开发。
- 总控/架构/多角色/派发/回调/台账类任务必须先读取 `agent-role-orchestrator` 和项目 `.codex/role-windows.md`。
- `总控` 维护全局技能路由和模型预算台账，`架构` 维护技术子树台账，`内容主编` 维护内容子树台账。
- 机械字段、提示词模板、CodeGraph 状态、台账状态、回调完整性和技能命中统计优先交给 `agent-role-orchestrator/scripts/` 做 fail-closed 校验。
- `开发` 默认是 `开发负责人 / Dev Lead`：用 `gpt-5.5` + `xhigh` 拆解、集成、纠偏和最终提交；`gpt-5.3-codex-spark` + `xhigh` 只作为短小可验证的开发执行 subagent。
- `QA` 默认做对抗式审查：主动找反例、边界、回归面、证据缺口和过度声明。
- 新建或接续角色窗口时默认写清 model/thinking 路由。
- 已建立角色默认继承/接续，不重复开新窗口。
- 下游完成、阻塞或需要决策时，先更新并提交 `.codex/role-windows.md`，再向来源 thread 主动发送压缩回调；仅完成台账更新不算闭环。
- 当前窗口没有发送工具时，最终输出必须以 `<codex_delegation>` 或 `压缩回调` 开头，方便系统/用户转发给来源窗口。
- 闭环结束要写 `可复用优化沉淀：无 / 建议 / 已沉淀`。

## 技术亮点

### 1. CEO-First Gateway

`agent-role-orchestrator` 的默认入口是 `总控 / CEO`。它先澄清目标、判断价值和风险、决定是否值得开多窗口、选择模型/思考档，再把任务派给 `架构 / CTO`、`内容主编`、`知识库`、`技能维护` 或直接专业角色。

### 2. CEO/CTO Role Tree

新的角色体系直接分成管理层和执行层：

```text
总控 / CEO
├─ 架构 / CTO
│  ├─ 开发
│  ├─ UI/PPT / UI/Frontend
│  ├─ 测试
│  ├─ QA
│  ├─ 安全
│  ├─ DBA
│  └─ 运维
├─ 内容主编
│  ├─ 公众号发布
│  ├─ 小红书
│  ├─ 视频
│  └─ UI/PPT 视觉资产协作
├─ 知识库
└─ 技能维护
```

`总控` 类似 CEO，管入口、优先级、任务规模、角色路由、模型预算和最终验收。它可以顺手处理 `tiny` 低风险局部小改动，也可以把 `small` 单一开发任务直接交给 `开发`；但普通以上任务必须先交给负责人层。`架构` 类似 CTO，管技术方案和开发/UI/测试/QA/安全/DBA/运维闭环。`内容主编` 管公众号、小红书、视频和视觉资产协作。

Loop 深度按任务折叠：

| 深度 | 链路 | 适用 |
| --- | --- | --- |
| `L0` | 用户 -> 执行角色 | 用户明确指定角色、低风险小任务 |
| `L1` | 总控 -> 负责人层 | 需要目标、风险、路线判断，但暂不需要多角色执行 |
| `L2` | 总控 -> 负责人 -> 执行角色 -> 负责人 -> 总控 | 普通复杂技术或内容任务 |
| `L3` | L2 + 测试/QA/安全/DBA/运维等独立门禁 | 关键 PR、发布、生产、账号、安全、数据库、公开声明风险 |

总控还要输出任务分发决策：

| 任务规模 | 默认路径 |
| --- | --- |
| `tiny` | 总控自办，只限低风险、局部、可验证的小改动 |
| `small` | 总控可直派 `开发`，只限单一、短、小、可验证的低风险开发任务 |
| `medium` | 总控 -> 负责人层，由 `架构 / CTO` 或 `内容主编` 判断是否拆下游 |
| `large` | 启动完整角色团队，负责人拆给执行角色并回流总控 |
| `critical` | 启动 L3 门禁团队，加入测试/QA/安全/DBA/运维等独立复核 |

总控不默认追开发细节，也不默认写测试脚本、验收脚本或自动化验证脚本；超过 `tiny` 自办范围或 `small` 直派开发范围的产物交给 `开发` 或 `测试`，由 `架构` / `QA` 复核证据。

### 3. Multi-Window / Role-Based Loop Engineering

这套设计把多个 Codex 窗口当作长期角色，而不是一次性聊天。每个角色只承接自己的职责，反馈进入下一轮闭环。

```text
用户目标
→ 总控分流 / 模型路由
→ 架构或内容主编拆解 / 派发
→ 执行角色窗口执行
→ QA 或发起窗口验收
→ 结构化反馈
→ 返工或决策
→ 架构/内容主编验收
→ 总控终验
→ 可复用优化沉淀
```

关键点：

- `总控` 是全局 controller，不是所有任务的执行者。
- `架构` 是 CTO，不是总入口；它负责技术交付闭环。
- `内容主编` 是内容域负责人，不替代公众号/小红书/视频执行角色。
- `开发`、`UI`、`内容发布`、`DBA`、`运维`、`测试`、`QA` 分离职责。
- `QA` 是 evaluator，不默认写测试报告，也不替开发修问题。
- 回调按任务来源流动：A 派 B，B 完成后回 A；如果 B 再派 C，C 回 B。
- 反馈默认只传状态增量、证据句柄、决策需求、下一回流对象和可复用优化，不搬运完整上下文。
- 闭环完成必须同时有台账提交和来源 thread 压缩回调；只有 `.codex/role-windows.md` 更新不算完成。

### 4. Fail-Closed Tool Layer

`agent-role-orchestrator` 不只靠 Markdown 约束。它内置一个小型 fail-closed 工具层：

| 脚本 | 作用 |
| --- | --- |
| `skills/agent-role-orchestrator/scripts/ensure_project_role_files.py` | 默认 dry-run 检查项目 `AGENTS.md` 和 `.codex/role-windows.md`，显式 `--write` 时创建或刷新托管入口规则块 |
| `skills/agent-role-orchestrator/scripts/render_role_prompt.py` | 根据角色、目标、来源窗口、风险等级和 skill 路由生成固定提示词骨架 |
| `skills/agent-role-orchestrator/scripts/validate_role_loop.py` | 校验 `.codex/role-windows.md`、角色 prompt 和压缩回调是否包含必填字段，并统计必选 skill 命中 |
| `skills/agent-role-orchestrator/scripts/check_codegraph.py` | 输出 CodeGraph 工具可用性、初始化状态、索引路径、建议动作和跳过原因，避免架构凭感觉判断 |
| `skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py` | 从回调或台账文件聚合必选命中、漏召、误召、临时发现应补用和有效产出 skill |

设计边界是：Markdown 管原则和角色边界，脚本管台账、模板、字段、枚举、统计、校验。校验失败就不应该继续派发或关闭 loop。

```bash
python skills/agent-role-orchestrator/scripts/ensure_project_role_files.py \
  --project /path/to/project \
  --write

python skills/agent-role-orchestrator/scripts/render_role_prompt.py \
  --role 开发 \
  --objective "实现订单列表筛选修复" \
  --source-role 架构 \
  --task-size small \
  --profile auto \
  --required-skill gstack-investigate

python skills/agent-role-orchestrator/scripts/validate_role_loop.py \
  --prompt /path/to/prompt.md \
  --callback /path/to/callback.md

python skills/agent-role-orchestrator/scripts/check_codegraph.py \
  --project /path/to/project

python skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py \
  /path/to/callbacks-or-ledgers
```

### 5. Skill as Capability Routing

角色不会把所有能力塞进一个超级提示词，而是按任务加载对应 skill：

| 任务类型 | 默认路由 |
| --- | --- |
| 入口分流、模型预算、最终验收 | `总控` + `agent-role-orchestrator` |
| 技术架构/规格/计划审查 | `架构 / CTO` + `gstack-*` |
| 代码实现、调查、评审 | 开发角色 + `gstack-investigate/review/ship/health` |
| UI、网页 PPT、社交卡、封面 | UI/PPT 角色 + 预览图实现路线选择 + `design-taste-frontend`、`guizang-*` |
| 内容规划和跨平台分发 | `内容主编` + 内容角色工具 |
| 爆款内容研究、热点扫描、对标账号 | `内容主编` + X MCP 内容研究源（只读、需授权，见 https://docs.x.com/tools/mcp） |
| 公众号发布 | `wechat-ai-app-ops`、`wechat-tech-writer`、`wechat-article-formatter` |
| 小红书视觉、发布与内容实验 | `xhs-visual-director`、`cheat-on-content`、`xhs-publish-assistant`、`xhs-comment-research` |
| 中文正式对外文案 | `反老登味 / 反 AI 味内容闸门` + `humanizer-zh`，叙事类再按需用 `story-deslop` |
| 运维只读诊断 | Hermes-owned 运维 skills |
| 数据库实例风险 | DBA 角色卡，危险动作二次授权 |
| 测试资产和压测验证 | `test-case-report-builder`、`playwright` |
| 安全审计 | `authorized-blackbox-web-security` 或 Codex Security 系列 |
| 技能命中复盘、registry/README/docs 调优 | `技能维护` 角色 + `agent-role-orchestrator` |

### 6. Model Routing Defaults

默认模型路由按角色分配：

| 角色 | 默认模型 |
| --- | --- |
| `总控 / CEO` | `gpt-5.5` + `xhigh` |
| `架构 / CTO` | `gpt-5.5` + `xhigh` |
| `开发负责人 / Dev Lead` | `gpt-5.5` + `xhigh` |
| `开发执行 subagent` | `gpt-5.3-codex-spark` + `xhigh`，窗口内一次性 worker，只执行单一、短、小、可验证的代码任务 |
| `QA` 普通验收 | `gpt-5.5` + `medium` |
| `QA` 关键 PR / 对抗式审查 / 发布门禁 | `gpt-5.5` + `xhigh` |
| `技能维护` / `文档/交付` | `gpt-5.3-codex-spark` + `high`，小文档可用 `gpt-5.4-mini` |
| `内容主编` / 内容执行角色 | 默认 `gpt-5.3-codex-spark` + `high`，高风险定位或公开声明升 `gpt-5.5` + `xhigh` |

新建窗口时由 `总控` 或 `架构` 显式指定 model/thinking；已开窗口优先复用，并可在后续消息里覆盖 model/thinking，覆盖只影响之后的回复。

长任务不要让 Spark 独立扛完整上下文。`开发负责人 / Dev Lead` 先写任务卡，明确目标、文件白名单、禁止范围、验证命令、期望输出和回调对象，再把短小执行片段派给 `开发执行 subagent`。这里的 subagent 是当前窗口内的一次性 worker：任务结束后关闭，不写入 `.codex/role-windows.md`，不作为角色窗口复用。最终 review、整合、纠偏、验证和提交仍由 Dev Lead 负责。

### X MCP 内容研究源

X MCP 可作为内容角色的只读研究源，用来研究爆款内容、热点话题、对标账号、公开讨论脉络和选题池。默认由 `内容主编` 统筹，`小红书`、`公众号发布`、`视频` 继承研究结论或在被明确指派时使用。

- 官方文档：https://docs.x.com/tools/mcp
- 默认只读：搜索 posts、用户、用户时间线、trends/news 和公开讨论。
- 需要授权：真实访问需要 X Developer app、OAuth 和本机 `xurl mcp` 配置；不要把 `CLIENT_ID`、`CLIENT_SECRET`、token、cookie 或账号状态写进仓库。
- 默认禁止：发帖、发布 Article、关注/取关、点赞、转发、私信、账号设置、书签变更和任何互动/写操作。
- 平台化处理：X 数据只是趋势和对标信号，不能直接等同于小红书或公众号爆款规律；最终仍要结合 `$cheat-on-content`、`$xhs-comment-research`、`$humanizer-zh` 等平台技能加工。

### 内容语气闸门

`内容主编` 负责 `反老登味 / 反 AI 味内容闸门`。公众号、小红书、视频和含公开中文文案的 UI/PPT 产物，在正式预览、发布包、复制文本、封面/社交卡或视频脚本交付前，先去掉说教、爹味、上位者口吻、油腻成功学、模板化排比和万能套话，再使用 `humanizer-zh` 做最终人味化。这个闸门只改表达，不改变事实、数据、价格、日期、来源、授权边界、背书或发布状态。

### 7. Measured Skill Routing and Token-Aware Loops

skill 变多以后，`总控` 不只派角色，也负责建立全局轻量路由台账；`架构` 维护技术子树台账，`内容主编` 维护内容子树台账。下游角色在回调里用 `技能命中回传` 报告实际使用、误召、漏召和产出影响。

多窗口路由还要求先读项目 `.codex/role-windows.md`：有线程 ID 就复用，状态不明写 `待确认`，派发/回调后更新最新结果、下一步和循环状态；误开的窗口也要记录为 `误开/废弃/纠偏`，不能靠聊天记忆跳过台账。

上下文预算规则：当窗口历史变长时，不等 remote compact 失败后再补救。`.codex/role-windows.md` 需要保留固定角色表格和 `压缩交接卡`，用最近摘要、关键决策、证据句柄、下一步和新窗口接续提示支撑续跑。回调只传增量、证据和决策需求，不搬运完整聊天记录。完成、阻塞或需来源窗口决策时，必须提交台账更新并向来源 thread 主动发送压缩回调；如果没有发送工具，最终输出必须以 `<codex_delegation>` 或 `压缩回调` 开头。

Token Budget Profile 负责把“少开窗口、少传上下文”变成可执行档位。`render_role_prompt.py --profile auto` 会按风险和 loop 深度选择 `compact` / `standard` / `full`：`compact` 用于 L0/L1 小闭环，只保留模型、来源、范围、验证、技能台账和回调字段；`standard` 用于 L2、架构或新代码项目；`full` 用于 L3、关键 PR、对抗审查、高风险公开声明或生产/数据/安全相关闭环。生成下游 prompt 时默认先用 `auto`，除非用户明确要求或负责人判断需要升级。

这让体系可以量化：

- `技能路由命中率 = 实际命中的必选 skill 数 / 来源窗口标记的必选 skill 数`
- `误召率 = 加载但最终无效的 skill 数 / 总加载 skill 数`
- `漏召数 = 任务结束后发现本该使用但没有使用的 skill 数`

长期的漏召、误召、触发描述过期、registry 漂移和 README 说明混乱，不交给 `总控` 或 `架构` 长期背锅，而是路由给 `技能维护 / Skill Curator` 专门收敛。

### 8. Source and Safety Governance

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
| `总控` | 新需求、跨域任务、多窗口协作 | 入口分流、模型预算、角色台账、最终验收 |
| `架构` / `CTO` | 技术需求、复杂技术拆分、开发闭环 | 技术选型、开源参考扫描、管理开发/UI/测试/QA 等技术角色 |
| `开发` | 代码实现、修复、项目内测试 | 按第一性原理拆解后在架构范围内改代码并验证 |
| `UI/PPT` / `UI/Frontend` | 视觉、前端体验、网页 PPT、社交卡 | 负责视觉方向、预览图实现路线选择和视觉验证 |
| `内容主编` | 公众号/小红书/视频等内容任务的上层协调 | 平台策略、账号边界、发布授权、视觉资产协作 |
| `视频` | 宣传视频、分镜、动效素材 | 产出脚本、分镜和渲染计划 |
| `公众号发布` | 微信公众号文章、草稿、预览、发布准备 | 默认草稿/预览，最终发布需授权 |
| `小红书` | 小红书笔记、图文视觉、标题标签、发布复制包 | 新图文视觉默认先走视觉导演，最终发布需授权 |
| `文档/交付` | 交付清单、验收表、演示脚本、交接文档 | 不替代 QA、开发事实或法律/税务意见 |
| `知识库` | Obsidian/个人笔记整理 | 不删除、不公开、不改写成专业建议 |
| `技能维护` | skill 命中率、触发规则、registry/README/docs 维护 | 不替代产品实现，不同步项目私有状态 |
| `运维` | 部署检查、日志、cron、服务诊断 | Hermes 优先，只读优先，写操作授权 |
| `DBA` | 容量、锁、binlog/WAL、长事务、备份恢复 | 只读诊断优先，危险动作二次授权 |
| `安全` | 授权安全审计、仓库/PR 扫描、黑盒报告 | 低影响验证，委派安全专项 skill |
| `测试` | 测试用例、测试报告、证据包、压测验证 | 不实现功能，不伪造测试结果 |
| `QA` | Review readiness、验收缺口、阻塞风险 | 对抗式审查，不默认写测试报告或替开发修复 |

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
│   ├── validate_public_skills.py
│   ├── validate_role_system.py
│   └── test_role_system_tools.py
├── skills/agent-role-orchestrator/scripts/
│   ├── aggregate_skill_hits.py
│   ├── check_codegraph.py
│   ├── ensure_project_role_files.py
│   ├── render_role_prompt.py
│   └── validate_role_loop.py
└── README.md
```

## 维护方式

常规维护流程：

1. 本机使用中发现可复用改进。
2. 优先沉淀到对应 skill；跨角色命中率、触发规则、registry/README/docs 改进交给 `技能维护`，角色编排类规则落在 `agent-role-orchestrator`。
3. 可公开复用的部分同步到本仓库，项目私有状态不进仓库。
4. 更新 `registry/skills.json` 和必要 docs。
5. 涉及角色编排时，运行 `python3 scripts/validate_role_system.py` 或 `python3 scripts/test_role_system_tools.py`。
6. 运行 `python3 scripts/validate_public_skills.py`；它会自动包含 role-system 校验。
7. 做公开发布检查，提交中文 commit，并开 PR。

更详细的新增/同步规则见 [docs/add-skill.md](docs/add-skill.md) 和 [docs/publication-checklist.md](docs/publication-checklist.md)。
