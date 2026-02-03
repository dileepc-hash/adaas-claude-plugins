# Attachments Extraction Phase Review

## Overview

The attachments extraction phase retrieves attachment files from the external system and uploads them to DevRev. This phase occurs after data extraction is complete.

**Triggering Events:**

- `ExtractorEventType.AttachmentsExtractionStart` - Initial start
- `ExtractorEventType.AttachmentsExtractionContinue` - Resume after timeout/delay

**Response Events:**

- `ExtractorEventType.AttachmentsExtractionDone` - Extraction complete
- `ExtractorEventType.AttachmentsExtractionProgress` - Timeout reached
- `ExtractorEventType.AttachmentsExtractionDelayed` - Rate limited
- `ExtractorEventType.AttachmentsExtractionError` - Fatal error

---

## SDK Default vs Custom Implementation

The SDK provides a **default implementation** for attachments extraction. If the default behavior (iterating through attachment metadata and uploading from URLs) meets requirements, **no custom implementation is needed**.

### When to Use Custom Implementation

- External system requires authentication for file downloads
- Files need transformation before upload
- Custom rate limiting logic required
- Non-standard URL patterns

---

## File: `attachments-extraction.ts` (If Custom)

### MUST Follow

- [ ] **Uses `processTask` from SDK** - Standard worker pattern
- [ ] **Uses `adapter.streamAttachments()`** - SDK streaming helper
- [ ] **Provides `stream` function** - For downloading attachments
- [ ] **Returns proper stream response** - `{ httpStream }` or `{ error }`
- [ ] **Emits exactly ONE message** - Done, Progress, Delay, or Error
- [ ] **Implements `onTimeout` callback** - For graceful exit
- [ ] **4xx errors emit error with message** - Client errors are non-retryable, emit error immediately (exceptions need comment explaining why)
- [ ] **5xx errors retry with warn log** - Server errors are retryable, log warning and retry (exceptions need comment explaining why)
- [ ] **Define explicit attachment timeout** - Set timeout for attachment downloads
- [ ] **Handle timeout errors by retrying** - Timeout errors are retryable, retry with warn log

### SHOULD Follow

- [ ] **Sets appropriate `batchSize`** - Balance memory vs performance (5-50 typical)
- [ ] **Uses streaming, not buffering** - For large files
- [ ] **Return clear error messages for failed attachments** - avoid any logging on attachment failures
- [ ] **Handles missing attachments gracefully** - Don't fail entire sync

### Nice-to-Have

- [ ] Configurable batch size
- [ ] Progress tracking (X of Y attachments)
- [ ] Retry logic for transient failures

---

## Stream Function Implementation

### MUST Follow

- [ ] **Accepts `item` parameter** - Attachment metadata
- [ ] **Returns `httpStream` or `error`** - Not both
- [ ] **Uses `responseType: 'stream'`** - For axios/fetch
- [ ] **Sets `Accept-Encoding: 'identity'`** - Avoid compression issues

### SHOULD Follow

- [ ] **Catches and reports errors** - With attachment ID
- [ ] **Handles 404 gracefully** - Missing files
- [ ] **Respects rate limits** - 429 responses

---

## Review Questions

```
Q1: Implementation Choice
    - Is default SDK implementation sufficient?
    - If custom, why is it needed?

Q2: Stream Function
    - Does it handle authentication correctly?
    - Does it use streaming (not buffering entire file)?
    - Are errors properly caught and reported?

Q3: Batch Size
    - Is batch size appropriate for file sizes?
    - Consider lambda memory limits
    - Consider external system rate limits

Q4: Error Handling
    - Are individual failures logged but not fatal?
    - Is the sync marked successful even with some failures?
    - Are failed attachments tracked for retry?

Q5: Rate Limiting
    - Is 429 response handled?
    - Is Retry-After header respected?
    - Is ExtractionAttachmentsDelay emitted?
```

---

## Implementation Example

```typescript
import { ExtractorEventType, processTask } from "@devrev/ts-adaas";
import axios from "axios";

processTask({
  task: async ({ adapter }) => {
    const response = await adapter.streamAttachments({
      stream: getFileStream,
      batchSize: 10, // Process 10 files concurrently
    });

    await adapter.emit(ExtractorEventType.ExtractionAttachmentsDone);
  },
  onTimeout: async ({ adapter }) => {
    await adapter.emit(ExtractorEventType.ExtractionAttachmentsProgress);
  },
});

async function getFileStream({ item }) {
  const { id, url } = item;

  try {
    const response = await axios.get(url, {
      responseType: "stream",
      headers: {
        "Accept-Encoding": "identity",
        Authorization: `Bearer ${token}`, // If needed
      },
    });

    return { httpStream: response };
  } catch (error) {
    // Handle rate limiting
    if (axios.isAxiosError(error) && error.response?.status === 429) {
      const retryAfter =
        error.response.headers["retry-after"] || DEFAULT_RETRY_DELAY_SECONDS;
      return { delay: retryAfter };
    }

    // Return error message only - don't log full error object (memory overflow risk)
    return {
      error: { message: `Failed to fetch attachment ${id}: ${error.message}` },
    };
  }
}
```

---

## Common Anti-Patterns

### 1. Buffering Entire File in Memory

