---
name: xhs-short-video-workflow
description: Create Xiaohongshu/Rednote short-video packages for the user's AI-application account. Use when the user asks to make, plan, script, storyboard, voice, subtitle, render, preview, or review a short video, especially with HyperFrames, TTS, Codex/AI tool topics, or a "human only approves" workflow.
---

## Bundled Reference Contract

This is an on-demand method bundled by `agent-role-orchestrator`, not an independently discoverable skill. Load it only after the orchestrator routes the current role and task here. Resolve `scripts/`, `references/`, and `assets/` relative to this file's directory. Do not scan or preload sibling bundles.


# XHS Short Video Workflow

## Overview

Produce short videos as an approval-first pipeline: Codex proposes the topic, verifies facts, writes the 40-60 second script, prepares storyboard and subtitles, generates a vertical HyperFrames video with TTS, and asks the user only to approve or request changes.

## Boundaries

- Use this for Xiaohongshu AI-application short videos, not WeChat long articles or Xianyu listings.
- Do not click the final publish button. Stop at a reviewed MP4 and copy-ready posting package.
- Keep short-video data separate from image-text data until the user explicitly merges evaluation rules.
- Treat already-published XHS packages as read-only history unless the user explicitly asks for a re-edit/repost.

## Production Flow

1. Suggest topics from recent AI tool news, comments, account data, and the user's own intent.
2. After the user confirms a topic, verify current facts online and keep source links.
3. Write a 40-60 second script with a hard first-3-second hook.
4. Save `script.md`, `storyboard.md`, and `subtitles.srt` or `subtitles.md`.
5. Build a vertical HyperFrames video: big-text hook, evidence screenshots, motion cards, captions.
6. Generate voiceover with HyperFrames TTS first. Use Jianying/CapCut only as a fallback for voice style or final polish.
7. Render MP4, then return the file path and ask for one of: `通过`, `改钩子`, `改配音`, `改节奏`.

## File Layout

Default to the repo-local XHS video directory:

```text
content/xhs/videos/<yyyy-mm-dd>/<slug>/
  script.md
  storyboard.md
  subtitles.md or subtitles.srt
  sources.md
  DESIGN.md
  index.html
  assets/
  renders/
  report.md
```

Use `content/xhs/scripts/` only for loose pre-production drafts. Once a topic is confirmed for video production, create a folder under `content/xhs/videos/`.

## Script Rules

- Start at the conflict; avoid "today let's talk about".
- First 3 seconds: one spoken line plus one large on-screen line.
- Keep the script around 180-240 Chinese characters for 40-60 seconds.
- Use short sentences. Avoid long subordinate clauses because TTS sounds worse on them.
- Separate facts from judgment. Do not exaggerate unresolved bugs into confirmed universal damage.
- End with a takeaway, not a marketing-style question.
- Before generating voiceover, mark the emotional arc of the spoken script: hook tension, shared frustration, factual anchor, risk judgment, and short closing line. Do not let the whole video sound like one flat explainer paragraph.

## Visual Rules

- Use 1080x1920 vertical video.
- Prefer screenshot evidence, issue titles, simple comparison cards, and kinetic typography.
- Keep each scene to one idea.
- Keep subtitles readable without sound: at most two lines, high contrast, safe from bottom UI.
- Use HyperFrames visual identity gate: define `DESIGN.md` before writing composition HTML.
- Run HyperFrames lint, validate, inspect, and render when the environment supports it.
- If HyperFrames bundled Chrome or FFmpeg download fails, try the local fallback before interrupting the user: system Chrome plus project-local `ffmpeg-static` and `@ffprobe-installer/ffprobe`. Ask the user to manually download FFmpeg only after this fallback fails.
- If the default voice sounds robotic or too slow, use a neural TTS fallback such as `edge-tts`. For emotional pacing without a paid expressive TTS API, split the narration into sections and vary rate/pitch per section before concatenating the final audio.

## Approval Contract

After rendering, ask the user to choose only one review action:

- `通过`: prepare publish copy and paths.
- `改钩子`: revise first 3 seconds, cover frame, title, and opening subtitles.
- `改配音`: change voice, speed, pauses, or switch to Jianying/CapCut TTS fallback.
- `改节奏`: revise scene durations, subtitle density, and motion pacing.

## Metrics

For video reports, record account, title, publish time, video length, first-3-second hook, voice type, visual style, views/exposure, average watch time, approximate completion rate, likes, comments, saves, shares, follows, traffic source, and audience profile.
