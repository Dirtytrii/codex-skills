---
name: xhs-comment-research
description: Read and analyze Xiaohongshu/Rednote comments from the user's logged-in Chrome session. Use when the user asks to crawl, collect, export, summarize, classify, or use 小红书评论区 / XHS comments for content planning, follow-up posts, audience research, reply strategy, or 引流文案. Works best for already-open note pages or creator-manager note links.
---

# XHS Comment Research

Use this skill to turn Xiaohongshu comment threads into content intelligence.

## Safety

- Stay read-only except for opening/expanding/scrolling comment UI needed to load text.
- Do not like, reply, delete, pin, report, publish, follow, message, or change settings.
- Do not inspect cookies, local storage, passwords, tokens, or browser profile files.
- Treat comments as user research. Quote sparingly; prefer paraphrase and theme summaries.
- If a captcha, login prompt, or permission prompt appears, stop and ask the user.

## Browser Path

Use the Chrome plugin when comments require the user's logged-in session.

1. Connect to Chrome with the plugin's `browser-client.mjs`.
2. Read `await browser.documentation()` once per fresh browser session.
3. Use `browser.user.openTabs()` to find an already-open note page when possible.
4. Claim the exact tab with `browser.user.claimTab(tabInfo)`.
5. Prefer Playwright `domSnapshot()` or read-only `evaluate()` for extraction.
6. Use clicks only for harmless UI expansion such as "展开 ... 条回复".
7. End with `browser.tabs.finalize({ keep: [] })` unless the user needs the page kept.

## Extraction Workflow

1. Confirm target note title/URL and output folder.
2. Capture visible note metadata:
   - title
   - URL
   - displayed comment count
   - current loaded comment count
3. Scroll the `.note-scroller` container from top to bottom in small batches.
4. Repeatedly expand visible reply buttons matching `展开` / `条回复` when present.
5. Extract `.comment-item` records:
   - `id`
   - `isSub`
   - `name`
   - `content`
   - `date`
   - `like`
6. Deduplicate by `id` when available; otherwise by `name + content + date`.
7. Save raw JSON and an analysis markdown file in the article folder.

## Analysis Workflow

Group comments by useful content angles, not generic sentiment:

- engineering-complexity: architecture, components, concurrency, data, maintainability
- local-vs-online: localhost, "works on my machine", environment, deployment
- black-box-debugging: cannot debug, prompt iteration, token burn, frontend/backend diagnosis
- professional-validation: programmer still needed, someone must own review/兜底
- security-and-commercial-risk: security, data, payment, business liability
- pro-ai-non-cs: non-CS can build MVPs, product sense, demand discovery
- identity-conflict: 文科/理科/程序员 identity jokes or disputes
- content-hooks: phrases that can become titles, covers, comments, or follow-up posts

When revising content based on comments:

- Correct any earlier assumption that the comments do not support.
- Start from the actual dominant tension in the thread.
- Separate "what the comments say" from "our content judgment".
- Keep follow-up copy emotionally aware: acknowledge programmers' objections before giving advice to non-CS readers.

## Output Files

Use stable filenames:

- `comments-raw.json`: raw deduplicated comment records and metadata.
- `comment-analysis.md`: summary, themes, evidence snippets, and content implications.
- `content-pack.md`: update only when the user asks to revise the article package.

## Quality Bar

Before claiming the crawl is complete:

- Report loaded versus displayed comment counts.
- Explain if the platform did not expose all comments or if replies were still collapsed.
- Save enough raw data for later re-analysis.
- Do not pretend partial data is complete.

