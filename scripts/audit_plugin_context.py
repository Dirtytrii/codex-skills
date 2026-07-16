#!/usr/bin/env python3
"""Estimate skill-catalog context for a selected plugin set and legacy installs."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from plugin_packages import (
    CATALOG_TARGET,
    load_package_specs,
    package_catalog_chars,
    package_records,
    records_by_public_skill,
    resolve_selected_packages,
)


def installed_skill_names(root: Path) -> set[str]:
    if not root.is_dir():
        return set()
    return {
        path.name
        for path in root.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    }


def build_report(requested: list[str], scan_user_roots: bool, home: Path) -> dict[str, object]:
    source_root, specs, _ = load_package_specs()
    if not requested:
        requested = [spec.name for spec in specs if spec.default_install]
    selected = resolve_selected_packages(requested, specs)
    grouped = records_by_public_skill(source_root)
    selected_public = {skill for spec in selected for skill in spec.skills}
    chars = sum(package_catalog_chars(spec, grouped) for spec in selected)
    records = sum(len(package_records(spec, grouped)) for spec in selected)

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
        "catalog_records": records,
        "catalog_chars": chars,
        "catalog_target": CATALOG_TARGET,
        "within_target": chars <= CATALOG_TARGET,
        "legacy_root_scan": legacy_duplicates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--plugin", action="append", default=[], help="enabled plugin name; repeatable")
    parser.add_argument("--scan-user-roots", action="store_true", help="report duplicate legacy flat installs")
    parser.add_argument("--home", type=Path, default=Path.home(), help="home used by --scan-user-roots")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    parser.add_argument("--strict", action="store_true", help="exit nonzero when the target is exceeded")
    args = parser.parse_args()
    try:
        report = build_report(args.plugin, args.scan_user_roots, args.home.expanduser())
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
    return 1 if args.strict and not report["within_target"] else 0


if __name__ == "__main__":
    sys.exit(main())
