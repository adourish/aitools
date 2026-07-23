---
name: section-508-compliance
description: Section 508 accessibility requirements for the SERIO / SERIO+ web app, its diagrams, and its generated PDFs (the seizure-recommendation memo). Use when building or reviewing any SERIO UI, writing a doc/diagram, or generating a PDF that a real user will read — SERIO is a federal (FDA) application, so Section 508 is a legal requirement, not a nice-to-have.
metadata:
  version: "1.0.0"
  repository: fda-serio
  last_updated: "2026-07-17"
  type: reference
---

# Section 508 compliance — SERIO / SERIO+

**Section 508 is the federal accessibility law: anything the U.S. government builds or buys must be
usable by people with disabilities.** SERIO is an FDA application, so its screens, the documents we
write about it, and the PDFs it generates all have to meet it. This skill is the short "what to check
and why"; the sibling skills carry the color and diagram detail.

> Siblings: [`section-508-color-palette`](../section-508-color-palette/SKILL.md) (the accessible
> palette rule), [`mermaid-section-508`](../mermaid-section-508/SKILL.md) (accessible diagrams).

---

## Quick reference

**Use when:** building/reviewing a SERIO+ screen, writing a brief or diagram, or generating a PDF.
**The one number to remember:** text needs a **4.5:1 contrast ratio** against its background (3:1 for
large text ≥18pt and for UI controls/borders). Check it at <https://webaim.org/resources/contrastchecker/>.
**The one habit:** never signal meaning with color alone — add a label, icon, or shape (see below).

The five things Section 508 asks of any content:
- **Enough contrast** — 4.5:1 for normal text.
- **A text alternative** for every image, chart, and icon (`alt` text / a caption).
- **Keyboard reachable** — every action works without a mouse; focus is visible; no keyboard traps.
- **Screen-reader friendly** — real headings, labelled form fields, tables with header rows.
- **Not color-dependent** — information survives in grayscale.

---

## SERIO+ web app (the Angular UI)

- **Semantic structure.** Use real headings and landmarks (`<header>`, `<nav aria-label="…">`,
  `<main>`, `<footer>`), not styled `<div>`s. Screen readers navigate by these.
- **Label every field.** Each input needs a `<label for="…">` (or `aria-label`). A placeholder is
  not a label — it disappears on typing.
- **Keyboard + focus.** Every control reachable by Tab in a logical order; a **visible focus ring**;
  no trap you can't Tab out of. Custom widgets (dropdowns, modals) need the matching ARIA roles.
- **Don't rely on color.** A field that turns a color to mean "error" must also show text/an icon
  (e.g. "Required" with a warning glyph). See the color skill for the repo's palette rule.
- **Zoom + reflow.** Content stays usable at 200% zoom without horizontal scrolling.
- **Tables.** Data tables get a header row (`<th scope="col">`); don't use tables for layout.

## Generated PDFs (the seizure-recommendation memo)

SERIO+ generates the **seizure-recommendation (SZR) memo PDF** server-side (Thymeleaf → iText); design
in [`../../docs/features/FS-018-serioplus-seizure-memo-pdf.md`](../../docs/features/FS-018-serioplus-seizure-memo-pdf.md).
A PDF that a person reads must be accessible too — treat this as a **best-effort "tagged PDF"
requirement**:

- **Tag the PDF** so it has a real reading order and structure (headings, paragraphs, lists) a screen
  reader can follow — a flat "picture of text" is not accessible. iText can emit tagged/PDF-UA output
  when the document is built with tagging enabled.
- **Alt text** on any logo or image in the template; a **document title** in the metadata.
- **Selectable, searchable text** — never a scanned/flattened image of the memo.
- **Readable contrast** in the template (the palette rule applies to the PDF too).
- If full tagging is out of scope for a story, at minimum keep text selectable, set the title, and log
  the accessibility gap rather than silently shipping an untagged file.

## Documents & diagrams we write

- **Headings in order** (don't skip levels), alt text / captions on every image and diagram, and
  descriptive link text ("Download the runbook", not "click here").
- **Diagrams:** see [`mermaid-section-508`](../mermaid-section-508/SKILL.md) and always give a diagram a
  one-line text summary in the prose so a non-visual reader gets the same information.

---

## Fast review checklist

- [ ] Text contrast ≥ 4.5:1 (large text / UI ≥ 3:1)
- [ ] No meaning carried by color alone — label/icon/shape backs it up
- [ ] Every image/chart/diagram has a text alternative
- [ ] Keyboard reaches everything; focus is visible; no traps
- [ ] Real headings; form fields labelled; data tables have header rows
- [ ] Generated PDFs are tagged, titled, and have selectable text
