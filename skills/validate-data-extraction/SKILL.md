---
name: validate-data-extraction
description: Validate data extraction phase for DevRev connectors. Use when user asks to "review data extraction", "validate data extraction", "check extraction phase", "review extraction worker", "validate data-extraction.ts", or any request to validate data extraction implementation.
argument-hint: [path/to/data-extraction.ts]
allowed-tools: Read, Bash(*), Grep, Glob
---

# Data Extraction Phase Validator

Validates data extraction worker implementations for DevRev connectors against established patterns and requirements.

## Workflow

### 1. Locate Target Files

**Auto-Discovery Pattern:**

```bash
# Find data-extraction.ts
find . -path "*/functions/extraction/workers/data-extraction.ts" 2>/dev/null

# Find extraction index.ts (state definition)
find . -path "*/functions/extraction/index.ts" 2>/dev/null
```

**Fallback:** If user provides path, use that directly.

### 2. Load Validation Rules (REQUIRED)

**MUST read these KB files in order:**

1. `${CLAUDE_PLUGIN_ROOT}/skills/validate-data-extraction/references/data-extraction.md` - Primary validation rules
2. `${CLAUDE_PLUGIN_ROOT}/skills/validate-data-extraction/references/state-management.md` - State pattern requirements
3. `${CLAUDE_PLUGIN_ROOT}/skills/validate-data-extraction/references/common-anti-patterns.md` - Quick detection patterns
4. `${CLAUDE_PLUGIN_ROOT}/skills/validate-data-extraction/references/anti-pattern-detection.md` - Automated grep patterns

### 3. Execute Validation

Run checks in priority order: CRITICAL → HIGH → MEDIUM

**CRITICAL Checks (C1-C14)** - Must all pass:

- **C1: Progress Events Have NO Parameters** ⚠️ CHECK FIRST
- C2: Uses `processTask<ExtractorState>` Pattern
- C3: Checks `adapter.isTimeout` in Loops
- C4: Single Message Emission Per Invocation
- C5: State Tracks Pagination/Completion
- C6: Implements `onTimeout` Callback
- C7: Required Fields Present
- C8: Work Items Include `item_url_field`
- C9: No Manual Data Batching
- C10: 4xx Errors Emit Error Immediately
- C11: 5xx Errors Retry with Warning
- C12: Initializes Repos Before Use
- C13: Repo `itemType` Matches Metadata `record_type`
- C14: Provides `initialDomainMapping` to spawn()

**HIGH Priority Checks (H1-H9)** - Strongly recommended:

- H1: Rate Limiting with Delay Event
- H2: Pagination with Reasonable Batch Sizes
- H3: TIME_SCOPED_SYNCS Support (If Enabled)
- H4: State Persistence Before Timeout
- H5: Handles `EXTRACTION_DATA_CONTINUE` Event
- H6: Distinguishes Initial vs Incremental Sync
- H7: Updates `lastSuccessfulSyncStarted` After Success
- H8: External API Errors Logged Clearly
- H9: No PII in Logs

**MEDIUM Priority Checks (M1-M3)** - Nice-to-have:

- M1: Configurable Batch Sizes
- M2: Extraction Statistics
- M3: Parallel Extraction

### 4. Anti-Pattern Detection (Automated)

Load and execute detection patterns from:

- `${CLAUDE_PLUGIN_ROOT}/skills/validate-data-extraction/references/anti-pattern-detection.md`

Run the Quick Detection Script to identify:

- **6 CRITICAL patterns** (AP-C1, C3a, C3b, C4, C6, C9) - Must fix before deployment
- **5 HIGH priority patterns** (AP-H1, H9a, H9b, H9c, H9d, H9e) - Strongly recommended
- **1 MEDIUM pattern** (AP-M1) - Optional improvement

Each pattern includes:

- Grep command for automated detection
- Violation example showing incorrect code
- Fix example showing correct implementation
- Impact explanation of why it matters

The detection file also includes a runnable bash script that checks all patterns at once and provides a summary of issues found.

### 5. Output Results

**Format:**

```markdown
# Data Extraction Validation Results

## File: functions/extraction/workers/data-extraction.ts

### CRITICAL Issues ❌

C1: [issue] (line X)
Problem: [explanation]
Fix: [specific fix with code]
Reference: [KB section]

### HIGH Priority Issues ⚠️

[issues]

### MEDIUM Priority Issues ℹ️

[issues]

### Summary

✅ PASSED: X checks
❌ CRITICAL: X issues (MUST FIX)
⚠️ HIGH: X issues (RECOMMENDED)
ℹ️ MEDIUM: X issues (OPTIONAL)
```

## Key Enforcement Rules

**ALWAYS check C1 first** - Progress event parameters (most critical, frequently missed)
**STOP if CRITICAL fails** - Must fix before deployment
**Include line numbers** - For every issue found
**Provide specific fixes** - With code examples ready to copy-paste
**Reference KB sections** - For detailed context

## Cross-References

This skill may recommend other validators:

- **validate-manifest** - If TIME_SCOPED_SYNCS capability check needed
- **validate-http-security** - For rate limiting and HTTP client issues
- **validate-state-error-handling** - For complex state management issues

## References

All rules: `${CLAUDE_PLUGIN_ROOT}/skills/validate-data-extraction/references/`

```

```
