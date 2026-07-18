# 技术亮点与设计取舍

这份文档解释 `codex-skills` 的系统设计。README 负责安装和快速上手；完整角色规则在 `role-usage.md`；这里专门说明为什么采用多窗口负责人体系、哪些约束由脚本执行，以及如何在可靠性和 Token 成本之间取平衡。

## CEO-First 与负责人分层

新需求默认从 `总控 / CEO` 进入，而不是直接生成一组执行窗口。

```text
总控 / CEO
├─ 架构 / CTO -> 开发、UI、测试、QA、安全、DBA、运维
├─ 内容主编 -> 公众号、小红书、视频、视觉协作
├─ 知识库
├─ 技能维护
└─ 文档/交付
```

设计目的：

- 总控只关注目标、优先级、范围、预算、风险和最终结果，避免陷入代码或平台操作细节。
- 架构负责技术方案、拆解、集成和技术角色验收，内容主编负责内容域的同类工作。
- 执行角色拿到明确白名单、禁止范围、验证和退出条件，不承担上层方向判断。
- 小任务可以折叠组织结构，不为“形式完整”制造额外窗口。

这种分层增加一次 owner 判断，但降低了范围漂移、重复返工和用户持续介入的概率。负责人层的价值不是转发消息，而是压缩信息、做取舍并承担集成责任。

## 隐性规划契约

规划不是一个需要用户记忆的命令，也不是新角色。`render_role_prompt.py` 根据角色、`task-size` 和 Token Budget Profile 自动生成最小契约：

```text
总控：价值 / 成功标准 / 非目标 / owner / 预算 / 风险
  -> CTO：Scoped Recon -> Vet evidence -> Implementation Spec
    -> Dev Lead：Zero-context executor cards -> Integrate -> Re-verify
      -> Executor：Drift check -> Execute -> Verify or STOP
    -> QA：Evidence review -> Falsify readiness
```

