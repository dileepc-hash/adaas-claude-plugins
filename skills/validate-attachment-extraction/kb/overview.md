# Attachment Extraction Phase Validation Overview

## Purpose

This skill validates attachment extraction worker implementations for proper streaming, error handling, rate limiting, and timeout management. Ensures connectors follow best practices to avoid memory overflow, data loss, and API failures.

## What is Attachment Extraction?

Attachment extraction is the phase where connectors download files from external systems:

1. Receives attachment metadata (id, url, file_name, etc.)
2. Downloads files via `adapter.streamAttachments()`
3. Handles authentication and rate limiting
4. Manages concurrent downloads with batch size control
5. Provides graceful timeout and error handling

**Primary File:** `functions/extraction/workers/attachment-extraction.ts` or `attachments-extraction.ts`

## Critical Checks Quick Reference

| Check | Issue                                    | Detection                           | Impact                       |
| ----- | ---------------------------------------- | ----------------------------------- | ---------------------------- |
| **C1** | Not using `processTask`                 | Missing `processTask`                | SDK protocol violation       |
| **C2** | Not using `streamAttachments()`         | Missing `streamAttachments`          | Core functionality missing   |
| **C5** | No streaming (buffering files)          | Missing `responseType: 'stream'`     | **Memory overflow**          |
| **C7** | Batch size >50                          | `batchSize` >50                      | **Memory overflow**          |
| **C10** | Logging full error objects              | `JSON.stringify(error)`              | **Memory overflow**          |
| **C4** | Multiple message emissions              | >2 emit calls                        | State inconsistency          |
| **C6** | Missing onTimeout                       | No `onTimeout` handler               | Crashes on timeout           |
| **C9** | No rate limit handling                  | Missing 429 detection                | Permanent failures           |

## Validation Tiers

### CRITICAL (10 checks)

**Must all pass.** Violations cause crashes, memory overflow, or data loss.

**Top 3 Memory Risks:**
1. C5: No streaming (buffers entire files)
2. C7: Batch size >50 (too many concurrent streams)
3. C10: Logging full errors (memory overflow on large syncs)

**Top 3 Stability Risks:**
4. C4: Multiple emissions (state inconsistency)
5. C6: Missing onTimeout (crash on timeout)
6. C9: No 429 handling (permanent API failures)

**Other Critical:**
7. C1: Must use processTask
8. C2: Must use streamAttachments
9. C3: Stream function return type
10. C8: Try/catch coverage

### HIGH (7 checks)

**Strongly recommended.** Issues cause failures under load, security risks, or operational problems.

**Timeout Management:**
- H1: Explicit timeout configuration (30s typical)
- H2: Timeout error handling with retry (ECONNABORTED)

**Security & Reliability:**
- H3: Authentication headers
- H4: Accept-Encoding: identity
- H5: 4xx errors emit Error immediately
- H6: 5xx errors retry with warning
- H7: Clear error messages

### MEDIUM (3 checks)

**Nice-to-have.** Performance tuning and operational visibility.

- M1: Appropriate batch size tuning
- M2: State persistence on timeout
- M3: Progress tracking

## Knowledge Base Navigation

1. **attachment-extraction.md** (symlink → `/references/04-attachments-extraction.md`)
   - Primary validation rules
   - Stream function requirements
   - Error handling patterns
   - Batch size guidelines

2. **common-anti-patterns.md** (symlink → `/references/common-anti-patterns.md`)
   - Quick detection commands
   - Pre-merge checklist
   - Common mistakes

3. **anti-pattern-detection.md** (NEW)
   - Automated grep patterns
   - Runnable detection script
   - 7 CRITICAL + 4 HIGH + 1 MEDIUM patterns
   - Code examples with violations/fixes

## When to Use This Skill

**Use this skill when:**

- Reviewing attachment extraction implementation
- User asks to "validate attachment extraction"
- Debugging attachment download failures or memory issues
- Pre-merge code review for attachment workers
- Investigating Lambda OOM errors during attachment sync

**Don't use this skill for:**

- Data extraction validation (use `/validate-data-extraction`)
- Manifest validation (use `/validate-manifest`)
- Metadata extraction validation

## Common Validation Scenarios

### Scenario 1: Memory Overflow During Attachment Sync

**Symptom:** Lambda crashes with OOM (Out of Memory) error
**Check:** C5 - responseType: 'stream', C7 - batch size, C10 - error logging
**Fix:** Add streaming, reduce batch size, remove error object logging

### Scenario 2: Attachments Lost on Timeout

**Symptom:** After Lambda timeout, attachments not resumed
**Check:** C6 - onTimeout handler, H2 - timeout error handling
**Fix:** Add onTimeout with state persistence and emit Progress

### Scenario 3: Rate Limit Causes Permanent Failures

**Symptom:** 429 errors stop entire attachment sync
**Check:** C9 - 429 rate limit handling
**Fix:** Detect 429, return { delay: retryAfter } to retry

### Scenario 4: Some Attachments Never Download

**Symptom:** Files with auth fail with 401
**Check:** H3 - authentication headers
**Fix:** Add Authorization header to stream function

### Scenario 5: State Becomes Inconsistent

**Symptom:** Extraction restarts but state is wrong
**Check:** C4 - multiple message emissions
**Fix:** Ensure exactly ONE emit per invocation

## Comparison: Data Extraction vs Attachment Extraction

| Aspect                  | Data Extraction                        | Attachment Extraction                |
| ----------------------- | -------------------------------------- | ------------------------------------ |
| **Core Method**         | Custom pagination logic                | `adapter.streamAttachments()`        |
| **Memory Risk**         | State accumulation                     | **File buffering (CRITICAL)**        |
| **Batch Control**       | Not typically used                     | **Critical (5-50)**                  |
| **Streaming**           | Optional                               | **Required (responseType: 'stream')** |
| **Error Tolerance**     | Partial success acceptable             | Individual file failures OK          |
| **Timeout Impact**      | May involve API pagination             | File download limited by timeout     |
| **Common Issue**        | Progress with parameters               | **Memory overflow from buffering**   |

## Integration with Other Skills

This skill complements:

- **validate-data-extraction** - Validates data extraction phase
- **validate-manifest** - Checks capability declarations
- **validate-http-security** (future) - HTTP client best practices

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
/validate-attachment-extraction path/to/attachment-extraction.ts
```

**Natural language triggers:**

- "review attachment extraction"
- "validate attachment extraction implementation"
- "check attachment worker"
- "review attachments-extraction.ts"
- "validate attachment extraction code"

**Auto-discovery:**

If no path provided, searches for:

- `**/functions/extraction/workers/*attachment*-extraction.ts`
- `**/functions/extraction/index.ts` (for context)
