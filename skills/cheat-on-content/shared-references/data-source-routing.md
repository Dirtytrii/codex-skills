# Data Source Routing — 热点工具的触发与路由协议

被 cheat-seed / cheat-trends 引用。规定**何时**调热点工具、**调哪个**、**不调时怎么办**。

---

## 核心哲学

> **热点工具是"前置素材库"，不是"主菜单"。**
>
> - 用户在**内省**（讲自己的经历 / 思考动机）→ **不调**，避免外部信息污染
> - 用户在**找素材**（没想法 / 要批量 / 显式抓热点）→ **调**，按 content_form 路由数据源
> - 用户在**确认 angle**（讲了时事话题）→ **不主动调**，让用户决定要不要外部数据作参考

设计目的：保护 cheat-seed 的核心论点——"好内容来自用户的真实经历，AI 不凭空 brainstorm"——同时不让"完全没想法"的新博主卡死。

---

## 触发矩阵（被 cheat-seed Phase 1 引用）

| cheat-seed Mode | 默认调？ | 触发条件 |
|---|---|---|
| **Mode A**（用户给了具体经历/topic） | ❌ 默认不调 | 仅当用户讲的本身是时事话题（含产品名/人名/事件名 + 时间词）+ 用户**主动同意** |
| **Mode B**（方向不具体，问"为什么"） | ❌ **永远不调** | 这阶段用户在内省，外部素材是噪音 |
| **Mode C**（完全没想法） | ✅ 默认调 | Mode C 的核心动作就是把外部素材摆出来 |
| `--batch N` | ✅ 默认调 | 批量 brainstorm 必须有 anchor |
| `/cheat-trends` 显式 | ✅ 调 | 主入口，无需解释 |
| `/cheat-recommend` | ❌ 默认不调 | 已有 pool；除非 pool >7 天没更新 → 提示先 trends |

---

## 时事话题判定（Mode A 灰色场景用）

让 Claude 判断，**不写正则白名单**：

| 信号 | 含义 |
|---|---|
| 含**专有名词**（人名 / 产品名 / 事件名） | 强信号——可能是时事 |
| 含**时间词**（"今天" / "刚" / "最近" / "刚刚发生"） | 强信号 |
| 含**结构词**（"对比" / "回应" / "事件"） | 弱信号 |
| 仅含通用名词 + 个人经历词（"我" / "昨天" / "我同事"） | 反信号——是长青个人经历，**不是时事** |

判定结果：
- **强信号** → 询问用户"要不要拉一下这话题的舆论风向作参考"
- **弱信号 / 模糊** → 不主动询问，直接进 Mode A 深挖
- **反信号** → 100% 不调

跟 [bump-validation-protocol.md](bump-validation-protocol.md) 的"软规则、Claude 判断"哲学一致。

---

## 数据源路由（按 content_form）

[adapters/trend-sources/](../adapters/trend-sources/) 目前有两个一等公民 + 一个保底：

| Adapter | 适合的 content_form |
|---|---|
| [`aihot`](../adapters/trend-sources/aihot.md) | `tutorial-builder` / AI 行业评论 / AI 教程 / AI 产品测评 |
| [`trendradar-mcp`](../adapters/trend-sources/trendradar-mcp.md) | `opinion-video` / `long-essay` / `short-text` / `podcast` / `other`（生活/职场/文化） |
| `manual-paste` | 永远的 fallback——用户粘 URL/标题列表 |

### content_form → 主调 + 备调矩阵

| content_form | 主调 | 备调 | 不调 |
|---|---|---|---|
| `opinion-video` | trendradar-mcp | aihot（仅当话题与 AI 行业相关） | — |
| `long-essay` | trendradar-mcp | aihot（同上） | — |
| `short-text` | trendradar-mcp | aihot（同上） | — |
| `podcast` | trendradar-mcp | aihot（同上） | — |
| `tutorial-builder` | **aihot** | trendradar-mcp（仅当涉及通用工具/产品发布） | — |
| `mixed` | 两个都调 | — | 由 Claude 判断每条候选属于哪个垂类 |
| `other`（美食/妆教/剧情/...）| trendradar-mcp | — | aihot（与 AI 无关） |

### 用户层覆盖

`.cheat-state.json` 的 `enabled_trend_sources` 字段是**显式开关**：

```json
"enabled_trend_sources": ["aihot", "trendradar-mcp", "manual-paste"]
```

数组里有的才会被调。空数组 → 仅走 manual-paste。

cheat-trends 显式调用时支持 override：`/cheat-trends — sources: aihot`（仅这次用 aihot）。

---

## 失败降级链

```
[cheat-seed Mode C 触发拉热点]
  ↓
[按 content_form 选主调]
  ↓
  ├─ 主调成功 → 拿数据 → 进流程
  ├─ 主调失败（API down / MCP 没装 / 超时）
  │   ↓
  │   [按 content_form 选备调]
  │   ├─ 备调成功 → 拿数据 → 提示用户"主调用不了，用了备调"
  │   └─ 备调也失败 → 走 manual-paste 兜底
  │       ↓
  │       [询问用户："今天看到啥可以拍的？粘几条 URL/标题给我"]
  └─ 用户当前没启用任何 source → 提示如何启用 + 这次直接走 manual-paste
```

**关键纪律**：所有失败都**不抛异常**。cheat-seed 永远能跑——区别只是有没有外部素材。

---

## Token 成本意识

热点 API 调用**有成本**（aihot 是 token / trendradar-mcp 是 MCP 调用 + LLM context）。判定原则：

| 场景 | 调用频率 |
|---|---|
| Mode C 触发 | 每次会话最多 1 次（拿数据后 cache 在内存） |
| Mode A 灰色场景 | 用户同意才调，1 次 |
| `--batch N` | 1 次拿足够候选 |
| 用户连说"再来一批" | 第二次允许，第三次提示"要不要换 query 角度" |

不要在同一会话里反复调同一个端点——那是浪费。

---

## 与 candidates.md 的关系

热点工具拉回的数据**最终落到** [candidate-schema.md](candidate-schema.md) 定义的 `candidates.md`：

```
[trend tool] → items
  → 去重（vs candidates.md / predictions/ / .cheat-cache/trends-history.jsonl）
  → 粗打分（cheat-seed 内联 rubric）
  → 写入 candidates.md（带 source 字段标明来自哪个 adapter）
```

cheat-seed Mode C 拿到数据后**不**直接进 brainstorm，先入 candidates.md，再让 Claude 从池子里选。这样数据可追溯、可被后续 cheat-recommend 复用。

---

## 给 maintainer 的扩展指南

新增一个 trend source：

1. 写 `adapters/trend-sources/<name>.md`，按现有 aihot.md / trendradar-mcp.md 的格式
2. 在本文件"数据源路由"段加一行——明确该 adapter 适合的 content_form
3. 不需要改 cheat-seed 内部逻辑——按 `enabled_trend_sources` 自动启用
4. CHANGELOG 标 MINOR

不要把硬编码"aihot"/"trendradar-mcp" 写进 cheat-seed SKILL.md——保持 adapter 模型可扩展。
