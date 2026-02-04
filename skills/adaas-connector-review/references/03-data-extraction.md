# Data Extraction Phase Review

## Overview

The data extraction phase retrieves items from the external system and uploads them to DevRev. This is the core phase of the extraction process, handling pagination, state management, rate limiting, and timeouts.

**Triggering Events:**

- `ExtractorEventType.DataExtractionStart` - Initial start
- `ExtractorEventType.DataExtractionContinue` - Resume after timeout/delay

**Response Events:**

- `ExtractorEventType.DataExtractionDone` - Extraction complete
- `ExtractorEventType.DataExtractionProgress` - Timeout reached, needs continuation
- `ExtractorEventType.DataExtractionDelayed` - Rate limited, needs backoff
- `ExtractorEventType.DataExtractionError` - Fatal error occurred

---

## File: `data-extraction.ts`

### MUST Follow

- [ ] **Uses `processTask<ExtractorState>` from SDK** - Standard worker pattern
- [ ] **Initializes repos with `adapter.initializeRepos(repos)`** - Before any extraction
- [ ] **Repo `itemType` matches metadata record_type** - Case-sensitive match
- [ ] **Normalization function provided per repo** - If using normalize option
- [ ] **Emits exactly ONE message per invocation** - Done, Progress, Delay, or Error
- [ ] **Progress events have NO parameters** - **CRITICAL**: `emit(ExtractionDataProgress)` only!
- [ ] **Implements `onTimeout` callback** - Must emit Progress event (no params)
- [ ] **Checks `adapter.isTimeout` in loops** - Exit gracefully before hard timeout
- [ ] **Handles `EXTRACTION_DATA_CONTINUE` event** - Resume from saved state
- [ ] **State tracks extraction progress** - Pagination cursors, completion flags
- [ ] **Data includes required fields** - `id`, `created_date`, `modified_date`
- [ ] **Work items include `item_url_field`** - URL to item in external system
- [ ] **No manual data batching** - SDK handles batching internally
- [ ] **4xx errors emit error with message** - Client errors are non-retryable, emit error immediately (exceptions need comment explaining why)
- [ ] **5xx errors retry with warn log** - Server errors are retryable, log warning and retry (exceptions need comment explaining why)

### SHOULD Follow

- [ ] **Handles rate limiting gracefully** - Emits Delay event with backoff time
- [ ] **Uses pagination with reasonable batch sizes** - Typically 50-100 items
- [ ] **Handles `extract_from` and `reset_extract_from` parameters** - Required for TIME_SCOPED_SYNCS
- [ ] **Tracks last successful sync timestamp in state** - Updates after successful extraction
- [ ] **Distinguishes initial vs incremental sync** - Different extraction logic
- [ ] **Saves state before timeout** - Via `adapter.state` updates
- [ ] **Handles empty results gracefully** - No errors on empty pages
- [ ] **External API errors logged clearly** - Show error code, message, and endpoint that failed
- [ ] **No PII in logs** - Never log user emails, names, or sensitive data

### Nice-to-Have

- [ ] Configurable batch sizes
- [ ] Extraction statistics/metrics
- [ ] Parallel extraction of independent item types

---

## TIME_SCOPED_SYNCS Implementation

### Overview

TIME_SCOPED_SYNCS capability enables custom timestamp control for data extraction. When enabled in manifest, the extraction logic must handle two optional parameters:

- **`extract_from`**: RFC3339 timestamp for extraction starting point (both initial and incremental)
- **`reset_extract_from`**: Boolean flag (incremental only) to control re-extraction behavior

### Implementation Pattern

**Complete Example:**

```typescript
import { EventType, SyncMode } from "@devrev/ts-adaas";

async function extractData(adapter: Adapter) {
  // Extract time-scoped parameters
  const { reset_extract_from, extract_from } =
    adapter.event.payload.event_context;
  const mode = adapter.event.payload.event_context.mode;

  let startTimestamp: string | undefined;

  // Determine starting timestamp based on mode and parameters
  if (mode === SyncMode.INITIAL) {
    // Initial sync: Use extract_from if provided
    startTimestamp = extract_from;
    if (startTimestamp) {
      console.log(`Initial sync from timestamp: ${startTimestamp}`);
    } else {
      console.log("Initial sync: extracting all data");
    }
  } else if (mode === SyncMode.INCREMENTAL) {
    // Incremental sync: Check reset flag
    if (reset_extract_from) {
      // Reset requested: Use extract_from or extract all
      startTimestamp = extract_from;
      console.log(
        `Reset flag true. Starting from: ${startTimestamp || "beginning"}`
      );
    } else {
      // Normal incremental: Use last successful sync time
      startTimestamp = adapter.state.lastSuccessfulSyncStarted;
      console.log(`Incremental sync from: ${startTimestamp}`);
    }
  }

  // Fetch data with timestamp filter
  const items = startTimestamp
    ? await client.getItemsModifiedSince(startTimestamp)
    : await client.getAllItems();

  // Emit items...
  for (const item of items) {
    await adapter.emit(transformItem(item));
  }
}
```

