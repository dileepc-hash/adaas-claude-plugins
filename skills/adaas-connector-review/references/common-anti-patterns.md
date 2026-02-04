# Common Anti-Patterns Quick Reference

## Critical (Must Fix Before Merge)

| Anti-Pattern                 | Problem                | Fix                                         |
| ---------------------------- | ---------------------- | ------------------------------------------- |
| Multiple event emissions     | Protocol violation     | Single emit with try/catch wrapper          |
| Missing onTimeout            | State lost on timeout  | Always implement onTimeout callback         |
| No pagination state          | Restarts from page 1   | Use `adapter.state[type].page`              |
| Hardcoded rate limit delays  | Ignores Retry-After    | Use `error.response.headers['retry-after']` |
| Credentials in logs/errors   | Security vulnerability | Redact: `Authorization: '[REDACTED]'`       |
| Progress events with params  | SDK expects NO params  | `adapter.emit(EventType.Progress)` only     |
| Magic numbers                | Unclear code           | Use named constants with comments           |
| Missing initialDomainMapping | Extraction fails       | Include in `spawn()` call                   |

---

## High Priority (Should Fix)

| Anti-Pattern                   | Problem                | Fix                                            |
| ------------------------------ | ---------------------- | ---------------------------------------------- |
| Not checking adapter.isTimeout | Force terminated       | Check `!adapter.isTimeout` in loops            |
| Manual data batching           | Unnecessary            | SDK handles batching internally                |
| Stopping on first item error   | One item breaks sync   | Try/catch per item, re-throw rate limits       |
| Wrong data normalization       | Validation fails       | String IDs, RFC3339 timestamps, arrays not CSV |
| Buffering large files          | Memory exhaustion      | Use `responseType: 'stream'`                   |
| Missing item_url_field         | Users can't navigate   | Include URL to external item                   |
| Excessive logging              | Memory issues          | Log at critical points only                    |

---

## Medium Priority (Consider Fixing)

| Anti-Pattern                 | Problem               | Fix                                  |
| ---------------------------- | --------------------- | ------------------------------------ |
| Infinite retry loop          | Never terminates      | Limit to 3-5 retries                 |
| Case sensitivity mismatch    | Validation fails      | Match metadata exactly               |
| Empty string instead of null | Invalid data          | Use `null` or omit field             |
| Non-serializable state       | State corrupted       | No Map, Set, functions, Date objects |
| Completion set too early     | Incomplete extraction | Set after ALL pages extracted        |

---

## Quick Detection Commands

```bash
# Multiple emits
grep -n "emit(" code/src/functions/extraction/workers/*.ts

# Hardcoded delays
grep -n "delay\|setTimeout" --include="*.ts" code/src/

# Credentials in logs
grep -n "console.log.*token\|console.log.*key" code/src/

# Missing stream for attachments
grep -n "axios.get" code/src/ | grep -v "responseType"

# Infinite loops
grep -n "while.*true" code/src/
```

---

## Pre-Merge Checklist

```
CRITICAL:
[ ] SDK version >= 1.13.0
[ ] Only ONE emit per invocation
[ ] Progress events have NO parameters
[ ] onTimeout handler exists
[ ] initialDomainMapping in spawn()
[ ] No credentials in logs/errors

IMPORTANT:
[ ] Pagination state persisted
[ ] adapter.isTimeout checked in loops
[ ] Rate limits use Retry-After header
[ ] Item failures don't stop sync
[ ] 4xx/5xx errors handled properly
```
