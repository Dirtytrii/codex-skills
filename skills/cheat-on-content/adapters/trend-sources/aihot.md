# adapters/trend-sources/aihot — AI 行业热点

**适合谁**：AI 教程 / Builder / 工具号 / AI 行业评论。**不适合**普通生活/职场/文化垂类（用 trendradar-mcp.md）。

---

## 它是什么

通过 AIHOT Skill 获取中文 AI 行业的每日精选和历史归档。[AIHOT 官网](https://aihot.news/)

- **5 类内容**：模型 / 产品 / 行业 / 论文 / 技巧
- **数据新鲜度**：每天人工精选 + 实时增量；items 端点最近 7 天
- **安装后直接使用**，此适配无需 API Key 或 MCP 连接

## 装

按所用客户端和运行环境选择安装方式。官方说明包含 Codex、Claude Code 和 Windows 原生环境的安装与验证步骤。[AIHOT Skill 安装说明](https://aihot.news/aihot-skill/README.md)

官方也提供安装脚本源文件供审阅。[install.sh](https://aihot.news/aihot-skill/install.sh)

## cheat-seed / cheat-trends 怎么调

**不要直接 curl** —— 让 Claude 自然触发 aihot skill 即可：

| cheat-seed 场景 | 给 Claude 的内部指令 |
|---|---|
| Mode C，content_form 含 AI/教程/Builder | "调 aihot skill 拿今天 AI 圈精选条目，按 content_form 过滤后给 5 条" |
| Mode A 用户提到 AI 产品名（"DeepSeek V5"） | "调 aihot skill 用 q 参数搜该关键词最近 7 天动态" |

aihot skill 的 SKILL.md 已经详尽描述了端点 + 路由优先级（默认走精选不走日报）——cheat-seed 不需要重复写这套逻辑，**信任 aihot skill 自己的判断**。

## 输出格式契约

aihot skill 默认返回 markdown，按 5 类（模型/产品/行业/论文/技巧）分组。cheat-seed 收到后：

1. 按 `content_form` 过滤掉不相关类别（如 opinion-video → 留行业 + 产品；tutorial-builder → 留模型 + 工具）
2. 用当前 rubric 粗筛 5 条最适合的
3. 转成 [candidate-schema.md](../../shared-references/candidate-schema.md) 的 schema 写入 `candidates.md`

## 失败模式

| 症状 | 处理 |
|---|---|
| 403 Forbidden | 核对 AIHOT 官方安装说明和当前 skill 版本。若仍无法访问，降级到 trendradar-mcp 或 manual-paste |
| 端点超时 / 5xx | 优雅降级到 trendradar-mcp 或 manual-paste；不抛异常 |
| 用户的 content_form 跟 AI 完全无关（如美食/妆教） | cheat-seed 应该**不调 aihot**——按 [data-source-routing.md](../../shared-references/data-source-routing.md) 的路由表 |

## 稳定性

★★★★★ — 公开 API，作者维护，无认证依赖。

---

## 与其他 adapter 的关系

- **vs trendradar-mcp.md**：互补不重叠。aihot 是 AI 垂直，trendradar 是综合。两者都启用时按 `content_form` 路由。
- **vs manual-paste**：永远的 fallback。aihot/trendradar 都失败时走 manual-paste。
