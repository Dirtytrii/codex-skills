# Frontend Visual Direction

Read this reference only for marketing, brand, portfolio, editorial/content, or similarly expressive pages that need a visual direction beyond the existing project system. Do not load it for routine dashboards, lists, details, forms, settings, or small product UI corrections.

## Outcome

Produce one coherent, implementable direction that fits the product, audience, content, assets, and technical stack. Visual novelty is useful only when it improves recognition, hierarchy, comprehension, trust, or emotional fit.

## Inputs

Use available evidence before inventing a direction:

- page purpose and primary action;
- audience, context, and expected level of trust or energy;
- real brand assets, product imagery, content, and claims;
- existing components, tokens, typography, and neighboring pages;
- stack, performance, accessibility, localization, and maintenance constraints;
- selected layout, visual, component, or motion references from `source-catalog.md`.

Start with no persistent aesthetic preference. Do not inherit taste rules or review judgments from the old `design-taste-frontend` workflow. Explicit constraints in the current brief and fresh feedback on rendered work remain valid evidence.

If a material input is unknown, state the smallest assumption. Do not fabricate brand history, customer proof, metrics, product capabilities, or visual assets presented as real.

## Visual Direction Brief

Return a compact brief before implementation:

```text
concept: one sentence describing the visual idea and why it fits
design variance: 1-10 with one reason
motion intensity: 1-10 with one reason
visual density: 1-10 with one reason
foundation: existing system or one chosen design system
typography: display/body roles and hierarchy
palette: semantic roles, contrast, and image relationship
composition: focal point, section rhythm, container/grid behavior
material: borders, surfaces, radii, shadows, texture
assets: real, searched, generated, illustrated, 3D, video, or none
motion: purpose, trigger, duration range, reduced-motion behavior
avoid: up to five patterns that would make this page generic or off-brand
acceptance: visible evidence that proves the direction works
```

The dials communicate intent; they are not universal presets.

## Dial Guidance

### Design Variance

- `1-3`: restrained extension of an established system;
- `4-6`: recognizable structure with deliberate visual distinction;
- `7-9`: expressive composition for brand, campaign, portfolio, or editorial work;
- `10`: experimental only when the brief, audience, and implementation budget support it.

### Motion Intensity

- `0-2`: state transitions and feedback only;
- `3-5`: purposeful entrance, hover, or scroll sequencing;
- `6-8`: motion is part of storytelling or spatial navigation;
- `9-10`: experimental choreography with explicit performance and accessibility budget.

Every motion should communicate hierarchy, feedback, state, or narrative. Remove effects whose only rationale is that they look impressive.

### Visual Density

- `1-3`: sparse, image-led, or luxury/editorial pacing;
- `4-6`: balanced marketing or product-story density;
- `7-9`: information-rich layouts with strong grouping and scan paths;
- `10`: use only for intentionally dense expert surfaces with proven readability.

## Foundation Decision

Use the existing project system first. Introduce a different design system only when the project has no suitable foundation and the task authorizes dependency changes.

- Choose one component/design system per surface.
- Treat visual styles such as editorial, brutalist, neo-industrial, playful, cinematic, or minimal as directions, not packages.
- Do not imitate a named company's identity or copy a reference page wholesale.
- Check license, dependency cost, accessibility, bundle impact, and maintenance before adopting code.

## Composition

Build a clear focal point and a readable path through the page. Vary section composition when the content jobs differ; reuse a pattern when repetition improves comprehension.

For a landing-page hero:

- make the brand, product, person, place, or literal offer visible in the first viewport;
- keep the primary action findable without turning the hero into a control panel;
- use imagery that reveals the actual subject when inspection matters;
- leave a visible cue that more content follows.

These are decision criteria, not fixed word counts or mandatory layouts. Operational UI should follow the main workflow's density and ergonomics rules instead.

## Typography And Palette

- Assign explicit display, heading, body, label, data, and caption roles as needed.
- Use type contrast to express hierarchy; avoid novelty type where reading speed matters.
- Select semantic color roles before decorative shades.
- Keep sufficient contrast and test real text lengths, localization, and error states.
- Use dark mode only when the product, environment, brand, or user setting calls for it.
- Avoid one-note palettes and familiar AI defaults when they do not fit the brief.

## Assets And Material

Choose the visual medium from the page's job:

- real product or venue imagery when users must inspect the subject;
- generated or illustrated assets when the concept is fictional, abstract, or explicitly art-directed;
- texture, 3D, Canvas, WebGL, Lottie, or video only when the benefit justifies complexity;
- no hero media when typography and product UI carry the message better.

Do not force image generation merely because a tool is available. Do not fake technical diagrams, testimonials, logos, analytics, or precision data as decoration.

Cards, glass, gradients, pills, grids, shadows, marquees, and bento layouts are tools, not defaults. Use each only when it supports grouping, hierarchy, interaction, or the selected concept.

## Anti-Template Review

Check whether the page looks as if its content could be swapped with any unrelated startup. Common causes include:

- generic purple/blue gradients, glass surfaces, and floating blobs without brand rationale;
- every section becoming a rounded card grid;
- placeholder companies, metrics, testimonials, dashboards, or trust logos;
- repeated centered headline/subtitle/button composition;
- decorative labels, fake coordinates, fake system data, or pseudo-technical diagrams;
- motion libraries added because they are available rather than needed;
- identical visual treatment for unrelated sections;
- default component-library styling shipped without project-level tokens.

Replace generic treatment with evidence from the actual product, audience, content, assets, and selected references. Do not create a new blanket ban to fix one recurring aesthetic failure.

## Responsive And Interaction Direction

Define how hierarchy changes, not only how columns stack:

- what remains first and visible on mobile;
- which media crops, moves, simplifies, or disappears;
- how navigation, controls, forms, and long labels fit;
- how pointer-only effects translate to touch and keyboard;
- how reduced motion changes transitions and scroll behavior;
- how loading, empty, error, success, disabled, and focus states retain the concept.

## Direction Selection

Use one direction when the brief is clear. For an ambiguous `medium+` visual task, offer at most three materially different directions. Explain the tradeoff and recommend one; do not blend them before selection.

Once a direction is accepted, stop exploring new aesthetics. If rendered acceptance fails, use the main workflow's reference ledger and replace only the failed layout, visual, component, or motion dimension.

During the preference-reset period, record explicit user or designated-reviewer feedback as raw evidence using `visual-review-signals.md`. Do not infer or activate a lasting aesthetic profile.

## Acceptance

The direction is ready for implementation when:

- it can be explained in one sentence tied to product and audience;
- typography, palette, composition, assets, and motion form one system;
- the chosen stack can implement it without fragile imitation;
- real content and interaction states fit;
- mobile and desktop hierarchy are explicit;
- accessibility and performance constraints are named;
- screenshot criteria distinguish success from subjective preference.
