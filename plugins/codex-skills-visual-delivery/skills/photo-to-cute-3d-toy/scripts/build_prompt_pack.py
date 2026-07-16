#!/usr/bin/env python3
"""Build a cute 3D toy prompt pack from a scene manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_SCENE_KEYS = {
    "id",
    "title",
    "mainPhoto",
    "toyReferences",
    "stage",
    "props",
    "outputs",
}


def load_manifest(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def resolve(root: Path, rel: str) -> Path:
    candidate = Path(rel)
    return candidate if candidate.is_absolute() else root / candidate


def require_scene(manifest: dict[str, Any], scene_id: str) -> dict[str, Any]:
    for scene in manifest.get("scenes", []):
        if scene.get("id") == scene_id:
            missing = sorted(REQUIRED_SCENE_KEYS - set(scene))
            if missing:
                raise SystemExit(f"Scene {scene_id} is missing keys: {', '.join(missing)}")
            return scene
    raise SystemExit(f"Scene not found: {scene_id}")


def check_paths(project_root: Path, scene: dict[str, Any]) -> list[str]:
    warnings: list[str] = []
    paths = [scene["mainPhoto"]]
    refs = scene.get("toyReferences", {})
    for values in refs.values():
        if isinstance(values, list):
            paths.extend(value for value in values if isinstance(value, str) and "/" in value)
    for rel in paths:
        if not resolve(project_root, rel).exists():
            warnings.append(f"Missing referenced file: {rel}")
    return warnings


def render_pack(manifest: dict[str, Any], scene: dict[str, Any], warnings: list[str]) -> str:
    defaults = manifest.get("defaults", {})
    refs = scene.get("toyReferences", {})
    outputs = scene.get("outputs", {})
    negative = scene.get("ipSafety", {}).get("mustAvoid", defaults.get("negative", []))
    must_preserve = scene.get("mustPreserve", [])
    props = scene.get("props", [])

    return f"""# {scene['id']} Prompt Pack

## Input Roles

- Main photo: `{scene['mainPhoto']}`
- Face references: {', '.join(f'`{item}`' for item in refs.get('face', [])) or 'None'}
- Outfit references: {', '.join(f'`{item}`' for item in refs.get('outfit', [])) or 'None'}
- Pose references: {', '.join(f'`{item}`' for item in refs.get('pose', [])) or 'None'}
- Mood references: {', '.join(f'`{item}`' for item in refs.get('mood', [])) or 'None'}

## 2D Concept Prompt

Create an original cute collectible toy concept for `{scene['title']}`.
Use the face references only for face, hair, expression, and gentle identity cues.
Use the outfit references for clothing silhouette, accessories, bag, footwear, and body styling.
Use the mood references and stage description for the environment, lighting, props, and memory.

Toy style: {scene.get('toyStyle', defaults.get('toyStyle', 'original cute collectible toy'))}.
Scene/stage: {scene['stage']}
Props: {', '.join(props)}.
Must preserve: {', '.join(must_preserve) or 'subject identity cues, scene-specific outfit details'}.

Avoid: {', '.join(negative)}.

## 3D Conversion Notes

- Prefer a clean full-body three-quarter toy view for conversion.
- Keep the hair, outfit silhouette, accessories, and props readable at mobile size.
- Export target: `{outputs.get('model', 'public/models/<scene-id>.glb')}`.
- Concept output target: `{outputs.get('concept', 'assets/toy-concepts/<scene-id>-concept-v1.png')}`.

## Validation Warnings

{chr(10).join(f'- {warning}' for warning in warnings) if warnings else '- None'}
"""


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--project-root", required=True, type=Path)
    parser.add_argument("--scene", required=True)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()

    manifest = load_manifest(args.manifest)
    scene = require_scene(manifest, args.scene)
    project_root = args.project_root.resolve()
    warnings = check_paths(project_root, scene)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(render_pack(manifest, scene, warnings), encoding="utf-8")
    print(f"Wrote prompt pack: {args.out}")
    if warnings:
        print("Warnings:")
        for warning in warnings:
            print(f"- {warning}")


if __name__ == "__main__":
    main()
