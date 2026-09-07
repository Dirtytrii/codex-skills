# Skill 体系可靠性与经济性实施验收

日期：2026-09-07。基线：`088ffee`；实现：`015066e`。结论：源仓库和生成包的确定性验收通过；不代表已经部署到用户安装目录或验证了真实模型降本。

## 已完成

| 提交 | 结果 |
| --- | --- |
| `1f700f4` | CodeGraph 严格校验 initialized、pendingChanges 和 worktreeMismatch；未知类型不再冒充最新 |
| `8b94291` | executor 独立短卡；禁止提交、台账写入和再派发；L3 与适用 CodeGraph 门禁不随压缩丢失 |
| `2b7395a` | gstack 27 个方法改显式入口；宠物 v1/PDF 保留兼容；收窄内容触发；增加只读配置诊断与 6 条路由用例 |
| `015066e` | 高风险父任务下的受控文档/fixture 机械叶子；质量优先的成对消耗评估器；补负例和操作说明 |

宠物/PDF 原流程移入 references，脚本和旧资产未删除。没有复制或宣称验证本机另一份 v2 实现。

## 自验结果

- full 审计：catalog、public_skills、role_system、plugins、bundle_sync、routing_cases、contract_tests、role_tests、plugin_tests 共 9 项全部通过，required_failures 为空。
- 新增契约回归：12 个测试方法通过，包含 executor tier/profile 矩阵、L3 risk/loop/profile 矩阵、权限字段篡改/重复、CodeGraph 畸形数据、叶子路径和禁派边界、配置缺依赖与成本记录质量门禁。
- 原有角色工具回归通过；8 个插件打包测试通过；7 个治理测试通过。
- 68 个顶层、15 个子 Skill 校验通过；27 条路由用例结构合法。路由用例并未进行真实模型回放。
- canonical/bundle 同步通过；`git diff --check` 通过。
- 过程中先看到 CodeGraph 和 executor 反例失败，再修复至通过。完整校验曾发现固定措辞和文档预算问题，已修复，未放宽预算。

复验命令（仓库根）：

```bash
python -B skills/skill-system-governance/scripts/audit_skill_system.py --repo . --mode full --json --timeout 60
python -B scripts/test_skill_system_governance.py
python -B scripts/evaluate_task_economy.py
git diff --check
```

## 可测量变化

- 用相同参数 `--role 开发 --objective 修改单个常量 --task-size small --executor-tier mechanical` 比较基线与当前生成器：1,953 → 986 字符，减少约 49.5%。不是 Token 或费用比例。
- 全部自维护包的隐式候选：81 → 52；开发方案 core+engineering：38 → 11。所有 83 个入口仍保留可调用能力。
- 开发方案原始目录估算仍为 7,880 字符（含显式入口），隐式目录估算为 2,866。宿主实际注入量可能不同。

## 未实施及剩余不确定性

- 未改用户配置、已安装缓存、业务项目、外部 agent-reach 或独立 RoleFlow 仓库；没有推送、合并或执行 marketplace/plugin 升级。以上效果是源版本的结果，必须发布/升级并开启新任务后再核对真实可见目录。
- 本机配置仍显式开启五个自维护插件。只读诊断报告启用事实及拟用方案，不擅自切换全局配置影响其他任务。
- `routing_observed`、`skill_hits`、真实会员额度节省为 `not_evaluable`。成本评估器只处理提供的观测，不证明证据真实性；缺数据、质量下降或返工增加不能通过。
- 高风险叶子仅试点文档与非可执行 fixture；隔离性必须由负责人核实，路径检查不是操作系统沙箱，更不代表高风险实现可以降级。
- 未自动降低常规模型的 reasoning effort，未进行付费图像生成或真实宠物/PDF 端到端制作。

下一步发布时应合并源变更、升级插件、用新任务验证入口与 executor 短卡，再采集脱敏真实任务对照；不能把本次静态验收充当运行降本结论。
