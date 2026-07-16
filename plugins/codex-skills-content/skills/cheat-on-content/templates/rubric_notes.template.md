# 评分校准笔记

> **本文件是 cheat-on-content 评分规则进化的载体**。每次复盘实际播放数据 vs 预测分数后，把判断依据和规律显式写在这里，下次打分前 `/cheat-score` `/cheat-predict` 会先读这个文件再动手。
>
> **核心原则**：规律必须可追溯到具体样本。不写"情感共鸣很重要"这种空话，要写"XX 这篇 ER=5 得到验证 / 推翻，因为评论区 top 3 都是 YY 模式"。
>
> 完整生命周期协议见 [shared-references/observation-lifecycle.md](../cheat-on-content/shared-references/observation-lifecycle.md)。
> 升级流程见 [shared-references/bump-validation-protocol.md](../cheat-on-content/shared-references/bump-validation-protocol.md)。

---

## Rubric 版本日志

_结构性变更才 bump 版本号；纯观察积累不算。升版后，校准池里的样本必须用新公式重打分。每次升级写一份结构化 evidence memo（见下方各版本 section）。_

**当前版本**: `v0`

**版本速查表**:

| 版本 | 生效日期 | 变更类型 | 驱动样本数 | 驱动 article_ids |
|---|---|---|---|---|
| v0 | [YOUR-INIT-DATE] | 初版占位（cold-start） | 0（先验） | — |

**升级决策原则**:
- 纯权重微调（如 SR×1.5 → ×1.8）→ 不 bump，trigger 重算 composite
- 维度定义细化（如 SR=5 的门槛变严）→ 不 bump，但复盘时标注新门槛
- 新增/删除维度、或定义颠覆性改写 → bump 主版本号

**迁移触发**: 候选筛选时如遇旧版打分的文章进入 top → 当场重读重评；不做全量重评。**校准池（带实绩数据）必须在每次升级时全量重打**。

---

## 当前评分维度 (0-5)

> **示例：下表是「视频分析」项目（中文观点视频博主，25+ 已发样本）的实测 v2 公式。
> Cold-start 用户应该等权起步——见 [opinion-video-zero.md](../cheat-on-content/starter-rubrics/opinion-video-zero.md)。
> 校准 5 篇之后再决定要不要把这个表换成你自己拟合的版本。**

| 维度 | 权重 | 含义 | 典型信号 |
|---|---|---|---|
| emotional_resonance (ER) | 1.5 | 情感冲击力 | 评论"泪目 / 破防 / 我也是" |
| social_resonance (SR) | 1.5 | 社会议题共振 | 评论出现社会现象关键词 |
| hook_potential (HP) | 1.5 | 开头抓人程度 | 完播率 / 前 3s 留存 |
| quotable_lines (QL) | 1.0 | 金句密度 | 评论引用原文 |
| narrativity (NA) | 1.0 | 故事性 | 转发 / 保存率 |
| audience_breadth (AB) | 1.0 | 受众广度 | 非粉丝占比 |
| satire_depth (SAT) | 1.0 | 讽刺 / 反讽深度 | 评论"狠 / 透 / 支棱" |

**综合分公式**：

```
composite = (ER×1.5 + SR×1.5 + HP×1.5 + QL + NA + AB + SAT) / 8.5 × 2.0
```

> Cold-start 用户的占位公式（等权）：
> ```
> composite = (ER + HP + QL + NA + AB + SR + SAT) / 7 × 2.0
> ```

---

## 观察记录

> **模板**（每次复盘后追加一条）：
>
> ```
> ### YYYY-MM-DD [标题简称] (id) — [一句话定性，如"验证 ER 主导"]
> - 预测：composite=X.XX，bucket=Y
> - 实绩：播放 / 点赞 / 评论 / 转发（带 T+Nd 标注）
> - Top 评论关键词：[简短摘录 + 赞数]
> - 判断：哪个维度被验证 / 推翻？为什么？
> - Rubric 调整：[如果有，写明 "下次打 XX 类文章时改 YY"]
> - 详见：[predictions/<file>.md]
> ```
>
> 删除规则见 [shared-references/observation-lifecycle.md](../cheat-on-content/shared-references/observation-lifecycle.md)：被吸收为维度 → 删；被推翻 → 删。git history 是档案。

### 示例条目（来自视频分析项目，仅供参考；你的项目的真实条目从复盘后开始累计）

#### 2026-04-24 停止期待 (ab61ed09) — 验证情感向爆款【T+7d 数据】
- 预测：composite=8.24（v2: ER5/HP5/QL5/NA3/AB5/SR2/SAT4），bucket=30-100w
- 实绩：T+7d 71.1w（中枢 50w，**+42%**），分播比 **2.53%**
- Top 评论关键词：「她不一样」/「他不一样」全文出现 12+ 次变体（最高 2266 赞）
- 判断：ER=5 主导被强证据验证（与同 composite 谁问你了 11.7w 比，**6.07x 流量比**）
- Rubric 调整：候选下次 bump 把 ER 从 ×1.5 提到 ×2.0
- 详见：[predictions/2026-04-24_ab61ed09_停止期待.md]

