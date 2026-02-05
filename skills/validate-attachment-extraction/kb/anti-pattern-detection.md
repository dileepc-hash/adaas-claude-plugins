# Attachment Extraction Anti-Pattern Detection

Automated grep patterns for detecting common attachment extraction anti-patterns. Organized by severity (CRITICAL → HIGH → MEDIUM) and mapped to validation checks.

---

## Quick Detection Script

```bash
#!/bin/bash
# Usage: bash detect-anti-patterns.sh <attachment-extraction.ts>
FILE="${1:-attachment-extraction.ts}"
[[ ! -f "$FILE" ]] && { echo "Error: File not found: $FILE"; exit 1; }

CRIT=0; HIGH=0; MED=0
echo "=== Attachment Extraction Anti-Pattern Detection: $FILE ==="

# CRITICAL Patterns
echo -e "\n❌ CRITICAL Issues:"

# AP-C1: Missing responseType: 'stream'
! grep -q "responseType.*['\"]stream['\"]" "$FILE" && echo "AP-C1: No responseType: 'stream' (MEMORY OVERFLOW RISK)" && ((CRIT++))

# AP-C2: Multiple emissions
EMIT_CNT=$(grep -c "\.emit(" "$FILE" 2>/dev/null || echo "0")
[[ "$EMIT_CNT" -gt 2 ]] && echo "AP-C2: Multiple emissions ($EMIT_CNT) - expect 1-2" && ((CRIT++))

# AP-C3: Batch size > 50
grep -n "batchSize.*:.*\([5-9][0-9]\|[1-9][0-9][0-9]\)" "$FILE" 2>/dev/null && echo "AP-C3: Batch size > 50 (MEMORY OVERFLOW RISK)" && ((CRIT++))

# AP-C4: Missing onTimeout
! grep -q "onTimeout:" "$FILE" 2>/dev/null && echo "AP-C4: Missing onTimeout handler" && ((CRIT++))

# AP-C5: No 429 handling
! grep -q "429\|rate.*limit\|Retry-After" "$FILE" 2>/dev/null && echo "AP-C5: No rate limit handling" && ((CRIT++))

# AP-C6: Missing processTask
! grep -q "processTask" "$FILE" 2>/dev/null && echo "AP-C6: Not using processTask" && ((CRIT++))

# AP-C7: Missing streamAttachments
! grep -q "streamAttachments" "$FILE" 2>/dev/null && echo "AP-C7: Not using streamAttachments" && ((CRIT++))

# HIGH Priority Patterns
echo -e "\n⚠️  HIGH Priority Issues:"

# AP-H1: Logging full error objects
grep -n "JSON\.stringify.*error\|console\.error.*error[^.]" "$FILE" 2>/dev/null && echo "AP-H1: Logging full error objects (memory risk)" && ((HIGH++))

# AP-H2: No timeout configuration
! grep -q "timeout.*[0-9]" "$FILE" 2>/dev/null && echo "AP-H2: No timeout configuration" && ((HIGH++))

# AP-H3: No timeout error handling
! grep -q "ECONNABORTED\|timeout" "$FILE" 2>/dev/null && echo "AP-H3: No timeout error handling" && ((HIGH++))

# AP-H4: No authentication
! grep -q "Authorization\|auth" "$FILE" 2>/dev/null && echo "AP-H4: No authentication headers" && ((HIGH++))

# MEDIUM Priority Patterns
echo -e "\nℹ️  MEDIUM Priority Issues:"

# AP-M1: Very small batch size (<5)
grep -n "batchSize.*:.*[1-4][^0-9]" "$FILE" 2>/dev/null && echo "AP-M1: Batch size too small (<5)" && ((MED++))

echo -e "\n=== Summary ==="
echo "❌ CRITICAL: $CRIT (MUST FIX) | ⚠️  HIGH: $HIGH (RECOMMENDED) | ℹ️  MEDIUM: $MED (OPTIONAL)"
[[ "$CRIT" -gt 0 ]] && exit 1 || exit 0
```

---

## Pattern Reference

### CRITICAL Patterns (Must Fix Before Deployment)

| ID         | Pattern                                     | Issue                        | Fix                                                | Impact                          |
| ---------- | ------------------------------------------- | ---------------------------- | -------------------------------------------------- | ------------------------------- |
| **AP-C1**  | `! grep -q "responseType.*stream" FILE`     | No streaming                 | Add `responseType: 'stream'`                       | Memory overflow from buffering  |
| **AP-C2**  | `grep -c "\.emit(" FILE` (>2)               | Multiple emissions           | Single emit per execution path                     | State inconsistency             |
| **AP-C3**  | `grep "batchSize.*[5-9][0-9]"`              | Batch size >50               | Set batchSize: 10-50                               | Memory overflow                 |
| **AP-C4**  | `! grep -q "onTimeout:"`                    | Missing onTimeout            | Add onTimeout handler                              | Timeout without graceful exit   |
| **AP-C5**  | `! grep -q "429"`                           | No rate limit handling       | Detect 429, return { delay }                       | Permanent failures on rate limits |
| **AP-C6**  | `! grep -q "processTask"`                   | Not using processTask        | Use processTask pattern                            | SDK protocol violation          |
| **AP-C7**  | `! grep -q "streamAttachments"`             | Not using streamAttachments  | Use adapter.streamAttachments()                    | Missing streaming functionality |

