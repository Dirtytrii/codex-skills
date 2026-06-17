---
name: wechat-ai-app-ops
description: Operate the user's WeChat Official Account AI application content workflow. Use when working in an accounts/content repository on WeChat articles about AI applications, Agents, MCP, Skills, tool calling, workflows, open-source AI tooling updates, weekly AI application digests, image-rich WeChat article formatting, draft-box API updates, or local WeChat content handoff. Do not use for Xiaohongshu or Xianyu work.
---

# WeChat AI App Ops

Use this skill for the user's WeChat Official Account AI application content workflow, usually inside an `accounts` or content-operations repository. Stay inside the WeChat content lane unless the user explicitly asks for Xiaohongshu or Xianyu.

## Quick Workflow

1. Check repository state first:

```powershell
git status --short --branch
```

2. Read the current handoff and target article files before editing or API calls.
3. Classify the article as `weekly` or `flexible`.
4. For weekly articles, review the previous weekly article in the same series before drafting.
5. Improve the article as a WeChat article, not a cold changelog: use a strong hook, human judgment, varied section structures, visible reader stakes, and explanatory image anchors. Before generating preview or draft-box handoff, run a `humanizer-zh` pass to remove template phrasing, fake reader emotions, repetitive contrast structures, and AI-ish section labels without changing facts or attribution.
6. If the article feels visually dry, add 1-2 useful illustrations before draft-box update. Save images inside the WeChat article folder and configure `inline-images.json`.
7. Format with WeChat-compatible inline HTML and generate a local preview before touching the API.
8. Write to the WeChat draft box only when authorized. Before the user publishes, remind them that 原创、赞赏、留言 should stay enabled by default. Never publish unless the user explicitly authorizes publishing in the current turn.

## References

- For weekly/flexible article continuity, read `references/weekly-series-workflow.md`.
- For draft-box API guardrails, `.env.wechat.local`, IP whitelist handling, and verification, read `references/draft-box-workflow.md`.
- For article tone, anti-AI texture, varied subhead structures, inline illustrations, and brand/avatar assets, read `references/formatting-and-visuals.md`.

## Conditional Related Skills

Load these only when the article task needs that capability. If a related skill is not installed in the current Codex environment, state that and continue with the closest safe fallback:

- `wechat-tech-writer`: use for AI technology topic research, source gathering, and first-pass Chinese WeChat article drafting.
- `humanizer-zh`: use for Chinese article copy humanization, anti-AI texture, and final voice polish before WeChat preview or draft-box handoff.
- `story-deslop`: use only when a WeChat article contains narrative prose, story fragments, or dialogue that needs a natural storytelling pass; do not apply it to ordinary AI/tooling analysis copy.
- `wechat-article-formatter`: use when Markdown-to-WeChat HTML formatting needs a dedicated formatter or when polishing an existing WeChat HTML layout.
- `guizang-social-card-skill`: use for WeChat covers, inline social-card-style illustrations, explanatory Swiss-style figures, and image-rich article assets.
- `imagegen`: use for new bitmap brand assets such as avatars or non-vector visual concepts; copy final project assets into `content/wechat/...`.

## Local Commands

Prefer the repository's documented `node` command or system `node`. Use Codex bundled Node only when system `node` is unavailable or denied; discover the bundled path from the active Codex runtime/workspace dependencies instead of hard-coding a personal machine path.

On Windows PowerShell, read Chinese article files with explicit UTF-8 and avoid trusting garbled terminal output:

```powershell
Get-Content -Raw -Encoding UTF8 content\wechat\<date>\article.md
```

If a Node one-liner needs to match Chinese text, prefer reading UTF-8 files directly or use Unicode escapes in the check script instead of piping raw Chinese through a shell that may recode it.

```powershell
node --check scripts\wechat\create-draft.cjs
```

For this repository, the draft script is:

```powershell
node scripts\wechat\create-draft.cjs content\wechat\<date>
```

Use `WECHAT_MP_DRY_RUN=1` with `WECHAT_MP_HTML_PREVIEW_PATH` to generate the local HTML preview without WeChat API calls.

When updating an existing draft, set these only for the current shell:

```powershell
$result = Get-Content -Raw -Encoding UTF8 content\wechat\<date>\wechat-draft-result.json | ConvertFrom-Json
$env:WECHAT_MP_UPDATE_DRAFT_MEDIA_ID = $result.draft_media_id
$env:WECHAT_MP_THUMB_MEDIA_ID = $result.thumb_media_id
```

## Non-Negotiables

- Never publish by default. Draft-box write is not publishing.
- Never write AppID/AppSecret into repository files, article files, result JSON, or responses.
- Do not print secrets when checking `.env.wechat.local`; check presence only.
- Do not modify `content/xiaohongshu`, `content/xianyu`, or unrelated directories unless explicitly asked.
- If updating an existing WeChat draft, reuse the existing `draft_media_id` and `thumb_media_id` where possible instead of creating duplicate drafts.
- Do not leave generated WeChat assets only under `.codex/generated_images`; copy final assets into `content/wechat/...`.
- Body images must be uploaded through the WeChat article image path before API update; do not send draft content with local filesystem image paths.
- After API calls, report title, article path, cover path, source list path, draft `media_id`, and explicitly state whether it was only written to draft box and not published.
