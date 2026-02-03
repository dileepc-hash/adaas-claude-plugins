---
name: review-connector
description: Review DevRev AdaaS connector code for best practices, anti-patterns, and security issues
allowed-tools:
  - Read
  - Grep
  - Glob
  - Bash
argument-hint: "[--phases=phase1,phase2] [--severity=critical|all]"
---

# Review Connector Command

Review a DevRev AdaaS connector implementation for code quality, best practices, anti-patterns, and security issues.

## Overview

Use this command to perform comprehensive or targeted reviews of AdaaS connector code. The command leverages the `adaas-connector-review` skill which contains detailed review guidelines for all connector phases.

## Command Behavior

When this command executes:

1. **Load the skill**: The `adaas-connector-review` skill loads automatically, providing access to all review guidelines
2. **Parse arguments**: Extract `--phases` and `--severity` filters if provided
3. **Identify connector structure**: Locate `manifest.yaml` and `code/src/` directory
4. **Perform review**: Apply review criteria based on specified scope
5. **Generate findings**: Output conversational findings organized by severity level

## Arguments

### `--phases` (optional)

Comma-separated list of phases to review. If omitted, reviews all phases.

**Available phases:**
- `project-structure` - Project structure, manifest.yaml, package.json
- `metadata-extraction` - Metadata extraction phase
- `data-extraction` - Data extraction phase
- `attachments-extraction` - Attachments extraction phase
- `external-sync-units` - External sync units extraction
- `data-loading` - Data loading phase
- `attachments-loading` - Attachments loading phase
- `http-client` - HTTP client implementation
- `normalization` - Data normalization/denormalization
- `state-management` - State management patterns
- `error-handling` - Error handling patterns
- `security` - Security checklist

**Examples:**
```bash
/review-connector --phases=metadata-extraction,data-extraction
/review-connector --phases=security
/review-connector --phases=project-structure,http-client,security
```

### `--severity` (optional)

Filter findings by severity level. Default is `all`.

**Options:**
- `critical` - Show only MUST fix issues (critical problems that break functionality)
- `all` - Show all issues (MUST + SHOULD + NICE-TO-HAVE) [default]

**Examples:**
```bash
/review-connector --severity=critical
/review-connector --phases=data-extraction --severity=critical
```

## Implementation Instructions

### Step 1: Parse Arguments

Extract arguments from the command invocation:

```
--phases=<comma-separated-list>  → phases to review
--severity=<critical|all>        → severity filter
```

If no arguments provided:
- Default phases: all phases
- Default severity: all

### Step 2: Validate Connector Structure

Check that the current directory or a subdirectory contains:
- `manifest.yaml` file
- `code/src/` directory structure

If not found, ask user to navigate to connector root directory.

### Step 3: Determine Review Scope

Based on `--phases` argument, determine which files to review:

**project-structure**: `manifest.yaml`, `package.json`, directory structure
**metadata-extraction**: `functions/extraction/workers/metadata-extraction.ts`
**data-extraction**: `functions/extraction/workers/data-extraction.ts`
**attachments-extraction**: `functions/extraction/workers/attachments-extraction.ts`
**external-sync-units**: `functions/extraction/workers/external-sync-units.ts`
**data-loading**: `functions/loading/workers/load-data.ts`
**attachments-loading**: `functions/loading/workers/load-attachments.ts`
**http-client**: `functions/external-system/http-client.ts`
**normalization**: `functions/external-system/data-normalization.ts`, `data-denormalization.ts`
**state-management**: Review all worker files for state usage
**error-handling**: Review all worker files for error handling
**security**: Review all files for security issues

If reviewing all phases, check all files.

### Step 4: Read Files

Use Read tool to read relevant files based on review scope. For each phase:
- Read the corresponding worker file(s)
- Read relevant supporting files (types.ts, http-client.ts, etc.)

### Step 5: Apply Review Criteria

For each file, consult the appropriate reference document from the skill:

- `references/01-project-structure.md` for project structure
- `references/02-metadata-extraction.md` for metadata phase
- `references/03-data-extraction.md` for data extraction
- (etc. - see skill documentation)

