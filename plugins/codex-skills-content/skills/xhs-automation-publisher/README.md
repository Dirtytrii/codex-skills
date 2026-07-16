# XHS Automation Publisher

Vendored from [white0dew/XiaohongshuSkills](https://github.com/white0dew/XiaohongshuSkills) at upstream commit `988fd2efac377cc6dab3a630ed157336b5ebfb03`.

This local adaptation keeps the Python CDP automation scripts, but changes the Codex skill contract so Xiaohongshu publishing remains fail-closed:

- preview/fill is the default role behavior;
- final posting and all interaction actions require explicit user approval;
- local cookies, account config, QR payloads, and Chrome profile paths must stay out of git;
- `xhs-publish-assistant` remains the copy-ready package formatter.

Runtime dependencies are listed in `requirements.txt`.
