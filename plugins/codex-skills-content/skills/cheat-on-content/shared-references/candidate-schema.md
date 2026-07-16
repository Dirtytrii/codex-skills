# Candidate Schema（候选项统一 schema）

被这些子 skill 引用：`cheat-trends`、`cheat-recommend`、`cheat-init`、所有 `adapters/`。

任何"待决定要不要做"的内容素材——不管来自手粘列表 / RSS / Notion / 平台热点抓取——都必须 normalize 成本 schema 之后才进入候选池。这是 `adapters/` 的输出契约。

字段设计参考博主项目的 `articles` 表 schema（私有项目，工具的方法论由此抽象而来）。

---

## 必填字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | string (12 chars) | 稳定 hash：`sha256(source + normalized_title + url_path)[:12]`。同一条素材在不同时间被抓到 → 同 id |
| `title` | string | 候选项的人类可读标题 |
| `source` | string | 来源标识，格式 `<adapter-type>:<source-name>`，例：`trend:hackernews`、`pool:notion-mybook`、`paste:manual` |
| `snapshot_text` | string | 候选项的全文或摘要——**这是打分的输入**，不是 url。adapter 必须负责把 url 拓展成可读文本 |
| `snapshot_at` | ISO 8601 | 抓取/录入这条 item 的时间 |

---

## 可选字段

| 字段 | 类型 | 说明 |
|---|---|---|
| `url` | string | 原始链接（便于追溯） |
| `tier` | enum | `tier1` / `tier2` / `tier3` / `skip` / `risky` / `done`。粗分类，用于过滤 |
| `read_status` | enum | `unread` / `skimmed` / `deep_read` / `done`。处理状态 |
| `category` | string | 自定义分类标签（如"社会"、"家庭"、"学术"） |
| `composite_score` | float | 用当前 rubric 打分得到的综合分（如已打） |
| `dimension_scores` | object | 各维度的整数分，键名对齐当前 rubric 的维度（如 `{"ER": 5, "HP": 4, ...}`） |
| `scored_under_rubric_version` | string | 打分时用的 rubric 版本号 |
| `predicted_bucket` | string | 粗预测桶（如 `30-100w`），**注意：不是正式预测**——选题阶段的粗略估计，与 `predictions/*.md` 的 immutable 预测完全独立 |
| `predicted_reason` | string | 一句话理由 |
| `note` | string | 自由文本备注，例如"等节点再发"、"待重读"、"风险议题" |
| `rejected_at` / `rejected_reason` | ISO 8601 / string | 用户主动跳过此候选时记录 |

---

## JSON 范例

### Markdown 列表 adapter 输出

```json
{
  "id": "a3f2c1d4e5b6",
  "title": "为什么我们都讨厌主动联系朋友",
  "source": "pool:markdown-list",
  "snapshot_text": "[用户从 candidates.md 复制的全文]",
  "snapshot_at": "2026-05-04T08:30:00+08:00",
  "url": null,
  "tier": "tier1",
  "read_status": "skimmed",
  "category": "社交",
  "composite_score": 7.4,
  "dimension_scores": {"ER": 4, "HP": 4, "QL": 5, "NA": 3, "AB": 5, "SR": 3, "SAT": 3},
  "scored_under_rubric_version": "v0",
  "predicted_bucket": "5-30w",
  "predicted_reason": "ER=4+QL=5 强金句感，AB=5 普适，但 SR=3 议题不够强",
  "note": ""
}
```

### Trend adapter 输出（HN）

```json
{
  "id": "8c4d92e1f0b3",
  "title": "Show HN: I built a tool that predicts whether your video will go viral",
  "source": "trend:hackernews",
  "snapshot_text": "[文章全文 + 评论 top 5 的摘要]",
  "snapshot_at": "2026-05-04T09:15:00+08:00",
  "url": "https://news.ycombinator.com/item?id=12345678",
  "tier": null,
  "read_status": "unread",
  "category": "tech-meta",
  "composite_score": null,
  "dimension_scores": null,
  "scored_under_rubric_version": null
}
```

