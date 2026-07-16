# 插件安装、更新与跨机器同步

本仓库以 Git marketplace 分发 `core + domain plugins`。其他机器不再复制整套 `skills/`；每台机器注册同一个 marketplace，显式安装 Core，并只启用当前任务需要的 Domain。

## 更新模型

插件更新分成两步，不能只做第一步：

1. `codex plugin marketplace upgrade` 刷新远程仓库快照。
2. `codex plugin add` 从新快照重写所选插件的本地安装缓存。

已经运行的任务不会重载 Skill catalog。安装或更新完成后必须新建任务验证。PR 分支中的更新也不会进入其他机器；只有合并到 `main` 后，使用 `main` 的机器才能拉到。

以下流程已在 `codex-cli 0.144.5` 验证。这里把它作为已验证基线，不声称它是插件命令首次出现的最低版本。若本机没有 `codex plugin` 或 `codex plugin marketplace upgrade`，先升级独立 CLI：

```bash
codex update
```

若当前安装不支持自更新，使用 npm：

```bash
npm install --global @openai/codex
```

## 新机器首次安装

```bash
codex plugin marketplace add Dirtytrii/codex-skills --ref main
codex plugin add codex-skills-core@dirtytrii-codex-skills
codex plugin list
```

不要假定注册 marketplace 会自动安装 Core。`INSTALLED_BY_DEFAULT` 是 marketplace 的推荐策略；CLI 路径仍显式执行 `plugin add codex-skills-core`，跨版本和跨界面更稳定。

Windows 如果桌面应用附带的 WindowsApps `codex.exe` 被系统拒绝执行，不需要修改系统目录权限。安装 npm CLI 后可以直接使用它的 shim：

```powershell
$codex = Join-Path (npm prefix -g) "codex.cmd"
& $codex --version
& $codex plugin marketplace add Dirtytrii/codex-skills --ref main
& $codex plugin add codex-skills-core@dirtytrii-codex-skills
```

## 日常更新

只更新默认 Core：

```bash
codex plugin marketplace upgrade dirtytrii-codex-skills
codex plugin add codex-skills-core@dirtytrii-codex-skills
codex plugin list
```

准备进入某个领域任务时，再刷新对应 Domain：

```bash
codex plugin add codex-skills-engineering@dirtytrii-codex-skills
codex plugin add codex-skills-operations@dirtytrii-codex-skills
codex plugin add codex-skills-content@dirtytrii-codex-skills
codex plugin add codex-skills-visual-delivery@dirtytrii-codex-skills
```

这些命令会安装并启用对应插件。任务结束后，在 Codex 桌面的 Plugins 面板或 CLI 的 `/plugins` 浏览器中关闭不再需要的 Domain；Core 保持启用。不要把四个 Domain 长期全部常驻。

需要把一台机器的五个缓存一次更新到最新时，可以运行：

```powershell
$plugins = @(
  "codex-skills-core",
  "codex-skills-engineering",
  "codex-skills-operations",
  "codex-skills-content",
  "codex-skills-visual-delivery"
)

codex plugin marketplace upgrade dirtytrii-codex-skills
foreach ($plugin in $plugins) {
  codex plugin add "$plugin@dirtytrii-codex-skills"
}
codex plugin list
```

批量更新后重新关闭四个 Domain，恢复 Core-only 默认状态。

## 新任务验证

至少完成三层检查：

1. `codex plugin list` 显示 Core 为 `installed, enabled`，需要的 Domain 为 `installed, enabled`。
2. 新建任务，确认代表 Skill 出现在该任务启动时的 Available skills catalog。
3. 确认 Skill 来源是插件缓存，而不是旧平铺目录。

代表 Skill：

| 插件 | 验证 Skill |
| --- | --- |
| Core | `agent-role-orchestrator`、`browser-automation-router`、`startup-pressure-test` |
| Engineering | `gstack`、`playwright` |
| Operations | `application-problem-diagnosis-workflow` |
| Content | `cheat-on-content`、`humanizer-zh` |
| Visual Delivery | `ui-implementation-workflow`、`delivery-document-package` |

Windows 的来源路径应类似：

```text
%USERPROFILE%\.codex\plugins\cache\dirtytrii-codex-skills\<plugin>\<version>\skills\<skill>\SKILL.md
```

可以在新任务中直接要求：

```text
只根据本任务启动时的 Available skills catalog，确认 agent-role-orchestrator
是否可见，并报告它的 SKILL.md 来源。不要只扫描文件系统猜测。
```

## 旧平铺安装迁移

先验证插件，再清理旧目录。只看到缓存文件存在不算通过；新任务必须能从插件路径加载代表 Skill。

克隆了本仓库时，可以先审计重复项：

```bash
python scripts/audit_plugin_context.py --plugin codex-skills-engineering --scan-user-roots --strict
```

迁移规则：

- 只归档已被插件覆盖的同名顶层 Skill，不直接永久删除。
- 保留 `$HOME/.codex/skills/.system`。
- 不处理其他来源的 `$HOME/.agents/skills`，除非逐项确认已被插件替代。
- 同名 Skill 不要同时保留在插件缓存和旧平铺发现目录中。
- bundled references 随旧的 `agent-role-orchestrator` 目录一起退出发现范围，不再单独维护。

若验证失败，保持旧目录不动。已经归档后需要回滚时，先关闭对应插件，再从归档中恢复所需 Skill；不要让两份同名 Skill 同时生效。

## 常见问题

### marketplace 已经是最新，但 Skill 还是旧的

`marketplace upgrade` 只刷新 marketplace 快照。再次运行对应的 `codex plugin add <plugin>@dirtytrii-codex-skills`，然后新建任务。

### 当前任务仍然看到旧 Skill

任务启动时已经固定了 Skill catalog。关闭旧任务并创建新任务；不要用同一长任务判断安装是否生效。

### PR 已合并，但另一台机器还看不到

确认该机器的 marketplace 跟踪 `main`，依次执行 `marketplace upgrade`、对应插件的 `plugin add`，再开新任务。不要把日常机器长期固定在 PR 分支。

### 更新 Domain 后上下文变大

检查是否同时启用了多个 Domain。完成当前阶段后关闭不需要的插件；跨域组合超过目录预算时，按阶段拆任务并使用压缩交接。

Codex 官方命令和 marketplace 结构参考：[Developer commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli#cli-codex-plugin) 与 [Build plugins](https://learn.chatgpt.com/docs/build-plugins#build-your-own-curated-plugin-list)。官方说明也要求插件安装后在新任务或新 CLI session 中加载 bundled skills。
