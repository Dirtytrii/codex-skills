# 对标账号：[BENCHMARK-NAME]

> **本文件由 `/cheat-learn-from` 创建和维护**。
>
> 前期工具的 rubric / pattern / 选题方向感**大量**从这里推——这是你刚 init 时还没自己历史数据的 anchor。
>
> 当你自己累计 N≥10 校准样本后，benchmark 影响**自然减弱**——你的真实数据成为主要信号源。但 benchmark 不删，保留作 sanity check（看你账号是否真的偏离对标方向）。
>
> 你随时可以：
> - **追加**对标视频：`/cheat-learn-from --append <new-videos>`
> - **替换**对标账号：`/cheat-learn-from --replace <new-account>`

---

## 账号信息

- **名字**: [对标账号名]
- **平台**: [抖音 / B站 / YouTube / 公众号 / ...]
- **URL**: [账号主页]
- **粉丝量级**: [用户提供的，参考用——比如 "1w / 10w / 100w"]
- **风格 / 调性**: [用户描述——例 "知识科普 / 学术戏仿" / "个人吐槽" / "技术教程"]
- **导入时间**: [YYYY-MM-DD]
- **样本数**: N

---

## 导入的样本

| # | 视频标题 | 播放 | 点赞 | 评论 | 转发 | 你的印象 | transcript |
|---|---|---|---|---|---|---|---|
| 1 | [示例] 怎么停止期待 | 71w | 2.4w | 899 | 1.8w | 高 | samples/[BENCHMARK-NAME]/ab61ed09/transcript.md |
| 2 | [示例] 老板废话 | 39w | 1.2w | 567 | 7.9k | 中 | samples/[BENCHMARK-NAME]/5fe5d869/transcript.md |
| 3 | [示例] 谁问你了 | 11w | 3.8k | 198 | 2.7k | 低 | samples/[BENCHMARK-NAME]/8b5627e6/transcript.md |

> **印象档**：高 / 中 / 低 是你看完这条视频后**主观**判断的"算不算这个账号的代表作"——不是数据驱动，是直觉判断。这个判断比数据更能告诉 Claude 你想做什么风格。

---

## 基础 rubric 派生（init 时一次性，**仅给定性方向**）

> 基于 N 条对标样本观察，Claude 总结哪些维度看起来跟"高表现"相关、哪些不太相关。
> **不直接给数值权重**——5-10 样本数值拟合容易过拟合。给方向就行，用户决定要不要在 rubric_notes.md 调权重。

### 高表现样本共有的维度（看起来重要）

- [示例] **ER (情感共鸣) 高**：3/3 高表现样本都有强情感锚点
- [示例] **QL (金句密度) 高**：3/3 高表现样本都有 ≥2 句独立可传金句
- [示例] **MS (模因可挪用性) 高**：3/3 高表现样本评论区出现了挪用句式

### 低表现样本共有的维度（看起来不太重要）

- [示例] **SR (社会议题) 不显著**：低表现样本里 SR=4 也没救
- [示例] **NA (叙事性) 不显著**：高低样本 NA 分布无明显差异

### Claude 给的初始建议

- [示例] 你的对标账号看起来是**情感共鸣 + 金句**驱动型
- 建议初始 rubric 权重在 ER / QL / MS（如启用）上 ×1.5
- **但请等你自己跑 5+ 篇校准再正式 bump**——5 个对标样本不足以下结论

详见 [rubric_notes.md](rubric_notes.md) 的"benchmark-derived initial signals"段。

---

## 基础 patterns 派生

详见 [script_patterns.md](script_patterns.md) 的"对标 [BENCHMARK-NAME] 借鉴"段。

每条 pattern 标 **Imported, untested on my channel** —— 你的频道未必适用，实拍验证后（≥2 次跑出 + 复盘确认有效）再去掉这个标记。

---

## 选题方向感

> cheat-seed brainstorm 时会读这里——根据对标账号的主题分布给提议。

[示例] 对标账号常做的主题类型：
- 暗恋 / 情感戒断（占比 ~40%）
- 学术议题戏仿（占比 ~30%）
- 职场观察（占比 ~20%）
- 社会议题评论（占比 ~10%）

> 你不一定要做完全一样的主题——这只是个 reference frame。
> cheat-seed Mode A/B/C 仍以你的实际想做什么为主。

---

## 维护历史

| 日期 | 操作 | 详情 |
|---|---|---|
| YYYY-MM-DD | 首次导入 | N=3 条样本，方式 [way a 粘文本 / way b whisper] |

---

## 后续何时淡出

- 当 `state.calibration_samples >= 10` 时，cheat-status 会提示"你已有足够自己数据，benchmark 主要作 sanity check 不再主导"
- 但 benchmark.md **不删**——它仍是 cheat-seed brainstorm 的 reference frame
- 如果对标账号本身风格变了 / 你不想再对标了 → 跑 `/cheat-learn-from --replace <none>` 解除（保留历史在文件，但 cheat-seed 不再读）
