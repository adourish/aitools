---
name: mermaid-visio-diagrams
description: Create and convert diagrams — Mermaid syntax, generating Visio drawings from Mermaid, converting Visio back to Mermaid, and the Visio icon/stencil library. Use for "draw a diagram", "make a flowchart", "convert this to Visio", "mermaid", "architecture diagram", or when a doc needs a visual.
---

# Diagrams — Mermaid & Visio

| Task | Guide |
|------|-------|
| Mermaid syntax and patterns | `documentation/skill_mermaid_diagrams.md` |
| Build a Visio drawing via Mermaid | `documentation/skill_visio_via_mermaid.md` |
| Convert an existing Visio file to Mermaid | `documentation/skill_mermaid_from_visio.md` |
| Visio icons and stencils | `documentation/skill_visio_icons.md`, `documentation/skill_diagram_icons.md`, `documentation/skill_mermaid_visio_icons.md` |
| Icon gallery | `documentation/VISIO_ICON_GALLERY.md`, `documentation/visio_icons/` |
| Grant lifecycle diagram spec | `documentation/skill_visio_grant_lifecycle_diagram.md` |
| QIF DNDD fillable forms architecture | `documentation/skill_qif_dndd_fillable_forms_visio_spec.md` |

## Tooling

```bash
python documentation/diagram-tools/mermaid_to_visio.py   # see diagram-tools/QUICKSTART.md
python _tools/mermaid-to-visio.py
python _tools/extract_visio_icons.py                     # and export_visio_icons_v2.py
```

**Every diagram must be Section 508 compliant** — `documentation/skill_mermaid_section_508.md` and
`documentation/skill_visio_section_508.md`. That means never colour alone, cyan/yellow/magenta over
red/green, and a text alternative.
