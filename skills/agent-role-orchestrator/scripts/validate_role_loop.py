#!/usr/bin/env python3
"""Fail-closed checks for agent-role-orchestrator ledgers, prompts, and callbacks."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


CANONICAL_ROLES = [
    "总控",
    "架构",
    "开发",
    "UI/PPT",
    "测试",
    "QA",
    "安全",
    "DBA",
    "运维",
    "内容主编",
    "公众号发布",
    "小红书",
    "视频",
    "知识库",
    "技能维护",
    "文档/交付",
]

ALLOWED_STATUSES = {"未建立", "已建立", "接续中", "已关闭", "误开/废弃", "待确认"}
PLACEHOLDERS = {"", "TODO", "TBD", "<待填写>", "<todo>", "null", "None"}

PROMPT_REQUIRED_MARKERS = [
    "模型建议：",
    "角色树位置",
    "Loop 深度（可折叠路由）：",
    "任务分发决策：",
    "负责人交互边界：",
    "目标：",
    "请先阅读/检查：",
    "允许修改：",
    "禁止修改：",
    "验证：",
    "闭环状态：",
    "路由前检查",
    "技能路由台账",
    "上下文预算：",
    "闭环完成条件：",
    "回调/通知规则：",
    "结构化反馈格式",
    "压缩回调：",
    "技能命中回传：",
    "规则沉淀：",
]

LEDGER_REQUIRED_HEADERS = ["角色", "状态", "thread id", "来源窗口", "当前职责", "下一步", "循环状态"]
TOP_LEVEL_REQUIRED_ROLES = {"总控", "架构", "内容主编"}

CALLBACK_REQUIRED_MARKERS = [
    "压缩回调：",
    "当前状态：",
    "本轮变化：",
    "证据链接/文件/命令：",
    "需要决策：",
    "下一回流对象：",
    "技能命中回传：",
    "已加载并使用：",
    "来源窗口要求但未使用：",
    "临时发现应补用：",
    "误召/无效加载：",
    "影响产出的 skill：",
    "规则沉淀：",
    "可复用优化沉淀：",
]


@dataclass
class CheckResult:
    target: str
    errors: list[str]
    warnings: list[str]
    metrics: dict[str, object]


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def has_placeholder_value(line: str) -> bool:
    stripped = line.strip()
    if "：" in line:
        value = line.split("：", 1)[1].strip()
    elif ":" in line:
        value = line.split(":", 1)[1].strip()
    else:
        return False
    if not value and not stripped.startswith("-"):
        return False
    return value in PLACEHOLDERS


def missing_markers(text: str, markers: list[str]) -> list[str]:
    return [marker for marker in markers if marker not in text]


def extract_field(text: str, field: str) -> str:
    pattern = re.compile(rf"{re.escape(field)}[ \t]*[:：][ \t]*(.*)")
    match = pattern.search(text)
    return match.group(1).strip() if match else ""


def split_skill_list(value: str) -> set[str]:
    value = value.strip()
    if not value or value in {"无", "不适用", "待确认", "无 / 待确认"}:
        return set()
    parts = re.split(r"[、,，;；\n]+", value)
    cleaned = set()
    for part in parts:
        item = part.strip().strip("- ").strip()
        if not item or item in {"无", "不适用", "待确认"}:
            continue
        if ":" in item:
            item = item.split(":", 1)[0].strip()
        if "：" in item:
            item = item.split("：", 1)[0].strip()
        cleaned.add(item)
    return cleaned


def split_markdown_row(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped.strip("|").split("|")]


def is_separator_row(cells: list[str]) -> bool:
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def is_canonical_or_numbered_role(role: str) -> bool:
    if role in CANONICAL_ROLES:
        return True
    return any(re.fullmatch(rf"{re.escape(base)}\d+号", role) for base in CANONICAL_ROLES)


def parse_ledger_table(text: str) -> tuple[list[dict[str, str]], list[str]]:
    errors: list[str] = []
    lines = text.splitlines()
    for index, line in enumerate(lines):
        headers = split_markdown_row(line)
        if not headers:
            continue
        normalized = [header.lower() for header in headers]
        if not all(required.lower() in normalized for required in LEDGER_REQUIRED_HEADERS):
            continue
        canonical_headers = [
            next((required for required in LEDGER_REQUIRED_HEADERS if required.lower() == header.lower()), header)
            for header in headers
        ]
        if index + 1 >= len(lines) or not is_separator_row(split_markdown_row(lines[index + 1])):
            errors.append("ledger table header must be followed by a markdown separator row")
            return [], errors

        rows: list[dict[str, str]] = []
        for row_line in lines[index + 2 :]:
            cells = split_markdown_row(row_line)
            if not cells:
                break
            if len(cells) != len(canonical_headers):
                errors.append(f"ledger table row has {len(cells)} cells but header has {len(canonical_headers)}: {row_line.strip()}")
                continue
            rows.append(dict(zip(canonical_headers, cells)))
        return rows, errors

    errors.append("ledger missing recommended table header: " + " | ".join(LEDGER_REQUIRED_HEADERS))
    return [], errors


def validate_ledger(path: Path) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, object] = {}

    if not path.is_file():
        return CheckResult(str(path), [f"ledger missing: {path}"], warnings, metrics)

    text = read_text(path)
    rows, table_errors = parse_ledger_table(text)
    errors.extend(table_errors)

    seen_roles: set[str] = set()
    seen_statuses: set[str] = set()
    thread_ids: dict[str, str] = {}

    for row_index, row in enumerate(rows, 1):
        role = row.get("角色", "").strip()
        status = row.get("状态", "").strip()
        thread_id = row.get("thread id", "").strip()
        source = row.get("来源窗口", "").strip()
        responsibility = row.get("当前职责", "").strip()
        next_step = row.get("下一步", "").strip()
        loop_state = row.get("循环状态", "").strip()

        if not role:
            errors.append(f"ledger row {row_index}: blank role")
            continue
        seen_roles.add(role)

        if not is_canonical_or_numbered_role(role):
            errors.append(f"ledger row {row_index}: unknown role: {role}")
        if status not in ALLOWED_STATUSES:
            errors.append(f"ledger row {row_index}: invalid status for {role}: {status}")
        else:
            seen_statuses.add(status)
        if not thread_id:
            errors.append(f"ledger row {row_index}: blank thread id; use 待确认 when unknown")
        elif thread_id not in {"待确认", "无", "不适用"}:
            if thread_id in thread_ids:
                errors.append(f"ledger row {row_index}: duplicate thread id {thread_id} for {role}; already used by {thread_ids[thread_id]}")
            else:
                thread_ids[thread_id] = role

        for field_name, value in (
            ("来源窗口", source),
            ("当前职责", responsibility),
            ("下一步", next_step),
            ("循环状态", loop_state),
        ):
            if value in PLACEHOLDERS:
                errors.append(f"ledger row {row_index}: blank or placeholder {field_name} for {role}")

    if not rows:
        errors.append("ledger does not contain any role-window table rows")
    for expected in TOP_LEVEL_REQUIRED_ROLES:
        if expected not in seen_roles:
            errors.append(f"ledger missing top-level role: {expected}")

    if "待确认" in text:
        warnings.append("ledger contains 待确认; confirm before creating/continuing affected windows")

    metrics["roles_seen"] = sorted(seen_roles)
    metrics["statuses_seen"] = sorted(seen_statuses)
    return CheckResult(str(path), errors, warnings, metrics)


def validate_prompt(path: Path) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, object] = {}
    text = read_text(path)

    for marker in missing_markers(text, PROMPT_REQUIRED_MARKERS):
        errors.append(f"missing prompt marker: {marker}")

    model = extract_field(text, "model")
    thinking = extract_field(text, "thinking")
    if not model or model == "待确认":
        errors.append("模型建议.model is blank or 待确认")
    if not thinking or thinking == "待确认":
        errors.append("模型建议.thinking is blank or 待确认")

    source = extract_field(text, "本任务发起方")
    if not source:
        errors.append("callback source is missing")

    required = split_skill_list(extract_field(text, "必选 skill"))
    candidate = split_skill_list(extract_field(text, "候选 skill"))
    metrics["required_skills"] = sorted(required)
    metrics["candidate_skills"] = sorted(candidate)

    if "是否读取 agent-role-orchestrator：" in text and "是否读取 agent-role-orchestrator：是" not in text:
        warnings.append("prompt does not confirm agent-role-orchestrator was read")
    if "是否读取 .codex/role-windows.md：" in text and "是否读取 .codex/role-windows.md：是" not in text:
        warnings.append("prompt does not confirm .codex/role-windows.md was read")

    return CheckResult(str(path), errors, warnings, metrics)


def validate_callback(path: Path, required_skills: set[str]) -> CheckResult:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, object] = {}
    text = read_text(path)
    stripped_text = text.lstrip()

    if not (stripped_text.startswith("<codex_delegation>") or stripped_text.startswith("压缩回调")):
        errors.append("callback must start with <codex_delegation> or 压缩回调 for forwarding")

    for marker in missing_markers(text, CALLBACK_REQUIRED_MARKERS):
        errors.append(f"missing callback marker: {marker}")

    loaded = split_skill_list(extract_field(text, "已加载并使用"))
    declared_unused = split_skill_list(extract_field(text, "来源窗口要求但未使用"))
    missing_required = sorted(required_skills - loaded - declared_unused)

    if missing_required:
        errors.append("required skills neither loaded nor declared unused: " + "、".join(missing_required))

    if "下一回流对象：" in text and "下一回流对象：" + "\n" in text:
        errors.append("blank 下一回流对象; use a role name or 待确认 with reason")

    if "可复用优化沉淀：" not in text:
        errors.append("missing reusable sedimentation status")
    else:
        sediment = extract_field(text, "可复用优化沉淀")
        if sediment and not any(token in sediment for token in ("无", "建议", "已沉淀")):
            errors.append("可复用优化沉淀 must be one of: 无 / 建议 / 已沉淀")

    for line_no, line in enumerate(text.splitlines(), 1):
        if has_placeholder_value(line.strip()):
            errors.append(f"line {line_no}: placeholder value is not allowed: {line.strip()}")

    metrics["loaded_skills"] = sorted(loaded)
    metrics["declared_unused_required_skills"] = sorted(declared_unused)
    metrics["required_skill_count"] = len(required_skills)
    metrics["loaded_required_skill_count"] = len(required_skills & loaded)
    metrics["skill_hit_rate"] = 1.0 if not required_skills else round(len(required_skills & loaded) / len(required_skills), 4)
    if declared_unused:
        warnings.append("some required skills were declared unused: " + "、".join(sorted(declared_unused)))

    return CheckResult(str(path), errors, warnings, metrics)


def print_result(result: CheckResult) -> None:
    status = "PASS" if not result.errors else "FAIL"
    print(f"[{status}] {result.target}")
    for error in result.errors:
        print(f"  ERROR: {error}")
    for warning in result.warnings:
        print(f"  WARN: {warning}")
    if result.metrics:
        print("  METRICS: " + json.dumps(result.metrics, ensure_ascii=False, sort_keys=True))


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate role-window ledgers, generated prompts, and callback messages. Exits non-zero on missing mechanical fields.",
    )
    parser.add_argument("--project", type=Path, help="Project root; validates .codex/role-windows.md by default.")
    parser.add_argument("--ledger", type=Path, help="Explicit role-windows ledger file.")
    parser.add_argument("--allow-missing-ledger", action="store_true", help="Do not fail when project ledger is absent.")
    parser.add_argument("--prompt", type=Path, action="append", default=[], help="Prompt file to validate. Repeatable.")
    parser.add_argument("--callback", type=Path, action="append", default=[], help="Callback file to validate. Repeatable.")
    parser.add_argument("--required-skill", action="append", default=[], help="Required skill expected in callback. Repeatable.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    targets = []
    results: list[CheckResult] = []

    if args.project:
        ledger = args.project / ".codex" / "role-windows.md"
        if ledger.exists() or not args.allow_missing_ledger:
            targets.append(("ledger", ledger))
    if args.ledger:
        targets.append(("ledger", args.ledger))
    for prompt in args.prompt:
        targets.append(("prompt", prompt))
    for callback in args.callback:
        targets.append(("callback", callback))

    if not targets:
        print("validate_role_loop failed: provide --project, --ledger, --prompt, or --callback", file=sys.stderr)
        return 2

    required_skills = set(args.required_skill)
    for kind, path in targets:
        if kind == "ledger":
            result = validate_ledger(path)
        elif kind == "prompt":
            result = validate_prompt(path)
            required_skills.update(result.metrics.get("required_skills", []))
        else:
            result = validate_callback(path, required_skills)
        results.append(result)

    if args.json:
        print(json.dumps([result.__dict__ for result in results], ensure_ascii=False, indent=2))
    else:
        for result in results:
            print_result(result)

    return 1 if any(result.errors for result in results) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
