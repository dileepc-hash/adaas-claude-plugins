# External Sync Units Extraction Phase Review

## Overview

External sync units extraction identifies the boundaries of data that can be synced independently. This allows users to select specific projects, repositories, or workspaces to sync rather than syncing everything.

**When Used:** Initial sync only (not incremental)
**Triggering Event:** `ExtractorEventType.ExternalSyncUnitsStart`
**Success Event:** `ExtractorEventType.ExternalSyncUnitsDone`
**Error Event:** `ExtractorEventType.ExternalSyncUnitsError`

---

## Sync Unit Concepts

A **sync unit** is a self-encompassing unit of data from the external system:

| External System | Example Sync Units             |
| --------------- | ------------------------------ |
| Jira            | Projects                       |
| GitHub          | Repositories                   |
| Salesforce      | Accounts                       |
| Zendesk         | Single instance (no sub-units) |
| Slack           | Channels                       |
| Linear          | Teams/Projects                 |

---

## File: `external-sync-units-extraction.ts`

### MUST Follow

- [ ] **Uses `processTask` from SDK** - Standard worker pattern
- [ ] **Initializes repo for `external_sync_units`** - Required item type
- [ ] **Returns `ExternalSyncUnit[]` format** - With required fields
- [ ] **Emits exactly ONE message** - Done or Error
- [ ] **Required fields present** - `id`, `name`
- [ ] **4xx errors emit error with message** - Client errors are non-retryable, emit error immediately (exceptions need comment explaining why)
- [ ] **5xx errors emit error with message** - Server errors emit error (exceptions need comment explaining why)
- [ ] **Missing/special sync unit handling justified** - Any special handling for missing or inaccessible sync units must have a comment explaining why

### SHOULD Follow

- [ ] **Fetches sync units from API** - Not hardcoded
- [ ] **Includes useful metadata** - `description`, `item_count`, `item_type`
- [ ] **Implements `onTimeout` callback** - For long lists
- [ ] **Handles pagination** - If many sync units exist

### Nice-to-Have

- [ ] Sorting by name or size
- [ ] Filtering inactive/archived units
- [ ] Additional context (owner, last updated)

---

## ExternalSyncUnit Interface

```typescript
interface ExternalSyncUnit {
  id: string; // REQUIRED: Unique identifier
  name: string; // REQUIRED: Display name
  description?: string; // Optional: Additional context
  item_count?: number; // Optional: Number of items in unit
  item_type?: string; // Optional: Type of items
}
```

---

## Review Questions

```
Q1: Sync Unit Definition
    - What is the natural sync unit for this external system?
    - Can users sync partial data or only everything?
    - Are sync units hierarchical (org > team > project)?

Q2: Data Completeness
    - Are ALL available sync units returned?
    - Are inactive/archived units included or filtered?
    - Is pagination handled for systems with many units?

Q3: User Experience
    - Is the `name` human-readable?
    - Is `description` helpful for selection?
    - Does `item_count` help users gauge sync size?

Q4: Edge Cases
    - What if user has no accessible sync units?
    - What if sync unit is empty?
    - What if sync unit name contains special characters?
```

---

## Implementation Example

```typescript
import {
  ExtractorEventType,
  processTask,
  ExternalSyncUnit,
} from "@devrev/ts-adaas";
import { HttpClient } from "../../external-system/http-client";
import { normalizeProject } from "../../external-system/data-normalization";

const repos = [{ itemType: "external_sync_units" }];

processTask({
  task: async ({ adapter }) => {
    adapter.initializeRepos(repos);

    const client = new HttpClient(adapter.event);
    const projects = await client.getProjects();

    const syncUnits: ExternalSyncUnit[] = projects.map((project) => ({
      id: project.id,
      name: project.name,
      description: project.description,
      item_count: project.issueCount,
      item_type: "project",
    }));

    await adapter.getRepo("external_sync_units")?.push(syncUnits);
    await adapter.emit(ExtractorEventType.ExternalSyncUnitsDone);
  },
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExternalSyncUnitsError, {
      error: { message: "Timeout extracting sync units" },
    });
  },
});
```

---

## Common Anti-Patterns

### 1. Hardcoded Sync Units

```typescript
// BAD - Hardcoded values
const syncUnits = [{ id: "1", name: "Default Project" }];

// GOOD - Fetched from API
const projects = await client.getProjects();
const syncUnits = projects.map((p) => ({
  id: p.id,
  name: p.name,
}));
```

### 2. Missing Required Fields

```typescript
// BAD - Missing name
const syncUnits = projects.map((p) => ({
  id: p.id,
  // name is required!
}));

// GOOD - All required fields
const syncUnits = projects.map((p) => ({
  id: String(p.id), // Ensure string
  name: p.name || `Project ${p.id}`, // Always have a name
}));
```

### 3. No Pagination for Large Lists

```typescript
// BAD - Only first page
const projects = await client.getProjects(); // May be paginated!

// GOOD - Get all pages
async function getAllProjects() {
  const allProjects = [];
  let page = 1;
  let hasMore = true;

  while (hasMore) {
    const response = await client.getProjects(page);
    allProjects.push(...response.data);
    hasMore = response.hasNextPage;
    page++;
  }

  return allProjects;
}
```

### 4. Including Inaccessible Units

```typescript
// BAD - Returns units user can't access
const projects = await client.getAllProjects(); // Includes others' private projects

// GOOD - Only accessible units
const projects = await client.getMyProjects(); // Only user's projects
```

### 5. Non-String IDs

```typescript
// BAD - Numeric ID
const syncUnits = projects.map((p) => ({
  id: p.id, // If p.id is number: 123
  name: p.name,
}));

// GOOD - String ID
const syncUnits = projects.map((p) => ({
  id: String(p.id), // "123"
  name: p.name,
}));
```

---

## When Sync Units Don't Apply

Some external systems don't have natural sub-divisions:

```typescript
// For systems like Zendesk with single instance
const syncUnits = [
  {
    id: "default",
    name: "Zendesk Instance",
    description: "All tickets and articles",
  },
];
```

This is valid - users just see one option to sync.
