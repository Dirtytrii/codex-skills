#!/usr/bin/env python3
"""Validate marketplace metadata, plugin manifests, bundles, and context budgets."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from plugin_packages import (
    CATALOG_TARGET,
    MARKETPLACE,
    bundle_sync_errors,
    canonical_public_skill_names,
    load_json,
    load_package_specs,
    package_catalog_chars,
    package_records,
    records_by_public_skill,
    resolve_selected_packages,
)


REQUIRED_MANIFEST_FIELDS = {
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "skills",
    "interface",
}
INSTALL_POLICIES = {"INSTALLED_BY_DEFAULT", "AVAILABLE"}
ALLOWED_AGENT_FIELDS = {"interface", "policy", "dependencies"}


def validate_agent_yaml_shape(path: Path, errors: list[str]) -> None:
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    top_level_fields = {
        match.group(1)
        for line in text.splitlines()
        if (match := re.fullmatch(r"([A-Za-z_][A-Za-z0-9_-]*):(?:\s*.*)?", line))
    }
    unsupported = top_level_fields - ALLOWED_AGENT_FIELDS
    if unsupported:
        errors.append(f"{path}: unsupported top-level agent fields {sorted(unsupported)}")
    if "interface" not in top_level_fields:
        errors.append(f"{path}: interface mapping is required for plugin compatibility")


def validate() -> tuple[list[str], dict[str, object]]:
    errors: list[str] = []
    source_root, specs, marketplace_name = load_package_specs()
    grouped = records_by_public_skill(source_root)
    canonical = canonical_public_skill_names(source_root)
    spec_names = [spec.name for spec in specs]

    if len(spec_names) != len(set(spec_names)):
        errors.append("package names must be unique")

    defaults = [spec for spec in specs if spec.default_install]
    if [spec.name for spec in defaults] != ["codex-skills-core"]:
        errors.append("codex-skills-core must be the only default-installed package")

    assignments: dict[str, list[str]] = {}
    for spec in specs:
        if spec.name != "codex-skills-core" and "codex-skills-core" not in spec.requires:
            errors.append(f"{spec.name}: domain plugin must require codex-skills-core")
        for skill in spec.skills:
            assignments.setdefault(skill, []).append(spec.name)
    for skill in sorted(canonical - assignments.keys()):
        errors.append(f"unassigned canonical skill: {skill}")
    for skill in sorted(assignments.keys() - canonical):
        errors.append(f"package references unknown canonical skill: {skill}")
    for skill, owners in sorted(assignments.items()):
        if len(owners) != 1:
            errors.append(f"skill must belong to exactly one package: {skill} -> {owners}")

    try:
        marketplace = load_json(MARKETPLACE)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors.append(f"cannot read marketplace: {exc}")
        marketplace = {}
    if not isinstance(marketplace, dict):
        errors.append("marketplace must be a JSON object")
        marketplace = {}
    if marketplace.get("name") != marketplace_name:
        errors.append("marketplace name does not match package registry")
    entries = marketplace.get("plugins", [])
    if not isinstance(entries, list):
        errors.append("marketplace plugins must be a list")
        entries = []
    entries_by_name = {
        entry.get("name"): entry for entry in entries if isinstance(entry, dict)
    }
    if [entry.get("name") for entry in entries if isinstance(entry, dict)] != spec_names:
        errors.append("marketplace plugin order/names must match registry/plugin-packages.json")

    package_metrics: list[dict[str, object]] = []
    for spec in specs:
        entry = entries_by_name.get(spec.name)
        expected_install = "INSTALLED_BY_DEFAULT" if spec.default_install else "AVAILABLE"
        if not isinstance(entry, dict):
            errors.append(f"{spec.name}: missing marketplace entry")
        else:
            source = entry.get("source")
            if source != {"source": "local", "path": f"./plugins/{spec.name}"}:
                errors.append(f"{spec.name}: marketplace source must point to its local plugin")
            policy = entry.get("policy")
            if not isinstance(policy, dict):
                errors.append(f"{spec.name}: marketplace policy is missing")
            else:
                installation = policy.get("installation")
                if installation not in INSTALL_POLICIES or installation != expected_install:
                    errors.append(f"{spec.name}: invalid installation policy {installation!r}")
                if policy.get("authentication") != "ON_INSTALL":
                    errors.append(f"{spec.name}: authentication policy must be ON_INSTALL")
            if not entry.get("category"):
                errors.append(f"{spec.name}: marketplace category is required")

        manifest_path = spec.plugin_root / ".codex-plugin" / "plugin.json"
        try:
            manifest = load_json(manifest_path)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"{spec.name}: cannot read manifest: {exc}")
            manifest = {}
        if not isinstance(manifest, dict):
            errors.append(f"{spec.name}: manifest must be a JSON object")
            manifest = {}
        missing_fields = REQUIRED_MANIFEST_FIELDS - manifest.keys()
        if missing_fields:
            errors.append(f"{spec.name}: manifest missing fields {sorted(missing_fields)}")
        if manifest.get("name") != spec.name:
            errors.append(f"{spec.name}: manifest name mismatch")
        if manifest.get("skills") != "./skills/":
            errors.append(f"{spec.name}: manifest skills must be ./skills/")
        interface = manifest.get("interface")
        if not isinstance(interface, dict) or not interface.get("defaultPrompt"):
            errors.append(f"{spec.name}: manifest interface.defaultPrompt is required")

        errors.extend(bundle_sync_errors(source_root, spec))
        records = package_records(spec, grouped)
        for record in records:
            validate_agent_yaml_shape(record.agents_file, errors)
        chars = package_catalog_chars(spec, grouped)
        package_metrics.append(
            {
                "name": spec.name,
                "default_install": spec.default_install,
                "public_skills": len(spec.skills),
                "catalog_records": len(records),
                "catalog_chars": chars,
            }
        )

    default_names = [spec.name for spec in defaults]
    combinations: list[dict[str, object]] = []
    for spec in specs:
        requested = default_names if spec.default_install else default_names + [spec.name]
        selected = resolve_selected_packages(requested, specs)
        chars = sum(package_catalog_chars(item, grouped) for item in selected)
        combination = "+".join(item.name for item in selected)
        combinations.append({"selection": combination, "catalog_chars": chars})
        if chars > CATALOG_TARGET:
            errors.append(
                f"context catalog target exceeded: {combination} = {chars} > {CATALOG_TARGET}"
            )

    report = {
        "catalog_target": CATALOG_TARGET,
        "canonical_public_skills": len(canonical),
        "packages": package_metrics,
        "default_plus_domain": combinations,
    }
    return errors, report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    args = parser.parse_args()
    try:
        errors, report = validate()
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        errors, report = [str(exc)], {}

    if args.json:
        print(json.dumps({"ok": not errors, "errors": errors, **report}, ensure_ascii=False, indent=2))
    else:
        for item in report.get("packages", []):
            print(
                f"{item['name']}: {item['public_skills']} public / "
                f"{item['catalog_records']} catalog records / {item['catalog_chars']} chars"
            )
        if errors:
            print("Plugin validation failed:")
            for error in errors:
                print(f"- {error}")
        else:
            print("Plugin marketplace, bundles, ownership, and context budgets are valid.")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
