"""把抓到的 B站数据渲染成 NotebookLM 友好的 Markdown（与 douyin-session 同格式）。"""
from __future__ import annotations

import datetime as dt
from pathlib import Path


def _fmt_time(ts: int) -> str:
    if not ts:
        return "未知"
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def _fmt_num(n: int | None) -> str:
    if n is None:
        return "-"
    if n >= 10000:
        return f"{n / 10000:.1f}w"
    return str(n)


def _fmt_duration(s: int) -> str:
    if not s:
        return "-"
    return f"{s // 60}:{s % 60:02d}" if s >= 60 else f"{s}s"


def _ratio(num: int | None, den: int | None) -> str:
    if not num or not den:
        return "-"
    return f"{num / den * 100:.2f}%"


def render_report(video: dict, script: str, comments: list[dict]) -> str:
    lines: list[str] = []
    title = video.get("title") or "(无标题)"
    bvid = video["bvid"]
    play = video.get("play_count") or 0

    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"- BV 号：`{bvid}`")
    lines.append(f"- UP 主：{video.get('owner') or '-'}")
    lines.append(f"- 发布时间：{_fmt_time(video.get('pubdate', 0))}")
    lines.append(f"- 时长：{_fmt_duration(video.get('duration_s', 0))}")
    lines.append(f"- 链接：https://www.bilibili.com/video/{bvid}")
    lines.append(f"- 抓取时间：{dt.datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append("")

    lines.append("## 播放数据")
    lines.append("")
    lines.append(f"- 播放：{_fmt_num(play)}")
    lines.append(f"- 点赞：{_fmt_num(video.get('like_count'))}（赞播比 {_ratio(video.get('like_count'), play)}）")
    lines.append(f"- 投币：{_fmt_num(video.get('coin_count'))}（投币率 {_ratio(video.get('coin_count'), play)}）")
    lines.append(f"- 收藏：{_fmt_num(video.get('favorite_count'))}（收藏率 {_ratio(video.get('favorite_count'), play)}）")
    lines.append(f"- 分享：{_fmt_num(video.get('share_count'))}（分播比 {_ratio(video.get('share_count'), play)}）")
    lines.append(f"- 评论：{_fmt_num(video.get('comment_count'))}")
    lines.append(f"- 弹幕：{_fmt_num(video.get('danmaku_count'))}")
    lines.append("")
    lines.append("> 派生比率（赞播比 / 投币率 / 收藏率 / 分播比）是单纯播放量看不出的信号；"
                 "B站「三连率」（点赞+投币+收藏）尤其能反映内容的硬核认可度。")
    lines.append("")

    lines.append("## 原始稿子")
    lines.append("")
    lines.append(script.strip() if script.strip() else "（未提供）")
    lines.append("")

    lines.append(f"## 评论（按点赞降序，共 {len(comments)} 条）")
    lines.append("")
    if not comments:
        lines.append("（未抓到评论，可能评论区关闭或该视频暂无评论）")
    else:
        for c in comments:
            text = (c.get("text") or "").replace("\n", " ").strip()
            reply = f" 💬{c['reply_comment_total']}" if c.get("reply_comment_total") else ""
            loc = f" [{c['ip_label']}]" if c.get("ip_label") else ""
            lines.append(f"- [👍{c['digg_count']}{reply}]{loc} {text}")
    lines.append("")

    return "\n".join(lines)


def slugify(text: str, max_len: int = 30) -> str:
    bad = '<>:"/\\|?*\n\r\t'
    out = "".join("_" if ch in bad else ch for ch in text).strip()
    return out[:max_len] or "untitled"


def output_dir_for(video: dict, root: Path) -> Path:
    date = _fmt_time(video.get("pubdate", 0))[:10].replace("未知", "nodate")
    slug = slugify(video.get("title") or video["bvid"])
    return root / f"{date}_{slug}"