Apply the MUST/SHOULD/NICE-TO-HAVE checklist from each reference.

### Step 6: Check Common Anti-Patterns

Use grep commands to quickly detect common issues:

```bash
# Check for multiple emits
grep -n "emit(" code/src/functions/extraction/workers/*.ts

# Check for credentials in logs
grep -n "console.log.*token\|console.log.*key" code/src/

# Check for timeout handling
grep -n "adapter.isTimeout" code/src/

# Check for hardcoded delays
grep -n "delay\|setTimeout" code/src/
```

Reference `references/common-anti-patterns.md` for complete list of detection patterns.

### Step 7: Perform Security Scan

Check security criteria from `references/12-security-checklist.md`:
- Credentials not hardcoded
- Credentials not in logs
- HTTPS only
- No PII logged
- Input validation present

### Step 8: Generate Findings Report

Structure findings conversationally by severity level:

**Format:**
```
## Review Results: [Connector Name]

### Scope
- Phases reviewed: [list]
- Files analyzed: [count]
- Severity filter: [critical|all]

### MUST Fix (Critical Issues)

**[Issue Title]**
- Location: `file.ts:line`
- Problem: [Description]
- Impact: [Why this is critical]
- Fix: [Recommendation]

### SHOULD Fix (High Priority)

**[Issue Title]**
- Location: `file.ts:line`
- Problem: [Description]
- Fix: [Recommendation]

### NICE-TO-HAVE (Improvements)

**[Enhancement Title]**
- Benefit: [Why this helps]
- Suggestion: [Recommendation]

### Summary

- Critical issues: [count]
- High priority: [count]
- Improvements: [count]
```

If `--severity=critical`, only show MUST Fix section.

### Step 9: Provide Actionable Summary

End with:
- Count of issues by severity
- Recommendation on next steps
- Offer to review specific phases in more detail if needed

## Examples

### Full Review

```
User: /review-connector
```

Review all phases, all severity levels. Check manifest, package.json, all worker files, http-client, normalization, and cross-cutting concerns.

### Targeted Phase Review

```
User: /review-connector --phases=data-extraction,security
```

Review only data extraction phase and security checklist. Skip other phases.

### Critical Issues Only

```
User: /review-connector --severity=critical
```

Review all phases but only report MUST fix issues (critical problems).

### Focused Security Review

```
User: /review-connector --phases=security --severity=critical
```

Review only security checklist, report only critical security issues.

## Tips

1. **Start with anti-patterns**: Quick grep scans catch common issues fast
2. **Check SDK version first**: Many issues come from old SDK versions (`package.json`)
3. **Security scan early**: Credential leaks are critical
4. **Use phase references**: Don't try to remember everything - load relevant reference docs
5. **Be specific**: Provide file paths and line numbers in findings
6. **Explain why**: For each issue, explain the impact and why it matters
7. **Actionable fixes**: Provide concrete recommendations, not just problems

## Integration with Skill

This command automatically loads the `adaas-connector-review` skill, which provides:
- All 12 phase-specific review documents in `references/`
- Common anti-patterns quick reference
- Security checklist
- Runtime constraints and critical rules

Reference these skill resources when generating review findings.

## Error Handling

If connector structure not found:
```
Could not find connector structure (manifest.yaml or code/src/).
Please navigate to the connector root directory and try again.
```

If invalid phase specified:
```
Unknown phase: [phase-name]
Valid phases: project-structure, metadata-extraction, data-extraction, ...
```

If invalid severity specified:
```
Invalid severity: [value]
Valid options: critical, all
```

## Workflow Summary

1. Parse arguments (`--phases`, `--severity`)
2. Validate connector structure exists
3. Determine files to review based on phases
4. Read relevant files with Read tool
5. Apply phase-specific review criteria from skill references
6. Run anti-pattern grep scans
7. Perform security checks
8. Generate conversational findings report
9. Filter by severity level
10. Provide actionable summary

Focus on being thorough but conversational. Explain not just what's wrong, but why it matters and how to fix it.
