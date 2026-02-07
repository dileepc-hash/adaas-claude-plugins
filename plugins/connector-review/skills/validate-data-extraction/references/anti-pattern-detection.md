# Data Extraction Anti-Pattern Detection

Automated grep patterns for detecting common data extraction anti-patterns. Organized by severity (CRITICAL → HIGH → MEDIUM) and mapped to validation checks in `data-extraction.md`.

---

## Quick Detection Script

```bash
#!/bin/bash
# Usage: bash detect-anti-patterns.sh <data-extraction.ts>
FILE="${1:-data-extraction.ts}"
[[ ! -f "$FILE" ]] && { echo "Error: File not found: $FILE"; exit 1; }

CRIT=0; HIGH=0; MED=0
echo "=== Data Extraction Anti-Pattern Detection: $FILE ==="

# CRITICAL Patterns
echo -e "\n❌ CRITICAL Issues:"
grep -n "emit.*DataExtractionProgress.*{" "$FILE" 2>/dev/null && echo "AP-C1: Progress with parameters" && ((CRIT++))
grep -n "while.*{" "$FILE" 2>/dev/null | grep -v "isTimeout" | grep -v "^$" && echo "AP-C3a: While loop no timeout" && ((CRIT++))
grep -n "for.*{" "$FILE" 2>/dev/null | grep -v "isTimeout" | grep -v "^$" && echo "AP-C3b: For loop no timeout" && ((CRIT++))
EMIT_CNT=$(grep -c "emit(ExtractorEventType\." "$FILE" 2>/dev/null || echo "0")
[[ "$EMIT_CNT" -gt 2 ]] && echo "AP-C4: Multiple emissions ($EMIT_CNT)" && ((CRIT++))
! grep -q "onTimeout:" "$FILE" 2>/dev/null && echo "AP-C6: Missing onTimeout" && ((CRIT++))
grep -n "chunk\|batch\|slice" "$FILE" 2>/dev/null | grep -v "pageSize\|limit" && echo "AP-C9: Manual batching" && ((CRIT++))

# HIGH Priority Patterns
echo -e "\n⚠️  HIGH Priority Issues:"
! grep -q "429\|rate.*limit\|Retry-After" "$FILE" 2>/dev/null && echo "AP-H1: No rate limit detection" && ((HIGH++))
grep -n "console\.log.*email\|console\.log.*password\|console\.log.*token" "$FILE" 2>/dev/null && echo "AP-H9a: PII in logs" && ((HIGH++))
LOG_CNT=$(grep -c "console\.\(log\|warn\)[^)]" "$FILE" 2>/dev/null || echo "0")
[[ "$LOG_CNT" -gt 5 ]] && echo "AP-H9b: Excessive logging ($LOG_CNT > 5)" && ((HIGH++))
grep -n "console.*adapter\.event[^.]" "$FILE" 2>/dev/null && echo "AP-H9c: Logging adapter.event" && ((HIGH++))
grep -n "console.*\(error\|err\|response\.error\)" "$FILE" 2>/dev/null | grep -v "console\.error" && echo "AP-H9d: Logging error objects" && ((HIGH++))
grep -n "JSON\.stringify.*\(adapter\.event\|error\|response\)" "$FILE" 2>/dev/null && echo "AP-H9e: JSON.stringify sensitive" && ((HIGH++))

# MEDIUM Priority Patterns
echo -e "\nℹ️  MEDIUM Priority Issues:"
grep -n "pageSize.*=.*[0-9]\|limit.*=.*[0-9]" "$FILE" 2>/dev/null | grep -v "const\|let.*pageSize.*=" && echo "AP-M1: Hardcoded batch sizes" && ((MED++))

echo -e "\n=== Summary ==="
echo "❌ CRITICAL: $CRIT (MUST FIX) | ⚠️  HIGH: $HIGH (RECOMMENDED) | ℹ️  MEDIUM: $MED (OPTIONAL)"
[[ "$CRIT" -gt 0 ]] && exit 1 || exit 0
```

---

## Pattern Reference

### CRITICAL Patterns (Must Fix Before Deployment)

