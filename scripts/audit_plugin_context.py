#!/usr/bin/env python3
"""Estimate skill-catalog context for a selected plugin set and legacy installs."""

from __future__ import annotations

import argparse
import json
import sys
import tomllib
from pathlib import Path

from plugin_packages import (
    CATALOG_TARGET,
    load_package_specs,
    package_catalog_chars,
    package_records,
    records_by_public_skill,
    resolve_selected_packages,
)


PRESETS = {name: ["codex-skills-core", f"codex-skills-{domain}"] for name, domain in
           (("development", "engineering"), ("content", "content"),
            ("operations", "operations"), ("visual", "visual-delivery"))}


def configured_plugins(path: Path) -> list[str]:
    """Read only the self-maintained namespace; never print the full configuration."""
    _, _, marketplace = load_package_specs()
    with path.open("rb") as handle:
        plugins = tomllib.load(handle).get("plugins", {})
    if not isinstance(plugins, dict):
        raise ValueError("plugins must be a TOML table")
    suffix = f"@{marketplace}"
    selected = []
    for name, entry in plugins.items():
        if not name.endswith(suffix):
            continue
        if not isinstance(entry, dict) or type(entry.get("enabled")) is not bool:
            raise ValueError(f"{name}: enabled must be an explicit boolean")
        if entry["enabled"]:
            selected.append(name.removesuffix(suffix))
    return selected


def installed_skill_names(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def build_report(requested: list[str], scan_user_roots: bool, home: Path,
                 *, actual_config: bool = False) -> dict[str, object]:
    source_root, specs, _ = load_package_specs()
    if not requested and not actual_config:
        requested = [spec.name for spec in specs if spec.default_install]
    selected = resolve_selected_packages(requested, specs)
    if actual_config:
        selected = [spec for spec in selected if spec.name in requested]
    grouped = records_by_public_skill(source_root)
    selected_public = {skill for spec in selected for skill in spec.skills}
    chars = sum(package_catalog_chars(spec, grouped) for spec in selected)
    all_records = [record for spec in selected for record in package_records(spec, grouped)]
    implicit = [record for record in all_records if record.allow_implicit_invocation is not False]
    missing_dependencies = sorted({name for spec in selected for name in spec.requires if name not in requested}) if actual_config else []

    legacy_duplicates: list[dict[str, object]] = []
    if scan_user_roots:
        for root in (home / ".agents" / "skills", home / ".codex" / "skills"):
            installed = installed_skill_names(root)
            duplicated = sorted(installed & selected_public)
            legacy_duplicates.append(
                {
                    "root": str(root),
                    "installed_public_skills": len(installed),
                    "duplicates_selected_plugins": duplicated,
                }
            )

    return {
        "selected_plugins": [spec.name for spec in selected],
        "public_skills": len(selected_public),
        "catalog_records": len(all_records),
        "implicit_catalog_records": len(implicit),
        "implicit_catalog_chars": sum(record.catalog_chars for record in implicit),
        "selection_source": "explicit_config" if actual_config else "proposed_selection",
        "missing_dependencies": missing_dependencies,
        "runtime_visibility": "not_evaluable",
        "measurement_note": "source catalog estimate, not runtime injection or membership billing",
        "catalog_chars": chars,
        "catalog_target": CATALOG_TARGET,
        "within_target": chars <= CATALOG_TARGET,
        "legacy_root_scan": legacy_duplicates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument("--plugin", action="append", default=[], help="proposed plugin name; repeatable")
    selection.add_argument("--preset", choices=sorted(PRESETS), help="read-only core/domain selection proposal")
    selection.add_argument("--codex-config", type=Path, help="inspect explicit enablement without changing configuration")
    parser.add_argument("--scan-user-roots", action="store_true", help="report duplicate legacy flat installs")
    parser.add_argument("--home", type=Path, default=Path.home(), help="home used by --scan-user-roots")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    parser.add_argument("--strict", action="store_true", help="exit nonzero when the target is exceeded")
    args = parser.parse_args()
    try:
        requested = (configured_plugins(args.codex_config) if args.codex_config else
                     PRESETS[args.preset] if args.preset else args.plugin)
        report = build_report(requested, args.scan_user_roots, args.home.expanduser(),
                              actual_config=args.codex_config is not None)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Plugin context audit failed: {exc}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        print(f"Selected: {', '.join(report['selected_plugins'])}")
        print(
            f"Catalog: {report['catalog_records']} records, {report['catalog_chars']} / "
            f"{report['catalog_target']} chars"
        )
        for root_report in report["legacy_root_scan"]:
            duplicates = root_report["duplicates_selected_plugins"]
            if duplicates:
                print(f"Duplicate legacy installs in {root_report['root']}: {', '.join(duplicates)}")
    return 1 if args.strict and (not report["within_target"] or report["missing_dependencies"]) else 0


if __name__ == "__main__":
    sys.exit(main())
