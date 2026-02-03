# Data Loading Phase Review

## Overview

The data loading phase creates or updates items in the external system based on changes made in DevRev. This enables 2-way sync functionality.

**Triggering Events:**

- `LoaderEventType.StartLoadingData` - Initial start
- `LoaderEventType.ContinueLoadingData` - Resume after timeout

**Response Events:**

- `LoaderEventType.DataLoadingDone` - Loading complete
- `LoaderEventType.DataLoadingProgress` - Timeout reached
- `LoaderEventType.DataLoadingError` - Fatal error

---

## File: `load-data.ts`

### MUST Follow

- [ ] **Uses `processTask<LoaderState>` from SDK** - Standard worker pattern
- [ ] **Uses `adapter.loadItemTypes()`** - SDK loading helper
- [ ] **Provides `create` and `update` functions** - For each item type
- [ ] **Returns `id` from create/update** - External system ID
- [ ] **Handles rate limiting** - Returns error with delay
- [ ] **Emits exactly ONE message** - Done or Progress
- [ ] **4xx errors return error with message** - Client errors are non-retryable (exceptions need comment explaining why)
- [ ] **5xx errors retry with warn log** - Server errors are retryable (exceptions need comment explaining why)
- [ ] **Implements `onTimeout` callback** - Must emit Progress event (NO params!)
- [ ] **Progress events have NO parameters** - **CRITICAL**: Only Done events get reports
- [ ] **Passes `reports` and `processed_files`** - ONLY in DataLoadingDone event

### SHOULD Follow

- [ ] **Orders item types by dependency** - Parents before children
- [ ] **Handles partial failures** - Log and continue
- [ ] **Returns `modifiedDate`** - For tracking
- [ ] **Uses object mappers** - To track ID relationships

### Nice-to-Have

- [ ] Batch operations for efficiency
- [ ] Idempotency keys for safety
- [ ] Dry-run mode for testing

---

## Create/Update Function Signature

```typescript
interface LoaderCreateResult {
  id: string; // REQUIRED: External system ID
  modifiedDate?: string; // Optional: RFC3339 timestamp
  error?: LoaderError; // Optional: If create failed
}

interface LoaderUpdateResult {
  id: string; // REQUIRED: External system ID
  modifiedDate?: string; // Optional: RFC3339 timestamp
  error?: LoaderError; // Optional: If update failed
}

interface LoaderError {
  message: string;
  retryAfter?: number; // For rate limiting
}
```

---

## Review Questions

```
Q1: Record Type Coverage
    - Are all loadable record types from metadata handled?
    - Is the loading order correct (users before issues)?
    - Are nested items handled (comments with parent)?

Q2: Create Function
    - Does it denormalize DevRev data to external format?
    - Does it return the created item's external ID?
    - Are required fields validated before API call?
    - Is the created item retrievable via returned ID?

Q3: Update Function
    - Does it handle partial updates?
    - Does it preserve fields not in the update?
    - Does it handle version conflicts (optimistic locking)?
    - What happens if item doesn't exist?

Q4: ID Mapping
    - Are sync mapper records used correctly?
    - Is getByExternalId used to find existing items?
    - Is getByTargetId used to get external IDs?
    - Are new mappings created after create?

Q5: Error Handling
    - Are rate limits detected and returned?
    - Are transient errors retried?
    - Are permanent errors logged and skipped?
    - Does sync continue after individual failures?

Q6: Data Integrity
    - Is data denormalized correctly?
    - Are references resolved to external IDs?
    - Are enum values mapped correctly?
    - Are timestamps formatted correctly?
```

---

## Implementation Example

```typescript
import {
  LoaderEventType,
  processTask,
  LoaderRecordAction,
} from "@devrev/ts-adaas";
import { HttpClient } from "../../external-system/http-client";
import { denormalizeTodo } from "../../external-system/data-denormalization";

processTask<LoaderState>({
  task: async ({ adapter }) => {
    const client = new HttpClient(adapter.event);

    const { reports, processed_files } = await adapter.loadItemTypes({
      itemTypesToLoad: [
        {
          itemType: "todos",
          create: async (record) => createTodo(client, adapter, record),
          update: async (record) => updateTodo(client, adapter, record),
        },
      ],
    });

    // Done events CAN have reports
    await adapter.emit(LoaderEventType.DataLoadingDone, {
      reports,
      processed_files,
    });
  },
  onTimeout: async ({ adapter }) => {
    // CRITICAL: Progress events must have NO parameters!
    await adapter.emit(LoaderEventType.DataLoadingProgress);
  },
});

async function createTodo(client, adapter, record) {
  try {
    const externalData = denormalizeTodo(record.data);
    const result = await client.createTodo(externalData);

    return {
      id: result.id,
      modifiedDate: result.updatedAt,
    };
  } catch (error) {
    if (error.response?.status === 429) {
      return {
        id: "",
        error: {
          message: "Rate limited",
          retryAfter: parseInt(error.response.headers["retry-after"] || "60"),
        },
      };
    }

    return {
      id: "",
      error: { message: error.message },
    };
  }
}

async function updateTodo(client, adapter, record) {
  try {
    // Get external ID from sync mapper
    const externalId = await adapter.objectMapper.getByTargetId(record.id);

    if (!externalId) {
      return {
        id: "",
        error: { message: `No mapping found for ${record.id}` },
      };
    }

    const externalData = denormalizeTodo(record.data);
    const result = await client.updateTodo(externalId, externalData);

    return {
      id: result.id,
      modifiedDate: result.updatedAt,
    };
  } catch (error) {
    return {
      id: record.id,
      error: { message: error.message },
    };
  }
}
```

