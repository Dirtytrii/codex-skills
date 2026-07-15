# UI Reference Source Catalog

Load this file only when the project lacks enough local design evidence or the user explicitly asks for external references.

## Inspiration Sources

| Source | Best use | Do not use as |
| --- | --- | --- |
| [Lapa Ninja](https://www.lapa.ninja/) | Landing-page structure, section order, full-page examples | Product workflow or dashboard specification |
| [Landing.love](https://www.landing.love/) | Motion, scroll behavior, 3D/WebGL, hero timing | Default motion budget for enterprise UI |
| [Landbook](https://land-book.com/) | Commercial visual language, typography, page/section references | License to copy a complete design |
| [Siteinspire](https://www.siteinspire.com/) | Restrained editorial, portfolio, grid, type, and image direction | Ready-to-use component source |
| [MotionSites](https://motionsites.ai/) | Marketing hero prompts and visual experiments when explicitly requested | Dashboard, form, data table, or end-to-end product UI source |

Use one layout reference and one visual reference at most. Capture specific observations such as grid, hierarchy, type scale, motion trigger, or image treatment rather than labels like "premium" or "modern".

## React Components And Templates

| Source | Role |
| --- | --- |
| [shadcn/ui](https://ui.shadcn.com/) | Accessible owned-code foundation and responsive blocks; customize tokens instead of shipping defaults |
| [21st.dev](https://21st.dev/community/components) | Searchable React/Next.js community components and marketing sections; inspect source, dependency, and license per item |
| [Magic UI](https://magicui.design/docs) | Marketing-oriented React/Tailwind/Motion components; use a few purposeful effects |
| [Aceternity UI](https://ui.aceternity.com/components) | Animated React/Next.js sections and effects; verify whether a component/block is free or paid |
| [React Bits](https://www.reactbits.dev/get-started/index) | Experimental text, background, hover, and interaction components; performance-test before adoption |
| [Cruip free templates](https://cruip.com/free-templates/) | Coded React/Next.js/Vue/admin starting points and Figma references; verify each template license and stack |

Do not combine multiple animation libraries just because they appear in different references. Reuse the project's current motion stack when possible.

## Operational Product UI

Start from the project's existing component library and neighboring pages. If no foundation exists:

- React enterprise/admin: [Ant Design](https://ant.design/docs/react/introduce/) or a deliberately configured shadcn/ui system.
- Vue 3 enterprise/admin: [Element Plus](https://element-plus.org/en-US/guide/design) with project-level variables and size/density rules.
- Mixed or legacy stacks: choose the maintained library already closest to the codebase; do not introduce a second system for one screen.

Reference priorities are information hierarchy, table density, filters, forms, details, permissions, loading, empty/error states, and keyboard/focus behavior. Motion is limited to state transitions, dialogs, collapse/expand, and meaningful feedback.

## Template And No-Code Sources

Framer, Webflow, HTMLrev, and similar template galleries may help with layout or responsive reasoning. Treat them as secondary references, not drop-in source code. Confirm exportability, licensing, dependencies, accessibility, and maintainability before adoption.

## Selection Record

For each reference record:

```text
role: layout | visual | component/motion
url:
borrow:
reject:
stack/license check:
acceptance evidence:
```
