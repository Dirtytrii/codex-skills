#!/usr/bin/env python3
"""Discover skills and expose their catalog metadata without external deps."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


IMPLICIT_POLICY_RE = re.compile(
    r"(?ms)^policy:\s*$.*?^\s+allow_implicit_invocation:\s*(true|false)\s*$"
)


@dataclass(frozen=True)
class SkillRecord:
    skill_md: Path
    relative_path: Path
    name: str
    description: str
    top_level: bool
    agents_file: Path
    allow_implicit_invocation: bool | None

    @property
    def catalog_chars(self) -> int:
        return len(self.name) + len(self.description) + len(self.relative_path.as_posix())


def parse_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("missing YAML frontmatter")
    try:
        end = lines.index("---", 1)
    except ValueError as exc:
        raise ValueError("unterminated YAML frontmatter") from exc

    data: dict[str, str] = {}
    index = 1
    while index < end:
        raw = lines[index]
        if not raw.strip() or raw[:1].isspace() or ":" not in raw:
            index += 1
            continue
        key, raw_value = raw.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value in {"|", ">"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index].strip() or lines[index][:1].isspace()):
                block.append(lines[index].strip())
                index += 1
            separator = "\n" if value == "|" else " "
            data[key] = separator.join(part for part in block if part).strip()
            continue
        data[key] = value.strip("\"'")
        index += 1
    return data


def read_implicit_policy(agents_file: Path) -> bool | None:
    if not agents_file.is_file():
        return None
    match = IMPLICIT_POLICY_RE.search(agents_file.read_text(encoding="utf-8"))
    if not match:
        return None
    return match.group(1) == "true"


def discover_skills(skills_root: Path) -> list[SkillRecord]:
    records: list[SkillRecord] = []
    for skill_md in sorted(skills_root.rglob("SKILL.md")):
        relative_path = skill_md.relative_to(skills_root)
        metadata = parse_frontmatter(skill_md)
        agents_file = skill_md.parent / "agents" / "openai.yaml"
        records.append(
            SkillRecord(
                skill_md=skill_md,
                relative_path=relative_path,
                name=metadata.get("name", ""),
                description=metadata.get("description", ""),
                top_level=len(relative_path.parts) == 2,
                agents_file=agents_file,
                allow_implicit_invocation=read_implicit_policy(agents_file),
            )
        )
    return records
