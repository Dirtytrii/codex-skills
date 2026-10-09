# 路由、Token 与 Skill 评估指南

可靠性回归与成本对照入口：`python scripts/test_skill_contract_regressions.py`；`python scripts/evaluate_task_economy.py --observed /path/to/observations.jsonl`。没有真实记录时后者报告 not_evaluable，不自动修改模型默认值。

这份文档回答三个容易混在一起的问题：任务应该走多深的角色 Loop、应该使用哪一档模型和 Prompt，以及 Skill 是否真的选对。角色边界仍以 `agent-role-orchestrator` 为准；这里解释脚本输入、有效值和指标口径。

在角色路由之前，先做插件层路由：默认仅保留 core，当前任务需要哪个领域再启用哪个 domain。`prepare_role_window.py` 根据角色和必选 Skill 查询包注册表，插件未启用时阻断 Prompt 生成；`audit_plugin_context.py` 用于估算所选插件目录并发现旧平铺安装重复项。包边界见 [plugin-packaging.md](plugin-packaging.md)。

## 一条统一决策链

`prepare_role_window.py` 是角色派发入口；插件前置检查通过后，它调用 `render_role_prompt.py`。底层生成器不应分别猜测模型、Loop 和 Profile。推荐决策顺序是：

```text
原始输入
  task-size + risk + loop-depth + role + delegation-policy + executor-tier
      ↓
effective controls
  effective risk + effective loop
      ↓
执行路由
  owner/executor + model/thinking + Spark eligibility
      ↓
Token Budget Profile
  compact / standard / full
      ↓
角色 Prompt
  范围 + 验证 + 回调 + 技能台账 + 必要门禁
```

四个常用输入的职责不同：

| 输入 | 控制什么 | 不控制什么 |
| --- | --- | --- |
| `--task-size` | 默认组织路径和最小 Loop 深度 | 不直接代表代码行数 |
| `--risk` | 风险升级、模型余量和独立门禁 | 不等同于任务规模 |
| `--loop-depth` | 角色链路深度 | 不应单独绕过风险升级 |
| `--profile` | 生成 Prompt 的字段量 | 不降低 effective risk、模型或 Loop |

默认使用 `--profile auto`。显式 Profile 是兼容和诊断入口；它可以改变 Prompt 体积，因此不要用 `compact` 或 `standard` 删减 critical/L3 任务需要的门禁字段。

## Effective Controls

脚本先把原始输入收敛为一组有效控制值：

| 原始条件 | effective risk | effective loop | auto profile |
| --- | --- | --- | --- |
| `tiny/small/medium + normal + L0/L1` | 保持输入 | 保持输入 | `compact` |
| `large + normal + L0/L1` | `normal` | 至少 `L2` | `standard` |
| `task-size=critical` | 至少 `critical` | `L3` | `full` |
| `risk=critical|extreme` | 保持输入 | `L3` | `full` |
| 显式 `loop-depth=L3` 且普通风险 | 提升为 `critical` | `L3` | `full` |
| `role=架构` 或 `--new-code-project` | 按风险 | 按有效 Loop | 至少 `standard` |

自动提升只向更安全的方向发生。生成结果中的 `任务控制` 会同时显示输入值、有效值和提升原因，验收时以有效值为准。

## 隐性规划契约

规划契约和模型、Loop、Profile 使用同一组 effective controls，但不新增用户命令或角色：

| task-size | 默认契约 | Token 约束 |
| --- | --- | --- |
| `tiny` | route-only | 不做仓库审计，不建持久计划 |
| `small` | outcome/task brief | 只写范围、验证和升级条件 |
| `medium` | owner contract | owner 补目标、非目标、证据、风险和回调 |
| `large` | implementation spec | CTO 规格 + Dev Lead 零上下文执行卡 |
| `critical` | gated spec | 增加独立门禁、失败回退、剩余风险和 go/no-go |

角色分工固定为：总控决定规划深度，CTO 做 scoped Recon/Vet，Dev Lead 编译任务卡并集成复验，executor 只执行，QA 只做 evidence review。完整全库或多类别 audit 必须显式请求；`large` 只提高规格完整度，不自动提高审计广度或 worker 数量。任务卡优先传文件、符号、commit 和测试句柄，只有承载决策时才内联短代码，避免同一上下文在窗口间重复支付 Token。