| ID         | Pattern                                          | Issue                            | Fix                                                                   | Impact                                                 |
| ---------- | ------------------------------------------------ | -------------------------------- | --------------------------------------------------------------------- | ------------------------------------------------------ |
| **AP-C1**  | `grep -n "emit.*DataExtractionProgress.*{" FILE` | Progress events with parameters  | Remove all parameters: `emit(ExtractionDataProgress)`                 | SDK protocol violation, extraction fails               |
| **AP-C3a** | `grep -n "while.*{" FILE \| grep -v "isTimeout"` | While loop without timeout check | Add to condition: `while (hasMore && !adapter.isTimeout)`             | Lambda timeout, no state save, restarts from beginning |
| **AP-C3b** | `grep -n "for.*{" FILE \| grep -v "isTimeout"`   | For loop without timeout check   | Add inside loop: `if (adapter.isTimeout) break;`                      | Cannot interrupt iterations, timeout without save      |
| **AP-C4**  | `grep -c "emit(ExtractorEventType\." FILE`       | Multiple emissions (>2)          | Single emit per invocation (1-2 max: task + onTimeout)                | Protocol confusion, inconsistent state                 |
| **AP-C6**  | `grep -q "onTimeout:" FILE`                      | Missing onTimeout callback       | Add to processTask: `{ onTimeout: async ({adapter,state}) => {...} }` | Timeout causes failure, no graceful continuation       |
| **AP-C9**  | `grep -n "chunk\|batch\|slice" FILE`             | Manual data batching             | Remove - SDK handles batching: `await repo.upload(items)`             | Double-batching issues, SDK batches at 500 items       |

### HIGH Priority Patterns (Strongly Recommended)

| ID         | Pattern                                                               | Issue                          | Fix                                                                              | Impact                                             |
| ---------- | --------------------------------------------------------------------- | ------------------------------ | -------------------------------------------------------------------------------- | -------------------------------------------------- |
| **AP-H1**  | `grep -q "429\|rate.*limit\|Retry-After" FILE`                        | No rate limit detection        | Detect 429, emit Delay: `adapter.emit(Delay, {duration_in_seconds: retryAfter})` | Extraction fails on rate limits, no backoff        |
| **AP-H9a** | `grep -n "console\.log.*email\|password\|token" FILE`                 | PII in logs                    | Log IDs not emails: `console.log("User ID:", user.id)`                           | Security violation, PII in CloudWatch, GDPR issues |
| **AP-H9b** | `grep -c "console\.\(log\|warn\)[^)]" FILE`                           | Excessive logging (>5)         | Keep ≤5 essential logs, use console.error for errors                             | Memory pressure, CloudWatch costs, timeout risk    |
| **AP-H9c** | `grep -n "console.*adapter\.event[^.]" FILE`                          | Logging adapter.event object   | Log specific props: `adapter.event.payload.event_type`                           | Exposes credentials, circular refs, massive output |
| **AP-H9d** | `grep -n "console.*\(error\|err\|response\.error\)" FILE`             | Logging error objects          | Log safe fields: `console.error("Error:", error.status, error.message)`          | May contain Bearer tokens in headers               |
| **AP-H9e** | `grep -n "JSON\.stringify.*\(adapter\.event\|error\|response\)" FILE` | Stringifying sensitive objects | Extract safe fields: `JSON.stringify({status, message})`                         | Exposes secrets, circular refs fail                |

### MEDIUM Priority Pattern (Optional)

| ID        | Pattern                                              | Issue                 | Fix                                                           | Impact                                   |
| --------- | ---------------------------------------------------- | --------------------- | ------------------------------------------------------------- | ---------------------------------------- |
| **AP-M1** | `grep -n "pageSize.*=.*[0-9]\|limit.*=.*[0-9]" FILE` | Hardcoded batch sizes | Make configurable: `adapter.event.payload.page_size \|\| 100` | Cannot tune per instance, testing harder |

---

## Code Examples

### AP-C1: Progress Events

```typescript
// ❌ WRONG - Parameters not allowed
adapter.emit(ExtractorEventType.ExtractionDataProgress, { count: 100 });

// ✅ CORRECT - No parameters
adapter.emit(ExtractorEventType.ExtractionDataProgress);
```

### AP-C3: Timeout Checks

