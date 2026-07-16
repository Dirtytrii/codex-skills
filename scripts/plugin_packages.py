#!/usr/bin/env python3
"""Shared catalog and file helpers for codex-skills plugin packages."""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from skill_catalog import SkillRecord, discover_skills


ROOT = Path(__file__).resolve().parents[1]
PACKAGE_CONFIG = ROOT / "registry" / "plugin-packages.json"
MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
PLUGINS_ROOT = ROOT / "plugins"
CATALOG_TARGET = 8_000
IGNORED_DIR_NAMES = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
}
IGNORED_FILE_NAMES = {".DS_Store", ".env", ".env.local"}
IGNORED_FILE_SUFFIXES = {".pyc", ".pyo"}


@dataclass(frozen=True)
class PackageSpec:
    name: str
    default_install: bool
    requires: tuple[str, ...]
    skills: tuple[str, ...]

    @property
    def plugin_root(self) -> Path:
        return PLUGINS_ROOT / self.name

    @property
    def bundle_root(self) -> Path:
        return self.plugin_root / "skills"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def load_package_specs(path: Path = PACKAGE_CONFIG) -> tuple[Path, list[PackageSpec], str]:
    payload = load_json(path)
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    if payload.get("schema_version") != 1:
        raise ValueError(f"{path} schema_version must be 1")
    marketplace = payload.get("marketplace")
    if not isinstance(marketplace, str) or not marketplace:
        raise ValueError(f"{path} marketplace must be a non-empty string")
    source_root_raw = payload.get("source_root")
    if not isinstance(source_root_raw, str) or not source_root_raw:
        raise ValueError(f"{path} source_root must be a non-empty string")
    source_root = (ROOT / source_root_raw).resolve()
    if ROOT.resolve() not in source_root.parents:
        raise ValueError(f"{path} source_root must stay inside the repository")

    raw_packages = payload.get("packages")
    if not isinstance(raw_packages, list) or not raw_packages:
        raise ValueError(f"{path} packages must be a non-empty list")

    specs: list[PackageSpec] = []
    for index, raw in enumerate(raw_packages):
        if not isinstance(raw, dict):
            raise ValueError(f"{path} packages[{index}] must be an object")
        name = raw.get("name")
        default_install = raw.get("default_install")
        requires = raw.get("requires")
        skills = raw.get("skills")
        if not isinstance(name, str) or not name:
            raise ValueError(f"{path} packages[{index}].name must be a non-empty string")
        if not isinstance(default_install, bool):
            raise ValueError(f"{path} package {name} default_install must be boolean")
        if not isinstance(requires, list) or not all(isinstance(item, str) for item in requires):
            raise ValueError(f"{path} package {name} requires must be a string list")
        if not isinstance(skills, list) or not skills or not all(
            isinstance(item, str) and item for item in skills
        ):
            raise ValueError(f"{path} package {name} skills must be a non-empty string list")
        specs.append(
            PackageSpec(
                name=name,
                default_install=default_install,
                requires=tuple(requires),
                skills=tuple(skills),
            )
        )
    return source_root, specs, marketplace


def should_package(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in IGNORED_DIR_NAMES for part in relative.parts[:-1]):
        return False
    if path.name in IGNORED_FILE_NAMES or path.suffix.lower() in IGNORED_FILE_SUFFIXES:
        return False
    return path.is_file() and not path.is_symlink()


def file_inventory(root: Path) -> dict[str, str]:
    if not root.is_dir():
        return {}
    inventory: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        if not should_package(path, root):
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        inventory[path.relative_to(root).as_posix()] = digest
    return inventory


def compare_skill_trees(source: Path, bundled: Path) -> list[str]:
    source_inventory = file_inventory(source)
    bundled_inventory = file_inventory(bundled)
    errors: list[str] = []
    for relative in sorted(source_inventory.keys() - bundled_inventory.keys()):
        errors.append(f"missing bundled file: {relative}")
    for relative in sorted(bundled_inventory.keys() - source_inventory.keys()):
        errors.append(f"stale bundled file: {relative}")
    for relative in sorted(source_inventory.keys() & bundled_inventory.keys()):
        if source_inventory[relative] != bundled_inventory[relative]:
            errors.append(f"changed bundled file: {relative}")
    return errors


def canonical_public_skill_names(source_root: Path) -> set[str]:
    return {
        path.name
        for path in source_root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def records_by_public_skill(source_root: Path) -> dict[str, list[SkillRecord]]:
    grouped: dict[str, list[SkillRecord]] = {}
    for record in discover_skills(source_root):
        top_level_dir = record.relative_path.parts[0]
        grouped.setdefault(top_level_dir, []).append(record)
    return grouped


def package_records(
    spec: PackageSpec, grouped: dict[str, list[SkillRecord]]
) -> list[SkillRecord]:
    return [record for skill in spec.skills for record in grouped.get(skill, [])]


def package_catalog_chars(
    spec: PackageSpec, grouped: dict[str, list[SkillRecord]]
) -> int:
    return sum(record.catalog_chars for record in package_records(spec, grouped))


def resolve_selected_packages(
    requested: list[str], specs: list[PackageSpec]
) -> list[PackageSpec]:
    by_name = {spec.name: spec for spec in specs}
    selected_names = set(requested)
    unknown = selected_names - by_name.keys()
    if unknown:
        raise ValueError(f"unknown plugin packages: {sorted(unknown)}")

    pending = list(selected_names)
    while pending:
        name = pending.pop()
        for dependency in by_name[name].requires:
            if dependency not in by_name:
                raise ValueError(f"package {name} requires unknown package {dependency}")
            if dependency not in selected_names:
                selected_names.add(dependency)
                pending.append(dependency)

    return [spec for spec in specs if spec.name in selected_names]


def bundle_sync_errors(source_root: Path, spec: PackageSpec) -> list[str]:
    errors: list[str] = []
    expected = set(spec.skills)
    if not spec.bundle_root.is_dir():
        return [f"{spec.name}: missing generated skills directory"]

    actual = {path.name for path in spec.bundle_root.iterdir() if path.is_dir()}
    for skill in sorted(expected - actual):
        errors.append(f"{spec.name}: missing generated skill {skill}")
    for skill in sorted(actual - expected):
        errors.append(f"{spec.name}: stale generated skill {skill}")

    for skill in spec.skills:
        source = source_root / skill
        bundled = spec.bundle_root / skill
        if not source.is_dir():
            errors.append(f"{spec.name}: canonical skill is missing: {skill}")
            continue
        errors.extend(
            f"{spec.name}/{skill}: {error}"
            for error in compare_skill_trees(source, bundled)
        )
    return errors
