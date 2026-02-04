---
name: review-phase
description: Review a specific phase of DevRev AdaaS connector implementation
allowed-tools:
  - Read
  - Grep
  - Glob
argument-hint: "<phase-name>"
---

# Review Phase Command

Perform a deep-dive review of a specific connector sync phase.

## Overview

Use this command for focused, in-depth review of a single connector phase. Provides more detailed analysis than broad multi-phase reviews.

## Command Behavior

When this command executes:

1. **Load the skill**: The `adaas-connector-review` skill loads automatically
2. **Parse phase argument**: Extract the phase name from command invocation
3. **Validate phase**: Ensure phase name is valid
4. **Load phase documentation**: Read appropriate reference from skill
5. **Identify files**: Determine which files to review for this phase
6. **Perform deep review**: Apply all criteria from phase documentation
7. **Generate detailed findings**: Output comprehensive phase-specific review

## Arguments

### `<phase-name>` (required)

The connector phase to review.

**Available phases:**

| Phase                    | Files Reviewed                                        | Focus                                                                  |
| ------------------------ | ----------------------------------------------------- | ---------------------------------------------------------------------- |
| `project-structure`      | manifest.yaml, package.json, directory structure      | Configuration, dependencies, file organization                         |
| `metadata-extraction`    | metadata-extraction.ts, external_domain_metadata.json | Schema definition, field types, references                             |
| `data-extraction`        | data-extraction.ts                                    | Pagination, state management, event emission                           |
| `attachments-extraction` | attachments-extraction.ts                             | File streaming, progress tracking, error handling                      |
| `external-sync-units`    | external-sync-units.ts                                | Sync boundaries, organization structure                                |
| `data-loading`           | load-data.ts                                          | Denormalization, item creation, error handling                         |
| `attachments-loading`    | load-attachments.ts                                   | File upload, validation, retry logic                                   |
| `http-client`            | http-client.ts                                        | Authentication, retry logic, rate limiting                             |
| `normalization`          | data-normalization.ts, data-denormalization.ts        | Data transformation, validation, type conversions                      |
| `state-management`       | All worker files                                      | State structure, persistence, serialization                            |
| `error-handling`         | All worker files                                      | Error classification, retry strategies, logging                        |
| `security`               | All files                                             | Credentials, PII, HTTPS, proper declaration of request, response types |

**Examples:**

```bash
/review-phase metadata-extraction
/review-phase data-extraction
/review-phase security
/review-phase http-client
```

## Implementation Instructions

### Step 1: Parse Phase Argument

Extract phase name from command invocation. If no argument provided, ask user which phase to review.

Validate phase name against allowed phases list. If invalid, show error with valid options.

### Step 2: Load Phase Documentation

Based on phase name, load the appropriate reference document from the skill:

```
project-structure     → references/01-project-structure.md
metadata-extraction   → references/02-metadata-extraction.md
data-extraction       → references/03-data-extraction.md
attachments-extraction → references/04-attachments-extraction.md
external-sync-units   → references/05-external-sync-units.md
data-loading          → references/06-data-loading.md
attachments-loading   → references/07-attachments-loading.md
http-client           → references/08-http-client.md
normalization         → references/09-normalization.md
state-management      → references/10-state-management.md
error-handling        → references/11-error-handling.md
security              → references/12-security-checklist.md
```

Read the full reference document to understand all review criteria for the phase.

### Step 3: Identify Files to Review

Determine which files to read based on the phase:

**project-structure**:

- `manifest.yaml`
- `package.json`
- `package-lock.json` (check existence)
- `tsconfig.json`
- `eslint.config.mts`
- Directory structure via Glob

**metadata-extraction**:

- `code/src/functions/extraction/workers/metadata-extraction.ts`
- `code/src/functions/extraction/index.ts`
- `code/src/functions/external-system/types.ts`
- `code/src/functions/external-system/external_domain_metadata.json` (if exists)

**data-extraction**:

- `code/src/functions/extraction/workers/data-extraction.ts`
- `code/src/functions/extraction/index.ts`
- `code/src/functions/external-system/types.ts`
- `code/src/functions/external-system/http-client.ts`

**attachments-extraction**:

- `code/src/functions/extraction/workers/attachments-extraction.ts`
- `code/src/functions/external-system/http-client.ts`

**external-sync-units**:

- `code/src/functions/extraction/workers/external-sync-units.ts`
- `code/src/functions/external-system/http-client.ts`

**data-loading**:

- `code/src/functions/loading/workers/load-data.ts`
- `code/src/functions/loading/index.ts`
- `code/src/functions/external-system/data-denormalization.ts`
- `code/src/functions/external-system/http-client.ts`

