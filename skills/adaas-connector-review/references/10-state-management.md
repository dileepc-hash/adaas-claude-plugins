# State Management Review

## Overview

State persists pagination positions, extraction progress, and sync metadata across invocations.

| Property   | Details                      |
| ---------- | ---------------------------- |
| Format     | JSON serializable object     |
| Size limit | < 1 MB (~500,000 characters) |
| Access     | Via `adapter.state`          |

---

## MUST Follow

- [ ] **State interface defined with JSDoc** - TypeScript interface with documented fields
- [ ] **Initial state has all fields** - With default values
- [ ] **State is JSON serializable** - No functions, Maps, Sets, circular refs
- [ ] **State under 1MB** - Check with `JSON.stringify(state).length`
- [ ] **Pagination state tracked** - Cursors, page numbers, offsets

## SHOULD Follow

- [ ] **Completion flags per item type** - `{ itemType: { completed: boolean } }`
- [ ] **`lastSuccessfulSyncStarted` tracked** - For incremental sync (TIME_SCOPED_SYNCS)
- [ ] **Minimal state** - Only cursors/positions, not extracted data

---

## lastSuccessfulSyncStarted Field

**Purpose:** Tracks when the last successful extraction completed, used for TIME_SCOPED_SYNCS capability.

**Format:** RFC3339 timestamp string (e.g., `"2024-01-15T10:30:00.000Z"`)

**When to Update:** After successful completion of data extraction phase

**Usage:**
```typescript
interface ExtractorState {
  // ... other fields
  /** Timestamp of last successful sync for incremental mode */
  lastSuccessfulSyncStarted?: string; // RFC3339 format
}

// Update after successful extraction
adapter.state.lastSuccessfulSyncStarted = new Date().toISOString();
```

**Important:** Only update this field after data extraction fully succeeds. Do not update if extraction fails or times out, as this would skip data in next incremental sync.

**TIME_SCOPED_SYNCS Integration:**
- Used when `reset_extract_from` is `false` or absent
- Ignored when `reset_extract_from` is `true`
- Should always be set after initial sync to enable incremental syncs

---

## State Interface Example

```typescript
interface ExtractorState {
  /** Issue extraction state */
  issues: { completed: boolean; page?: number; cursor?: string };
  /** User extraction state */
  users: { completed: boolean; page?: number };
  /** Comment extraction state - parentIndex tracks which issue */
  comments: { completed: boolean; parentIndex?: number };
  /** Timestamp of last successful sync for incremental mode */
  lastSuccessfulSyncStarted?: string; // RFC3339 format
}

const initialExtractorState: ExtractorState = {
  issues: { completed: false },
  users: { completed: false },
  comments: { completed: false },
};
```

---

## Common Anti-Patterns

| Anti-Pattern              | Problem                      | Fix                                           |
| ------------------------- | ---------------------------- | --------------------------------------------- |
| Local pagination variable | Lost on timeout              | Use `adapter.state[type].page`                |
| Non-serializable state    | `Map`, `Set`, functions fail | Use plain objects                             |
| Storing extracted data    | Exceeds 1MB limit            | Store only cursors/IDs                        |
| Not checking completion   | Re-extracts completed types  | `if (adapter.state[type].completed) continue` |
| Completion set too early  | Before all pages extracted   | Set after `while (hasMore)` loop              |
| Unbounded state growth    | `allProcessedIds` array      | Store only `lastProcessedId`                  |

### Nested Pagination

```typescript
// Track position in both parent and child
const startIndex = adapter.state.comments.parentIndex || 0;
for (let i = startIndex; i < issues.length; i++) {
  const comments = await getComments(issues[i].id);
  await adapter.getRepo("comments")?.push(comments);
  adapter.state.comments.parentIndex = i + 1; // Track position
}
```

---

## Review Questions

```
Q1: Is pagination position stored in state (not local variable)?
Q2: Does state survive JSON.parse(JSON.stringify())?
Q3: Is state size under 1MB (no extracted data stored)?
Q4: Is completion set only after ALL pages extracted?
Q5: Is lastSuccessfulSyncStarted tracked for incremental sync?
Q6: Are nested extractions tracked (parent + child position)?
```