> 上面是示例。Cold-start 期请删除，从你的第一次复盘开始累计真实条目。

---

## 重大跨视频观察（≥2 样本支持但需要更多验证）

> 单样本观察先放在"观察记录"段，不上来。≥2 样本同 pattern 才升格到这里。

（暂无——开始记录后会自动累积）

---

## 规律沉淀区（高置信度，打分前必看）

> 每条规律要有 ≥2 样本支持 + 已通过升级验证流程（即被吸收为维度或显式确认）。

（暂无——升级 1-2 次后会有内容）

---

## Benchmark-derived initial signals

> 由 [benchmark.md](benchmark.md) 派生（如有），表示对标账号的高/中/低样本里**哪些维度看起来重要**。
>
> **仅定性方向，不直接采纳为数值权重**——5-10 样本拟合容易过拟合。
> 等你自己 N≥5 校准样本后正式 bump 时再决定是否调权重。
>
> 初始为空——`/cheat-learn-from` 完成后会填这里。

（待 cheat-learn-from 填入）

---

## 待验证假设

> 单样本观察 + 强信号但还没复现的，暂存这里。

- [ ] [示例] 类比型文章 > 直抒型文章（等下一篇类比稿发完看）
- [ ] [示例] 春节 / 清明等节点，家庭类文章 AB 临时 +1（无样本）

---

## 被拒升级 log

> 提议过但未通过验证的 bump，记录在这里——避免半年后重复提相同的失败方案。

（暂无）

---

## Bucket 方案（**当前: ratio**）

> ⚠️ **bucket 边界是用户账号的属性，不是普适常量**——绝对数桶（"5w 是底部"）只对有粉丝基础的老手成立，对 0 粉新人会让所有视频都落"底部 99%"，bucket 失去排序意义。
>
> 本工具按校准阶段切换三种 bucket 方案。当前生效方案由 `.cheat-state.json` 的 `bucket_scheme` 字段决定。

### 阶段 1：cold-start，比率桶（当前阶段）

`bucket_scheme = "ratio"`

**第 1 篇**：用平台通用默认（实际播放数）

| Bucket | 范围（实际播放）| 含义 | 先验概率 |
|---|---|---|---|
| 底部 | < 100 | 几乎被算法埋了 | 30% |
| 基础盘 | 100 - 1,000 | 完播率支撑的小推荐 | 40% |
| 命中 | 1,000 - 10,000 | 第一次破圈的信号 | 20% |
| 小爆 | 10,000 - 100,000 | 极罕见的"零粉首爆" | 8% |
| 大爆 | > 100,000 | 平台算法异常加权 | 2% |

**第 2 篇起**：`baseline = 上一篇实际播放数`（或最近 3 篇中位数）

| Bucket | 倍数范围 | 含义 |
|---|---|---|
| 退步 | < 0.3 × baseline | 比上一篇明显差 |
| 持平 | 0.3 - 1 × baseline | 与上一篇同档 |
| 命中 | 1 - 3 × baseline | 中度突破 |
| 小爆 | 3 - 10 × baseline | 显著破圈 |
| 大爆 | > 10 × baseline | 量级跃迁 |

详见 [starter-rubrics/opinion-video-zero.md](../cheat-on-content/starter-rubrics/opinion-video-zero.md) 的"比率桶方案"段。

### 阶段 2：N=5 后切到固定绝对桶（带 ratio 备用）

`bucket_scheme = "absolute_with_ratio"`

跑完 5 篇后，`/cheat-bump --bucket-only` 自动派生：
- `baseline = 5 篇实际播放的中位数`
- 边界 = baseline × {0.3 / 1 / 3 / 10 / 30}

`/cheat-bump --bucket-only` 落地时会替换本段表格。

### 阶段 3：N≥10 后切到 percentile 桶（推荐长期方案）

`bucket_scheme = "percentile"`

边界 = 你历史样本的 percentile：
- 底部 = bottom 30%
- 基础盘 = 30-60%
- 命中 = 60-85%
- 小爆 = 85-95%
- 大爆 = top 5%

`/cheat-status` 在 N=10 时主动建议切换。这种方案永远自洽——不管账号多大，"top 5%"语义稳定。

---

> **参考博主的绝对桶**（25+ 视频拟合，**只适用于已有粉丝基础的成熟博主**——你 calibrated 之前不要照搬）：
>
> | Bucket | 范围（万播放） | 先验概率 |
> |---|---|---|
> | 底部 | <5w | 5% |
> | 基础盘 | 5-30w | 35% |
> | 命中 | 30-100w | 45% |
> | 爆款 | 100-150w | 12% |
> | 现象级 | >150w | 3% |

---

## 默认复盘窗口

`RETRO_WINDOW_DAYS = 3`

为什么 3 天：算法分发决策一般在 72 小时内基本结束；等更久只引入噪声不增信号。

如果你的平台特别——记得在这里写明覆盖原因，例如：
> 公众号 RETRO_WINDOW_DAYS = 7（推送后 24h 内发完，长尾更慢）
