# 本地轻量观测

只在用户明确授权采集/启用时使用。产品默认关闭；安装器不修改模型、插件 enable 状态、业务代码、AGENTS、角色台账或全局 `config.toml`。不启用后台轮询，也不调用额外模型。

## 接入与首次信任

采用 [Codex 原生 hooks](https://learn.chatgpt.com/docs/hooks)：`UserPromptSubmit`、`SubagentStart`、`SubagentStop`、`Stop`、`Interrupt`。不是每次工具调用埋点。只追加命令 hook，现有通知与 hook 保留；命令输出始终是 `{}`，不阻塞、批准或续跑任务。

准备私有项目清单，每项包含明确的 `root` 和已核实属于该项目的 `worktrees` 路径列表；不要提交此清单。先查看安装计划：

```bash
python scripts/install_workflow_observation.py \
  --projects /private/projects.json --install-dir /private/observation \
  --hooks-file /private/codex/hooks.json --transcript-root /private/codex/sessions
```

这里的 `scripts/` 相对本 skill 目录。授权后添加 `--enable --write` 才会安装并打开项目开关。安装器复制带内容哈希目录的独立运行时，保存原 hook 文件备份，向用户 hook 文件追加五组观测 handler；未选中的项目直接跳过。已有安装用相同参数重跑是幂等的。更换代码版本、项目范围或已有未知观测目录时先检查，不静默覆盖。

已核实的现有安装更新采集器时，使用相同清单和 transcript 范围添加 `--upgrade` 查看计划，再添加 `--write` 执行。只替换与旧哈希版本精确匹配的五个观测 handler；保留安装总开关、各项目开关、盐、匿名 ID、工作副本范围和所有既有事件，不重写项目配置。旧运行时及 hook 备份保留；遇到未知命令、被修改的旧运行时或范围变化时拒绝升级。更新后仍需由宿主重新审阅变更的 hook，不能复制旧信任哈希。

每个项目的 `.codex/telemetry/config.json` 保存独立开关，目录内 `.gitignore` 使用 `*` 排除全部观测文件。主目录与已登记工作副本共用主目录中的存储；新建工作副本不会自动纳入，需重新核实清单。全局安装清单中的 `enabled=false` 是总开关，项目配置中的 `enabled=false` 是单项目开关；两处都必须严格为 JSON 布尔 `true` 才记录。

**安装成功不等于宿主已信任。** 新增/变更 hook 须通过 Codex `/hooks` 入口审阅并信任，原生 hook 信任不可用时停在待确认；不能写自造 `trusted_hash`，不能使用绕过信任参数或伪装成 managed hook。重开/恢复任务后再核对真实事件。手动 smoke 与真实宿主事件分开标记。

## 数据口径

自动记录：UTC 时间、匿名项目/任务/轮次/子任务标识、hook 类型、采集器代码哈希、宿主模型，以及可验证的 transcript 元数据。仅在已授权 transcript 根目录中读取传入的单个 `.jsonl`，核对会话身份和项目路径，最多解析首行及末尾 2 MB；原始正文不复制、不落盘，不扫描历史会话。

- 会话与轮次 ID 使用本地随机盐 HMAC；公共仓库不保存盐、项目清单、事件或原始路径。
- `actual_model`：主任务来自宿主 hook 字段；子任务必须有匹配的子任务 transcript，不将父模型冒充子模型。
- `thinking`：只有匹配轮次的元数据可用才填写，否则 `null`。
- `usage_snapshot`：会话累计计数，不是每次调用增量。汇总只计算有起止快照的同轮次差值；缺基线、计数回退或未知结构不计入。父子统计可能重叠，不能直接相加后当作完整账单。
- `quality_pass`、`safety_pass`、`retries`、`skills_observed` 当前保持 `null`。首次接入只捕获客观生命周期；后续质量与技能命中分析必须补独立验收/路由证据，不能把 Stop 当作成功，把模型自报当作实际加载。
- 不把这些事件直接伪装成 `evaluate_task_economy.py` 所需的成对、质量已验证样本。会员额度节省始终不可直接从 Token 推断。

采集不保存 prompt、源码、工具输入/输出、最后回复、凭据、原始日志、真实项目路径或原始任务 ID。只写固定 schema，未知输入丢弃。使用跨进程文件锁防止并发 JSONL 交错；退出码保持成功，观测错误不改变开发任务行为。

输入读取以完整 JSON 为结束条件，不依赖换行或 stdin EOF，仍限制为 1 MB。采集进程内部最多等待 1.5 秒，空输入、残缺输入和慢采集到期均返回 `{}`；可能丢失该次观测，不应解释为零活动。短生命周期 daemon 仅用于当前 hook 的退出预算，不创建常驻服务。外部五个 hook 的 3 秒上限保持不变，Windows 保留已验证的 PowerShell 命令封装。

`events-YYYY-MM-DD.jsonl` 自动保留最近 30 天，事件总量上限每项目 10 MB。达到上限先移除最老日期的观测文件；当天单文件已满则停止追加，不能把缺失事件解释为零活动。只清理该观测目录中归属本采集器的日期文件，保留其他文件。

## 自验与后续分析

```bash
python /private/runtime/workflow_observation.py smoke --manifest /private/observation/installation.json
python /private/runtime/workflow_observation.py status --manifest /private/observation/installation.json
python /private/runtime/workflow_observation.py summary --manifest /private/observation/installation.json
```

`smoke` 验证所有已启用项目能写入，但标记 `synthetic_smoke` 并从真实统计剔除。`status/summary` 只汇总本地已脱敏事件，不再次读取原始会话，也不联网。

安装后至少确认：原有 hook 语义未变；目录被 Git 忽略；项目业务改动未变；精确 hook 命令能正确接收 stdin 并输出 `{}`；原生事件实际发生后有 `host_hook` 记录。没有最后一项时只能报告“安装/开关完成，原生触发尚未验证”。

输入链路回归还须覆盖：完整 JSON 无换行且 stdin 保持打开、分片 UTF-8、空或残缺输入不关闭、超限输入、采集卡住，以及精确 Windows 命令在 EOF 前完成。`subprocess.run(input=...)` 会关闭 stdin，单独通过该测试不能证明宿主输入流兼容。

源仓库回归：`python -B scripts/test_workflow_observation.py`；修改 skill 后同步 bundle 并运行 full 审计。公开材料只记录脚本行为和汇总证据，不发布真实本地事件。

## 自然闭环的结果证据

只记录已经发生的验收、返工和技能使用，不为填数据发起额外测评、模型调用或角色窗口。已启用项目的负责人/复核者在自然闭环时执行同包 `scripts/record_workflow_evidence.py --manifest <既有安装清单>`，通过 stdin 传一个 JSON。清单路径取既有 `Local workflow observation` handler 的 `--manifest` 参数；不要猜测位置、修改 hook 信任或重新启用未授权项目。

通用字段：`schema_version=1`、`cwd`、`session_id`、`turn_id`、`reporter_session_id`、`kind`、`evidence_files`。目标 session/turn 必须已有真实生命周期记录；目标和报告者必须登记在项目 `.codex/role-windows.md`。仅负责人或既有复核角色写入，一次性 executor 回传文件证据后由负责人处理。

- `kind=review`：填写明确布尔值 `quality_pass`、`safety_pass`；报告者必须是与目标不同的已登记架构/QA/测试/安全/DBA/运维/总控/内容主编线程。它证明“不同登记线程提交了带文件句柄的复核报告”，不自动证明复核内容真实或质量通过。
- `kind=rework`：报告者须是目标线程本人，填写非负整数 `retries`，表示该工作流实际重试/返工次数；没有事实依据时不填零，不提交虚构记录。
- `kind=skill_usage`：报告者须是目标线程本人，填写 `skills_loaded`、`skills_used`、`skills_missed`、`skills_misfired` 四个列表；used/misfired 必须属于 loaded，missed 与 loaded 互斥。这是角色自报，不是独立路由器观测。

`evidence_files` 为 1–8 个现有项目相对报告文件，允许 `.codex/tasks/`、`.codex/reports/`、`docs/`、`target/surefire-reports/`、`test-results/` 下的 md/json/txt/xml，每个最多 2 MB。保存相对路径与内容 SHA256，不复制报告正文、输入或原始身份；绝对路径、越界/链接文件和未知轮次被拒绝。先落实报告文件再记录，后续审查可用哈希检查文件是否改变。若缺台账、已有验收或文件证据，保持缺失并回传原因，不用自证补齐。

记录独立追加到 `evidence-YYYY-MM-DD.jsonl`，与生命周期事件共用锁、30 天保留期和每项目 10 MB 总上限；不改写旧事件的空字段。`status/summary` 只显示各类证据数量，quality、实际路由命中和会员节省仍不自动评分。

示例结构（占位身份须换成当前真实登记身份，不要把示例当真实数据）：

```json
{"schema_version":1,"cwd":"<已授权项目>","session_id":"<目标线程>","turn_id":"<已观测轮次>","reporter_session_id":"<既有复核线程>","kind":"review","quality_pass":true,"safety_pass":true,"evidence_files":[".codex/tasks/acceptance.md"]}
```

Windows `\\?\` 驱动器/UNC 路径只在解析真实路径之后统一比较，不扩大 transcript 授权根。无法匹配的会话仍保持 `unavailable`；不扫描或回填历史聊天，不用当前累计 Token 伪造过去的起点。
