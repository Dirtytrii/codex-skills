# Codex Skills

个人沉淀的 Codex skills 公共仓库。

这个仓库用于保存可公开复用的技能目录，方便在不同 Codex 环境、远程 Hermes 服务器和新机器之间同步。每个 skill 都应是一个可以独立复制到 `${CODEX_HOME:-$HOME/.codex}/skills/` 的目录。

## Skills

| Skill | 用途 | 来源 | 主要角色 |
| --- | --- | --- | --- |
| `agent-role-orchestrator` | 架构先行的多窗口角色编排、继承、交接提示词 | local | 架构 / 全角色 |
| `authorized-blackbox-web-security` | 授权黑盒 Web 安全测试和报告 | local | 安全 |
| `design-taste-frontend` | Landing/作品集/重设计的前端审美防模板化规则 | external-github | UI/PPT |
| `guizang-ppt-skill` | 横向翻页网页 PPT，杂志风和瑞士风模板 | external-github | UI/PPT |
| `hatch-pet` | Codex pet 精灵图生成、修复、校验和打包 | local | UI/PPT / 视频 |
| `pdf` | PDF 读取、生成、渲染校验工作流 | local | QA / 开发 / UI/PPT |
| `playwright` | 终端 Playwright CLI 浏览器自动化 | external-github | UI/PPT / QA / 开发 |
| `startup-pressure-test` | 创业想法压力测试、MVP 和首批客户计划 | local | 架构 |
| `test-case-report-builder` | 测试用例 Excel、测试报告 Word/DOCX 和 QA 证据包 | local | QA |

暂不公开：

- `chronicle`：和本机屏幕录制/记忆能力绑定，公开复用价值低，容易造成误用。
- `.backup-*`：历史备份目录，不进入公开仓库。

## 目录结构

```text
.
├── skills/                 # 可复制安装的 skill 目录
├── registry/skills.json    # skill 清单和状态
├── docs/
│   ├── add-skill.md        # 新增 skill 的流程
│   ├── publication-checklist.md
│   └── source-policy.md    # local / external / hermes 来源治理
├── scripts/
│   └── validate_public_skills.py
└── README.md
```

## 安装

复制单个 skill：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
rsync -a "skills/agent-role-orchestrator/" "${CODEX_HOME:-$HOME/.codex}/skills/agent-role-orchestrator/"
```

复制全部 active skills：

```bash
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
for d in skills/*; do
  [ -d "$d" ] || continue
  rsync -a "$d/" "${CODEX_HOME:-$HOME/.codex}/skills/$(basename "$d")/"
done
```

## Hermes 后续补充

Hermes 服务器有新的 skill 时，按这个流程加入：

1. 在 `skills/<skill-name>/` 下放完整 skill 目录。
2. 确保 `skills/<skill-name>/SKILL.md` frontmatter 至少包含 `name` 和 `description`。
3. 更新 `registry/skills.json`，填好 `origin_type`、`maintenance` 和 `consumed_by_roles`。
4. 运行：

```bash
python3 scripts/validate_public_skills.py
```

5. 按 `docs/publication-checklist.md` 做公开发布前检查。
6. 使用中文 commit message 提交。

## 公开发布原则

- 不提交 token、密钥、账号密码、生产域名凭据、内网地址、私有日志、截图原始敏感信息。
- 不提交 `.backup-*`、临时输出、生成图片缓存、运行时录屏、记忆文件。
- 第三方来源 skill 保留原始许可证、README 和 provenance。
- 外部 GitHub 来源 skill 使用 `origin_type=external-github` 标记；除兼容 Codex/Hermes 所需的适配外，不把它当成本地原创。
- 每个 skill 保持最小自洽：`SKILL.md` 必须能说明何时使用、怎么使用、边界和校验方式。

## 维护约定

- 新需求先过 `agent-role-orchestrator` 的 `架构` 角色。
- 已建立角色默认走继承/接续，不重复新建窗口。
- 安全审计默认委派到安全专项 skill。
- QA 生成测试用例/测试报告默认使用 `test-case-report-builder`。
- 使用中发现可复用优化时，优先沉淀回对应 skill。
