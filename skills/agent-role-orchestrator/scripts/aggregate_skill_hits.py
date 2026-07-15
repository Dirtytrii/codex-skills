#!/usr/bin/env python3
"""Aggregate skill hit-rate metrics from role callbacks and ledgers."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


EMPTY_VALUES = {"", "无", "不适用", "待确认", "无 / 待确认"}
FIELD_REQUIRED = "必选 skill"
FIELD_LOADED = "已加载并使用"
FIELD_UNUSED = "来源窗口要求但未使用"
FIELD_DISCOVERED = "临时发现应补用"
FIELD_MISFIRES = "误召/无效加载"
FIELD_EFFECTIVE = "影响产出的 skill"
CALLBACK_FIELDS = (
    FIELD_LOADED,
    FIELD_UNUSED,
    FIELD_DISCOVERED,
    FIELD_MISFIRES,
    FIELD_EFFECTIVE,
)


def iter_input_files(paths: list[Path]) -> list[Path]:
    files: list[Path] = []
    for path in paths:
        if path.is_dir():
            for candidate in sorted(path.rglob("*")):
                if candidate.is_file() and candidate.suffix.lower() in {".md", ".txt"}:
                    files.append(candidate)
        elif path.is_file():
            files.append(path)
    return files


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def field_values(text: str, field: str) -> list[str]:
    values: list[str] = []
    lines = text.splitlines()
    pattern = re.compile(rf"^\s*-?\s*{re.escape(field)}[ \t]*[:：][ \t]*(.*)$")
    top_level_field = re.compile(r"^\s*-\s*[^:：]+[ \t]*[:：]")

    index = 0
    while index < len(lines):
        line = lines[index]
        match = pattern.match(line)
        if not match:
            index += 1
            continue

        value = match.group(1).strip()
        if value:
            values.append(value)
            index += 1
            continue

        block: list[str] = []
        index += 1
        while index < len(lines):
            next_line = lines[index]
            if top_level_field.match(next_line):
                break
            stripped = next_line.strip()
            if stripped.startswith("-"):
                block.append(stripped.lstrip("-").strip())
            elif stripped:
                block.append(stripped)
            index += 1
        values.append("、".join(block))
    return values


def split_skill_list(values: list[str]) -> set[str]:
    skills: set[str] = set()
    for value in values:
        if value.strip() in EMPTY_VALUES:
            continue
        for raw in re.split(r"[、,，;；\n]+", value):
            item = raw.strip().strip("- ").strip()
            if not item or item in EMPTY_VALUES:
                continue
            if ":" in item:
                item = item.split(":", 1)[0].strip()
            if "：" in item:
                item = item.split("：", 1)[0].strip()
            if item and item not in EMPTY_VALUES:
                skills.add(item)
    return skills


def parse_file(path: Path) -> dict[str, object]:
    text = read_text(path)
    required = split_skill_list(field_values(text, FIELD_REQUIRED))
    loaded = split_skill_list(field_values(text, FIELD_LOADED))
    declared_unused = split_skill_list(field_values(text, FIELD_UNUSED))
    discovered = split_skill_list(field_values(text, FIELD_DISCOVERED))
    misfires = split_skill_list(field_values(text, FIELD_MISFIRES))
    effective = split_skill_list(field_values(text, FIELD_EFFECTIVE))

    loaded_required = required & loaded
    unused_required = required & declared_unused
    missing_required = required - loaded - declared_unused
    callback_fields_present = [field for field in CALLBACK_FIELDS if field_values(text, field)]
    effective_loaded = effective & loaded

    return {
        "path": str(path),
        "required_skills": sorted(required),
        "loaded_skills": sorted(loaded),
        "declared_unused_required_skills": sorted(unused_required),
        "discovered_should_use_skills": sorted(discovered),
        "misfire_skills": sorted(misfires),
        "effective_skills": sorted(effective),
        "missing_required_skills": sorted(missing_required),
        "required_skill_count": len(required),
        "loaded_required_skill_count": len(loaded_required),
        "declared_unused_required_skill_count": len(unused_required),
        "missing_required_skill_count": len(missing_required),
        "misfire_skill_count": len(misfires),
        "loaded_skill_count": len(loaded),
        "effective_loaded_skill_count": len(effective_loaded),
        "has_routing_declaration": bool(field_values(text, FIELD_REQUIRED)),
        "callback_fields_present": callback_fields_present,
        "callback_complete": len(callback_fields_present) == len(CALLBACK_FIELDS),
    }


def aggregate(paths: list[Path]) -> dict[str, object]:
    files = [parse_file(path) for path in iter_input_files(paths)]
    by_skill: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    totals = {
        "files_scanned": len(files),
        "required_skill_count": 0,
        "loaded_required_skill_count": 0,
        "declared_unused_required_skill_count": 0,
        "missing_required_skill_count": 0,
        "misfire_skill_count": 0,
        "discovered_should_use_skill_count": 0,
        "effective_skill_count": 0,
        "loaded_skill_count": 0,
        "effective_loaded_skill_count": 0,
        "files_with_routing_declaration": 0,
        "files_with_complete_skill_callback": 0,
    }

    for item in files:
        totals["required_skill_count"] += int(item["required_skill_count"])
        totals["loaded_required_skill_count"] += int(item["loaded_required_skill_count"])
        totals["declared_unused_required_skill_count"] += int(item["declared_unused_required_skill_count"])
        totals["missing_required_skill_count"] += int(item["missing_required_skill_count"])
        totals["misfire_skill_count"] += int(item["misfire_skill_count"])
        totals["discovered_should_use_skill_count"] += len(item["discovered_should_use_skills"])
        totals["effective_skill_count"] += len(item["effective_skills"])
        totals["loaded_skill_count"] += int(item["loaded_skill_count"])
        totals["effective_loaded_skill_count"] += int(item["effective_loaded_skill_count"])
        totals["files_with_routing_declaration"] += int(bool(item["has_routing_declaration"]))
        totals["files_with_complete_skill_callback"] += int(bool(item["callback_complete"]))

        for skill in item["required_skills"]:
            by_skill[skill]["required"] += 1
        for skill in item["loaded_skills"]:
            by_skill[skill]["loaded"] += 1
        for skill in item["declared_unused_required_skills"]:
            by_skill[skill]["declared_unused_required"] += 1
        for skill in item["missing_required_skills"]:
            by_skill[skill]["missing_required"] += 1
        for skill in item["misfire_skills"]:
            by_skill[skill]["misfire"] += 1
        for skill in item["discovered_should_use_skills"]:
            by_skill[skill]["discovered_should_use"] += 1
        for skill in item["effective_skills"]:
            by_skill[skill]["effective"] += 1

    required_count = totals["required_skill_count"]
    loaded_count = totals["loaded_skill_count"]
    files_scanned = totals["files_scanned"]
    totals["hit_rate"] = (
        None
        if required_count == 0
        else round(totals["loaded_required_skill_count"] / required_count, 4)
    )
    totals["effective_use_rate"] = (
        None
        if loaded_count == 0
        else round(totals["effective_loaded_skill_count"] / loaded_count, 4)
    )
    totals["misfire_rate"] = (
        None
        if loaded_count == 0
        else round(totals["misfire_skill_count"] / loaded_count, 4)
    )
    totals["routing_declaration_coverage"] = (
        None
        if files_scanned == 0
        else round(totals["files_with_routing_declaration"] / files_scanned, 4)
    )
    totals["skill_callback_completeness"] = (
        None
        if files_scanned == 0
        else round(totals["files_with_complete_skill_callback"] / files_scanned, 4)
    )
    totals["files"] = files
    totals["by_skill"] = {skill: dict(counts) for skill, counts in sorted(by_skill.items())}
    return totals


def render_human(payload: dict[str, object]) -> str:
    hit_rate = payload["hit_rate"]
    hit_rate_text = "不可评估（未声明必选 skill）" if hit_rate is None else str(hit_rate)
    return "\n".join(
        [
            "【技能命中率统计】",
            f"- 扫描文件数：{payload['files_scanned']}",
            f"- 必选 skill 数：{payload['required_skill_count']}",
            f"- 实际命中的必选 skill 数：{payload['loaded_required_skill_count']}",
            f"- 声明未使用的必选 skill 数：{payload['declared_unused_required_skill_count']}",
            f"- 漏召必选 skill 数：{payload['missing_required_skill_count']}",
            f"- 误召/无效加载 skill 数：{payload['misfire_skill_count']}",
            f"- 临时发现应补用 skill 数：{payload['discovered_should_use_skill_count']}",
            f"- 影响产出的 skill 数：{payload['effective_skill_count']}",
            f"- 路由声明覆盖率：{payload['routing_declaration_coverage']}",
            f"- 技能回调完整率：{payload['skill_callback_completeness']}",
            f"- 必选 skill 自报命中率：{hit_rate_text}",
            f"- 已加载 skill 有效使用率：{payload['effective_use_rate']}",
            f"- 已加载 skill 误召率：{payload['misfire_rate']}",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Aggregate self-reported required/actual/effective skill metrics from callbacks or ledgers.",
    )
    parser.add_argument("paths", type=Path, nargs="+", help="Callback/ledger files or directories to scan.")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON.")
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)
    payload = aggregate(args.paths)
    if args.json:
        print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_human(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
