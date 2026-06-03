#!/usr/bin/env python3
"""Validate public Codex skill repository structure without external deps."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REGISTRY = ROOT / "registry" / "skills.json"

NAME_RE = re.compile(r"^[a-z0-9-]+$")
ORIGIN_TYPES = {"local", "external-github", "hermes", "upstream-adapted"}
MAINTENANCE_TYPES = {"local-owned", "vendored-upstream", "vendored-adapted", "hermes-owned"}
SENSITIVE_RE = re.compile(
    r"("
    r"gh[oprsu]_[A-Za-z0-9_]{20,}|"
    r"sk-[A-Za-z0-9_-]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"BEGIN (RSA|OPENSSH|EC|PRIVATE) KEY|"
    r"Authorization:\s*Bearer\s+[A-Za-z0-9._-]{12,}|"
    r"password\s*[:=]\s*[^\\s`'\"]+|"
    r"passwd\s*[:=]\s*[^\\s`'\"]+|"
    r"api[_-]?key\s*[:=]\s*[^\\s`'\"]+|"
    r"secret\s*[:=]\s*[^\\s`'\"]+|"
    r"/Users/cloudjiang|"
    r"/root/|"
    r"10\.\d{1,3}\.\d{1,3}\.\d{1,3}|"
    r"172\.(1[6-9]|2\d|3[0-1])\.\d{1,3}\.\d{1,3}|"
    r"192\.168\.\d{1,3}\.\d{1,3}"
    r")",
    re.IGNORECASE,
)

ALLOWED_SENSITIVE_EXAMPLES = (
    "password123",
    "%SHOPIFY_API_KEY%",
    "api_key = os.environ.get",
    "Authorization: Bearer {api_key}",
    'r"/Users/cloudjiang|',
    'r"/root/|',
)


def parse_frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    end = text.find("\n---\n", 4)
    if end == -1:
        raise ValueError("unterminated YAML frontmatter")
    body = text[4:end]
    data: dict[str, str] = {}
    current_key: str | None = None
    current_lines: list[str] = []
    for raw in body.splitlines():
        if not raw.strip():
            continue
        if raw.startswith((" ", "\t")) and current_key:
            current_lines.append(raw.strip())
            continue
        if current_key and current_lines:
            data[current_key] = "\n".join(current_lines).strip()
            current_lines = []
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        key = key.strip()
        value = value.strip()
        current_key = key
        if value in {"|", ">"}:
            current_lines = []
        else:
            data[key] = value.strip("\"'")
            current_key = None
    if current_key and current_lines:
        data[current_key] = "\n".join(current_lines).strip()
    return data


def iter_text_files() -> list[Path]:
    ignore_parts = {".git", "__pycache__", ".DS_Store"}
    files: list[Path] = []
    for path in ROOT.rglob("*"):
        if any(part in ignore_parts for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return files


def is_allowed_example(line: str) -> bool:
    return any(example in line for example in ALLOWED_SENSITIVE_EXAMPLES)


def main() -> int:
    errors: list[str] = []

    if not SKILLS.is_dir():
        errors.append("missing skills/ directory")

    try:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"cannot read registry/skills.json: {exc}")
        registry = []

    registry_names = {item.get("name") for item in registry if isinstance(item, dict)}

    for idx, item in enumerate(registry):
        if not isinstance(item, dict):
            errors.append(f"registry item {idx}: must be an object")
            continue
        name = item.get("name", f"<item {idx}>")
        if item.get("origin_type") not in ORIGIN_TYPES:
            errors.append(f"{name}: invalid or missing origin_type")
        if item.get("maintenance") not in MAINTENANCE_TYPES:
            errors.append(f"{name}: invalid or missing maintenance")
        roles = item.get("consumed_by_roles")
        if not isinstance(roles, list) or not roles:
            errors.append(f"{name}: consumed_by_roles must be a non-empty list")
        if item.get("origin_type") == "external-github" and "upstream_url" not in item:
            errors.append(f"{name}: external-github skills must include upstream_url, even if null")
        if item.get("origin_type") == "external-github" and item.get("upstream_url") is None:
            if not item.get("source_note"):
                errors.append(f"{name}: external-github skills with null upstream_url must include source_note")

    for skill_dir in sorted(p for p in SKILLS.iterdir() if p.is_dir()):
        skill_md = skill_dir / "SKILL.md"
        if not skill_md.is_file():
            errors.append(f"{skill_dir}: missing SKILL.md")
            continue
        try:
            fm = parse_frontmatter(skill_md)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{skill_md}: {exc}")
            continue
        name = fm.get("name", "")
        desc = fm.get("description", "")
        if not name:
            errors.append(f"{skill_md}: missing name")
        elif not NAME_RE.fullmatch(name):
            errors.append(f"{skill_md}: invalid name {name!r}")
        elif name != skill_dir.name:
            errors.append(f"{skill_md}: name {name!r} does not match directory {skill_dir.name!r}")
        if not desc:
            errors.append(f"{skill_md}: missing description")
        if name and name not in registry_names:
            errors.append(f"{skill_dir.name}: missing from registry/skills.json")

    skill_names = {p.name for p in SKILLS.iterdir() if p.is_dir()}
    for name in registry_names:
        if name and name not in skill_names:
            errors.append(f"registry references missing skill: {name}")

    for path in iter_text_files():
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for lineno, line in enumerate(text.splitlines(), 1):
            if is_allowed_example(line):
                continue
            if SENSITIVE_RE.search(line):
                rel = path.relative_to(ROOT)
                errors.append(f"possible sensitive value: {rel}:{lineno}: {line.strip()[:160]}")

    if errors:
        print("Validation failed:")
        for error in errors:
            print(f"- {error}")
        return 1

    print(f"Validated {len(skill_names)} skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
