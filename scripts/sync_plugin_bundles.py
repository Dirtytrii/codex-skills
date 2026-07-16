#!/usr/bin/env python3
"""Generate plugin skill bundles from the canonical top-level skills tree."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from plugin_packages import bundle_sync_errors, load_package_specs, should_package


def assert_safe_bundle_root(bundle_root: Path, plugin_root: Path) -> None:
    resolved_bundle = bundle_root.resolve()
    resolved_plugin = plugin_root.resolve()
    if resolved_bundle.parent != resolved_plugin or resolved_bundle.name != "skills":
        raise ValueError(f"refusing to replace unsafe bundle path: {resolved_bundle}")


def clear_bundle(bundle_root: Path, plugin_root: Path) -> None:
    assert_safe_bundle_root(bundle_root, plugin_root)
    bundle_root.mkdir(parents=True, exist_ok=True)
    for child in bundle_root.iterdir():
        resolved_child = child.resolve()
        if resolved_child.parent != bundle_root.resolve():
            raise ValueError(f"refusing to remove unsafe bundle child: {resolved_child}")
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def copy_skill(source: Path, destination: Path) -> int:
    copied = 0
    for path in sorted(source.rglob("*")):
        if not should_package(path, source):
            continue
        target = destination / path.relative_to(source)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, target)
        copied += 1
    return copied


def write_bundles() -> tuple[int, int]:
    source_root, specs, _ = load_package_specs()
    skill_count = 0
    file_count = 0
    for spec in specs:
        clear_bundle(spec.bundle_root, spec.plugin_root)
        for skill in spec.skills:
            source = source_root / skill
            if not source.is_dir():
                raise ValueError(f"canonical skill is missing: {source}")
            file_count += copy_skill(source, spec.bundle_root / skill)
            skill_count += 1
    return skill_count, file_count


def check_bundles() -> list[str]:
    source_root, specs, _ = load_package_specs()
    return [error for spec in specs for error in bundle_sync_errors(source_root, spec)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--write", action="store_true", help="replace generated plugin bundles")
    mode.add_argument("--check", action="store_true", help="check generated bundles (default)")
    args = parser.parse_args()

    try:
        if args.write:
            skill_count, file_count = write_bundles()
            print(f"Generated {skill_count} packaged skills with {file_count} files.")
        errors = check_bundles()
    except (OSError, ValueError) as exc:
        print(f"Plugin bundle sync failed: {exc}", file=sys.stderr)
        return 1

    if errors:
        print("Plugin bundles are out of sync:")
        for error in errors:
            print(f"- {error}")
        if not args.write:
            print("Run: python scripts/sync_plugin_bundles.py --write")
        return 1

    print("Plugin bundles match canonical skills/.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