典型命令：

```bash
# 普通、边界清楚的开发负责人任务
python skills/agent-role-orchestrator/scripts/prepare_role_window.py \
  --role 开发 --source-role 架构 \
  --objective "修复订单筛选" \
  --task-size medium --profile auto

# large 自动进入 L2 + standard
python skills/agent-role-orchestrator/scripts/prepare_role_window.py \
  --role 开发 --source-role 架构 \
  --objective "完成三个相关模块的集成交付" \
  --task-size large --profile auto

# critical 自动进入 risk=critical + L3 + full，并使用高风险模型路由
python skills/agent-role-orchestrator/scripts/prepare_role_window.py \
  --role QA --source-role 架构 \
  --objective "关键 PR 发布门禁" \
  --task-size critical --profile auto
```

## Owner、Executor 与模型

长期窗口负责上下文所有权，窗口内 subagent 只负责一次性任务：

| 类型 | 默认职责 | 典型模型层级 |
| --- | --- | --- |
| Owner | 拆解、取舍、集成、纠偏、最终验证和回调 | Terra/high 或 Sol/high |
| Mechanical executor | 单文件、规格完整、验证明确 | Luna/high |
| Bounded executor | 边界清楚、有限语义、可独立验证 | Luna/high |
| Semantic executor | 少量相关文件和业务语义 | Terra/high |
| High-risk owner work | 资金、账本、并发、生产、不可逆操作 | Sol/xhigh |

critical/high-risk 工作不得为了省额度下放给廉价 executor。Spark 只是一条显式机会通道：必须是 mechanical/bounded、当前可用、短小、text-only 且有独立验证；否则回退稳定层级。

开发派发另有独立契约：`forbidden` 禁止下放，`optional` 由串行 Dev Lead 在叶子任务资格内判断，`required` 必须使用至少一个一次性 executor；`auto` 根据具体禁止文本、风险、executor tier 和并行 profile 收敛。耗时长只影响任务卡和接续，不是派发条件。每次回调记录是否派发、实际模型、任务卡/证据、重试和 Dev Lead 复验，才能判断低成本路由是否真的生效。

自动路由有意封顶 `xhigh`。产品界面可能为符合条件的模型或账号显示 Max/Ultra，但只有用户明确选择、当前界面确认可用，并通过代表性 eval 证明额外成本有效时才使用。

## 三层 Skill 评估

“目录是否健康”“角色说自己用了什么”“给定输入是否选对”是三类指标，不能合并成一个命中率。

| 层次 | 工具 | 回答的问题 | 不能证明 |
| --- | --- | --- | --- |
| 目录审计 | `audit_skill_catalog.py` | Skill 是否可发现、描述是否超预算、隐式策略是否合理 | 某次任务真的选对 |
| 回调聚合 | `aggregate_skill_hits.py` | 角色自报的必选、加载、漏召、误召和有效使用 | 路由器独立判断正确 |
| 离线评分 | `evaluate_skill_routing.py` | 给定代表性 case 和实际 `selected_skills` 后是否符合预期 | Codex 已被自动运行 |

当前 `evaluate_skill_routing.py` 是离线评分器，不是实际调用 Codex 的 runtime runner。真实运行观测需要外部 runner 产生 `selected_skills`，再交给它评分。

## 回调聚合口径

只有包含 `必选 skill` 声明或至少一个技能回调字段的文件才是 eligible 文件。普通 Markdown、会议记录和无关说明会被发现但不进入指标分母。

最小可统计回调：

```markdown
技能路由台账：
- 必选 skill：agent-role-orchestrator

技能命中回传：
- 已加载并使用：agent-role-orchestrator
- 来源窗口要求但未使用：无
- 临时发现应补用：无
- 误召/无效加载：无
- 影响产出的 skill：agent-role-orchestrator
```

指标解释：

