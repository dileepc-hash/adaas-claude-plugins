# Marketplace Description Template

DevRev marketplace descriptions must follow this structure. Canonical source: `.claude/skills/marketplace-content/references/descsription.md` (or <https://github.com/devrev/marketplace-items/blob/main/description.md>).

## Format Rules (from mp-review.md)

- **Markdown-formatted** text
- **No level 1 (`#`) heading**
- **Do not start with a title or heading**
- **No inline images**
- **Features:** bullet list where each feature's description is on a **new line** (see below)

## Official Template Structure

```markdown
<!-- Do not start the page with a title or a heading. -->

Brief description of the snap-in and how it works.

## Features

<!-- List about 2-5 features. -->

- **Feature**

  Description of the feature.

- **Feature**

  Description of the feature.
```

## Feature Bullet Format

**Correct:**

```markdown
- **Calendar sync**
  Automatically syncs calendar events from Outlook into DevRev as meetings.

- **Meeting context**
  Attaches attendee lists, links, and recordings to work items.
```

**Incorrect (inline descriptions):**

```markdown
- **Calendar sync** - Syncs events (avoid inline)
- **Meeting context** - Attaches attendee lists (avoid inline)
```

## Example: Calendar Connector

```markdown
Sync Microsoft Outlook Calendar events and meetings into DevRev. Automatically creates meetings, links them to work items, and keeps your team's schedule in one place.

## Features

- **Automatic event sync**

  Imports calendar events as DevRev meetings with organizers, attendees, and times.

- **Internal vs external meetings**

  Identifies internal participants using configurable domains.

- **Meeting artifacts**

  Links meeting recordings and transcripts when available from Microsoft Teams.
```

## Example: Bidirectional Connector

```markdown
Two-way sync between Azure Boards and DevRev. Push work items to Azure DevOps and pull updates back into DevRev for a unified view of engineering work.

## Features

- **Extraction**

  Syncs work items, sprints, and areas from Azure Boards into DevRev.

- **Loading**

  Create and update work items in Azure Boards from DevRev.

- **Custom field mapping**

  Map Azure Board fields to DevRev custom fields.
```