```typescript
// ❌ WRONG - No timeout check
while (hasMore) {
  await fetchItems();
}
for (const repo of repos) {
  await process(repo);
}

// ✅ CORRECT - Check timeout
while (hasMore && !adapter.isTimeout) {
  await fetchItems();
}
for (const repo of repos) {
  if (adapter.isTimeout) break;
  await process(repo);
}
```

### AP-C6: onTimeout Handler

```typescript
// ❌ WRONG - No onTimeout
adapter.processTask("extraction", async ({adapter, state}) => {...});

// ✅ CORRECT - With onTimeout
adapter.processTask("extraction",
  async ({adapter, state}) => {...},
  {onTimeout: async ({adapter, state}) => {
    adapter.emit(ExtractorEventType.ExtractionDataProgress);
  }}
);
```

### AP-H9: Logging Anti-Patterns

```typescript
// ❌ WRONG - Security/performance issues
console.log("User:", user.email); // H9a: PII
console.log("Event:", adapter.event); // H9c: Entire event
console.log("Error:", error); // H9d: Error object
console.log(JSON.stringify(adapter.event)); // H9e: Stringify sensitive
// ... 10+ console.log statements              // H9b: Excessive (>5)

// ✅ CORRECT - Safe logging
console.log("User ID:", user.id); // No PII
console.log("Event type:", adapter.event.payload.event_type); // Specific prop
console.error("API Error:", error.status, error.message); // Safe fields
console.log(JSON.stringify({ status, count })); // Safe object
// Max 5 console.log/warn per file
```

### AP-H1: Rate Limiting

```typescript
// ❌ WRONG - No 429 handling
const response = await apiClient.get("/items");
if (!response.ok) throw new Error("API error");

// ✅ CORRECT - Handle rate limits
const response = await apiClient.get("/items");
if (response.status === 429) {
  const retryAfter = parseInt(response.headers.get("Retry-After") || "60");
  adapter.emit(ExtractorEventType.Delay, {
    duration_in_seconds: retryAfter,
    reason: "Rate limit exceeded",
  });
  return;
}
```

---

## Manual Inspection Required

Some patterns cannot be detected with grep:

**State Management:**

- C5: Pagination in adapter.state (not local variables)
- H4: State saved before return statements
- H7: lastSuccessfulSyncStarted updated after completion

**Error Handling:**

- C10: 4xx errors emit Error immediately (not retried)
- C11: 5xx errors retry with warning
- H8: Clear error logging in catch blocks

**SDK Patterns:**

- C2: Uses `processTask<ExtractorState>` signature
- C12: Repos initialized before use
- C13: Repo itemType matches metadata record_type
- C14: initialDomainMapping in spawn() call

---

## Testing

**Test CRITICAL patterns:**

```typescript
adapter.emit(ExtractorEventType.ExtractionDataProgress, { count: 100 }); // AP-C1
while (hasMore) {
  items = await fetch();
} // AP-C3a
// Missing onTimeout // AP-C6
const chunks = items.slice(0, 100); // AP-C9
```

**Test HIGH logging patterns:**

```typescript
console.log("Email:", user.email); // AP-H9a
console.log("1"); console.log("2"); ... console.log("6"); // AP-H9b (>5)
console.log("Event:", adapter.event); // AP-H9c
console.log("Error:", error); // AP-H9d
console.log(JSON.stringify(adapter.event)); // AP-H9e
```

**Valid patterns (no false positives):**

```typescript
while (hasMore && !adapter.isTimeout) {} // OK - has timeout check
console.error("Error:", error.message); // OK - console.error allowed
console.log("Count:", count); // OK - under threshold, safe data
const type = adapter.event.payload.event_type; // OK - specific property
console.log(JSON.stringify({ count, status })); // OK - safe object
```

---

## References

- `data-extraction.md` - Detailed validation rules
- `state-management.md` - State requirements
- `/references/03-data-extraction.md` - Anti-pattern examples
- `/references/12-security-checklist.md` - Logging security

**Changelog v1.0** (2026-02-04): Initial version with 12 patterns (6 CRITICAL, 5 HIGH, 1 MEDIUM) including 4 new logging anti-patterns (H9b-e)
