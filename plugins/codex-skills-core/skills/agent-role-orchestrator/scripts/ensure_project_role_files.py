#!/usr/bin/env python3
"""Ensure project-level role orchestration files exist and carry reusable guards."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass
from pathlib import Path


AGENTS_BEGIN = "<!-- BEGIN agent-role-orchestrator entry rule -->"
AGENTS_END = "<!-- END agent-role-orchestrator entry rule -->"

AGENTS_BLOCK = f"""{AGENTS_BEGIN}
## Agent Role Orchestrator Entry Rule

- 总控/架构/多角色/派发/回调/台账类任务必须先使用 agent-role-orchestrator。
- 执行前必须读取：
  - 已安装的 agent-role-orchestrator/SKILL.md（通常位于 `${{CODEX_HOME:-$HOME/.codex}}/skills/agent-role-orchestrator/SKILL.md` 或 Windows `%USERPROFILE%\\.codex\\skills\\agent-role-orchestrator\\SKILL.md`）
  - .codex/role-windows.md
- 若未读取，不允许创建、继续或派发角色窗口；状态未知一律写“待确认”。
- .codex/role-windows.md 是角色路由 source of truth：有线程 ID 就复用，不新建；误开、废弃、纠偏也必须记录。
- 下游角色完成、阻塞或需要决策时，回调任务发起窗口，不默认全部回总控或架构。
{AGENTS_END}
"""

LEDGER_TEMPLATE = """# 角色窗口台账

> 本文件是角色路由 source of truth。状态未知写“待确认”，不要编造 thread id。

| 角色 | 状态 | thread id | 来源窗口 | 当前职责 | 下一步 | 循环状态 |
| --- | --- | --- | --- | --- | --- | --- |
| 总控 | 待确认 | 待确认 | 用户 | 入口分流、模型预算、最终验收 | 待确认 | 待总控分流 |
| 架构 | 待确认 | 待确认 | 总控 | CTO 技术拆解、开发/UI/测试/QA/安全/DBA/运维闭环 | 待确认 | 待架构拆解 |
| 内容主编 | 待确认 | 待确认 | 总控 | 公众号、小红书、视频、视觉资产协作 | 待确认 | 待内容主编拆解 |
| 开发 | 待确认 | 待确认 | 架构 | 代码实现和验证 | 待确认 | 待确认 |
| UI/PPT | 待确认 | 待确认 | 架构/内容主编 | UI/Frontend、PPT、视觉资产 | 待确认 | 待确认 |
| 测试 | 待确认 | 待确认 | 架构 | 测试用例、测试报告、压测/性能/并发验证 | 待确认 | 待确认 |
| QA | 待确认 | 待确认 | 架构 | 对抗式验收、Review readiness、风险审查 | 待确认 | 待确认 |
| 安全 | 待确认 | 待确认 | 架构 | 授权安全审计和低影响验证 | 待确认 | 待确认 |
| DBA | 待确认 | 待确认 | 架构 | 数据库实例风险和只读诊断 | 待确认 | 待确认 |
| 运维 | 待确认 | 待确认 | 架构 | 部署、日志、cron、服务诊断 | 待确认 | 待确认 |
| 公众号发布 | 待确认 | 待确认 | 内容主编 | 微信公众号草稿、预览、发布准备 | 待确认 | 待确认 |
| 小红书 | 待确认 | 待确认 | 内容主编 | 小红书内容实验、发布包、评论研究 | 待确认 | 待确认 |
| 视频 | 待确认 | 待确认 | 内容主编 | 视频脚本、分镜、素材和渲染计划 | 待确认 | 待确认 |
| 知识库 | 待确认 | 待确认 | 总控 | Obsidian/个人知识库整理 | 待确认 | 待确认 |
| 技能维护 | 待确认 | 待确认 | 总控 | skill 命中率、触发规则、registry/README/docs 维护 | 待确认 | 待确认 |
| 文档/交付 | 待确认 | 待确认 | 总控/架构 | 交付清单、验收材料、操作指南和交接文档 | 待确认 | 待确认 |

## 最近回调

- 待确认

## 压缩交接卡

- 最近摘要：待确认
- 关键决策：待确认
- 当前证据：待确认
- 下一步：待确认
- 新窗口接续提示：待确认
"""


@dataclass
class Action:
    status: str
    path: str
    detail: str


def normalize_newlines(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n")


def ensure_agents_content(existing: str | None) -> tuple[str, bool, str]:
    if existing is None:
        return "# AGENTS.md\n\n" + AGENTS_BLOCK, True, "create AGENTS.md"

    text = normalize_newlines(existing).rstrip() + "\n"
    if AGENTS_BEGIN in text and AGENTS_END in text:
        before, rest = text.split(AGENTS_BEGIN, 1)
        _, after = rest.split(AGENTS_END, 1)
        new_text = before.rstrip() + "\n\n" + AGENTS_BLOCK + after.lstrip()
        changed = normalize_newlines(existing) != new_text
        return new_text, changed, "refresh managed AGENTS.md block" if changed else "AGENTS.md already up to date"

    new_text = text.rstrip() + "\n\n" + AGENTS_BLOCK
    return new_text, True, "append managed AGENTS.md block"


def ensure_ledger_content(existing: str | None) -> tuple[str, bool, str]:
    if existing is None:
        return LEDGER_TEMPLATE, True, "create .codex/role-windows.md"
    return existing, False, ".codex/role-windows.md already exists"


def write_if_needed(path: Path, content: str, write: bool) -> None:
    if not write:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_project(project: Path, write: bool) -> list[Action]:
    if not project.exists() or not project.is_dir():
        raise ValueError(f"project path must be an existing directory: {project}")

    actions: list[Action] = []

    agents = project / "AGENTS.md"
    existing_agents = agents.read_text(encoding="utf-8") if agents.exists() else None
    agents_content, agents_changed, agents_detail = ensure_agents_content(existing_agents)
    if agents_changed:
        write_if_needed(agents, agents_content, write)
        actions.append(Action("WRITE" if write else "DRY-RUN", str(agents), agents_detail))
    else:
        actions.append(Action("OK", str(agents), agents_detail))

    ledger = project / ".codex" / "role-windows.md"
    existing_ledger = ledger.read_text(encoding="utf-8") if ledger.exists() else None
    ledger_content, ledger_changed, ledger_detail = ensure_ledger_content(existing_ledger)
    if ledger_changed:
        write_if_needed(ledger, ledger_content, write)
        actions.append(Action("WRITE" if write else "DRY-RUN", str(ledger), ledger_detail))
    else:
        actions.append(Action("OK", str(ledger), ledger_detail))

    return actions


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or refresh project AGENTS.md and .codex/role-windows.md role orchestration files. Defaults to dry-run.",
    )
    parser.add_argument("--project", type=Path, required=True, help="Project root to inspect or update.")
    parser.add_argument("--write", action="store_true", help="Actually write files. Without this flag the command only prints planned changes.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    try:
        actions = ensure_project(args.project.resolve(), args.write)
    except Exception as exc:  # noqa: BLE001
        print(f"ensure_project_role_files failed: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps([action.__dict__ for action in actions], ensure_ascii=False, indent=2))
    else:
        for action in actions:
            print(f"[{action.status}] {action.path} - {action.detail}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
