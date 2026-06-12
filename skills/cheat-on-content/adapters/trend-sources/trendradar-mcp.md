# adapters/trend-sources/trendradar-mcp — 综合社会热点（MCP）

**适合谁**：观点视频 / 时评 / 文化垂类 / 美食 / 职场 / 社会议题——**任何非 AI 垂直**的内容。

---

## 它是什么

[TrendRadar](https://github.com/sansan0/TrendRadar) 是 57k stars 的中文热点聚合监控（用 newsnow API 拉微博 / 知乎 / 抖音 / B 站 / 头条 等多平台）。它自带独立的 MCP server `trendradar-mcp`，暴露 25+ 个 tool。

cheat-on-content 把它当作 trend-sources adapter 之一——用户配 MCP server 后，cheat-seed / cheat-trends 自然能调。

- **多平台覆盖**：微博 / 知乎 / 抖音 / B站 / 头条 / 36kr / 等等
- **AI 增强工具**：`analyze_topic_trend` 给爆火/衰退判定；`compare_periods` 给周环比；`analyze_sentiment` 给情感倾向
- **License**：TrendRadar 本体是 GPL-3.0，但我们**只通过 MCP 协议调用**他们的 server，不构成 linking——无 GPL 传染

## 装

参考 TrendRadar 仓库的 [MCP 配置文档](https://github.com/sansan0/TrendRadar)。装好后用户的 Claude Code `.claude/settings.json` 含 `mcp__trendradar__*` 系列工具。

cheat-on-content 不打包 TrendRadar——用户自己装、自己保管 server 资源。

## cheat-seed / cheat-trends 调用的关键工具

| MCP 工具 | 用途 | 在哪调 |
|---|---|---|
| `mcp__trendradar__get_latest_news` | 拿最新热榜（最直接） | cheat-seed Mode C 主调 / cheat-trends 主调 |
| `mcp__trendradar__get_trending_topics` | 自动提取话题统计 | cheat-seed Mode C 备用 |
| `mcp__trendradar__analyze_topic_trend` | 单话题趋势分析（爆火/衰退） | cheat-seed Mode A 灰色场景 enrich（用户提了具体话题且同意拉数据） |
| `mcp__trendradar__compare_periods` | 周环比 / 月环比 | cheat-bump 升级 rubric 时作"用户领域是否变化"的弱信号（罕见用） |
| `mcp__trendradar__search_news` | 关键词搜索 | cheat-seed Mode A 用户提了关键词时 |

## 输出格式契约

TrendRadar MCP 返回 JSON / markdown。cheat-seed 收到后：

1. 解析 items（title / source / hot_score / snapshot_at / url）
2. 按 [candidate-schema.md](../../shared-references/candidate-schema.md) 算稳定 id（`sha256(source + normalized_title + url_path)[:12]`）
3. 去重（参考 cheat-trends 的去重协议）
4. 用当前 rubric 粗筛
5. 写入 `candidates.md`

## 失败模式

| 症状 | 处理 |
|---|---|
| MCP server 没装 / 没启动 | cheat-seed 自动降级到下一个启用的源（如 aihot 或 manual-paste），不抛异常 |
| MCP 调用超时 | 30 秒后超时，提示用户"trendradar 慢，要等还是切别的源" |
| newsnow 上游 API 改了 | TrendRadar 维护者会修；用户跟着升级 |

## 稳定性

★★★★ — 取决于 TrendRadar 项目活跃度（57k stars，活跃）+ newsnow 上游稳定性。

---

## 与其他 adapter 的关系

- **vs aihot.md**：互补不重叠。trendradar 是综合社会，aihot 是 AI 垂直。两者都启用时按 `content_form` 路由（详见 [data-source-routing.md](../../shared-references/data-source-routing.md)）
- **vs manual-paste**：永远的 fallback。两个 API 都失败时走 manual-paste

## 给 TrendRadar 团队的话

如果你是 TrendRadar 维护者看到这份 adapter doc——感谢你把多平台聚合做成 MCP server。cheat-on-content 是你们项目的"内容生产侧下游"——用户用 TrendRadar 知道发生了啥，用 cheat-on-content 把这个变成可校准的内容预测循环。互补不替代。

欢迎 cross-link：[github.com/XBuilderLAB/cheat-on-content](https://github.com/XBuilderLAB/cheat-on-content)。