打分前 score 字段全部为 null——是预期的。`cheat-trends` 抓回来后会调 `cheat-score` 给每条算 composite。

---

## Markdown 表示（用户可见的存储格式）

候选池的默认存储是 `candidates.md`（人类可读），不是 JSON。每条 item 是一个 H3 entry：

```markdown
### [tier1] 为什么我们都讨厌主动联系朋友
- **id**: a3f2c1d4e5b6
- **source**: pool:markdown-list
- **snapshot_at**: 2026-05-04
- **category**: 社交
- **composite (v0)**: 7.4 — ER=4 HP=4 QL=5 NA=3 AB=5 SR=3 SAT=3
- **predicted bucket**: 5-30w
- **note**:

> [snapshot_text 段，如有]
```

升级到 SQLite 之后（见 `cheat-status` 的升级触发），同样字段走 `articles` 表存储，markdown 视图自动从 DB 渲染。

---

## ID 稳定性的关键规则

**同一条素材在不同时间被不同 adapter 抓到 → 必须算出同 id**。这是去重的基础。

算法：
```python
import hashlib

def candidate_id(source: str, title: str, url: str = None) -> str:
    normalized_title = title.strip().lower().replace(" ", "")
    url_path = url.split("?")[0].rstrip("/") if url else ""
    raw = f"{source.split(':')[0]}|{normalized_title}|{url_path}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:12]
```

注意：
- `source` 取冒号前的 adapter type（`trend:hackernews` → `trend`），不是具体 source name——同一标题被 HN 和 Reddit 都抓到，应判定为同一候选（避免重复打分）
- title 做了 lowercase + 去空格——避免 "Hello World" 和 "hello world" 被算成不同 id
- url 砍掉 query string—— `?utm_source=xxx` 不影响内容

---

## 去重协议

`cheat-trends` / `cheat-recommend` 在写入 `candidates.md` 前必须执行：

1. 计算新 item 的 id
2. 检查 `candidates.md` 是否已含此 id → 跳过
3. 检查 `predictions/*.md` 是否含此 id（已发过）→ 跳过
4. 检查 `.cheat-cache/trends-history.jsonl` 是否含此 id 且 `rejected_at != null` → 跳过（用户已主动拒绝过）
5. 通过则写入

`.cheat-cache/trends-history.jsonl` 是抓取历史的去重缓存，每行一个 JSON record，append-only。被用户拒绝的候选会在这里保留 6 个月；之后允许重新出现（也许素材在新 rubric 下评估不同）。

---

## tier 的语义

| Tier | 含义 | 对应行动 |
|---|---|---|
| `tier1` | 强候选，应推荐 | 进入 `cheat-recommend` 排序池 |
| `tier2` | 中等，备选 | 进入排序池但权重低 |
| `tier3` | 弱候选，备而不用 | 不进推荐池，留作长尾 |
| `skip` | 用户主动跳过 | 不再出现 |
| `risky` | 议题敏感 / 平台风控风险 | 推荐时额外标注，需用户确认 |
| `done` | 已发布 | 移出候选池，由 prediction file 接管 |

**Cold-start 期间所有 item 默认是 `unread`/`null tier`**——直到用户或 `cheat-score` 给出 composite 后才能粗分类。**未打分的 item 不应出现在 `cheat-recommend` 输出**——避免推荐没读过的素材。

---

## adapter 实现契约

任何 `adapters/` 下的 adapter 都必须：

1. 实现 `fetch() → List[Candidate]` 接口（伪签名，实际是 markdown 文档描述的协议）
2. 输出符合本 schema 的 items
3. 自己负责把 url / 短摘要拓展成可读 `snapshot_text`——**adapter 不输出"光秃秃的 url"**
4. 优雅降级：如配置缺失（API key、cookie），返回空列表 + 在 stderr/log 写明原因，**不抛异常**

详见 `adapters/HOWTO.md`（待批次 3 写）。
