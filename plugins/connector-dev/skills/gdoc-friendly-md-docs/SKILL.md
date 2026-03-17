---
name: gdoc-friendly-md-docs
description: Create or format Markdown and HTML documents so they copy cleanly into Google Docs. Use when writing docs for GDoc, pasting into Google Docs, gdoc-compatible format, or when tables/headings must paste correctly from browser or editor.
---

# MD docs that support Google Docs (gdoc) format

Use this skill when creating or editing documents that will be copied into Google Docs (e.g. technical design docs, meeting dedup specs, data mapping). Goal: **tables, headings, and lists paste with correct structure**.

## When to apply

- User asks for "gdoc compatible", "copy to GDoc", "paste into Google Docs", or "tables not copying".
- User wants a doc that "supports gdoc formats" or "formatted for Google Docs".
- Creating new MD/HTML docs that may be pasted into a GDoc (e.g. TDD, data mapping, collaboration docs).

## Two output options

| Need                          | Use                                                                                                                                    |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| **Single source, best paste** | Produce an **HTML** version with real `<table>`, flat sections, and minimal layout CSS so copy-paste from browser preserves structure. |
| **MD only**                   | Write **Markdown** with strict table syntax and clear heading hierarchy; paste from MD into GDoc is less reliable for tables.          |

Prefer **HTML for gdoc paste** when the doc has multiple tables or must match a GDoc style (e.g. "Expected format" tables, mapping tables).

---

## Rules for gdoc-friendly structure

### 1. Tables

- **HTML:** Use real `<table>`, `<thead>`, `<tbody>`, `<tr>`, `<th>`, `<td>`. No flex/div-based "tables" — they do not paste as tables.
- **One table per logical block.** Avoid wrapping two tables in a single flex container; use sequential blocks: heading → table → text → table.
- **Column headers:** Put headers in `<th>` in the first row so GDoc recognizes table structure.
- **Markdown:** Use standard pipe tables with header separator row. When pasting MD into GDoc, table structure may still break; offer to generate an HTML companion.

### 2. Headings

- **HTML:** Use `<h1>` for title, `<h2>` for main sections (e.g. "1. Problem", "2. Solution"), `<h3>` for subsections (e.g. "2.1 How it works"). GDoc preserves heading levels on paste.
- **Markdown:** Use `#`, `##`, `###` consistently. No skip levels (e.g. don’t go from `##` to `####`).

### 3. Section layout (HTML)

- **Flat, sequential structure.** Section = heading + paragraphs + table(s). No nested "diagram" wrappers (e.g. side-by-side source/target in one flex box) if the content will be copied — split into label paragraph, then table, then next label, then table.
- **Labels above tables:** Use `<p class="table-label">` or a bold paragraph (e.g. **Outlook Calendar: Meetings**) so the label pastes as normal text, then the table follows.

### 4. Code and lists

- **Code:** Use `<code>...</code>` (HTML) or backticks (MD) for field names, formats, and examples (e.g. `external_ref_id`, `ical://{uid}#{start_time_iso}`).
- **Lists:** Use `<ul>`/`<ol>` (HTML) or `-`/`1.` (MD) so they paste as bullet/numbered lists.

### 5. Styling (HTML only)

- Keep CSS simple: `border-collapse: collapse`, `border: 1px solid #ccc` on table cells, `th { background: #f5f5f5 }`. Avoid complex flex/grid that might be stripped on paste.
- Max-width and padding are fine; they don’t affect clipboard.

---

## Workflow: creating a gdoc-friendly doc

1. **Clarify output:** MD only, or MD + HTML for paste?
2. **If HTML (recommended for tables):**
   - Create a single `.html` file (or match existing pattern, e.g. `meeting-dedup-solution-draft.html`).
   - Use the structure above: flat sections, real tables, clear h1/h2/h3, code in `<code>`.
   - Optional: keep an `.md` as source and generate HTML from it, or maintain both in parallel.
3. **If MD only:** Use strict table syntax and consistent headings; warn that pasting tables into GDoc may require "Paste without formatting" or section-by-section paste.
4. **Tell the user:** "Open the HTML in a browser and copy the section (or full doc) into Google Docs for correct table/heading paste."

---

## Quick reference: HTML table pattern

```html
<h2 id="section-id">2. Section title</h2>
<p>Optional intro text.</p>
<table>
  <thead>
    <tr>
      <th>Column A</th>
      <th>Column B</th>
      <th>Column C</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>Cell</td>
      <td>Cell</td>
      <td>Cell</td>
    </tr>
  </tbody>
</table>
```

Use one such block per logical table; separate tables with a heading or paragraph so GDoc doesn’t merge them.

---

## Examples in this repo

- **TDD / data mapping style:** `adaas-connectors/airdrop-outlook-calendar/docs/tdd-brainstorm.html`, `docs/data-mapping-diagram.html` — flat sections, real tables, outline TOC.
- **Collaboration doc with tables:** `meeting_participants/meeting-dedup-solution-draft.html` — section 2.2 "Expected format" and other tables copy correctly into GDoc when pasted from the browser.
