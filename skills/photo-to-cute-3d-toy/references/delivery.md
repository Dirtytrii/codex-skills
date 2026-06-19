# Delivery And Validation

## Concept Image Delivery

Save project-bound concept images under:

```text
assets/toy-concepts/<scene-id>-concept-vN.png
```

Report:

- generation route used;
- input images referenced or uploaded;
- prompt pack path;
- visual QA notes.

## GLB Delivery

Save frontend-ready models under:

```text
public/models/<scene-id>.glb
```

If sidecar files are required, use:

```text
public/models/<scene-id>/
```

## Basic GLB Checks

At minimum:

- file exists and size is non-zero;
- first four bytes are `glTF` for `.glb`;
- Three.js `GLTFLoader` can load it in the frontend or a local viewer;
- model scale is documented;
- texture count and file size are acceptable for mobile.

Preferred mobile targets:

- one model visible at a time;
- under 10 MB for first iteration when possible;
- compressed with Draco or Meshopt only after the frontend loader supports it.

## Handoff To Frontend

Tell the frontend window:

- `modelPath`: `/models/<scene-id>.glb`;
- fallback if missing: use scene placeholder toy;
- concept preview path;
- required scale/position/rotation;
- any known material issues.
