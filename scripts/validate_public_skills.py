#!/usr/bin/env python3
"""Validate public Codex skill repository structure without external deps."""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

from audit_skill_catalog import audit as audit_catalog
from skill_catalog import discover_skills, parse_frontmatter


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
REGISTRY = ROOT / "registry" / "skills.json"
ROLE_SYSTEM_VALIDATOR = ROOT / "scripts" / "validate_role_system.py"
SKILL_ROUTING_EVALUATOR = ROOT / "scripts" / "evaluate_skill_routing.py"

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


def validate_role_system(errors: list[str]) -> None:
    if not ROLE_SYSTEM_VALIDATOR.is_file():
        errors.append("missing scripts/validate_role_system.py")
        return
    result = subprocess.run(
        [sys.executable, str(ROLE_SYSTEM_VALIDATOR)],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append(
            "role-system validation failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


def validate_skill_routing_cases(errors: list[str]) -> None:
    if not SKILL_ROUTING_EVALUATOR.is_file():
        errors.append("missing scripts/evaluate_skill_routing.py")
        return
    result = subprocess.run(
        [sys.executable, str(SKILL_ROUTING_EVALUATOR), "--validate-only", "--strict"],
        cwd=str(ROOT),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        errors.append(
            "skill-routing eval validation failed:\n"
            f"stdout:\n{result.stdout}\n"
            f"stderr:\n{result.stderr}"
        )


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

    try:
        skill_records = discover_skills(SKILLS)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"cannot discover skills recursively: {exc}")
        skill_records = []

    seen_names: dict[str, Path] = {}
    for record in skill_records:
        skill_md = record.skill_md
        skill_dir = skill_md.parent
        name = record.name
        desc = record.description
        if not name:
            errors.append(f"{skill_md}: missing name")
        elif not NAME_RE.fullmatch(name):
            errors.append(f"{skill_md}: invalid name {name!r}")
        elif name != skill_dir.name:
            errors.append(f"{skill_md}: name {name!r} does not match directory {skill_dir.name!r}")
        if not desc:
            errors.append(f"{skill_md}: missing description")
        if name in seen_names:
            errors.append(
                f"duplicate skill name {name!r}: {seen_names[name]} and {skill_md}"
            )
        elif name:
            seen_names[name] = skill_md
        if record.top_level and name and name not in registry_names:
            errors.append(f"{skill_dir.name}: missing from registry/skills.json")

    skill_names = {record.name for record in skill_records if record.top_level and record.name}
    for name in registry_names:
        if name and name not in skill_names:
            errors.append(f"registry references missing skill: {name}")

    _, catalog_errors = audit_catalog(skill_records)
    errors.extend(f"skill catalog: {error}" for error in catalog_errors)

    validate_role_system(errors)
    validate_skill_routing_cases(errors)

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

    nested_count = sum(not record.top_level for record in skill_records)
    print(f"Validated {len(skill_names)} public skills and {nested_count} nested skills.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
