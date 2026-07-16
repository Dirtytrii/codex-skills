# Prompting

Use one prompt pack per scene. Keep the person stylized and original, but preserve the user-approved photo roles.

## Prompt Pack Sections

1. `Input roles`: list each image and its role.
2. `Subject identity cues`: face/hair/expression cues from `face`.
3. `Outfit cues`: clothing, accessories, bag, footwear, and silhouette from `outfit`.
4. `Mood/stage cues`: environment, lighting, place, and memory.
5. `2D concept prompt`: one generation-ready prompt.
6. `Negative constraints`: privacy/IP/quality exclusions.
7. `3D conversion notes`: what must survive in GLB.

## 2D Concept Template

```text
Create an original cute collectible toy concept of the same subject for <scene title>.
Use <face refs> only for face, hair, expression, and gentle identity cues.
Use <outfit refs> for clothing silhouette, accessories, bag, footwear, and body styling.
Use <mood refs/text> for background mood, stage, lighting, and props.

Toy style: soft plush material mixed with premium designer blind-box proportions; rounded head, gentle stylized eyes, small hands, charming compact body, handmade collectible finish. Keep it cute and emotionally warm, not photorealistic.

Scene/stage: <stage>.
Props: <props>.
Must preserve: <short list of scene-specific face/outfit details>.
Avoid: celebrity likeness, brand logos, readable protected marks, real artist names, direct imitation of commercial toy IPs, extra characters, distorted face, unreadable text, watermark.
```

## 3D-Friendly Concept Rules

- Prefer a clean three-quarter or front view with visible full body.
- Keep hair, bag, belt, shoes, and props readable but not overly thin.
- Avoid transparent glass, smoke-only silhouettes, extremely loose strands, and tiny text.
- Ask for a neutral or simple background if the next route requires image-to-3D isolation.
- If using a stage concept image for the website rather than conversion, create a separate asset from the toy turntable concept.
