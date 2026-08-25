#!/usr/bin/env python3
"""Report and optionally refresh CodeGraph readiness from the real CLI state."""

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


def gitignore_declares_codegraph(project: Path) -> bool:
    """Recognize the common root and recursive forms, including a trailing slash."""
    for raw_line in read_gitignore(project).splitlines():
        pattern = raw_line.strip()
        if not pattern or pattern.startswith("#") or pattern.startswith("!"):
            continue
        normalized = pattern.replace("\\", "/").removeprefix("./")
        normalized = normalized.removeprefix("/").rstrip("/")
        if normalized in {".codegraph", "**/.codegraph"}:
            return True
    return False


def index_is_ignored(project: Path) -> bool:
    if gitignore_declares_codegraph(project):
        return True
    git_path = shutil.which("git")
    if not git_path or not (project / ".git").exists():
        return False
    result = subprocess.run(
        [git_path, "check-ignore", "-q", "--no-index", ".codegraph"],
        cwd=str(project),
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0


def compact_message(value: str, limit: int = 500) -> str:
    collapsed = " ".join(value.split())
    if len(collapsed) <= limit:
        return collapsed
    return collapsed[: limit - 1] + "…"


def pending_change_count(pending: object) -> int | None:
    if not isinstance(pending, dict):
        return None
    values = [value for value in pending.values() if isinstance(value, int)]
    return sum(values) if values else 0


def has_worktree_mismatch(value: object) -> bool:
    return value not in (None, False, "", [], {})


def apply_cli_status(
    status: dict[str, object], result: subprocess.CompletedProcess[str]
) -> None:
    status["status_attempted"] = True
    status["status_returncode"] = result.returncode
    status["status_stderr"] = compact_message(result.stderr)
    if result.returncode != 0:
        return

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        status["status_parse_error"] = str(exc)
        return
    if not isinstance(payload, dict):
        status["status_parse_error"] = "codegraph status JSON must be an object"
        return

    pending = payload.get("pendingChanges")
    mismatch = payload.get("worktreeMismatch")
    pending_count = pending_change_count(pending)
    status.update(
        {
            "status_checked": True,
            "status_reported_initialized": payload.get("initialized"),
            "file_count": payload.get("fileCount"),
            "node_count": payload.get("nodeCount"),
            "edge_count": payload.get("edgeCount"),
            "pending_changes": pending,
            "pending_change_count": pending_count,
            "worktree_mismatch": mismatch,
            "fresh": pending_count == 0 and not has_worktree_mismatch(mismatch),
        }
    )


def finish_status(status: dict[str, object]) -> dict[str, object]:
    initialized = bool(status["initialized"])
    tool_available = bool(status["tool_available"])
    status_checked = bool(status["status_checked"])
    reported_initialized = status.get("status_reported_initialized")
    fresh = status.get("fresh") is True
    status["ready"] = bool(
        status["project_exists"]
        and initialized
        and tool_available
        and status_checked
        and reported_initialized is not False
        and fresh
    )

    if not status["project_exists"]:
        recommendation = "确认项目路径后重新检查。"
        reason = "项目路径不存在或不是目录。"
        freshness = "未检查"
    elif not tool_available:
        recommendation = "安装或启用 CodeGraph CLI 后重查；检查器不会静默安装全局工具。"
        reason = "未发现 codegraph 命令。"
        freshness = "无法确认"
    elif not initialized:
        recommendation = "获得明确写入授权后运行 codegraph init，再重新检查。"
        reason = "尚未发现 .codegraph/ 索引目录。"
        freshness = "未初始化"
    elif not status_checked:
        detail = status.get("status_stderr") or status.get("status_parse_error") or "无可用错误详情"
        recommendation = "修复 codegraph status 错误后重查，不要仅凭 .codegraph/ 目录判定可用。"
        reason = f"codegraph status 未确认成功：{detail}"
        freshness = "无法确认"
    elif reported_initialized is False:
        recommendation = "CLI 未确认索引已初始化；检查索引版本并在授权后重新初始化。"
        reason = "存在 .codegraph/ 目录，但 codegraph status 报告 initialized=false。"
        freshness = "无法确认"
    elif not fresh:
        recommendation = "获得明确写入授权后运行 codegraph sync，再重新检查。"
        reason = (
            f"索引存在待同步状态：pending={status.get('pending_changes')}；"
            f"worktreeMismatch={status.get('worktree_mismatch')}。"
        )
        freshness = "存在待同步变更"
    else:
        recommendation = "索引可用于当前架构分析。"
        reason = "无。"
        freshness = "最新"

    if status["ready"] and not status["index_ignored_by_gitignore"]:
        recommendation += " 建议确认 .codegraph/ 是否应加入 .gitignore。"

    status["freshness_status"] = freshness
    status["recommendation"] = recommendation
    status["skip_or_failure_reason"] = reason
    return status


def build_status(project: Path, codegraph_command: str | None = None) -> dict[str, object]:
    resolved = project.expanduser().resolve()
    project_exists = resolved.is_dir()
    index_path = resolved / ".codegraph"
    initialized = project_exists and index_path.is_dir()
    codegraph_path = codegraph_command or shutil.which("codegraph")
    status: dict[str, object] = {
        "project": str(resolved),
        "project_exists": project_exists,
        "tool_available": bool(codegraph_path),
        "tool_path": codegraph_path or "未找到",
        "initialized": initialized,
        "initialization_status": "已初始化" if initialized else "未初始化",
        "index_path": str(index_path),
        "index_ignored_by_gitignore": index_is_ignored(resolved) if project_exists else False,
        "status_attempted": False,
        "status_checked": False,
        "status_returncode": None,
        "status_stderr": "",
        "status_parse_error": "",
        "status_reported_initialized": None,
        "file_count": None,
        "node_count": None,
        "edge_count": None,
        "pending_changes": None,
        "pending_change_count": None,
        "worktree_mismatch": None,
        "fresh": None,
    }

    if project_exists and initialized and codegraph_path:
        result = subprocess.run(
            [str(codegraph_path), "status", "--json", str(resolved)],
            cwd=str(resolved),
            text=True,
            capture_output=True,
            check=False,
        )
        apply_cli_status(status, result)
    return finish_status(status)


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
        [str(status["tool_path"]), "init"],
        cwd=str(project.expanduser().resolve()),
        text=True,
        capture_output=True,
        check=False,
    )
    refreshed = build_status(project, str(status["tool_path"]))
    refreshed["init_attempted"] = True
    refreshed["init_returncode"] = result.returncode
    refreshed["init_stdout"] = compact_message(result.stdout)
    refreshed["init_stderr"] = compact_message(result.stderr)
    refreshed["init_result"] = (
        "初始化并确认完成。"
        if result.returncode == 0 and refreshed["ready"]
        else "初始化未确认成功。"
    )
    return refreshed