### When to Reset Extraction Time

The `reset_extract_from` flag enables these scenarios:

1. **Manual Re-sync**: User wants to re-extract data from specific point
2. **Error Recovery**: Previous sync failed and needs restart from known-good timestamp
3. **Schema Changes**: External system changed and requires re-extraction
4. **Data Correction**: Issues found in previously synced data

### Timestamp Format

All timestamps must be **RFC3339 format**:

- Format: `YYYY-MM-DDTHH:mm:ss.sssZ`
- Example: `2024-01-15T10:30:00.000Z`
- Always UTC timezone

### State Management

Update `lastSuccessfulSyncStarted` after successful extraction:

```typescript
// After successful extraction phase
adapter.state.lastSuccessfulSyncStarted = new Date().toISOString();
```

### API Integration Examples

Different APIs have different timestamp parameter names:

**REST with query parameter:**

```typescript
const params = startTimestamp ? { updated_since: startTimestamp } : {};
const response = await client.get("/api/items", { params });
```

**GraphQL with variable:**

```typescript
const query = `
  query GetItems($updatedSince: DateTime) {
    items(updatedSince: $updatedSince) { id, title }
  }
`;
const variables = startTimestamp ? { updatedSince: startTimestamp } : {};
```

---

## File: `extraction/index.ts`

### MUST Follow

- [ ] **Defines `ExtractorState` interface** - All state fields typed
- [ ] **Initial state has all required fields** - With default values
- [ ] **Calls `spawn<ExtractorState>()` correctly** - With all required parameters
- [ ] **Provides `initialDomainMapping` to spawn()** - **CRITICAL**: Required parameter
- [ ] **Routes to correct workers** - Based on event type

### SHOULD Follow

- [ ] **State is serializable** - No functions, circular refs, or Map/Set
- [ ] **State size is reasonable** - Under 1MB limit
- [ ] **Worker paths are correct** - Point to actual worker files

---

## State Management Requirements

### MUST Follow

- [ ] **State persists pagination position** - Cursor, page number, or offset
- [ ] **State tracks completion per item type** - `{ completed: boolean }`
- [ ] **State survives JSON serialization** - Test with `JSON.parse(JSON.stringify(state))`
- [ ] **State under 1MB** - Approximately 500,000 characters

### SHOULD Follow

- [ ] **State includes `lastSuccessfulSyncStarted`** - For incremental sync
- [ ] **State tracks items extracted** - For progress reporting
- [ ] **State is minimal** - Don't store extracted data, only cursors

---

## Review Questions

```
Q1: Extraction Completeness
    - Are ALL item types from metadata being extracted?
    - Is extraction order correct (dependencies first)?
    - Are nested items handled (comments on issues)?

Q2: Pagination Handling
    - Is pagination cursor/offset stored in state?
    - Does extraction resume correctly after timeout?
    - Is there a maximum items per page limit?
    - How is end of data detected?

Q3: Incremental Sync Support
    - Is lastSuccessfulSyncStarted used?
    - Does extraction filter by modified_date?
    - Are deleted items handled?

Q7: Is TIME_SCOPED_SYNCS properly implemented?
    - Does it check `reset_extract_from` flag in incremental mode?
    - Does it use `extract_from` when provided?
    - Does it fall back to `lastSuccessfulSyncStarted` for normal incremental?
    - Are timestamps in RFC3339 format?

Q4: Rate Limiting
    - Is rate limit response detected (429 status)?
    - Is Retry-After header respected?
    - Is ExtractionDataDelay emitted with delay?

Q5: Timeout Handling
    - Is onTimeout implemented?
    - Is state saved before emitting Progress?
    - Will extraction resume from correct point?

Q6: Data Quality
    - Are all required fields present?
    - Is data normalized correctly?
    - Are null values handled (not empty strings)?
```

