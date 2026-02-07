---
name: validate-attachment-extraction
description: Validate attachment extraction phase for DevRev connectors. Use when user asks to "review attachment extraction", "validate attachment extraction", "check attachment worker", "review attachments-extraction.ts", or any request to validate attachment extraction implementation.
argument-hint: [path/to/attachment-extraction.ts]
allowed-tools: Read, Bash(*), Grep, Glob
---

# Attachment Extraction Phase Validator

Validates attachment extraction worker implementations for DevRev connectors against established patterns and requirements.

## Workflow

### 1. Locate Target Files

**Auto-Discovery Pattern:**

```bash
# Find attachment-extraction.ts or attachments-extraction.ts
find . -path "*/functions/extraction/workers/*attachment*-extraction.ts" 2>/dev/null

# Find extraction index.ts (for context)
find . -path "*/functions/extraction/index.ts" 2>/dev/null
```

**Fallback:** If user provides path, use that directly.

### 2. Load Validation Rules (REQUIRED)

**MUST read these KB files in order:**

1. `${CLAUDE_PLUGIN_ROOT}/skills/validate-attachment-extraction/references/attachment-extraction.md` - Primary validation rules
2. `${CLAUDE_PLUGIN_ROOT}/skills/validate-attachment-extraction/references/common-anti-patterns.md` - Quick detection patterns
3. `${CLAUDE_PLUGIN_ROOT}/skills/validate-attachment-extraction/references/anti-pattern-detection.md` - Automated grep patterns

### 3. Execute Validation

Run checks in priority order: CRITICAL → HIGH → MEDIUM

**CRITICAL Checks (C1-C10)** - Must all pass:

- **C1: Uses `processTask` Pattern** ⚠️ CHECK FIRST
- **C2: Calls `adapter.streamAttachments()`** - Core SDK streaming method
- C3: Stream Function Returns `{ httpStream }` or `{ error }`
- C4: Single Message Emission Per Invocation
- **C5: Uses `responseType: 'stream'`** - Prevents memory overflow
- C6: Implements `onTimeout` Callback
- **C7: Batch Size 5-50** - Memory management
- C8: Try/Catch Around Stream Operations
- **C9: 429 Rate Limit Handling with Delay** - Critical for API stability
- **C10: No Logging of Full Error Objects** - Memory overflow risk

**HIGH Priority Checks (H1-H7)** - Strongly recommended:

- **H1: Explicit Timeout Configuration (30s typical)** - Prevents hangs
- **H2: Timeout Error Handling with Retry** - ECONNABORTED detection
- H3: Authentication Headers Included
- H4: Accept-Encoding: identity Header
- H5: 4xx Errors Emit Error Immediately
- H6: 5xx Errors Retry with Warning
- H7: Clear Error Messages (No Full Objects)

**MEDIUM Priority Checks (M1-M3)** - Nice-to-have:

- M1: Appropriate Batch Size for File Sizes
- M2: State Persistence Before Timeout
- M3: Progress Tracking in State

### 4. Anti-Pattern Detection (Automated)

Load and execute detection patterns from:

- `${CLAUDE_PLUGIN_ROOT}/skills/validate-attachment-extraction/references/anti-pattern-detection.md`

Run the Quick Detection Script to identify:

- **7 CRITICAL patterns** (AP-C1-C7) - Must fix before deployment
- **4 HIGH priority patterns** (AP-H1-H4) - Strongly recommended
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
# Attachment Extraction Validation Results

## File: functions/extraction/workers/attachment-extraction.ts

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

**ALWAYS check C5 first** - responseType: 'stream' (most critical, prevents memory overflow)
**STOP if CRITICAL fails** - Must fix before deployment
**Include line numbers** - For every issue found
**Provide specific fixes** - With code examples ready to copy-paste
**Reference KB sections** - For detailed context

## Common Critical Issues

### Memory Overflow Issues (Top Priority)

- **C5**: Missing `responseType: 'stream'` → Files buffered in memory → Lambda crashes
- **C7**: Batch size >50 → Too many concurrent streams → Memory overflow
- **C10/H1**: Logging full error objects → Memory overflow on large syncs

### State Inconsistency Issues

- **C4**: Multiple emit calls → State becomes inconsistent
- **C6**: Missing onTimeout → Lambda timeout without graceful exit

### API Stability Issues

- **C9**: No 429 handling → Permanent failures on rate limits
- **H2**: No timeout handling → Lost attachments on transient failures

## Cross-References

This skill may recommend other validators:

- **validate-data-extraction** - For data extraction phase issues
- **validate-manifest** - For capability declarations
- **validate-http-security** - For HTTP client configuration

## References

All rules: `${CLAUDE_PLUGIN_ROOT}/skills/validate-attachment-extraction/references/`

```

```