def maybe_sync(project: Path, status: dict[str, object]) -> dict[str, object]:
    if not status["project_exists"]:
        status["sync_attempted"] = False
        status["sync_result"] = "跳过：项目路径不存在。"
        return status
    if not status["initialized"]:
        status["sync_attempted"] = False
        status["sync_result"] = "跳过：项目尚未初始化。"
        return status
    if not status["tool_available"]:
        status["sync_attempted"] = False
        status["sync_result"] = "跳过：未发现 codegraph 命令。"
        return status

    result = subprocess.run(
        [str(status["tool_path"]), "sync"],
        cwd=str(project.expanduser().resolve()),
        text=True,
        capture_output=True,
        check=False,
    )
    refreshed = build_status(project, str(status["tool_path"]))
    refreshed["sync_attempted"] = True
    refreshed["sync_returncode"] = result.returncode
    refreshed["sync_stdout"] = compact_message(result.stdout)
    refreshed["sync_stderr"] = compact_message(result.stderr)
    refreshed["sync_result"] = (
        "同步并确认完成。"
        if result.returncode == 0 and refreshed["ready"]
        else "同步未确认成功。"
    )
    return refreshed


def render_human(status: dict[str, object]) -> str:
    ignored = "是" if status["index_ignored_by_gitignore"] else "否/未配置"
    return "\n".join(
        [
            "【CodeGraph 状态】",
            f"- 项目：{status['project']}",
            f"- 工具可用性：{'可用' if status['tool_available'] else '不可用'}（{status['tool_path']}）",
            f"- 初始化状态：{status['initialization_status']}",
            f"- 索引新鲜度：{status['freshness_status']}；ready={'是' if status['ready'] else '否'}",
            f"- 索引路径/忽略策略：{status['index_path']}；.gitignore 忽略：{ignored}",
            f"- 索引摘要：files={status['file_count']}；nodes={status['node_count']}；edges={status['edge_count']}",
            f"- 待同步状态：pending={status['pending_changes']}；worktreeMismatch={status['worktree_mismatch']}",
            f"- 建议动作：{status['recommendation']}",
            f"- 跳过或失败原因：{status['skip_or_failure_reason']}",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Check CodeGraph CLI, initialization, and index freshness. Defaults to read-only.",
    )
    parser.add_argument("--project", type=Path, required=True, help="Project root to inspect.")
    mutation = parser.add_mutually_exclusive_group()
    mutation.add_argument("--init", action="store_true", help="Explicitly run codegraph init when the project is not initialized.")
    mutation.add_argument("--sync", action="store_true", help="Explicitly run codegraph sync for an initialized project.")
    parser.add_argument("--require-ready", action="store_true", help="Exit non-zero unless the CLI confirms an initialized, fresh index.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    status = build_status(args.project)
    if args.init:
        status = maybe_initialize(args.project, status)
    elif args.sync:
        status = maybe_sync(args.project, status)

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        print(render_human(status))

    if not status["project_exists"]:
        return 2
    if args.require_ready and not status["ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
