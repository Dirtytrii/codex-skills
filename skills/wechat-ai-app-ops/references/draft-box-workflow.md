# Draft Box Workflow

Use this reference when writing or updating WeChat Official Account drafts through API.

## Authorization Boundary

Only write to the draft box after the user has authorized draft creation or update. Draft-box write does not imply publish permission. Publishing requires a separate explicit authorization in the current turn.

## Credentials

Use `.env.wechat.local` in the repository root or process environment:

```text
WECHAT_MP_APPID
WECHAT_MP_APPSECRET
WECHAT_MP_AUTHOR
WECHAT_MP_CONTENT_SOURCE_URL
WECHAT_MP_HTML_PREVIEW_PATH
WECHAT_MP_DRY_RUN
WECHAT_MP_UPDATE_DRAFT_MEDIA_ID
WECHAT_MP_THUMB_MEDIA_ID
```

Never echo, save, commit, or summarize AppSecret. When checking configuration, report only whether keys are present.

## Verification Before API Calls

1. Run `git status --short --branch`.
2. Run `node --check` on `scripts/wechat/create-draft.cjs`; if system Node is denied, use Codex bundled Node.
3. Generate an HTML preview with `WECHAT_MP_DRY_RUN=1` when formatting has changed.
4. Confirm no internal sections remain in preview HTML: title alternatives, API status, publish suitability notes, raw `#`/`##`, or H1.
5. If inline images exist, confirm the preview contains `<img>` tags, captions, and local preview paths only during dry run.

## Updating Existing Drafts

Prefer updating the existing draft instead of creating duplicates:

- Set `WECHAT_MP_UPDATE_DRAFT_MEDIA_ID` to the existing draft media id.
- Set `WECHAT_MP_THUMB_MEDIA_ID` to the existing cover thumb media id when keeping the cover.
- Keep `publish_state` as `draft_updated_not_published` or equivalent.

Do not persist these IDs into `.env.wechat.local` unless the user explicitly wants a repeatable local workflow. Prefer setting them in the current shell from `wechat-draft-result.json`.

## Inline Body Images

Use `inline-images.json` in the article folder for images that should appear inside the article body:

```json
[
  {
    "path": "illustrations/output/example.png",
    "alt": "正文插图说明",
    "caption": "图 1：一句话解释这张图为什么值得看。",
    "after_heading": "目标二级标题"
  }
]
```

Expected behavior for the draft script:

- Dry run: render local preview paths such as `illustrations/output/example.png`.
- Live draft update: upload each body image to WeChat article image storage with `cgi-bin/media/uploadimg`, then render the returned URL into article HTML.
- Result JSON: record `inline_images` with local path, WeChat URL, caption, and insertion heading.

Never send draft content with local filesystem image paths in a live API update.

## IP Whitelist Failure

If WeChat returns `errcode: 40164`, report the exact IP from WeChat's error payload. Also check public egress IP with a simple public IP service if helpful, but prefer the IP WeChat actually reports.

## Completion Report

Report:

- article title
- article path
- cover path
- sources path
- draft `media_id`
- inline image paths and upload status when images were added
- whether only draft box was updated and not published
