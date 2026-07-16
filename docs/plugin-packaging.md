# Core 与 Domain Plugins

本仓库用插件拆包解决两个问题：默认上下文里不再常驻全部 skill；任务需要某个领域时，仍能一次安装完整能力集合。原则是 **只装 core，按任务启用 domain**。

## 包边界

| 插件 | 默认 | 顶层 skill | 目录字符预算 | 主要职责 |
| --- | --- | ---: | ---: | --- |
| `codex-skills-core` | 是 | 3 | 793 | 总控/角色路由、浏览器路由、项目压力测试 |
| `codex-skills-engineering` | 否 | 34 | 6677 | 架构、开发、测试、QA、工程发布 |
| `codex-skills-operations` | 否 | 9 | 2204 | 运维诊断、安全、部署门禁、恢复规划 |
| `codex-skills-content` | 否 | 12 | 6542 | 内容研究、写作、公众号、小红书和发布准备 |
| `codex-skills-visual-delivery` | 否 | 9 | 2669 | UI、视觉资产、PPT、PDF 和交付文档 |

内容插件还包含 `cheat-on-content` 下的 nested skills，因此它的 catalog record 多于顶层目录数。当前 core 与任一单个 domain 的组合都低于仓库的 8000 字符目录目标。这个数字是用于防止目录膨胀的稳定 guardrail，不等同于一次任务的精确 Token 账单。

跨域任务先运行审计。组合仍低于目标时可以同时启用；超过目标时拆成阶段任务，并用压缩交接传递必要事实。例如 content + visual-delivery 当前为 10004 字符，公众号文章和社交卡片应分别在内容阶段、视觉阶段处理，而不是让两个大目录长期同时常驻。不要复制同一个 skill，也不要把领域能力塞回 core。

## 安装

在普通终端使用独立 Codex CLI：

```bash
codex plugin marketplace add Dirtytrii/codex-skills --ref main
codex plugin add codex-skills-core@dirtytrii-codex-skills
codex plugin add codex-skills-content@dirtytrii-codex-skills
```

也可以从 Codex 桌面的 Plugins 面板添加 marketplace 和领域插件。marketplace 把 `codex-skills-core` 标为 `INSTALLED_BY_DEFAULT`，其他包标为 `AVAILABLE`；CLI 路径仍显式安装 Core，不假定注册 marketplace 会自动完成安装。

其他机器首次安装、日常刷新、同版本缓存更新、新任务验证和旧平铺目录迁移见[插件安装、更新与跨机器同步](plugin-update-guide.md)。

若 Windows 桌面应用内的子进程无法直接执行 WindowsApps 中的 `codex.exe`，而桌面 Codex 本身仍正常，无需修改系统目录权限。只有需要在终端运行上述命令时，才安装独立 CLI：

```powershell
npm install --global @openai/codex
```

插件机制暂不可用时，可把当前任务需要的 canonical 目录整体复制到 `$HOME/.agents/skills`。`$HOME/.codex/skills` 是旧兼容位置。不要默认复制全部，不要在插件和旧平铺目录里同时保留同名 skill。

## 唯一维护源

```text
skills/                          人工维护的 canonical 源
registry/plugin-packages.json    skill 到包的唯一归属与依赖
.agents/plugins/marketplace.json 安装策略与插件入口
plugins/*/skills/                自动生成副本，禁止手改
```

维护顺序：

```bash
python scripts/sync_plugin_bundles.py --write
python scripts/test_plugin_packages.py
python scripts/validate_plugins.py
python scripts/validate_public_skills.py
```

`sync_plugin_bundles.py --write` 只会清理经过路径验证的 `plugins/<package>/skills/`，然后从 canonical 源复制。`--check` 使用逐文件 SHA-256 比较，缺文件、旧文件和手改副本都会失败。

生成副本保留上游文件字节，包括 vendored 内容已有的格式。因此 `.gitattributes` 对 `plugins/*/skills/**` 关闭重复 whitespace 报警；canonical `skills/` 仍接受正常检查。

## 校验与审计

`validate_plugins.py` fail closed 检查：

- 67 个顶层 skill 恰好归属一个插件，没有漏包或重复打包。
- 只有 core 默认安装，所有 domain 都依赖 core。
- marketplace、manifest、`agents/openai.yaml` 和生成 bundle 一致且可用于插件。
- core 与任一单 domain 不超过 8000 字符目录目标。

按实际启用组合审计：

```bash
python scripts/audit_plugin_context.py \
  --plugin codex-skills-content \
  --plugin codex-skills-visual-delivery \
  --scan-user-roots --json
```

`--plugin` 可重复；依赖的 core 会自动加入。`--scan-user-roots` 只读取两个用户 skill 根目录中的顶层名称，用于提示同名旧平铺安装，不推测 Codex 当前任务真实启用了哪些插件。

加上 `--strict` 后，组合超过 8000 字符会返回非零状态。此时缩小插件集合或拆分任务，不要把警告解释成插件安装失败。

迁移旧安装时先审计，再确认新插件在新任务中可见，最后单独归档或删除重复的旧目录。仓库脚本不会自动删除用户目录。

Codex 插件结构、marketplace 和安装策略以 OpenAI 的 [Build plugins](https://learn.chatgpt.com/docs/build-plugins) 为准；初始 skill 列表预算和渐进加载规则见 [Build skills](https://learn.chatgpt.com/docs/build-skills)。
