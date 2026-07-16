#!/usr/bin/env python3
"""Report CodeGraph readiness without relying on chat memory or guessing."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path


def read_gitignore(project: Path) -> str:
    gitignore = project / ".gitignore"
    if not gitignore.is_file():
        return ""
    return gitignore.read_text(encoding="utf-8", errors="ignore")


def build_status(project: Path) -> dict[str, object]:
    resolved = project.resolve()
    project_exists = resolved.is_dir()
    index_path = resolved / ".codegraph"
    initialized = project_exists and index_path.exists()
    codegraph_path = shutil.which("codegraph")
    gitignore_text = read_gitignore(resolved) if project_exists else ""
    ignored = any(line.strip() == ".codegraph" for line in gitignore_text.splitlines())

    if not project_exists:
        recommendation = "确认项目路径后重新检查。"
        skip_reason = "项目路径不存在或不是目录。"
    elif initialized:
        recommendation = "可在架构分析前使用 CodeGraph；如索引过期，先刷新或重新初始化。"
        skip_reason = "无。"
    elif codegraph_path:
        recommendation = "从项目根目录运行 codegraph init -i 后重新检查。"
        skip_reason = "尚未发现 .codegraph/ 索引目录。"
    else:
        recommendation = "安装 CodeGraph CLI 或使用可用的 CodeGraph MCP 初始化后再继续深度架构分析。"
        skip_reason = "未发现 codegraph 命令，且项目未初始化。"

    return {
        "project": str(resolved),
        "project_exists": project_exists,
        "tool_available": bool(codegraph_path),
        "tool_path": codegraph_path or "未找到",
        "initialized": initialized,
        "initialization_status": "已初始化" if initialized else "未初始化",
        "index_path": str(index_path),
        "index_ignored_by_gitignore": ignored,
        "recommendation": recommendation,
        "skip_or_failure_reason": skip_reason,
    }


def maybe_initialize(project: Path, status: dict[str, object]) -> dict[str, object]:
    if not status["project_exists"]:
        status["init_attempted"] = False
        status["init_result"] = "跳过：项目路径不存在。"
        return status
    if status["initialized"]:
        status["init_attempted"] = False
        status["init_result"] = "跳过：已初始化。"
        return status
    if not status["tool_available"]:
        status["init_attempted"] = False
        status["init_result"] = "跳过：未发现 codegraph 命令。"
        return status

    result = subprocess.run(
        ["codegraph", "init", "-i"],
        cwd=str(project.resolve()),
        text=True,
        capture_output=True,
        check=False,
    )
    refreshed = build_status(project)
    refreshed["init_attempted"] = True
    refreshed["init_returncode"] = result.returncode
    refreshed["init_stdout"] = result.stdout.strip()
    refreshed["init_stderr"] = result.stderr.strip()
    refreshed["init_result"] = "初始化完成。" if result.returncode == 0 and refreshed["initialized"] else "初始化未确认成功。"
    return refreshed


def render_human(status: dict[str, object]) -> str:
    ignored = "是" if status["index_ignored_by_gitignore"] else "否/未配置"
    return "\n".join(
        [
            "【CodeGraph 状态】",
            f"- 项目：{status['project']}",
            f"- 工具可用性：{'可用' if status['tool_available'] else '不可用'}（{status['tool_path']}）",
            f"- 初始化状态：{status['initialization_status']}",
            f"- 索引路径/忽略策略：{status['index_path']}；.gitignore 忽略：{ignored}",
            f"- 建议动作：{status['recommendation']}",
            f"- 跳过或失败原因：{status['skip_or_failure_reason']}",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check CodeGraph CLI and project index status. Defaults to read-only.",
    )
    parser.add_argument("--project", type=Path, required=True, help="Project root to inspect.")
    parser.add_argument("--init", action="store_true", help="Run codegraph init -i when CLI exists and the project is not initialized.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    status = build_status(args.project)
    if args.init:
        status = maybe_initialize(args.project, status)

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(render_human(status))

    return 0 if status["project_exists"] else 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
