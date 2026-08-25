# 角色编排 Token 效率实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框跟踪进度。

**目标：** 在保留 fail-closed 回调、角色边界和高风险门禁的前提下，降低 agent-role-orchestrator 的常驻上下文与多窗口提示词开销。

**架构：** 主 `SKILL.md` 只保留入口、核心路由和按需 reference 索引；角色细节继续放在 `references/role-cards.md`。提示词生成器按角色和风险组合字段，新增 Luna 并行执行档，禁止无条件 3-5 worker 扇出。

**技术栈：** Markdown、Python 标准库、现有 fail-closed 校验脚本。

---

### 任务 1：锁定 token-first 行为

**文件：**
- 修改：`scripts/test_role_system_tools.py`
- 修改：`scripts/validate_role_system.py`

- [ ] 先添加失败测试：`extreme` 只能输出 `xhigh`，不允许 `max`。
- [ ] 添加 Luna 路由测试：明确、低风险、有限语义的开发 subagent 使用 `gpt-5.6-luna + high`。
- [ ] 添加并行门禁测试：默认 1 worker，普通并行最多 2；3-5 仅在显式 parallel profile、文件不重叠、验证独立时允许。
- [ ] 添加提示词体积预算：compact 不超过 90 行和 6000 UTF-8 bytes；critical QA 不出现 CodeGraph/开源扫描/技术方案占位。
- [ ] 添加 SKILL 体积预算：主文件不超过 350 行和 30000 UTF-8 bytes。
- [ ] 运行 `python scripts/test_role_system_tools.py`，确认因缺少新行为失败。

### 任务 2：实现模型与并行路由

**文件：**
- 修改：`skills/agent-role-orchestrator/scripts/render_role_prompt.py`

- [ ] 将架构 extreme 从 `max` 改为 `xhigh`。
- [ ] 增加 executor tier：Mini 机械执行、Luna 明确有限语义、Terra 跨文件业务语义、Sol 高风险 owner。
- [ ] 增加 `--execution-profile serial|parallel`、`--worker-count`、`--disjoint-scope`、`--independent-validation` 参数。
- [ ] fail-closed 校验并行前置条件，默认 serial/1 worker。
- [ ] 按角色决定输出块；单一执行角色不输出 owner 路由台账，QA 不输出架构占位。
- [ ] 运行角色工具测试并确认通过。
- [ ] 提交生成器与测试。

### 任务 3：拆薄主技能并同步文档

**文件：**
- 修改：`skills/agent-role-orchestrator/SKILL.md`
- 修改：`skills/agent-role-orchestrator/references/role-cards.md`
- 创建：`skills/agent-role-orchestrator/references/content-routing.md`
- 创建：`skills/agent-role-orchestrator/references/tool-routing.md`
- 修改：`README.md`
- 修改：`docs/role-usage.md`
- 修改：`registry/skills.json`

- [ ] 主 SKILL 只保留核心入口、角色树、loop、model、callback、token profile 和 reference 路由。
- [ ] 将内容平台 gate 移至 `content-routing.md`，工具清单移至 `tool-routing.md`。
- [ ] role card 保留角色边界，不重复完整核心规则。
- [ ] 文档加入 Luna 可选并行档和“Mini 仍是最低成本机械执行器”的边界。
- [ ] 更新 registry 摘要并运行体积预算测试。
- [ ] 提交文档与 skill 瘦身。

### 任务 4：部署与验证

**文件：**
- 同步：`%USERPROFILE%\.codex\skills\agent-role-orchestrator\`

- [ ] 运行 `python scripts/test_role_system_tools.py`。
- [ ] 运行 `python scripts/validate_role_system.py`。
- [ ] 运行 `python scripts/validate_public_skills.py`。
- [ ] 运行 `git diff --check`。
- [ ] 生成总控、架构、开发、QA、知识库提示词，记录新体积。
- [ ] 同步本机安装目录并用本机生成器复验。
- [ ] 推送分支并创建新的可读 PR。

### Addendum：Spark 独立额度机会通道

- `gpt-5.3-codex-spark` 不进入四级稳定路由，只作为 research preview 机会通道。
- 仅允许 mechanical/bounded、短小、text-only、可独立验证的一次性开发 executor。
- 通过 `--prefer-spark --spark-available` 显式启用；未确认可用时回退 Luna。
- Spark 不承担 owner、semantic 集成、最终 QA、critical/high-risk 或长上下文任务。
- 任务卡必须显式给出验证命令，脚本负责 fail-closed 校验。