| 字段 | 含义 | 常见误读 |
| --- | --- | --- |
| `hit_rate` | 实际加载的必选 Skill / 已声明必选 Skill | 未声明必选时是 `null`，不是 0% 或 100% |
| `routing_declaration_coverage` | 有必选声明的 eligible 文件占比 | 低值先检查负责人是否声明，不直接怪执行角色 |
| `skill_callback_completeness` | 五个回调字段齐全的回调文件占比 | 只以含回调的文件为分母，纯路由台账不拉低它 |
| `effective_use_rate` | 真正影响产出的已加载 Skill / 总加载 Skill | 属于自报效果，不是独立质量评分 |
| `misfire_rate` | 已加载且回传为误召的 Skill / 总加载 Skill | 未加载却写成误召会进入异常记录，不污染该比率 |
| `misfire_not_loaded_skill_count` | 回传为误召但未声明加载的数据不一致数 | 表示回调质量问题，不是真实误召 |

```bash
python skills/agent-role-orchestrator/scripts/aggregate_skill_hits.py \
  /path/to/callbacks --json
```

## 离线路由评分

评估 case 定义必选、允许和禁止 Skill。无需 Skill 的负样本把 `required_skills` 与 `allowed_skills` 都留空；任何选择都会被记为 unexpected。

```json
{"id":"no-skill-arithmetic","selected_skills":[]}
{"id":"role-window-routing","selected_skills":["agent-role-orchestrator"]}
```

```bash
python scripts/evaluate_skill_routing.py --validate-only --strict
python scripts/evaluate_skill_routing.py \
  --observed /path/to/observed.jsonl --strict
```

`--strict` 会在观测缺失、case 失败或观测格式错误时返回非零。重点同时看：

- `required_skill_recall`：应加载的 Skill 是否被选中；
- `negative_case_pass_rate`：无需 Skill 时是否克制；
- `unexpected_skills`：是否出现未允许的过度加载；
- `unevaluated_case_count`：是否有 case 没有真实观测。

## 推荐验收顺序

### 风险与压缩是两条轴

显式 compact/standard 不能删除有效 L3 的四项门禁；适用的 CodeGraph 检查也必须保留。一次性 executor 使用独立短卡，不写角色台账、不提交、不再派发；负责人继续负责集成、最终复验和闭环。

高风险父任务下只试点机械文档/非可执行 fixture 叶子，使用 `--parent-risk` 保留父任务事实，而非把高风险实现改标为低风险。参数、证据与路径限制见 [model-routing.md](../skills/agent-role-orchestrator/references/model-routing.md#isolated-assets-under-a-high-risk-parent)。生成器校验输入和范围形状，不替代负责人确认隔离性，也不执行文件系统权限隔离。

### 真实质量与消耗对照

JSONL 每条记录代表相同 case/contract 下的一种完整工作流，不是一名 worker：

- `case_id`、`contract_id`：相同目标、基线、验收和边界；重复试验使用不同 case_id。
- `variant`：direct 或 delegated；后者总量必须覆盖负责人拆卡、全部 worker、复验和返工。
- `quality_pass`、`safety_pass`：明确布尔值；`retries`：非负整数。
- `actual_models`：所有实际参与者的 model/thinking 对象列表；不要填推荐值冒充实际值。
- `total_tokens`：同一宿主计量口径的完整非负整数总量；不可取得时填 null，不能用字符估计补齐。
- `evidence`：可审查的测试/运行证据句柄，不放密钥、账号详情或完整聊天。

至少 3 个完整配对才给人工复核候选；缺数据返回 not_evaluable，安全/质量失败或返工上升拒绝通过。仅比较 Token，不推断价格或会员额度；脚本不证明输入证据真实，不自动修改模型默认值。不得把测试 fixture 当 observed。

### 验收步骤

1. 用代表性任务生成 Prompt，检查 effective controls 与模型/Profile 是否一致。
2. 用 `validate_role_loop.py` 检查 prompt、台账和 callback 契约。
3. 用 `aggregate_skill_hits.py --json` 看自报执行质量和数据一致性。
4. 用实际 `selected_skills` 跑离线路由评分，分别观察 recall 与负样本通过率。
5. 只有持续漏召、误召或过度加载才调整 Skill 描述或路由；不要为提升单一指标而加载更多 Skill。