### HIGH Priority Patterns (Strongly Recommended)

| ID        | Pattern                              | Issue                     | Fix                                  | Impact                             |
| --------- | ------------------------------------ | ------------------------- | ------------------------------------ | ---------------------------------- |
| **AP-H1** | `grep "JSON\.stringify.*error"`      | Logging full error objects | Return error message only            | Memory overflow on large syncs     |
| **AP-H2** | `! grep -q "timeout.*[0-9]"`         | No timeout config         | Add timeout: 30000                   | Hangs without timeout              |
| **AP-H3** | `! grep -q "ECONNABORTED"`           | No timeout error handling | Detect timeout, return { delay }     | Lost attachments on timeout        |
| **AP-H4** | `! grep -q "Authorization"`          | No authentication         | Add auth headers                     | 401 errors                         |

### MEDIUM Priority Pattern (Optional)

| ID        | Pattern                             | Issue                  | Fix                 | Impact            |
| --------- | ----------------------------------- | ---------------------- | ------------------- | ----------------- |
| **AP-M1** | `grep "batchSize.*[1-4][^0-9]"`     | Batch size too small   | Increase to 10+     | Slow performance  |

---

## Code Examples

### AP-C1: responseType: 'stream'

```typescript
// ❌ WRONG - Buffers entire file in memory
const response = await axios.get(item.url);
return { httpStream: response };

// ✅ CORRECT - Streams the file
const response = await axios.get(item.url, {
  responseType: 'stream',
});
return { httpStream: response };
```

**Impact:** Without streaming, large files are fully buffered in memory, causing Lambda to crash with OOM errors.

### AP-C2: Single Message Emission

```typescript
// ❌ WRONG - Multiple emissions
if (response?.delay) await adapter.emit(ExtractorEventType.AttachmentExtractionDelayed, ...);
if (response?.error) await adapter.emit(ExtractorEventType.AttachmentExtractionError, ...);
await adapter.emit(ExtractorEventType.AttachmentExtractionDone); // ALWAYS emits!

// ✅ CORRECT - Single emit per execution path
if (response?.delay) {
  await adapter.emit(ExtractorEventType.AttachmentExtractionDelayed, { delay: response.delay });
} else if (response?.error) {
  await adapter.emit(ExtractorEventType.AttachmentExtractionError, { error: response.error });
} else {
  await adapter.emit(ExtractorEventType.AttachmentExtractionDone);
}
```

**Impact:** Multiple emissions cause state inconsistency and unpredictable behavior.

### AP-C3: Batch Size

```typescript
// ❌ WRONG - Too many concurrent streams
const response = await adapter.streamAttachments({
  stream: getAttachmentStream,
  batchSize: 100, // Memory overflow!
});

// ✅ CORRECT - Safe batch size
const response = await adapter.streamAttachments({
  stream: getAttachmentStream,
  batchSize: 10, // Safe for most file sizes
});
```

**Impact:** Large batch sizes cause too many concurrent HTTP streams, leading to memory overflow.

### AP-C4: onTimeout Handler

```typescript
// ❌ WRONG - No onTimeout
return adapter.processTask({
  task: async ({ adapter }) => {
    const response = await adapter.streamAttachments({ stream: getStream, batchSize: 10 });
    // ... handle response
  },
});

// ✅ CORRECT - With onTimeout
return adapter.processTask({
  task: async ({ adapter }) => {
    const response = await adapter.streamAttachments({ stream: getStream, batchSize: 10 });
    // ... handle response
  },
  onTimeout: async ({ adapter }) => {
    await adapter.postState();
    await adapter.emit(ExtractorEventType.AttachmentExtractionProgress);
  },
});
```

**Impact:** Without onTimeout, Lambda timeout causes abrupt failure without state persistence.

### AP-C5: Rate Limit Handling

