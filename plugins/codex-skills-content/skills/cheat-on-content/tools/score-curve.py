#!/usr/bin/env python3
"""
score-curve.py — predict accuracy convergence chart for cheat-on-content.

Reads predictions/*.md (in the user's project), pairs each prediction's
center-of-bucket estimate against actual plays from the retrospective section,
and plots rolling-mean prediction error over time. The chart shows whether the
rubric is calibrating (error narrows) or drifting (error widens).

Usage:
    python tools/score-curve.py [--predictions DIR] [--out PATH] [--window N]

Defaults:
    --predictions  ./predictions
    --out          score-curve.png
    --window       5  (rolling-mean window in samples)

Dependencies: stdlib only for parsing; matplotlib for plotting (optional —
if absent, prints a CSV table to stdout instead).
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Bucket center mapping (the "中枢" if the prediction file doesn't spell it out
# explicitly). Units: 万 (10,000 plays). Adjust per platform if needed.
BUCKET_CENTERS = {
    "<5w": 2.5,
    "5-30w": 17.5,
    "30-100w": 65.0,
    "100-150w": 125.0,
    ">150w": 200.0,
}

PREDICTION_HEADER_RE = re.compile(r"^\*\*Bucket\*\*:\s*`?([^`\n]+?)`?\s*$", re.MULTILINE)
CENTER_RE = re.compile(r"中枢\s*[~约]?\s*(\d+(?:\.\d+)?)\s*w", re.IGNORECASE)
ACTUAL_PLAYS_RE = re.compile(r"播放[：:]\s*\*?\*?(\d+(?:\.\d+)?)\s*w", re.IGNORECASE)
DATE_FROM_FILENAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})_")


@dataclass
class Sample:
    file: Path
    date: datetime
    bucket: Optional[str]
    predicted_center_w: Optional[float]
    actual_plays_w: Optional[float]

    @property
    def has_retro(self) -> bool:
        return self.actual_plays_w is not None

    @property
    def signed_error_pct(self) -> Optional[float]:
        """(actual - predicted) / predicted, in percent."""
        if self.predicted_center_w is None or self.actual_plays_w is None or self.predicted_center_w == 0:
            return None
        return (self.actual_plays_w - self.predicted_center_w) / self.predicted_center_w * 100

    @property
    def abs_error_pct(self) -> Optional[float]:
        sep = self.signed_error_pct
        return abs(sep) if sep is not None else None


def parse_prediction_file(path: Path) -> Sample:
    text = path.read_text(encoding="utf-8")

    # Date from filename (YYYY-MM-DD_<id>_<short>.md)
    m = DATE_FROM_FILENAME_RE.search(path.name)
    if not m:
        raise ValueError(f"{path.name}: filename does not start with YYYY-MM-DD_")
    date = datetime.strptime(m.group(1), "%Y-%m-%d")

    # Split prediction vs retro section
    pred_section, _, retro_section = text.partition("## 复盘")

    # Bucket from prediction section
    bm = PREDICTION_HEADER_RE.search(pred_section)
    bucket = bm.group(1).strip() if bm else None

    # Predicted center: prefer explicit "中枢 ~50w", fall back to bucket midpoint
    cm = CENTER_RE.search(pred_section)
    if cm:
        predicted_center_w = float(cm.group(1))
    elif bucket and bucket in BUCKET_CENTERS:
        predicted_center_w = BUCKET_CENTERS[bucket]
    else:
        predicted_center_w = None

    # Actual plays from retro section
    actual_plays_w = None
    if retro_section.strip():
        am = ACTUAL_PLAYS_RE.search(retro_section)
        if am:
            actual_plays_w = float(am.group(1))

    return Sample(
        file=path,
        date=date,
        bucket=bucket,
        predicted_center_w=predicted_center_w,
        actual_plays_w=actual_plays_w,
    )


def collect_samples(predictions_dir: Path) -> list[Sample]:
    samples: list[Sample] = []
    for path in sorted(predictions_dir.glob("*.md")):
        try:
            samples.append(parse_prediction_file(path))
        except (ValueError, OSError) as e:
            print(f"warn: skipping {path.name}: {e}", file=sys.stderr)
    return samples


def rolling_mean(values: list[float], window: int) -> list[float]:
    if not values:
        return []
    out = []
    for i in range(len(values)):
        lo = max(0, i - window + 1)
        chunk = values[lo : i + 1]
        out.append(sum(chunk) / len(chunk))
    return out


def render_chart(samples: list[Sample], out_path: Path, window: int) -> bool:
    """Returns True on success, False if matplotlib is unavailable."""
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        from matplotlib import font_manager
    except ImportError:
        return False

    # Try to find a CJK-capable font so Chinese labels render. Falls back silently
    # to default if none available — labels will show as boxes but the chart still works.
    for cand in ("PingFang SC", "Heiti SC", "Hiragino Sans GB", "Noto Sans CJK SC", "Microsoft YaHei", "WenQuanYi Zen Hei"):
        try:
            if any(cand.lower() in f.name.lower() for f in font_manager.fontManager.ttflist):
                plt.rcParams["font.sans-serif"] = [cand] + plt.rcParams.get("font.sans-serif", [])
                plt.rcParams["axes.unicode_minus"] = False
                break
        except Exception:
            pass

    samples_with_retro = [s for s in samples if s.has_retro and s.abs_error_pct is not None]
    if not samples_with_retro:
        print("error: no samples with retro data — nothing to plot", file=sys.stderr)
        return True  # signal "we did our part"; nothing to plot is not a missing-deps issue

    samples_with_retro.sort(key=lambda s: s.date)
    abs_errors = [s.abs_error_pct for s in samples_with_retro]
    signed_errors = [s.signed_error_pct for s in samples_with_retro]
    rolling = rolling_mean(abs_errors, window)
    indices = list(range(1, len(samples_with_retro) + 1))

    fig, ax = plt.subplots(figsize=(10, 5))
    ax.bar(indices, abs_errors, alpha=0.3, label=f"|误差%| 单篇", color="steelblue")
    ax.plot(indices, rolling, marker="o", linewidth=2, label=f"|误差%| 滚动 {window} 篇均值", color="firebrick")
    ax.axhline(50, linestyle="--", linewidth=1, color="gray", label="cold-start 期参考线 (±50%)")
    ax.axhline(25, linestyle=":", linewidth=1, color="green", label="校准成熟期目标 (±25%)")

    ax.set_xlabel("第 N 篇校准样本")
    ax.set_ylabel("|预测中枢偏差%|")
    ax.set_title("Cheat-on-Content — 预测精度收敛曲线")
    ax.set_xticks(indices)
    ax.set_xticklabels([s.date.strftime("%m-%d") for s in samples_with_retro], rotation=45, ha="right")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    return True


def render_csv(samples: list[Sample]) -> None:
    """Fallback when matplotlib is unavailable."""
    writer = csv.writer(sys.stdout)
    writer.writerow(["file", "date", "bucket", "predicted_center_w", "actual_plays_w", "signed_error_pct"])
    for s in sorted(samples, key=lambda x: x.date):
        writer.writerow(
            [
                s.file.name,
                s.date.date().isoformat(),
                s.bucket or "",
                s.predicted_center_w if s.predicted_center_w is not None else "",
                s.actual_plays_w if s.actual_plays_w is not None else "",
                f"{s.signed_error_pct:.1f}" if s.signed_error_pct is not None else "",
            ]
        )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--predictions", type=Path, default=Path("predictions"), help="prediction files directory")
    ap.add_argument("--out", type=Path, default=Path("score-curve.png"), help="output chart path")
    ap.add_argument("--window", type=int, default=5, help="rolling-mean window in samples")
    args = ap.parse_args()

    if not args.predictions.is_dir():
        print(f"error: {args.predictions} is not a directory", file=sys.stderr)
        return 2

    samples = collect_samples(args.predictions)
    if not samples:
        print(f"error: no prediction files found under {args.predictions}", file=sys.stderr)
        return 1

    n_with_retro = sum(1 for s in samples if s.has_retro)
    print(f"found {len(samples)} predictions, {n_with_retro} with retrospective data", file=sys.stderr)

    plotted = render_chart(samples, args.out, args.window)
    if plotted:
        print(f"chart written → {args.out}", file=sys.stderr)
    else:
        print("matplotlib not installed — emitting CSV to stdout instead", file=sys.stderr)
        render_csv(samples)

    return 0


if __name__ == "__main__":
    sys.exit(main())