```typescript
// BAD - Loads entire file into memory
async function getFileStream({ item }) {
  const response = await axios.get(item.url); // Default: full buffer
  return { httpStream: response };
}

// GOOD - Stream the file
async function getFileStream({ item }) {
  const response = await axios.get(item.url, {
    responseType: "stream", // Streaming!
  });
  return { httpStream: response };
}
```

### 2. No Error Handling

```typescript
// BAD - Errors crash the extraction
async function getFileStream({ item }) {
  const response = await axios.get(item.url, { responseType: "stream" });
  return { httpStream: response };
  // No try/catch - any error fails the sync!
}

// GOOD - Graceful error handling, return error message only
async function getFileStream({ item }) {
  try {
    const response = await axios.get(item.url, { responseType: "stream" });
    return { httpStream: response };
  } catch (error) {
    // Just return error message - don't log full error object
    return {
      error: { message: `Failed to fetch ${item.id}: ${error.message}` },
    };
  }
}
```

### 2b. Logging Full Error Objects (Memory Overflow Risk)

```typescript
// BAD - Logging full error can cause memory overflow
async function getFileStream({ item }) {
  try {
    return {
      httpStream: await axios.get(item.url, { responseType: "stream" }),
    };
  } catch (error) {
    console.error(`Error:`, JSON.stringify(error, null, 2)); // Memory overflow risk!
    console.error(`Full error object:`, error); // Memory overflow risk!
    return { error: { message: error.message } };
  }
}

// GOOD - Return error message only, no logging of full objects
async function getFileStream({ item }) {
  try {
    return {
      httpStream: await axios.get(item.url, { responseType: "stream" }),
    };
  } catch (error) {
    // Just return the error message - SDK handles the rest
    return {
      error: { message: `Failed to fetch ${item.id}: ${error.message}` },
    };
  }
}
```

### 3. Too Large Batch Size

```typescript
// BAD - May exceed memory limits
const response = await adapter.streamAttachments({
  stream: getFileStream,
  batchSize: 100, // Too many concurrent streams!
});

// GOOD - Reasonable batch size
const response = await adapter.streamAttachments({
  stream: getFileStream,
  batchSize: 10, // Safe for most file sizes
});
```

### 4. Missing Authentication

```typescript
// BAD - URL might require auth
async function getFileStream({ item }) {
  const response = await axios.get(item.url, {
    // May fail with 401
    responseType: "stream",
  });
  return { httpStream: response };
}

// GOOD - Include authentication
async function getFileStream({ item }) {
  const response = await axios.get(item.url, {
    responseType: "stream",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return { httpStream: response };
}
```

### 5. Ignoring Rate Limits

```typescript
// BAD - 429 treated as error
async function getFileStream({ item }) {
  try {
    return {
      httpStream: await axios.get(item.url, { responseType: "stream" }),
    };
  } catch (error) {
    return { error: { message: error.message } }; // 429 just logged
  }
}

// GOOD - Rate limit triggers delay
async function getFileStream({ item }) {
  try {
    return {
      httpStream: await axios.get(item.url, { responseType: "stream" }),
    };
  } catch (error) {
    if (error.response?.status === 429) {
      throw new RateLimitError(error.response.headers["retry-after"] || 60);
    }
    return { error: { message: error.message } };
  }
}

// In worker, catch RateLimitError and emit delay
```

### 6. Not Using Default Implementation

```typescript
// BAD - Custom implementation when not needed
// If external system allows unauthenticated URL access,
// just let the SDK handle it!

// GOOD - Use SDK default when sufficient
// Simply don't implement attachments-extraction.ts
// and let the SDK use default behavior
```

### 7. Missing Timeout Configuration

```typescript
// BAD - No timeout defined, requests may hang indefinitely
const response = await axios.get(item.url, {
  responseType: "stream",
});

// GOOD - Explicit timeout with retry on timeout errors
// In constants.ts:
export const ATTACHMENT_TIMEOUT_MS = 30 * 1000; // 30 seconds
export const DEFAULT_RETRY_DELAY_SECONDS = 10;

// In attachments-extraction.ts:
import {
  ATTACHMENT_TIMEOUT_MS,
  DEFAULT_RETRY_DELAY_SECONDS,
} from "./constants";

try {
  const response = await axios.get(item.url, {
    responseType: "stream",
    timeout: ATTACHMENT_TIMEOUT_MS,
  });
  return { httpStream: response };
} catch (error) {
  // Handle timeout - return delay for retry
  if (error.code === "ECONNABORTED" || error.message?.includes("timeout")) {
    console.warn(`Timeout fetching attachment ${item.id}, will retry`);
    return { delay: DEFAULT_RETRY_DELAY_SECONDS };
  }
  // Handle rate limit
  if (error.response?.status === 429) {
    return {
      delay:
        error.response.headers["retry-after"] || DEFAULT_RETRY_DELAY_SECONDS,
    };
  }
  return { error: { message: error.message } };
}
```

---

## Attachment Data Requirements

During data extraction, attachments must be normalized with:

```typescript
{
  id: string,           // Unique attachment ID
  url: string,          // Download URL
  file_name: string,    // Original filename
  author_id: string,    // Reference to user who created it
  parent_id: string     // Reference to parent record (issue, etc.)
}
```