---

## Common Anti-Patterns

### 1. Progress Events with Parameters (CRITICAL!)

```typescript
// BAD - Passing data to progress event
onTimeout: async ({ adapter }) => {
  await adapter.emit(LoaderEventType.DataLoadingProgress, {
    reports: adapter.reports, // WRONG!
    processed_files: adapter.processedFiles, // WRONG!
  });
};

// GOOD - Progress events have NO parameters
onTimeout: async ({ adapter }) => {
  await adapter.emit(LoaderEventType.DataLoadingProgress); // No params!
};
```

### 2. Missing Reports in Done Event

```typescript
// BAD - No reports in Done
await adapter.emit(LoaderEventType.DataLoadingDone);

// GOOD - Include reports in Done (only Done, not Progress!)
const { reports, processed_files } = await adapter.loadItemTypes({...});
await adapter.emit(LoaderEventType.DataLoadingDone, {
  reports,
  processed_files
});
```

### 2. Wrong Item Type Order

```typescript
// BAD - Issues before users (issues reference users!)
itemTypesToLoad: [
  { itemType: "issues", create: createIssue, update: updateIssue },
  { itemType: "users", create: createUser, update: updateUser },
];

// GOOD - Users first
itemTypesToLoad: [
  { itemType: "users", create: createUser, update: updateUser },
  { itemType: "issues", create: createIssue, update: updateIssue },
];
```

### 3. Not Using Object Mappers

```typescript
// BAD - Can't find external ID
async function updateTodo(record) {
  // Where's the external ID?
  await client.updateTodo(record.id, data); // record.id is DevRev ID!
}

// GOOD - Use object mapper
async function updateTodo(record, adapter) {
  const externalId = await adapter.objectMapper.getByTargetId(record.id);
  await client.updateTodo(externalId, data);
}
```

### 4. Ignoring Rate Limit Returns

```typescript
// BAD - Error but no retry info
return {
  id: "",
  error: { message: "API error" }, // Lost retry-after info
};

// GOOD - Include retry info
return {
  id: "",
  error: {
    message: "Rate limited",
    retryAfter: 60, // SDK can schedule retry
  },
};
```

### 5. Wrong Denormalization

```typescript
// BAD - Not denormalizing references
function denormalizeTodo(data) {
  return {
    title: data.title,
    owner: data.owner, // This is DevRev ID, not external ID!
  };
}

// GOOD - Resolve references
async function denormalizeTodo(data, adapter) {
  const ownerExternalId = await adapter.objectMapper.getByTargetId(data.owner);
  return {
    title: data.title,
    owner: ownerExternalId,
  };
}
```

### 6. No Error Handling in Create

```typescript
// BAD - Throws on error, stops all loading
async function createTodo(record) {
  const result = await client.createTodo(record.data); // Throws!
  return { id: result.id };
}

// GOOD - Return error, continue loading
async function createTodo(record) {
  try {
    const result = await client.createTodo(record.data);
    return { id: result.id };
  } catch (error) {
    return {
      id: "",
      error: { message: error.message },
    };
  }
}
```

### 7. Treating Update as Replace

```typescript
// BAD - Overwrites all fields
async function updateTodo(record) {
  await client.replaceTodo(id, record.data); // Loses fields not in update
}

// GOOD - Partial update or merge
async function updateTodo(record) {
  const existing = await client.getTodo(id);
  const merged = { ...existing, ...record.data };
  await client.updateTodo(id, merged);
}
```

---

## Denormalization Checklist

| DevRev Format        | External Format | Action                          |
| -------------------- | --------------- | ------------------------------- |
| RFC3339 timestamp    | External format | Convert to external date format |
| DevRev ID reference  | External ID     | Look up via object mapper       |
| DevRev enum value    | External enum   | Map to external enum key        |
| Array of IDs         | External format | Resolve each ID                 |
| Rich text (markdown) | External format | Convert if needed               |
