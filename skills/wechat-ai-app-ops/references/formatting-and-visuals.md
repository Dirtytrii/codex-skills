# Formatting And Visuals

Use this reference when improving WeChat article tone, HTML formatting, or visual pacing.

## Anti-AI Tone

Avoid a cold information-feed style. Prefer:

- a human hook before the facts
- short paragraphs with occasional sentence fragments
- reader stakes: "who should care", "what gets dangerous", "what becomes expensive"
- clear opinion boundaries such as "我的判断"
- conservative factual claims with source boundaries
- a few sentence-level rhythm changes: one-line punches, small warnings, and plain-language transitions

Do not turn vendor press releases into verified market truth. Mark them as market signals when needed.

## Avoid Repeated Section Templates

Do not make every section use the same four subheads. Vary both copy and visual structure.

Bad repeated structure:

```text
发生了什么
为什么重要
谁该关注
我怎么看
```

Better pattern:

```text
这不是 IDE 小功能，是后台派工单
关键变化：Agent 从按钮变成流程
谁要关注 / 手里有仓库维护活的人，看这里
我的判断：成本和责任会一起浮出来
```

Use "谁要关注" instead of "适合谁看".

When there are numbered sections, do not give every section the same visual skeleton. Mix at least two of these structures:

- a short setup paragraph before the first subhead
- a risk callout before "为什么重要"
- a compact "谁要关注" line with a concrete audience
- a 2-3 item checklist or ledger
- a quote-like judgment block
- a short closing punch without a subhead

If `01` to `05` can be swapped without the reader noticing, the structure is too flat.

## WeChat HTML Formatting

Use inline styles compatible with WeChat. Remove H1 from body because WeChat has a separate title field.

Recommended rhythm:

- top meta strip
- strong lead block
- summary block
- section header with chapter-specific kicker
- varied subheads
- source notes in subdued blocks
- source list at the bottom only if needed

Generate a local preview HTML and inspect it before API updates.

## Inline Illustrations

When the article feels dry, add 1-2 inner illustrations only where they clarify the argument:

- after the opening or section 01: a workflow/relationship diagram
- after the governance/security sections: a risk chain or permissions map

Use `$guizang-social-card-skill` for the visual language, but do not update that skill unless explicitly asked. Prefer Swiss-style information graphics for AI/tooling articles. Keep text short, avoid decorative filler, and export local PNG assets before uploading or embedding them in WeChat content.

Images should be explanatory anchors, not generic AI art.

Recommended illustration spec:

- Size: `1200x675` PNG for inline WeChat figures.
- Storage: `content/wechat/<date>/illustrations/output/*.png`.
- Config: add each image to `content/wechat/<date>/inline-images.json`.
- Caption: start with `图 1：` / `图 2：` and state the argument, not the obvious contents.
- Validation: inspect the rendered PNG, confirm no text collision, then dry-run the HTML preview.

Good inline figures for this account:

- Agent execution chain: chat box -> API/task dispatch -> MCP/tools -> logs/audit -> rollback.
- MCP governance map: identity -> permissions -> approval -> trace -> rollback.
- Workflow before/after comparison: assistant as chat vs agent as operator.

Avoid:

- generic robot heads, glowing brains, stock AI clouds
- purely decorative social-card filler
- dense screenshots or diagrams that become unreadable in mobile preview
- one image after every section; two strong anchors are usually better

## Brand Assets

For WeChat brand assets such as account avatars, covers, or reusable identity marks:

- Keep final assets under `content/wechat/brand/...` or the article's own WeChat folder.
- If using generated images, copy the selected output out of `.codex/generated_images` into the workspace.
- Verify square avatars as square PNGs and visually inspect them at normal size.
- Do not include tiny text in avatars; WeChat crops and scales aggressively.
