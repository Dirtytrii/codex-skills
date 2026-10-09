# 本地轻量观测验收

日期：2026-09-07。实现提交：`657130b`。这是独立于可靠性/经济性优化 PR 的后续本地观测实现，不代表已合并、发布或升级插件。

## 确定性验收

- `test_workflow_observation.py`：15 项通过，包含固定字段脱敏、关闭/未选项目不写入、异常或越界 transcript 不作为证据、父子模型区分、并发 JSONL、保留策略、惰性安全输出、增量配对、合成样本排除、安装计划只读、安装幂等与原配置保留、精确 Windows 命令的 stdin 链路。
- `quick_validate.py skills/skill-system-governance`：通过。
- `audit_skill_system.py --mode full --json --timeout 60`：10 项必选检查通过，包含新增 `observation_tests`。
- 原有治理专项 7 项测试通过；canonical 与生成 bundle 一致；`git diff --check` 通过。

## 授权本机部署验收

- 已按用户授权，为应用登记的 10 个本地项目及其 24 个已核实工作副本登记观测范围；云端与未登记项目不纳入。
- 每个项目独立开关与安装总开关均为 `true`；新增 5 个原生生命周期 hook，不修改全局 `config.toml` 或业务代码。
- 10 个项目的标记写入自验全部成功，每个项目 `.codex/telemetry/` 的数据与配置均被 Git 忽略。
- 现有 PreCompact hook 语义保留；项目原有 tracked Git 状态保留。观测数据、真实项目清单、盐和 hook 备份没有进入本仓库。
- 每项目仅写入一条 `synthetic_smoke`；汇总不把它计为真实任务。部署后读回的 `native_hook_seen` 均为 `false`。

## 尚未通过的真实运行门槛

原生 hook 首次信任须由宿主入口审阅完成。已安装和启用项目开关，但未写入信任哈希、未使用信任绕过参数，也没有宣称原生任务已触发。

因此当前结论是：**实现与本地安装自验通过，真实触发仍待首次信任与下一轮任务验证**。路由命中、任务质量、安全通过率、返工与会员额度节省仍为 `not_evaluable`，不能从生命周期 Stop 或 Token 快照推断。

操作和字段口径见 [本地轻量观测](../skills/skill-system-governance/references/local-observation.md)。原始内容不上传，不启用额外模型、后台轮询或每工具调用采集。
