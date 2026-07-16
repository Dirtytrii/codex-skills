# Content Routing

Read this file only for public writing, content research, visual-content collaboration, or publishing.

## Editorial Ownership

`内容主编` owns topic value, audience fit, claims, sources, tone, platform split, and final editorial acceptance. `公众号发布`, `小红书`, and `视频` execute platform packages. `UI/PPT` owns visual assets when requested. Each platform action keeps its own authorization boundary.

## X MCP Content Research Source

Official documentation: [X MCP](https://docs.x.com/tools/mcp).

Use authorized read-only access for trend scanning, topic discovery, benchmark accounts, public posts, timelines, and discussion patterns. The content editor decides what evidence transfers across platforms.

Do not write client secrets into a repository or callback. Posting, publishing Articles, following, liking, reposting, messaging, or changing account settings requires separate explicit authorization.

## Content Tone Gate

All formal public Chinese copy must pass the `反老登味 / 反 AI 味内容闸门` before preview or delivery.

- Remove lecturing, paternal tone, status pressure, greasy success language, and conclusions imposed on readers.
- Remove generic templates, empty parallelism, mechanical transitions, inflated summaries, and unsupported confidence.
- Preserve concrete experience, natural speech, platform rhythm, and the reader's actual situation.
- Use `$humanizer-zh` for the final pass, but do not change facts, numbers, dates, sources, prices, authorization, or publication state.

## Xiaohongshu Automation Publisher Gate

Load `$browser-automation-router` first. Use the native Chrome surface for authorized interactive login state, creator-center filling, and visible publishing-blocker diagnosis. Use `$xhs-automation-publisher` for deterministic Python/CDP batch filling, search/detail reads, data export, or an explicit fallback when the native plugin is unavailable.

Default to preview/fill. Clicking publish, posting/responding to comments, likes, bookmarks, account switching, or profile cleanup requires a fresh explicit confirmation. Never store cookies, QR codes, real account state, or local Chrome profile paths in the repository.

Published local packages are historical records unless the user explicitly asks to republish or re-edit them.

## WeChat And Video

WeChat packages must separate copy/formatting/draft preparation from final publish authorization. Video packages must separate scripts/assets/rendering from platform publishing. Public claims need source evidence and owner review.

## Visual Collaboration

When a reference image exists, UI/PPT first selects the implementation route. Do not force complex illustration, texture, 3D, particles, or motion into fragile CSS when generated/manual assets, Canvas/SVG, Three.js, Lottie/video, or a proven library is more reliable.
