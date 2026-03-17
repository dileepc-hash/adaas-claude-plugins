---
name: marketplace-content
description: Write marketplace listing content (name, tagline, summary, description) for DevRev connectors. Use when writing or drafting marketplace name, tagline, summary, description, or when the user asks to "write marketplace listing", "draft marketplace content", "create marketplace description" for connectors in adaas-connectors.
argument-hint: [connector-name or path]
allowed-tools: Read, Grep, Glob, WebSearch, mcp_web_fetch
---

# Marketplace Content Writer

Drafts `name`, `tagline`, `summary`, and `description` for DevRev marketplace submissions. Connectors live in `./adaas-connectors/`.

## Workflow

### 1. Identify Connector & Gather Context

**Locate the connector:**

- If user specifies a connector (e.g. `airdrop-outlook-calendar`), use `./adaas-connectors/<connector>/`
- Otherwise list connectors in `./adaas-connectors/` and ask user to choose

**Read these in order:**

| Source   | Path                                                            | Purpose                                                      |
| -------- | --------------------------------------------------------------- | ------------------------------------------------------------ |
| Manifest | `<connector>/manifest.yaml`                                     | `name`, `description`, external system, connection types     |
| EDM      | `<connector>/code/src/**/external_domain_metadata.json`         | Record types, fields, schema (what data the connector syncs) |
| Template | `.claude/skills/marketplace-content/references/descsription.md` | Official marketplace description structure                   |
| KB       | `.cursor/connector-kb/00-index.md`                              | Phase/schema context if needed                               |

**EDM lookup:** Connectors store EDM at different paths. Search for `external_domain_metadata.json` under the connector `code/` directory. Common locations:

- `code/src/functions/external-system/external_domain_metadata.json`
- `code/src/functions/<connector-module>/external_domain_metadata.json`
- `code/src/config/external_domain_metadata.json` (e.g. Gong)

**Description template:** Read the official template from the workspace:

- `.claude/skills/marketplace-content/references/descsription.md` – canonical template with Features structure

### 2. Understand Connector Capabilities

From EDM and manifest, extract:

- **External system:** e.g. Microsoft Outlook, Gong, Freshdesk
- **Data types:** Record types from EDM `record_types` (e.g. users, tasks, enterprise_data, tickets)
- **Direction:** Extraction-only vs bidirectional (check for `loading` in manifest)
- **Auth:** OAuth, Secret, etc.

Use this to drive accurate, specific content.

### 3. Apply Text Field Guidelines

**Applicable to:** `name`, `tagline`, `summary`, `description`.

**Tagline vs summary differentiation:** Before finalizing, confirm tagline and summary are distinct – tagline is shorter and more memorable, uses different wording, and reads as a hook; summary reads as an overview.

Rules from `mp-review.md` and DevRev marketplace standards:

- **No grammar or spelling mistakes**
- **Clear, concise, professional**
- **Appropriate language** – no profanity or unusual wording
- **No abbreviations** – avoid ADaaS, CMS, CX PB, etc. Spell out (e.g. "customer experience platform"). Exceptions: well-known terms like AI.

### 4. Field Definitions & Examples

| Field           | Length / format      | Purpose                                                               |
| --------------- | -------------------- | --------------------------------------------------------------------- |
| **name**        | Short, product-style | Display name in marketplace (e.g. "Outlook Calendar", "Gong AirSync") |
| **tagline**     | One short phrase     | Concise, catchy hook – distinct from summary; must end with a period   |
| **summary**     | 1–2 sentences        | Brief overview of what it does and for whom                           |
| **description** | Markdown, structured | Full listing content (see reference)                                  |

**Name examples:**

- "Outlook Calendar"
- "Google Calendar"
- "Freshdesk Articles"
- "Microsoft Dynamics CRM AirSync"

**Tagline rules:** Must end with a period. Must be a concise, catchy hook – not a restatement of the summary. Keep it short and memorable.

**Tagline examples:**

- "Outlook meetings, synced to DevRev."
- "Gong insights, surfaced in your workspace."
- "Freshdesk articles, ready when you need them."

### 5. Description Structure (Markdown)

**Required:** Follow `.claude/skills/marketplace-content/references/descsription.md` and [references/description-template.md](references/description-template.md).

- Markdown-formatted
- Do **not** start with a title or heading
- Do **not** include inline images
- Features: 2–5 bullets; each feature's description on a **new line** (blank line between bullet and description)

**Feature list format:**

```markdown
- **Feature name**
  Description of the feature on a new line.

- **Another feature**
  Its description on the next line.
```

### 6. Output Format

Provide all four fields in a structured block:

```yaml
name: "<exact name>"
tagline: "<exact tagline>"
summary: "<exact summary>"
description: |
  <full markdown description>
```

Then optionally offer to write this into a file (e.g. `marketplace-listing.yaml` or paste for `devrev marketplace_submissions create`).

## Additional Resources

- **Review rules:** [mp-review.md](../../../mp-review.md) – icon, banner, description, text, external reference guidelines
- **Description template:** [references/description-template.md](references/description-template.md) – structure and examples
- **Connector KB:** [.cursor/connector-kb/00-index.md](../../../.cursor/connector-kb/00-index.md) – phase and schema docs
