# Error Handling Patterns Review

## Error Classification

| Error Type       | Recoverable | Action                             | Example             |
| ---------------- | ----------- | ---------------------------------- | ------------------- |
| Rate Limit (429) | Yes         | Delay & retry                      | API quota exceeded  |
| Transient (5xx)  | Yes         | Retry with warn log                | Server error        |
| Network          | Yes         | Retry                              | Connection timeout  |
| Auth (401)       | Sometimes   | Refresh token or fail              | Token expired       |
| Client (4xx)     | No          | Error message & skip (comment why) | Invalid request     |
| Permission (403) | No          | Error message & skip (comment why) | Access denied       |
| Not Found (404)  | No          | Error message & skip (comment why) | Item deleted        |
| Fatal            | No          | Stop sync                          | Invalid credentials |

---

## MUST Follow

- [ ] **Rate limits emit Delay event** - With retry-after duration
- [ ] **Timeouts emit Progress event** - Via onTimeout callback
- [ ] **Fatal errors emit Error event** - With descriptive message
- [ ] **Only ONE event emitted per invocation** - Never multiple
- [ ] **Errors don't expose credentials** - Redact sensitive data
- [ ] **Error messages are actionable** - Include context (item ID, endpoint)
- [ ] **4xx errors handled with error message** - Client errors are non-retryable (exceptions need comment explaining why)
- [ ] **5xx errors retry with warn log** - Server errors are retryable (exceptions need comment explaining why)

## SHOULD Follow

- [ ] **Transient errors retried** - With exponential backoff, limited retries
- [ ] **Individual item failures don't stop sync** - Log & continue
- [ ] **Rate limit Retry-After header respected** - Not hardcoded delay

---

## Key Patterns

### Rate Limit Handling

```typescript
if (error.response?.status === 429) {
  const retryAfter = error.response.headers["retry-after"] || "60";
  await adapter.emit(ExtractorEventType.DataExtractionDelayed, {
    delay: retryAfter,
  });
  return;
}
```

### Item-Level Error Handling

```typescript
for (const item of items) {
  try {
    await processItem(item);
  } catch (error) {
    if (error instanceof RateLimitError) throw error; // Re-throw rate limits
    // Log & continue for other errors - don't stop sync
  }
}
```

---

## Common Anti-Patterns

| Anti-Pattern                 | Problem                   | Fix                                          |
| ---------------------------- | ------------------------- | -------------------------------------------- |
| Multiple event emissions     | Protocol violation        | Single emit with try/catch wrapper           |
| Swallowing rate limits       | Incomplete extraction     | Throw RateLimitError, emit Delay             |
| Credentials in errors        | Security risk             | Redact: `Failed: ${status}` not `${headers}` |
| Generic error messages       | Hard to debug             | Include context: item ID, endpoint, project  |
| No retry for 5xx             | Fails on transient errors | Use exponential backoff with retry limit     |
| Infinite retry loop          | Never terminates          | Limit to 3-5 retries with backoff            |
| Stopping on first item error | One item breaks sync      | Try/catch per item, re-throw rate limits     |
| Missing onTimeout            | State lost on timeout     | Always implement onTimeout callback          |

---

## Review Questions

```
Q1: Is 429 detected and Delay event emitted with Retry-After?
Q2: Is onTimeout implemented and emits Progress event?
Q3: Are transient errors (5xx) retried with exponential backoff?
Q4: Do item failures log & continue (not stop sync)?
Q5: Are credentials redacted from error messages?
Q6: Is there only ONE event emission per invocation?
```
