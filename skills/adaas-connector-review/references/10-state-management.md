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
- [ ] **`lastSuccessfulSyncStarted` tracked** - For incremental sync
- [ ] **Minimal state** - Only cursors/positions, not extracted data

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
  lastSuccessfulSyncStarted?: string;
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
