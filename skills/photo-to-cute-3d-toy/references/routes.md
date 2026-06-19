# 3D Route Selection

Use official documentation or official GitHub/model pages when checking current capabilities.

## Default Recommendation

For this project, prefer a staged route:

1. generate or curate a 2D toy concept with strong identity/outfit preservation;
2. create a clean toy-only concept/turntable image;
3. convert to 3D with an API or local model;
4. inspect, simplify, and export `GLB` for Three.js.

## Route Matrix

### API first

Use when quality and speed matter more than local reproducibility.

- Tripo API / Tripo Studio: image-to-3D route, convenient for concept-to-model tests.
- Rodin / Hyper3D: useful if available to the user and supports the desired export format.

Before uploading private photos, report exactly which images will be uploaded and why.

### Local first

Use when privacy, cost, or repeatability matter more than setup time.

- Hunyuan3D 2.x: strong open-source route for image/text-to-3D, but may require model weights and GPU setup.
- TRELLIS: strong research/open-source route for 3D asset generation from image prompts, but setup can be heavier.
- TripoSR: lighter image-to-3D baseline for quick local tests; output quality may need cleanup.
- ComfyUI-3D-Pack: workflow wrapper when ComfyUI is already installed; treat it as integration glue, not the underlying model authority.

Do not download large weights or install CUDA/PyTorch stacks without explicit approval.

Windows/Python 3.12 note: TripoSR's `torchmcubes` dependency may require native build tools. For a first CPU prototype, a project-local `torchmcubes.py` shim can expose `marching_cubes(volume, level)` through `skimage.measure.marching_cubes`; document this as a local compatibility fallback and do not pretend it is the upstream package.

## Selection Heuristics

- Need the fastest `sence5` prototype: use API first, then inspect the GLB.
- Need no external upload: use a local lightweight route first, usually TripoSR or Hunyuan3D mini if available.
- Need best collectible quality: create a strong 2D concept first, then try Hunyuan3D/TRELLIS/API and compare.
- Need production frontend asset: choose the result with clean silhouette, stable scale, low material complexity, and reasonable file size.

## Character-Toy Quality Notes

For cute character toys, single-image reconstruction often creates a relief-like or standee-like mesh. Treat TripoSR as a technical prototype route unless visual QA proves otherwise.

Prefer a multi-view/turntable route when the target includes:

- face likeness or approved face style;
- hair volume;
- glasses or head accessories;
- small belts, bags, shoes, lace, or jewelry;
- a full-body toy silhouette that must look good while rotating.

If a local TripoSR result loads technically but fails display QA, mark it `technical prototype / not display-approved` and keep the frontend on a placeholder or debug toggle until a v2 asset exists.

## Official Sources To Recheck

- Hunyuan3D-2 official GitHub: `https://github.com/Tencent-Hunyuan/Hunyuan3D-2`
- Hunyuan3D-2.1 official GitHub: `https://github.com/Tencent-Hunyuan/Hunyuan3D-2.1`
- TRELLIS official GitHub: `https://github.com/microsoft/TRELLIS`
- TRELLIS.2 project page: `https://microsoft.github.io/TRELLIS.2/`
- TripoSR official GitHub: `https://github.com/VAST-AI-Research/TripoSR`
- ComfyUI-3D-Pack official GitHub: `https://github.com/MrForExample/ComfyUI-3D-Pack`
- Tripo platform docs: `https://platform.tripo3d.ai/`
- Tripo API feature page: `https://www.tripo3d.ai/api`
- Hyper3D Rodin Gen-2 API docs: `https://developer.hyper3d.ai/api-specification/rodin-generation-gen2_reset_v`
