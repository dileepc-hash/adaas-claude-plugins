# Attachments Loading Phase Review

## Overview
The attachments loading phase uploads attachments from DevRev to the external system. This phase handles file transfers in the reverse direction.

**Triggering Events:**
- `LoaderEventType.StartLoadingAttachments` - Initial start
- `LoaderEventType.ContinueLoadingAttachments` - Resume after timeout

**Response Events:**
- `LoaderEventType.AttachmentsLoadingDone` - Loading complete
- `LoaderEventType.AttachmentsLoadingProgress` - Timeout reached
- `LoaderEventType.AttachmentsLoadingError` - Fatal error

---

## File: `load-attachments.ts`

### MUST Follow

- [ ] **Uses `processTask<LoaderState>` from SDK** - Standard worker pattern
- [ ] **Handles file streaming** - For upload to external system
- [ ] **Associates attachments with parent** - Links to correct record
- [ ] **Emits exactly ONE message** - Done, Progress, or Error
- [ ] **Implements `onTimeout` callback** - For graceful exit
- [ ] **4xx errors return error with message** - Client errors are non-retryable (exceptions need comment explaining why)
- [ ] **5xx errors retry with warn log** - Server errors are retryable (exceptions need comment explaining why)
- [ ] **Define explicit upload timeout** - Set timeout for attachment uploads
- [ ] **Handle timeout errors by retrying** - Timeout errors are retryable

### SHOULD Follow

- [ ] **Uses streaming, not buffering** - For large files
- [ ] **Handles rate limiting** - Returns appropriate delay
- [ ] **Return clear error messages for failed attachments** - Avoid any logging on attachment failures
- [ ] **Handles individual failures** - Don't fail entire sync

### Nice-to-Have

- [ ] Batch uploads if API supports
- [ ] Progress percentage tracking
- [ ] Retry logic for transient failures

---

## Review Questions

```
Q1: File Handling
    - Is file content streamed or buffered?
    - Are large files handled without memory issues?
    - Is file metadata (name, type) preserved?

Q2: Parent Association
    - Are attachments linked to correct parent record?
    - Is parent external ID resolved via object mapper?
    - What if parent doesn't exist in external system?

Q3: API Requirements
    - Does external API support attachment uploads?
    - What file size limits exist?
    - What file types are supported?

Q4: Error Handling
    - Are upload failures logged?
    - Does sync continue after failures?
    - Are failed attachments tracked?

Q5: Rate Limiting
    - Is upload rate limit handled?
    - Is progress emitted before rate limit delay?
```

---

## Implementation Example

```typescript
import { LoaderEventType, processTask } from '@devrev/ts-adaas';
import { HttpClient } from '../../external-system/http-client';

processTask<LoaderState>({
  task: async ({ adapter }) => {
    const client = new HttpClient(adapter.event);

    // Get attachments to load
    const attachments = await adapter.getAttachmentsToLoad();

    for (const attachment of attachments) {
      try {
        // Get parent's external ID
        const parentExternalId = await adapter.objectMapper.getByTargetId(
          attachment.parentId
        );

        if (!parentExternalId) {
          // Skip attachment if parent not found - don't log to avoid memory issues
          continue;
        }

        // Stream file from DevRev
        const fileStream = await adapter.getAttachmentStream(attachment.id);

        // Upload to external system
        await client.uploadAttachment({
          parentId: parentExternalId,
          fileName: attachment.fileName,
          stream: fileStream
        });

      } catch (error) {
        if (error.response?.status === 429) {
          await adapter.emit(LoaderEventType.AttachmentsLoadingProgress);
          return;
        }
        // Continue with next attachment - don't log to avoid memory issues
      }
    }

    await adapter.emit(LoaderEventType.AttachmentsLoadingDone);
  },
  onTimeout: async ({ adapter }) => {
    await adapter.emit(LoaderEventType.AttachmentsLoadingProgress);
  }
});
```

---

## Common Anti-Patterns

### 1. Buffering Large Files
```typescript
// BAD - Full buffer in memory
const fileContent = await adapter.getAttachmentContent(id);  // Entire file
await client.uploadAttachment(parentId, fileContent);

// GOOD - Stream the file
const fileStream = await adapter.getAttachmentStream(id);
await client.uploadAttachmentStream(parentId, fileStream);
```

### 2. Missing Parent Resolution
```typescript
// BAD - Using DevRev ID as parent
await client.uploadAttachment({
  parentId: attachment.parentId,  // This is DevRev ID!
  ...
});

// GOOD - Resolve to external ID
const parentExternalId = await adapter.objectMapper.getByTargetId(
  attachment.parentId
);
await client.uploadAttachment({
  parentId: parentExternalId,
  ...
});
```

### 3. Failing on First Error
```typescript
// BAD - Any error stops all uploads
for (const attachment of attachments) {
  await uploadAttachment(attachment);  // Throws, stops loop
}

// GOOD - Continue after failures, don't log to avoid memory issues
for (const attachment of attachments) {
  try {
    await uploadAttachment(attachment);
  } catch (error) {
    // Continue with next attachment - don't log full errors
  }
}
```

### 4. No Progress on Rate Limit
```typescript
// BAD - Throws on rate limit
if (error.response?.status === 429) {
  throw error;  // Loses progress
}

// GOOD - Emit progress before delay
if (error.response?.status === 429) {
  await adapter.emit(LoaderEventType.AttachmentsLoadingProgress);
  return;  // Will be retried
}
```

---

## External System Considerations

| Consideration | Question |
|--------------|----------|
| File size limits | What's the max file size? |
| File type restrictions | Are certain file types blocked? |
| Upload endpoint | Is there a dedicated upload API? |
| Multipart uploads | Are large files chunked? |
| Rate limits | Are uploads rate limited separately? |

---

## Reviewer Summary

| Area | MUST | SHOULD | NICE |
|------|------|--------|------|
| Implementation | 5 | 4 | 3 |

**Key Questions:**
1. Are attachments uploaded without memory issues?
2. Are parent associations resolved correctly?
3. Do failures not break the sync?
