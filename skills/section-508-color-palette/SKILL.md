---
name: section-508-color-palette
description: The accessible color rule for anything visual in this repo — SERIO+ UI, diagrams, charts, status badges. Use when picking colors so content stays Section 508 compliant AND colorblind-safe. This repo's convention is cyan / yellow / magenta as the signal colors — never red/green as the sole indicator (red-green color blindness is the most common kind).
metadata:
  version: "1.0.0"
  repository: fda-serio
  last_updated: "2026-07-17"
  type: reference
---

# Accessible color palette — SERIO

**Two rules cover almost everything: hit the contrast ratio, and never let color be the only signal.**
Section 508 sets the contrast floor; this repo's cyan/yellow/magenta convention keeps color usable for
people with red-green color blindness (about 1 in 12 men).

> Siblings: [`section-508-compliance`](../section-508-compliance/SKILL.md) (the full checklist),
> [`mermaid-section-508`](../mermaid-section-508/SKILL.md) (applying this in diagrams).

---

## Quick reference

**Use when:** choosing colors for a SERIO+ screen, a diagram, a chart, or a status badge.
**Contrast floor:** **4.5:1** for normal text, **3:1** for large text (≥18pt) and UI borders/controls.
Verify at <https://webaim.org/resources/contrastchecker/>.
**Repo signal colors:** **cyan, yellow, magenta** — and **never red vs. green as the only difference**
between two states (that pair is invisible to the most common color blindness).

---

## Rule 1 — meaning never rides on color alone

If two states differ only by hue, someone will miss it. Always add a second, non-color signal:

| State | Color cue | Required backup (this is the part that matters) |
|-------|-----------|--------------------------------------------------|
| OK / done | cyan | a word ("Complete") or a check/✔ glyph |
| Caution / pending | yellow | a word ("Pending") or a triangle glyph |
| Attention / blocked | magenta | a word ("Blocked") or a distinct icon |

Same idea in charts: differentiate series by **label, line style, or shape marker**, not hue alone.

## Rule 2 — hit the contrast floor

Bright cyan/yellow/magenta are fine as **fills behind dark text** but usually fail as **text or thin
lines on white** — they're too light. So:

- **Body text / headings:** use high-contrast neutrals on white. These are safe and verified:

  | Use | Hex | Contrast on white |
  |-----|-----|-------------------|
  | Body text | `#000000` (black) | 21:1 |
  | Heading / link | `#003366` (dark blue) | 12.6:1 |
  | Heading (alt) | `#000080` (navy) | 16.9:1 |
  | Secondary text | `#555555` (dark gray) | 7.0:1 |

- **Signal colors as fills:** put the cyan/yellow/magenta behind **black text**, and keep a solid
  (near-black) border so the shape reads even in grayscale. Yellow in particular works **only** as a
  fill behind dark text — yellow text on white is unreadable.
- **Signal colors as text or lines:** darken them until they pass 4.5:1 (e.g. a deep teal-cyan / deep
  magenta), and always run the specific hex through the contrast checker before committing.

## Prohibited

- **Red vs. green as the sole difference** between two states — the headline rule of this repo.
- Any text below 4.5:1 (large text below 3:1). Light gray, pale blue, bright yellow **as text** all
  fail on white.

---

## Diagram / chart quick set

```
Text on light fills:  #000000 (black)
Borders / arrows:     #000000 (solid, 2px min)
Signal fills:         cyan  = OK/info   yellow = caution   magenta = attention
                      (each fill behind BLACK text, each with a text label)
Neutral fill:         #FFFFFF with #000000 text
```

Always give a diagram or chart a one-line **text summary** in the surrounding prose so the information
survives with no color and no vision at all. Full guidance:
[`mermaid-section-508`](../mermaid-section-508/SKILL.md).