---

## Data Normalization Rules

### Required Fields (Top Level)

```typescript
{
  id: string,           // Unique ID in external system
  created_date: string, // RFC3339 timestamp
  modified_date: string // RFC3339 timestamp
}
```

### Data Fields (In `data` Object)

```typescript
{
  id: "123",
  created_date: "2024-01-15T10:30:00Z",
  modified_date: "2024-01-15T10:30:00Z",
  data: {
    title: "Issue title",
    description: "Details...",
    owner: "user-456",  // Reference as string
    item_url_field: "https://external.com/issue/123"  // For work items
  }
}
```

### Field Format Requirements

| Data Type | Correct Format           | Wrong Format                |
| --------- | ------------------------ | --------------------------- |
| Null      | `null` or omit field     | `""`, `-1`, `"null"`        |
| Timestamp | `"2024-01-15T10:30:00Z"` | `1705315800`, `"Jan 15"`    |
| Date      | `"2024-01-15"`           | `"15/01/2024"`, `"January"` |
| Reference | `"user-123"`             | `123`, `{ id: "123" }`      |
| Number    | `42`                     | `"42"`                      |
| Array     | `["a", "b"]`             | `"a,b"`                     |

---

## Common Anti-Patterns

### 1. No State Persistence for Pagination

```typescript
// BAD - Pagination lost on timeout
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    let page = 1; // Local variable lost on restart!
    while (hasMore) {
      const items = await client.getItems(page++);
      await adapter.getRepo("items")?.push(items);
    }
  },
});

// GOOD - Pagination in state
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    let page = adapter.state.currentPage || 1;
    while (hasMore) {
      const items = await client.getItems(page);
      await adapter.getRepo("items")?.push(items);
      adapter.state.currentPage = ++page; // Saved on timeout
    }
  },
});
```

### 2. Missing Timeout Handler

```typescript
// BAD - No onTimeout
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    // Long extraction...
    await adapter.emit(ExtractorEventType.DataExtractionDone);
  },
  // Missing onTimeout!
});

// GOOD - Proper timeout handling
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.DataExtractionDone);
  },
  onTimeout: async ({ adapter }) => {
    // CRITICAL: Progress events must have NO parameters!
    await adapter.emit(ExtractorEventType.DataExtractionProgress);
  },
});
```

### 2b. Progress Events with Parameters (CRITICAL)

```typescript
// BAD - Passing data to progress event
onTimeout: async ({ adapter }) => {
  await adapter.emit(ExtractorEventType.DataExtractionProgress, {
    progress: 50, // WRONG!
    itemsProcessed: 100, // WRONG!
  });
};

// GOOD - Progress events have NO parameters
onTimeout: async ({ adapter }) => {
  await adapter.emit(ExtractorEventType.DataExtractionProgress); // No params!
};
```

### 2c. Not Checking adapter.isTimeout

```typescript
// BAD - Ignores timeout signal
while (hasMoreData) {
  const items = await fetchPage(page++);
  await adapter.getRepo("items")?.push(items);
  // Will be forcefully terminated at hard timeout!
}

// GOOD - Check timeout in loops
while (hasMoreData && !adapter.isTimeout) {
  const items = await fetchPage(page++);
  await adapter.getRepo("items")?.push(items);
  adapter.state.page = page; // Save progress
}
// Will exit gracefully and trigger onTimeout
```

### 3. Multiple Event Emissions

```typescript
// BAD - Multiple emissions
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    for (const type of itemTypes) {
      const items = await extract(type);
      await adapter.emit(ExtractorEventType.DataExtractionProgress); // WRONG!
    }
    await adapter.emit(ExtractorEventType.DataExtractionDone); // Multiple!
  },
});

// GOOD - Single emission at end
processTask<ExtractorState>({
  task: async ({ adapter }) => {
    for (const type of itemTypes) {
      const items = await extract(type);
    }
    await adapter.emit(ExtractorEventType.DataExtractionDone); // Once
  },
});
```

### 4. Ignoring Rate Limits

