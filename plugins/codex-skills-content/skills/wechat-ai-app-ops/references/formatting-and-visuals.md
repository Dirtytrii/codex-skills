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

Before preview generation, run a `humanizer-zh` pass over the public article body and section labels. Remove fake reader emotions such as "别急着兴奋" unless the article has actually built that emotion, reduce repetitive "不是...而是..." contrast scaffolding, and replace template labels with content-specific short headings.

Adjacent heading layers must not say the same thing twice. The small kicker, section title, and first sentence should each do a different job: context, claim, then evidence. If two neighboring headings both mean "先看这条线" or repeat the same noun, rewrite one before preview.

Avoid meta-explainer phrases such as "翻译成人话就是" / "说人话就是" in public copy. They sound like the writer is narrating the act of simplifying instead of simply writing clearly. Replace them with direct transitions such as "拆开看，是三件事" or no transition at all.

## Lightweight Frontmatter Layout Controls

When the draft script supports article-specific frontmatter controls, prefer small explicit fields instead of hard-coding one house style for every article:

```yaml
wechat_eyebrow: AI 应用短回应 / Agent / MCP / 企业治理
wechat_lead_punch: 每个人自己装 MCP，迟早会变成安全债。
wechat_summary_label: 回应上篇的一个坑
wechat_layout: short_response
```

Use these fields to let each article define its own column strip, opening punch line, summary label, and layout family. This is especially useful for flexible short articles that should not look like weekly digests.

For `wechat_layout: short_response`, treat it as a flexible layout family, not a fixed template:

- keep the top structure lighter and more conversational than weekly articles
- choose fresh short section labels for each article; do not reuse the same labels such as `短回应`, `先别急`, `我的判断`, or `谁要关注` by default
- prefer short titles with bite: 2-6 Chinese characters where possible, or one compact spoken phrase
- do not overuse question titles; rotate between claim titles, image-like nouns, tension statements, and only occasional questions
- avoid repeating the same lead-in sentence for every section
- vary visual rhythm by article: image-led cards, side-by-side comparisons, ledger/checklist blocks, quote punches, timeline strips, or mini diagrams
- vary accent colors or section shapes by article while keeping typography disciplined
- use "上篇文章" in public copy; keep "周观察" and week-tracking language as internal metadata only
- make short articles more image-rich than weekly digests when the topic benefits from visual explanation
- keep short-article prose flexible for now; do not lock a rigid house style until there are more successful samples

If two consecutive short articles look structurally similar, redesign the next one before touching the WeChat API. If a short article preview still reads like a weekly issue, adjust the layout branch or frontmatter first.

## Chinese Encoding On Windows

Windows PowerShell may display Chinese Markdown or stdin-piped Node checks as mojibake. Do not judge article text from garbled terminal output.

Use explicit UTF-8 reads:

```powershell
Get-Content -Raw -Encoding UTF8 content\wechat\<date>\article.md
```

For automated preview checks that match Chinese phrases, prefer a small `.js` file, direct UTF-8 file reads, or Unicode escapes in the Node snippet. Avoid piping raw Chinese through shell stdin when the console encoding is uncertain.

## Inline Illustrations

When the article feels dry, add inner illustrations where they clarify the argument:

- after the opening or section 01: a workflow/relationship diagram
- after the governance/security sections: a risk chain or permissions map
- for short articles: a higher image ratio is acceptable; use content-driven cards, diagrams, or visual metaphors instead of forcing the weekly article rhythm

Use `$guizang-social-card-skill` when its visual language fits, but do not force it for every short article and do not update that skill unless explicitly asked. Prefer content-first images that explain the article's specific argument. Keep text short, avoid decorative filler, and export local PNG assets before uploading or embedding them in WeChat content.

Images should be explanatory anchors, not generic AI art.

If generated images contain Chinese text, Chinese readability is a hard requirement: inspect the rendered PNG at normal mobile-reading size, regenerate or simplify the design if characters are distorted, crowded, or too small.

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