这里借鉴 [shadcn/improve](https://github.com/shadcn/improve) 的高能力模型负责理解与规格、低成本模型负责有界执行的思想，但按本仓库角色边界重新分配：CEO 不读代码写技术步骤，CTO 不默认实现，Dev Lead 不把集成责任下放给 subagent，QA 不生成开发计划。

为避免规划本身吞掉 Token：

- `tiny` 只保留 route-only，`small` 只生成 brief；
- `medium` 生成 owner contract，`large` 才生成 implementation spec，`critical` 再增加独立门禁和回滚/go-no-go；
- 全库、多类别、roadmap 或 branch improvement audit 必须由目标显式要求，不因任务规模自动 fan-out；
- 规格只写一次，跨窗口复用文件、符号、commit、测试和必要短片段；
- plan 是执行契约，经过实现、复验、集成和 owner 验收的交付才是产品。

完整字段、漂移检查和 STOP 条件见 [planning-contract.md](../skills/agent-role-orchestrator/references/planning-contract.md)。

## 可折叠的 Multi-Window Loop

角色树不是固定调用链。总控按风险选择最小 Loop 深度：

| 深度 | 链路 | 设计含义 |
| --- | --- | --- |
| `L0` | 用户 -> 执行角色 | 省略管理层，适合明确低风险任务 |
| `L1` | 总控 -> 负责人 | 先完成路线或结果判断，不急于拆执行 |
| `L2` | 总控 -> 负责人 -> 执行 -> 负责人 -> 总控 | 普通技术或内容闭环 |
| `L3` | L2 + 独立门禁 | 高风险工作增加 QA、安全、DBA、运维等复核 |

回调遵循 source-window，而不是所有角色都回总控：A 派 B，B 回 A；B 再派 C，C 回 B，同时 B 仍对 A 负责。

终态采用双写 fail-closed：

1. 更新并提交 `.codex/role-windows.md`；
2. 向来源 thread 主动发送压缩回调。

只写台账不算闭环，只发聊天消息也不能替代持久状态。没有跨线程发送工具时，输出以 `<codex_delegation>` 或 `压缩回调` 开头，保留可转发性。

## Fail-Closed Tool Layer

仅靠 Markdown 提示词容易漏字段、编造状态或在长上下文中失效。因此系统把职责拆成两层：

- Markdown：原则、角色边界、风险判断和业务取舍。
- Python 脚本：模板、枚举、台账、字段完整性、CodeGraph 状态和统计。

核心工具：

| 工具 | 机械保证 |
| --- | --- |
| `ensure_project_role_files.py` | 项目入口规则与角色台账存在，重复执行保持幂等 |
| `prepare_role_window.py` | 角色和必选 Skill 对应插件已启用，否则阻断派发并输出启用命令 |
| `render_role_prompt.py` | 前置检查通过后稳定生成角色、来源、模型、范围、验证和回调字段 |
| `validate_role_loop.py` | prompt、回调和台账缺字段时拒绝闭环 |
| `check_codegraph.py` | 读取真实初始化状态，避免架构凭感觉判断 |
| `aggregate_skill_hits.py` | 从产物计算技能命中、漏召和误召 |

脚本不替代负责人判断。它只保证“该填的字段存在、枚举合法、证据没有被口头状态替代”。

## Token-Aware Prompt Architecture

### Core + Domain 插件隔离

默认上下文只安装 `codex-skills-core`，工程、运维、内容和视觉交付作为独立 domain 按任务启用。`skills/` 保持唯一维护源，生成器把每个 skill 精确复制到一个插件，校验器拒绝漏包、重复归属、bundle 漂移和超预算组合。这样 Token 控制发生在任务开始前，而不是等所有 skill 描述进入目录后再依赖模型克制。

完整包边界、安装和审计命令见 [plugin-packaging.md](plugin-packaging.md)。

系统从三个层面控制 Token：

### 按需加载

`agent-role-orchestrator/SKILL.md` 只保留稳定闭环契约。角色、模型、工具和内容平台细则拆到独立 references，当前角色只读取相关文件，避免开发任务顺带加载公众号、DBA 和运维规则。

### Token Budget Profile

| Profile | 用途 | 输出策略 |
| --- | --- | --- |
| `compact` | tiny/small、普通 medium | 只保留闭环必需字段 |
| `standard` | large、L2、架构、新代码项目 | 加入必要方案与状态字段 |
| `full` | critical、L3、生产/安全/DB 风险 | 加入独立复核、失败回退、剩余风险和 go/no-go |

任务规模、风险、Loop 和 Profile 不再各自独立判断。生成器先推导 effective controls：`large -> L2+`，`critical/risk critical|extreme/显式 L3 -> L3`，然后用同一结果选择模型、Spark 资格和 Profile。

```text
task-size + risk + requested loop
              ↓
 effective risk + effective loop
              ↓
 role/executor model + Spark eligibility
              ↓
       auto Token Profile
```

这里的关键取舍是“安全控制先收敛，Prompt 体积后决定”。显式 Profile 只用于兼容或诊断，不应拿来删除 critical/L3 所需的独立门禁。可复制命令和完整提升矩阵见 [路由、Token 与 Skill 评估指南](routing-token-and-evaluation.md)。

生成器对 compact 设置行数和字节预算，QA 不接收 CTO 专属方案占位，内容角色也不会污染技术执行 prompt。

### GPT-5.6 Prompt Contract

角色 prompt 按 [OpenAI GPT-5.6 提示词指南](https://developers.openai.com/api/docs/guides/prompt-guidance-gpt-5p6) 收敛为同一契约：先写目标和完成标准，再写范围、证据、验证和退出条件。重复示例、工具说明和回调规则只保留一份；绝对措辞只用于权限、生产、发布、凭据和 fail-closed 等不可违反边界。

缺信息时只询问阻塞执行的最小字段；工具只暴露当前任务需要的能力；进度更新保持稀疏。Prompt、模型或 reasoning 默认值变更后，必须用代表性任务做对照评估，不能只凭阅读感觉判断更省或更强。

### 压缩交接

长任务不依赖完整聊天历史。台账和压缩交接卡只保留：目标、约束、当前状态、关键决策、提交/PR、验证、阻塞和下一步。新窗口从这些证据接续，避免 remote compact 失败后反复重建上下文。

## 稳定模型路由与 Spark 机会通道

模型路由把“长期 owner”和“一次性 executor”分开：

- Terra/high：大多数耐久 owner 和普通 QA。
- Sol/high 或 xhigh：架构 owner、不可逆决策、资金、账本、并发、生产和关键门禁。
- Mini/high：规格与测试明确的机械实现。
- Luna/high：边界清楚、有限语义、可独立验证的短任务。
- Terra/high executor：需要跨少量相关文件和业务语义的实现。

Spark 不进入稳定层级。它是 research preview 的独立额度机会通道，仅在当前可用性明确时用于 mechanical/bounded 一次性开发 executor。未确认可用时回退 Mini/Luna；owner、跨文件集成、最终 QA、critical/high-risk 和长上下文工作禁止使用 Spark。

自动模型策略有意止于 `xhigh`，这是本体系的成本与可预测性选择，不是声称产品不存在更高档位。Max/Ultra 仅在用户明确选择、当前界面可用且代表性评估证明收益时使用，不进入默认路由。

并行默认关闭。普通并行需要互斥范围和独立验证；3-5 worker 必须显式开启。这样不会因为模型便宜或额度独立，就把一个耦合任务拆成多个相互覆盖的上下文。

## 可量化的 Skill Routing

skill 多了以后，仅靠描述命中会产生“感觉都加载了”的错觉。系统要求负责人声明候选、必选、可选和跳过 skill，下游回调实际使用、要求但未用、临时发现、误召和真正影响产出的 skill。

回调聚合指标：

```text
必选自报命中率 = 实际使用的必选 skill / 声明的必选 skill
路由声明覆盖率 = 包含必选声明的文件 / 纳入统计的 eligible 文件
回调完整率 = 五个技能回传字段齐全的文件 / 包含技能回调的文件
有效使用率 = 真正影响产出的已加载 skill / 已加载 skill
误召率 = 已加载且回传为误召的 skill / 总加载 skill
漏召数 = 任务结束后确认本应使用但未使用的 skill 数
```

三层证据必须分开读取：

| 层次 | 证据 | 能回答 | 不能回答 |
| --- | --- | --- | --- |
| 目录审计 | Skill 元数据与描述预算 | 能否发现、是否膨胀 | 某次任务是否选对 |
| 回调聚合 | 角色产出的路由台账和回传 | 角色自报是否命中、漏召、误召 | 独立路由是否正确 |
| 离线评分 | case + 实际 `selected_skills` | 必选 recall、负样本克制、unexpected | Codex 是否已被脚本自动执行 |

`aggregate_skill_hits.py` 只统计含路由声明或技能回调的 eligible 文件；普通 Markdown 不进入分母。没有必选声明时返回 `null`，不会伪造 `100%`。回传为误召却未出现在已加载列表中的 skill 会作为不一致数据单列，不污染误召率。

`evals/skill-routing-cases.jsonl` 与 `evaluate_skill_routing.py` 是离线评分器，覆盖必选漏召、禁止误召、意外加载和无需 Skill 的负样本；它还不是自动运行 Codex 的 runtime runner。负样本通过率和必选 recall 必须一起看，否则“什么都加载”也可能制造虚假的高命中。单次异常只记录证据；持续漏召、误召、触发漂移或文档膨胀再交给 `技能维护` 修改 Skill 和 registry。

## Evidence-First Skill-System Governance

`skill-system-governance` 把以往分散在对话里的体系优化流程收成一个顶层 Core Skill，由现有 `技能维护` 角色负责，不新增角色层级。调用后默认先运行只读 quick audit，统一检查目录、公开边界、角色契约、插件归属、生成 bundle 和路由 case；full 模式再加入较慢的角色与插件回归测试。

它刻意允许 `no-change`。静态校验、实际路由观测和回调自报是三种不同证据：没有 observed routing 或 callback artifact 时，脚本返回 `not_evaluable`，模型不能把“结构正常”扩写成“命中率正常”。只有任务授权修改时，流程才从审计进入 canonical 源修复、bundle 同步、完整验证和 PR。

治理边界同样用于节省 Token：角色卡只负责把治理任务路由到该 Skill；详细审计维度按需加载；重复字段、枚举、聚合和一致性检查由脚本完成。这样不会为了“持续优化”让总控、CTO 和每个执行窗口都常驻一份治理提示词。

## 能力路由与内容门禁

角色 prompt 只描述边界，具体方法由 skill 提供。架构可以路由 gstack 方法，UI 先做预览图实现路线选择，测试与 QA 分离，运维/DBA 第一轮只读，安全能力按授权范围分流。

内容分支也采用分层门禁：

- X MCP 只作为只读趋势、选题和对标信号，不直接等同于其他平台规律。
- 内容主编负责反老登味、反 AI 味和事实边界，正式中文再使用 humanizer。
- 小红书自动化默认预览/填充；发布和互动动作需要二次授权。
- cookie、账号状态、token、生产细节和本机私有路径不进入公开仓库或回调正文。

## CodeGraph、开源参考与治理

新本地代码项目先检查 CodeGraph，让架构基于真实代码关系做判断；工具缺失或初始化失败时明确报告，不伪造“已初始化”。

复杂技术需求确认后，架构先扫描可借鉴的开源方案，再决定复用、适配或自研。扫描有明确边界，网络不可用或用户禁止时记录跳过原因。

可复用规则进入共享 skill 仓库，项目状态留在项目台账。外部 GitHub 内容保留来源，Hermes 运维经验先脱敏泛化；密钥、cookie、生产日志、本机 memory 和私有自动化不公开同步。

## 设计取舍

| 选择 | 收益 | 成本与约束 |
| --- | --- | --- |
| CEO/owner 分层 | 减少用户介入和执行漂移 | 小任务必须允许折叠，否则链路过长 |
| 隐性规划契约 | 高能力 owner 的判断可被低成本 executor 可靠消费 | 只按任务范围 Recon；完整审计必须显式触发 |
| 双写回调 | 状态可恢复、来源窗口能及时收到结果 | 需要脚本和角色共同执行 |
| 一次性 subagent | 利用低成本/独立额度做短任务 | Dev Lead 必须整合、验证和提交 |
| 按需 references | 降低固定上下文 | 文档路由必须清晰，不能隐藏关键门禁 |
| 量化 skill 命中 | 能持续调优触发和路由 | 指标必须来自产物，不能为了数字过度加载 |
| Fail-closed | 关键字段缺失时停止错误链路 | 不应把业务判断机械化 |