```typescript
// BAD - No rate limit handling
async function fetchItems() {
  try {
    return await client.get("/items");
  } catch (error) {
    throw error; // 429 not handled!
  }
}

// GOOD - Proper rate limit detection
async function fetchItems() {
  try {
    return await client.get("/items");
  } catch (error) {
    if (error.response?.status === 429) {
      const retryAfter = error.response.headers["retry-after"] || 60;
      throw new RateLimitError(retryAfter);
    }
    throw error;
  }
}

// In worker:
try {
  await extractItems();
} catch (error) {
  if (error instanceof RateLimitError) {
    await adapter.emit(ExtractorEventType.DataExtractionDelay, {
      delay: String(error.retryAfter),
    });
    return;
  }
  throw error;
}
```

### 5. Wrong Data Format

```typescript
// BAD - Invalid normalized data
function normalizeIssue(item) {
  return {
    id: item.id,
    created_date: item.createdAt, // Wrong format if timestamp
    modified_date: item.updatedAt,
    data: {
      title: item.title,
      owner: item.owner.id, // If owner is object, extract ID
      priority: String(item.priority), // Numbers should stay numbers
      tags: item.tags.join(","), // Arrays should stay arrays
    },
  };
}

// GOOD - Proper normalization
function normalizeIssue(item) {
  return {
    id: String(item.id),
    created_date: new Date(item.createdAt).toISOString(), // RFC3339
    modified_date: new Date(item.updatedAt).toISOString(),
    data: {
      title: item.title || null, // Null, not empty string
      owner: String(item.owner?.id || null),
      priority: item.priority, // Keep as number
      tags: item.tags || [], // Keep as array
      item_url_field: `https://external.com/issue/${item.id}`,
    },
  };
}
```

### 6. No Incremental Sync Support

```typescript
// BAD - Always extracts everything
async function extractIssues() {
  return await client.getAllIssues(); // Full extraction every time
}

// GOOD - Supports incremental sync
async function extractIssues(adapter) {
  const mode = adapter.event.payload.event_context.mode;

  if (mode === SyncMode.INCREMENTAL) {
    const since = adapter.state.lastSuccessfulSyncStarted;
    return await client.getIssuesModifiedSince(since);
  }

  return await client.getAllIssues();
}
```

### 7. Blocking Event Loop

```typescript
// BAD - Blocks event loop, misses soft timeout
processTask({
  task: async ({ adapter }) => {
    const items = hugeDataSet;
    for (let i = 0; i < items.length; i++) {
      // CPU-intensive sync work
      processItem(items[i]); // No await, blocks event loop
    }
  },
});

// GOOD - Async breaks for timeout handling
processTask({
  task: async ({ adapter }) => {
    const items = hugeDataSet;
    for (let i = 0; i < items.length; i++) {
      await processItemAsync(items[i]);

      // Periodic break for event loop
      if (i % 100 === 0) {
        await new Promise((resolve) => setImmediate(resolve));
      }
    }
  },
});
```

### 8. Manual Data Batching (Unnecessary)

```typescript
// BAD - Manual batching (SDK handles this!)
const items = await fetchAllItems();
if (items.length > 1000) {
  const chunks = chunkArray(items, 1000);
  for (const chunk of chunks) {
    await adapter.getRepo("items")?.push(chunk);
  }
} else {
  await adapter.getRepo("items")?.push(items);
}

// GOOD - Let SDK handle batching
const items = await fetchAllItems();
await adapter.getRepo("items")?.push(items); // SDK batches internally
```

### 9. Missing initialDomainMapping

```typescript
// BAD - Missing required parameter
await spawn<ExtractorState>({
  event,
  initialState: initialExtractorState,
  workerPath: file,
  // Missing initialDomainMapping!
});

// GOOD - All required parameters
await spawn<ExtractorState>({
  event,
  initialState: initialExtractorState,
  workerPath: file,
  initialDomainMapping, // Required!
});
```

### 10. Poor Logging Practices

```typescript
// BAD - PII in logs and unclear errors
try {
  const users = await client.getUsers();
  users.forEach((user) => {
    console.log(`Processing user: ${user.email}`); // PII!
    console.log(`User data: ${JSON.stringify(user)}`); // Excessive + PII!
  });
} catch (error) {
  console.log("Error occurred"); // Unclear!
}

// GOOD - No PII, clear errors, logs at critical points
try {
  const users = await client.getUsers();
  console.log(`Fetched ${users.length} users`); // Count only, no PII
} catch (error) {
  console.error(
    `API Error: ${error.response?.status} - ${error.message} at GET /users`
  );
}
```
