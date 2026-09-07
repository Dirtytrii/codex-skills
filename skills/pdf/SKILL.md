---
name: pdf
description: Explicit compatibility adapter for the collection's legacy PDF workflow and delivery conventions. Prefer the installed official PDF skill for generic PDF reading, generation, rendering and forms.
---

# PDF Delivery Compatibility

Prefer the installed official PDF skill as the single owner of general PDF work, including forms. Identify it by provider/path; do not recursively invoke this adapter or load both full workflows.

- Preserve the user's requested output directory. Collection defaults (`tmp/pdfs/`, `output/pdf/`) are optional conventions, not authority to move files or delete existing artifacts.
- When an official PDF skill is available, use its workflow and add only applicable delivery conventions here. For broader client handoff packaging, use the available delivery-document-package skill when requested.
- When the official capability is unavailable and the user chooses the legacy fallback, read [the retained workflow](references/legacy-pdf-workflow.md). Inspect existing dependencies first; installing packages or system tools requires authorization.
- State which implementation was actually used, the validation evidence and any unsupported capability. Do not claim AcroForms coverage from the legacy checklist alone.
