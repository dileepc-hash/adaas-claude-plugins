# Data Extraction Phase Validation Overview

## Purpose

This skill validates the data extraction phase of DevRev connectors - the most complex phase with the highest risk of anti-patterns. It ensures proper implementation of pagination, timeout handling, state management, and error handling.

## What is Data Extraction?

Data extraction is the core phase where the connector:

1. Fetches items from the external system (issues, tickets, users, etc.)
2. Normalizes data to DevRev format
3. Uploads items via SDK repos
4. Handles timeouts, rate limits, and pagination
5. Tracks progress in state for resumability

**File:** `functions/extraction/workers/data-extraction.ts`

## Critical Checks Quick Reference

These are the most common violations that MUST be fixed before deployment:

| Check       | Issue                           | Detection                                      |
| ----------- | ------------------------------- | ---------------------------------------------- |
| **C1**      | Progress events with parameters | `emit(Progress, { ... })`                      |
| **C3**      | Missing timeout checks in loops | `while(hasMore)` without `isTimeout`           |
| **C5**      | Pagination in local variables   | `let page = 1` instead of `adapter.state.page` |
| **C6**      | Missing onTimeout callback      | No `onTimeout:` in processTask                 |
| **C10/C11** | Wrong 4xx/5xx handling          | Retrying 4xx or not retrying 5xx               |

## Validation Tiers

### CRITICAL (14 checks)

Must all pass. Deployment blockers. These violations cause runtime failures, data loss, or protocol violations.

**Focus areas:**

- Progress event parameters (C1) - Most frequent violation
- Timeout handling (C3, C6)
- State management (C5)
- Error handling (C10, C11)
- SDK patterns (C2, C12, C13, C14)

### HIGH Priority (9 checks)

Strongly recommended. These issues cause poor user experience, missed functionality, or potential security issues.

**Focus areas:**

- Rate limiting (H1)
- TIME_SCOPED_SYNCS support (H3)
- State persistence (H4, H7)
- Sync modes (H5, H6)
- Logging quality (H8, H9)

### MEDIUM Priority (3 checks)

Nice-to-have improvements. Optional enhancements for better maintainability and observability.

**Focus areas:**

- Configuration (M1)
- Metrics (M2)
- Performance (M3)

## Knowledge Base Navigation

This skill uses these reference documents:

1. **data-extraction.md** (symlink → `/references/03-data-extraction.md`)
   - Primary validation rules
   - TIME_SCOPED_SYNCS implementation
   - Data normalization requirements
   - Anti-pattern examples

2. **state-management.md** (symlink → `/references/10-state-management.md`)
   - State interface requirements
   - Pagination tracking
   - Serialization rules
   - lastSuccessfulSyncStarted usage

3. **common-anti-patterns.md** (symlink → `/references/common-anti-patterns.md`)
   - Quick detection commands
   - Fix patterns
   - Pre-merge checklist

4. **anti-pattern-detection.md** (NEW)
   - Automated grep patterns for detecting violations
   - Quick detection script (runnable bash script)
   - 12 anti-patterns organized by priority (6 CRITICAL, 5 HIGH, 1 MEDIUM)
   - Enhanced logging anti-patterns:
     - Excessive logging (>5 statements)
     - Logging adapter.event object directly
     - Logging API error objects directly
     - JSON.stringify on sensitive objects
   - Each pattern includes: grep command, violation example, fix, impact
   - Maps to validation checks (C1, H9, etc.)

## When to Use This Skill

**Use this skill when:**

- Reviewing data extraction implementation
- User asks to "validate data extraction"
- Debugging extraction timeouts or failures
- Verifying TIME_SCOPED_SYNCS implementation
- Pre-merge code review checklist

**Don't use this skill for:**

- Manifest validation (use `/validate-manifest`)
- Metadata schema validation (use `/validate-metadata-extraction` when available)
- HTTP client security (use `/validate-http-security` when available)

## Common Validation Scenarios

### Scenario 1: Progress Event Violation

**Symptom:** Extraction fails with SDK error about Progress event
**Check:** C1 - Progress events have NO parameters
**Fix:** Remove all parameters from `emit(ExtractionDataProgress)`

### Scenario 2: Timeout Restarts from Beginning

**Symptom:** After timeout, extraction re-processes same items
**Check:** C5 - Pagination in state, not local variables
**Fix:** Move `page`/`cursor` to `adapter.state[itemType]`

### Scenario 3: Rate Limit Failures

**Symptom:** 429 errors causing extraction failures
**Check:** H1 - Rate limiting with Delay event
**Fix:** Detect 429, emit Delay with Retry-After value

### Scenario 4: TIME_SCOPED_SYNCS Not Working

**Symptom:** extract_from parameter ignored
**Check:** H3 - TIME_SCOPED_SYNCS implementation
**Fix:** Extract and use `extract_from` parameter from event_context

### Scenario 5: Missing initialDomainMapping

**Symptom:** Extraction fails to start or crashes immediately
**Check:** C14 - initialDomainMapping in spawn()
**Fix:** Add `initialDomainMapping` parameter to spawn call in extraction/index.ts

## Integration with Other Skills

This skill complements:

- **validate-manifest** - Checks TIME_SCOPED_SYNCS capability declaration
- **validate-http-security** (future) - Validates HTTP client and rate limiting
- **validate-state-error-handling** (future) - Deep dive into state management
- **validate-metadata-extraction** (future) - Validates schema definitions match extracted data

## Output Format

Results are grouped by severity with:

- Line numbers for precise location
- Problem description (what's wrong)
- Fix instructions (what to do)
- KB reference (where to learn more)

Summary shows:

- ✅ PASSED: Checks that succeeded
- ❌ CRITICAL: Deployment blockers (must fix)
- ⚠️ HIGH: Recommended fixes
- ℹ️ MEDIUM: Optional improvements

## Skill Invocation

**Slash command:**

```
/validate-data-extraction path/to/data-extraction.ts
```

**Natural language triggers:**

- "review data extraction"
- "validate data extraction implementation"
- "check extraction phase"
- "review data-extraction.ts"
- "validate extraction worker"

**Auto-discovery:**
If no path provided, searches for:

- `**/functions/extraction/workers/data-extraction.ts`
- `**/functions/extraction/index.ts`
