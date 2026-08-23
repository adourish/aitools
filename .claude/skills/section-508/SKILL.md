---
name: section-508
description: Section 508 / WCAG accessibility — the approved colour palette, accessible Mermaid and Visio diagrams, and compliance review of UI, documents and diagrams. Use for "is this 508 compliant", "accessibility review", "what colours can I use", "contrast", "screen reader", or before shipping any UI, diagram or document.
---

# Section 508 / WCAG compliance

Everything that ships — UI, diagram, document — has to pass. This is not a final polish step.

| Task | Guide |
|------|-------|
| The compliance rules and how to review against them | `system/skill_section_508_compliance.md` |
| Approved colour palette and contrast pairs | `documentation/skill_section_508_color_palette.md` |
| Accessible Mermaid diagrams | `documentation/skill_mermaid_section_508.md` |
| Accessible Visio diagrams | `documentation/skill_visio_section_508.md` |
| Most recent audit and its findings | `SECTION_508_COLOR_AUDIT_2026-03-01.md` |

## The rules that get broken most

- **Never colour as the sole indicator.** Pair it with text, shape, or an icon.
- **Never red/green as the only signal** — the palette is **cyan / yellow / magenta**.
- Contrast: 4.5:1 body text, 3:1 large text and UI boundaries.
- Every image, chart and diagram needs a real text alternative — "diagram" is not one.
- Keyboard reachable, visible focus, correct heading order, labelled form controls.
