# Weekly Series Workflow

Use this reference when an article is a weekly WeChat AI application digest, weekly observation, or any article marked with `content_dimension: weekly`.

## Mark Weekly Articles

Add weekly metadata to both frontmatter and metadata JSON when practical:

```yaml
content_dimension: weekly
series: AI 应用周观察
week_id: 2026-W23
weekly_reference_note: 后续按周发布文章需参考上一期周维度文章，尤其是“今日观察/下周关注”段落
```

Use `flexible` or omit the weekly field for articles published at flexible times that do not need weekly carry-forward.

## Before Drafting A Weekly Article

1. Find the previous article in the same series by `content_dimension`, `series`, and `week_id`.
2. Read its metadata and closing observation section, especially "今日观察", "下周关注", or equivalent follow-up points.
3. Decide which previous points should be carried forward, resolved, or explicitly dropped because the news cycle moved on.
4. Make the new weekly article feel like the next issue, not a standalone first issue.

## Continuity Pattern

Weekly articles should include one of these:

- A short callback to a previous observation.
- A note that a previous signal became stronger/weaker this week.
- A closing "next watch" list that future weekly articles can reference.

Do not force continuity into flexible-time articles unless the user asks.

## Closing Anchor

End weekly articles with a reusable follow-up anchor. The exact section name can vary, but it should give the next weekly window something concrete to inspect:

```text
今日观察：...
下周关注：...
下一期重点盯：...
```

Mirror the anchor into `metadata.json` when practical:

```json
{
  "weekly_reference": {
    "is_weekly": true,
    "policy": "后续按周发布文章需先参考上一期周维度文章，尤其是上一期“今日观察/下周关注”段落",
    "current_follow_up_anchor": "今日观察：..."
  }
}
```

Use this anchor as memory for the next weekly article; do not treat it as a promise to publish next week.
