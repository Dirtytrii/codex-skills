#!/usr/bin/env python3
"""Fail closed on plugin readiness before rendering a role-window prompt."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path

from render_role_prompt import build_arg_parser, build_prompt, canonical_role


REGISTRY_RELATIVE_PATH = Path("registry") / "plugin-packages.json"


@dataclass(frozen=True)
class PluginPackage:
    name: str
    requires: tuple[str, ...]
    skills: tuple[str, ...]
    roles: tuple[str, ...]


@dataclass(frozen=True)
class PluginPlan:
    marketplace: str
    role: str
    required_skills: tuple[str, ...]
    required_plugins: tuple[str, ...]
    enabled_plugins: tuple[str, ...]
    missing_plugins: tuple[str, ...]


def find_plugin_registry(explicit: Path | None) -> Path:
    if explicit is not None:
        path = explicit.expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"plugin registry does not exist: {path}")
        return path

    for parent in Path(__file__).resolve().parents:
        candidate = parent / REGISTRY_RELATIVE_PATH
        if candidate.is_file():
            return candidate
    raise ValueError(
        "cannot locate registry/plugin-packages.json; pass --plugin-registry"
    )


def load_plugin_registry(path: Path) -> tuple[str, list[PluginPackage]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema_version") != 1:
        raise ValueError(f"unsupported plugin registry schema: {path}")

    marketplace = payload.get("marketplace")
    raw_packages = payload.get("packages")
    if not isinstance(marketplace, str) or not marketplace:
        raise ValueError("plugin registry marketplace must be a non-empty string")
    if not isinstance(raw_packages, list) or not raw_packages:
        raise ValueError("plugin registry packages must be a non-empty list")

    packages: list[PluginPackage] = []
    for index, raw in enumerate(raw_packages):
        if not isinstance(raw, dict):
            raise ValueError(f"plugin registry packages[{index}] must be an object")
        name = raw.get("name")
        requires = raw.get("requires")
        skills = raw.get("skills")
        roles = raw.get("roles")
        if not isinstance(name, str) or not name:
            raise ValueError(f"plugin registry packages[{index}].name is invalid")
        if not isinstance(requires, list) or not all(
            isinstance(item, str) and item for item in requires
        ):
            raise ValueError(f"plugin registry package {name} requires is invalid")
        if not isinstance(skills, list) or not all(
            isinstance(item, str) and item for item in skills
        ):
            raise ValueError(f"plugin registry package {name} skills is invalid")
        if not isinstance(roles, list) or not all(
            isinstance(item, str) and item for item in roles
        ):
            raise ValueError(f"plugin registry package {name} roles is invalid")
        packages.append(
            PluginPackage(
                name=name,
                requires=tuple(requires),
                skills=tuple(skills),
                roles=tuple(roles),
            )
        )

    names = [package.name for package in packages]
    if len(names) != len(set(names)):
        raise ValueError("plugin registry package names must be unique")
    return marketplace, packages


def resolve_required_plugins(
    role: str,
    required_skills: list[str],
    packages: list[PluginPackage],
) -> tuple[str, tuple[str, ...]]:
    canonical = canonical_role(role)
    package_by_name = {package.name: package for package in packages}
    role_owners: dict[str, str] = {}
    skill_owners: dict[str, str] = {}

    for package in packages:
        for mapped_role in package.roles:
            if mapped_role in role_owners:
                raise ValueError(
                    f"role is mapped to multiple plugins: {mapped_role}"
                )
            role_owners[mapped_role] = package.name
        for skill in package.skills:
            if skill in skill_owners:
                raise ValueError(f"skill is mapped to multiple plugins: {skill}")
            skill_owners[skill] = package.name

    role_plugin = role_owners.get(canonical)
    if role_plugin is None:
        raise ValueError(f"role is not mapped to a plugin: {canonical}")

    selected = {role_plugin}
    for skill in required_skills:
        skill_plugin = skill_owners.get(skill)
        if skill_plugin is None:
            raise ValueError(f"required skill is not mapped to a plugin: {skill}")
        selected.add(skill_plugin)

    pending = list(selected)
    while pending:
        package_name = pending.pop()
        package = package_by_name.get(package_name)
        if package is None:
            raise ValueError(f"unknown required plugin: {package_name}")
        for dependency in package.requires:
            if dependency not in package_by_name:
                raise ValueError(
                    f"plugin {package_name} requires unknown plugin {dependency}"
                )
            if dependency not in selected:
                selected.add(dependency)
                pending.append(dependency)

    ordered = tuple(
        package.name for package in packages if package.name in selected
    )
    return canonical, ordered


def default_codex_config() -> Path:
    codex_home = os.environ.get("CODEX_HOME")
    root = Path(codex_home).expanduser() if codex_home else Path.home() / ".codex"
    return root / "config.toml"


def load_enabled_plugins(config_path: Path, marketplace: str) -> set[str]:
    path = config_path.expanduser()
    if not path.is_file():
        return set()
    with path.open("rb") as handle:
        payload = tomllib.load(handle)
    raw_plugins = payload.get("plugins", {})
    if not isinstance(raw_plugins, dict):
        raise ValueError(f"{path}: plugins must be a TOML table")

    suffix = f"@{marketplace}"
    enabled: set[str] = set()
    for plugin_id, raw in raw_plugins.items():
        if (
            isinstance(plugin_id, str)
            and plugin_id.endswith(suffix)
            and isinstance(raw, dict)
            and raw.get("enabled") is True
        ):
            enabled.add(plugin_id.removesuffix(suffix))
    return enabled


def build_plugin_plan(args: argparse.Namespace) -> PluginPlan:
    registry_path = find_plugin_registry(args.plugin_registry)
    marketplace, packages = load_plugin_registry(registry_path)
    required_skills = tuple(args.required_skill or [])
    role, required_plugins = resolve_required_plugins(
        args.role,
        list(required_skills),
        packages,
    )
    config_path = (args.codex_config or default_codex_config()).expanduser()
    enabled = load_enabled_plugins(config_path, marketplace)
    enabled_required = tuple(
        plugin for plugin in required_plugins if plugin in enabled
    )
    missing = tuple(
        plugin for plugin in required_plugins if plugin not in enabled
    )
    return PluginPlan(
        marketplace=marketplace,
        role=role,
        required_skills=required_skills,
        required_plugins=required_plugins,
        enabled_plugins=enabled_required,
        missing_plugins=missing,
    )


def list_text(values: tuple[str, ...], default: str = "无") -> str:
    return "、".join(values) if values else default


def blocked_message(plan: PluginPlan) -> str:
    commands = [
        f"codex plugin marketplace upgrade {plan.marketplace}",
        *[
            f"codex plugin add {plugin}@{plan.marketplace}"
            for plugin in plan.missing_plugins
        ],
    ]
    return "\n".join(
        [
            "prepare_role_window blocked: required plugins are not enabled",
            f"- role: {plan.role}",
            f"- required skills: {list_text(plan.required_skills)}",
            f"- required plugins: {list_text(plan.required_plugins)}",
            f"- missing or disabled: {list_text(plan.missing_plugins)}",
            "- enable commands:",
            *commands,
            "- rerun prepare_role_window.py after enabling, then create the role task.",
        ]
    )


def passed_header(plan: PluginPlan) -> str:
    return "\n".join(
        [
            "插件前置检查：",
            f"- 角色：{plan.role}",
            f"- 必选 skill：{list_text(plan.required_skills)}",
            f"- 必需插件：{list_text(plan.required_plugins)}",
            f"- 已启用插件：{list_text(plan.enabled_plugins)}",
            "- 状态：通过",
        ]
    )


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = build_arg_parser()
    parser.description = (
        "Check role and required-skill plugin readiness before rendering a role prompt."
    )
    parser.add_argument(
        "--plugin-registry",
        type=Path,
        help="Override registry/plugin-packages.json for tests or custom installations.",
    )
    parser.add_argument(
        "--codex-config",
        type=Path,
        help="Override Codex config.toml; defaults to $CODEX_HOME/config.toml or ~/.codex/config.toml.",
    )
    return parser.parse_args(argv)


def main(argv: list[str]) -> int:
    try:
        args = parse_args(argv)
        plan = build_plugin_plan(args)
        if plan.missing_plugins:
            print(blocked_message(plan), file=sys.stderr)
            return 3
        prompt = f"{passed_header(plan)}\n\n{build_prompt(args)}"
    except Exception as exc:  # noqa: BLE001
        print(f"prepare_role_window failed: {exc}", file=sys.stderr)
        return 2

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(prompt, encoding="utf-8")
    else:
        print(prompt)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