**attachments-loading**:

- `code/src/functions/loading/workers/load-attachments.ts`
- `code/src/functions/external-system/http-client.ts`

**http-client**:

- `code/src/functions/external-system/http-client.ts`
- Any imports or dependencies

**normalization**:

- `code/src/functions/external-system/data-normalization.ts`
- `code/src/functions/external-system/data-denormalization.ts`
- `code/src/functions/external-system/types.ts`

**state-management**:

- All worker files in `functions/extraction/workers/`
- All worker files in `functions/loading/workers/`

**error-handling**:

- All worker files in `functions/extraction/workers/`
- All worker files in `functions/loading/workers/`
- `http-client.ts`

**security**:

- All files (comprehensive scan)
- Focus on `http-client.ts`, worker files, configuration

### Step 4: Read Files

Use Read tool to load all relevant files for the phase. Read complete files to get full context.

### Step 5: Apply Phase-Specific Criteria

For the phase being reviewed, apply ALL criteria from the reference document:

1. Check every item in the **MUST Follow** checklist
2. Check every item in the **SHOULD Follow** checklist
3. Check every item in the **Nice-to-Have** checklist
4. Review all **Common Anti-Patterns** for the phase
5. Answer all **Review Questions** from the reference

Be thorough - this is a deep-dive review, not a quick scan.

### Step 6: Run Phase-Specific Checks

Use grep/search commands relevant to the phase:

**For data-extraction**:

```bash
grep -n "emit(" code/src/functions/extraction/workers/data-extraction.ts
grep -n "onTimeout" code/src/functions/extraction/workers/data-extraction.ts
grep -n "adapter.isTimeout" code/src/functions/extraction/workers/data-extraction.ts
grep -n "adapter.state" code/src/functions/extraction/workers/data-extraction.ts
```

**For security**:

```bash
grep -rn "console.log.*token\|console.log.*key\|console.log.*password" code/src/
grep -rn "http://" code/src/
grep -rn "Authorization.*=" code/src/
```

**For error-handling**:

```bash
grep -rn "catch" code/src/
grep -rn "throw new Error" code/src/
grep -rn "retry" code/src/
```

Reference the phase documentation for complete list of relevant checks.

### Step 7: Generate Detailed Findings

Use the **Review Findings Format** defined in SKILL.md (lines 54-79).

**Format:**

```markdown
## Review: [Phase Name]

### Scope

- Phase: [phase name]
- Files reviewed: [list]
- Reference: references/[XX-phase-name].md

### Address Issue

**[Issue 1 Title]**

- **Location**: `file.ts:line` or `file.ts:startLine-endLine`
- **Problem**: [What's wrong and why it matters]
- **Fix**: [How to fix it with specific recommendations]

**[Issue 2 Title]**

- **Location**: `file.ts:line`
- **Problem**: [What's wrong and why it matters]
- **Fix**: [How to fix it with specific recommendations]
```

**Important:**

- Only report actionable issues that need to be fixed
- Include code snippets in Problem section when helpful
- Provide specific, actionable fixes
- Reference relevant sections from phase documentation

See SKILL.md for complete format specification.

## Examples

All phase reviews follow the same pattern:

1. Load phase reference document
2. Read relevant files for that phase
3. Apply all criteria from reference
4. Generate findings using SKILL.md format

**Example:**

```
User: /review-phase metadata-extraction
```

Process: Load `references/02-metadata-extraction.md` → Read `metadata-extraction.ts`, `types.ts`, `external_domain_metadata.json` → Check schema_version, record types, field definitions → Report findings

See SKILL.md "Example Workflows - Phase-Specific" for general pattern.

## Tips

**Command-specific:**

- This is a deep review - check everything in the phase documentation
- Some phases (state-management, error-handling, security) affect multiple files
- Reference specific sections from phase docs in findings

See SKILL.md "Tips" for general review guidance.

## Error Handling

If phase argument missing:

```
Please specify which phase to review.

Usage: /review-phase <phase-name>

Available phases:
- project-structure
- metadata-extraction
- data-extraction
- attachments-extraction
- external-sync-units
- data-loading
- attachments-loading
- http-client
- normalization
- state-management
- error-handling
- security
```

If invalid phase:

```
Unknown phase: [phase-name]

Valid phases: [list all phases]

Example: /review-phase metadata-extraction
```

If files not found:

```
Could not find expected files for [phase] phase.

Expected files:
- [list expected files]

Please ensure you're in the connector root directory.
```

## Integration with Skill

See SKILL.md "Reference Documentation" section for complete list of phase-specific reference files and their contents.

## Workflow Summary

Follow Implementation Instructions steps 1-7 above for complete workflow.
