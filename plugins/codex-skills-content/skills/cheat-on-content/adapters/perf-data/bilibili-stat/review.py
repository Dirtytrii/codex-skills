"""发完视频后跑一次：抓 B站数据/评论 → 生成 NotebookLM 友好的 md。

用法：
    python review.py login                          # B站无需登录（仅为接口一致）
    python review.py video <BV号或视频URL> [script.txt]   # 直接指定视频
"""
from __future__ import annotations

import sys
from pathlib import Path

import crawler
import renderer
from paths import videos_dir


def run_with_id(bvid: str, script_path: str | None) -> None:
    active_videos_dir = videos_dir()
    active_videos_dir.mkdir(parents=True, exist_ok=True)

    script = ""
    if script_path:
        p = Path(script_path).expanduser()
        if p.is_file():
            script = p.read_text(encoding="utf-8", errors="ignore")
            print(f"稿子：{p.name}（{len(script)} 字符）")
        else:
            print(f"[警告] 找不到稿子 {p}")

    print(f"[抓取] 视频 {bvid}")
    result = crawler.fetch_all(bvid)
    video = result["video"]
    comments = result["comments"]

    out_dir = renderer.output_dir_for(video, active_videos_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    if script:
        (out_dir / "script.txt").write_text(script, encoding="utf-8")
    md = renderer.render_report(video, script, comments)
    report = out_dir / "report.md"
    report.write_text(md, encoding="utf-8")
    print(f"\n✓ {report}")


def main() -> None:
    if len(sys.argv) > 1 and sys.argv[1] == "login":
        print("[B站] 视频数据与评论均为公开接口，无需登录，直接复盘即可。")
        return
    if len(sys.argv) > 1 and sys.argv[1] == "video":
        if len(sys.argv) < 3:
            print("用法：python review.py video <BV号或视频URL> [script.txt]")
            sys.exit(3)
        bvid = sys.argv[2]
        script_path = sys.argv[3] if len(sys.argv) > 3 else None
        run_with_id(bvid, script_path)
        return
    print(__doc__)


if __name__ == "__main__":
    main()
