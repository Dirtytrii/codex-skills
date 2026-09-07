---
name: hatch-pet
description: Explicit compatibility adapter for repairing existing v1 Codex pets with 8x9 atlases. Not for new pets or v2/8x11 packaging; use the installed v2-capable pet skill for those tasks.
---

# Legacy v1 Pet Compatibility

This packaged entrypoint preserves the old v1 pipeline without competing with the current v2 pet skill.

1. Confirm the user explicitly requested v1 compatibility and inspect the existing pet manifest/atlas. Do not infer v1 from this skill's name or from a missing version field alone.
2. For new pets, v2, 8x11 or 16-direction work, use an available v2-capable pet skill identified by its full location/provider. Never recursively invoke this same adapter. If no such skill is available, stop with the missing capability; do not silently produce v1 or install a dependency.
3. Only for confirmed v1 work, load [the retained v1 workflow](references/legacy-v1-workflow.md). Keep all scripts relative to this skill root. Preserve original assets and write a separate output until validation passes.
4. Report the actual atlas dimensions, manifest version (including absent for a legacy artifact), checks performed and compatibility limits. Never label v1 output as v2-compatible.

This compatibility package does not vendor or claim to validate the v2 implementation. New v2 work remains owned by the selected v2 skill and its tests.
