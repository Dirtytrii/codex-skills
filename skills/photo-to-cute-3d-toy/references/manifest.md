# Scene Manifest

Use a JSON manifest so every scene can be regenerated without rediscovering photo intent.

## Required Top-Level Fields

```json
{
  "version": 1,
  "project": "3Dling",
  "defaults": {
    "toyStyle": "original soft plush plus designer blind-box collectible proportions",
    "negative": ["celebrity likeness", "brand logo", "readable protected text"]
  },
  "paths": {
    "concepts": "assets/toy-concepts",
    "models": "public/models",
    "promptPacks": "docs/3d-generation"
  },
  "scenes": []
}
```

## Required Scene Fields

Each scene must include:

- `id`: stable scene folder id, for example `sence5`.
- `title`: human scene name.
- `mainPhoto`: project-root relative path for the website main photo.
- `toyReferences.face`: photos used for face, hair, expression, and identity cues.
- `toyReferences.outfit`: photos used for clothing, body proportion, accessories, and footwear.
- `toyReferences.pose`: optional pose/action photos.
- `toyReferences.mood`: photos or text cues used for place, lighting, and memory.
- `stage`: background/stage concept for the toy.
- `props`: small safe props that make the memory readable.
- `toyStyle`: scene-specific override when needed.
- `outputs.concept`: expected concept image path.
- `outputs.promptPack`: generated prompt pack path.
- `outputs.model`: expected GLB path.
- `privacy.externalUploadAllowed`: whether external AI services are allowed.
- `ipSafety.mustAvoid`: per-scene IP/brand/celebrity constraints.

## Photo Role Rules

- Use `face` photos only for face, hair, and expression. Do not infer unrelated outfit details from a close-up if the scene gives an outfit reference.
- Use `outfit` photos for clothing silhouette, accessories, shoes, bags, and wearable details.
- Use `mood` photos for environment, lighting, props, and color, not for identity.
- If multiple people appear, identify which person is the subject before writing prompts.
- If role assignment is ambiguous, ask the user before generating.

## Output Path Convention

- Concept image: `assets/toy-concepts/<scene-id>-concept-vN.png`
- Prompt pack: `docs/3d-generation/<scene-id>-prompt-pack.md`
- Model: `public/models/<scene-id>.glb`
- Optional texture/model sidecars: `public/models/<scene-id>/`