```typescript
// ❌ WRONG - 429 treated as permanent error
async function getAttachmentStream({ item }) {
  try {
    const response = await axios.get(item.url, { responseType: 'stream' });
    return { httpStream: response };
  } catch (error) {
    return { error: { message: error.message } }; // 429 fails permanently!
  }
}

// ✅ CORRECT - 429 triggers delay
async function getAttachmentStream({ item }) {
  try {
    const response = await axios.get(item.url, { responseType: 'stream' });
    return { httpStream: response };
  } catch (error) {
    if (error.response?.status === 429) {
      const retryAfter = parseInt(error.response.headers['retry-after'] || '60', 10);
      return { delay: retryAfter }; // SDK will retry
    }
    return { error: { message: error.message } };
  }
}
```

**Impact:** Without 429 handling, rate limits cause permanent failures instead of graceful delays.

### AP-H1: Logging Error Objects

```typescript
// ❌ WRONG - Memory overflow risk
try {
  return { httpStream: await axios.get(url, { responseType: 'stream' }) };
} catch (error) {
  console.error('Error:', JSON.stringify(error)); // MEMORY OVERFLOW!
  return { error: { message: error.message } };
}

// ✅ CORRECT - Return message only, no logging
try {
  return { httpStream: await axios.get(url, { responseType: 'stream' }) };
} catch (error) {
  return { error: { message: `Failed to fetch ${item.id}: ${error.message}` } };
}
```

**Impact:** Logging full error objects causes memory overflow on large syncs with many errors.

### AP-H2: Timeout Configuration

```typescript
// ❌ WRONG - No timeout
const response = await axios.get(item.url, {
  responseType: 'stream',
});

// ✅ CORRECT - Explicit timeout
const response = await axios.get(item.url, {
  responseType: 'stream',
  timeout: 30 * 1000, // 30 seconds
});
```

**Impact:** Without timeout, requests can hang indefinitely.

### AP-H3: Timeout Error Handling

```typescript
// ❌ WRONG - Timeout treated as permanent error
try {
  const response = await axios.get(url, { responseType: 'stream', timeout: 30000 });
  return { httpStream: response };
} catch (error) {
  return { error: { message: error.message } }; // Timeout = permanent failure!
}

// ✅ CORRECT - Retry on timeout
try {
  const response = await axios.get(url, { responseType: 'stream', timeout: 30000 });
  return { httpStream: response };
} catch (error) {
  if (error.code === 'ECONNABORTED' || error.message?.includes('timeout')) {
    console.warn(`Timeout fetching attachment ${item.id}, will retry`);
    return { delay: 10 }; // Retry after 10 seconds
  }
  return { error: { message: error.message } };
}
```

**Impact:** Timeouts are often transient - treating them as permanent errors loses attachments unnecessarily.

### AP-H4: Authentication Headers

```typescript
// ❌ WRONG - No authentication
async function getAttachmentStream({ item }) {
  const response = await axios.get(item.url, {
    responseType: 'stream',
  });
  return { httpStream: response };
}

// ✅ CORRECT - Include authentication
async function getAttachmentStream({ item, event }) {
  const response = await axios.get(item.url, {
    responseType: 'stream',
    headers: {
      Authorization: `Bearer ${event.payload.connection_data.key}`,
      'Accept-Encoding': 'identity',
    },
  });
  return { httpStream: response };
}
```

**Impact:** Missing auth causes 401 errors for protected resources.

---

## Manual Inspection Required

Some patterns cannot be detected with grep:

**Stream Function Return Type:**
- C3: Verify stream function returns `{ httpStream }` OR `{ error }` (never both)
- Check for proper error object structure

**Error Handling:**
- C8: Try/catch around all stream operations
- H5: 4xx errors emit Error immediately (not retried)
- H6: 5xx errors logged with warning and retried

**State Management:**
- M2: State posted before timeout emit
- M3: Progress percentage tracked in state

---

## Testing

**Test CRITICAL patterns:**

```typescript
// Should trigger multiple patterns
const response = await axios.get(url); // AP-C1: No streaming
await adapter.emit(...Done);
await adapter.emit(...Progress); // AP-C2: Multiple emissions
const r = await adapter.streamAttachments({ batchSize: 100 }); // AP-C3: Batch >50
```

**Test HIGH logging patterns:**

```typescript
console.error('Error:', JSON.stringify(error)); // AP-H1
const r = await axios.get(url, { responseType: 'stream' }); // AP-H2: No timeout
```

**Valid patterns (no false positives):**

```typescript
const response = await axios.get(url, {
  responseType: 'stream',
  timeout: 30000,
  headers: { Authorization: `Bearer ${token}` },
});
if (response.status === 429) return { delay: 60 };
```

---

## References

- `attachment-extraction.md` - Detailed validation rules
- `common-anti-patterns.md` - Quick reference
- `/references/04-attachments-extraction.md` - Core requirements
- `/references/07-attachments-loading.md` - Loading phase

**Changelog v1.0** (2026-02-04): Initial version with 7 CRITICAL, 4 HIGH, 1 MEDIUM patterns for attachment extraction validation
