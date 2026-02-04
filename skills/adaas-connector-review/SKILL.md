---
name: AdaaS Connector Review
description: This skill should be used when the user asks to "review this connector", "check connector code", "analyze AdaaS connector", "review connector for best practices", "check connector security", "validate connector implementation", mentions "connector anti-patterns", "connector metadata extraction", "connector data extraction", "connector loading", or any DevRev AirSync/AdaaS connector review questions. Provides comprehensive code review guidelines for DevRev AdaaS connectors.
version: 0.2.0
---

# AdaaS Connector Review Guidelines

## Purpose

Provide comprehensive code review for DevRev AdaaS (AirSync) connectors covering all sync phases, best practices, anti-patterns, and security. Review connector implementations against established patterns and ensure compliance with runtime constraints.

## Connector Architecture

DevRev AirSync connectors follow this structure:

```
connector-name/
├── manifest.yaml                 # Configuration
└── code/src/functions/
    ├── extraction/              # External System → DevRev
    │   └── workers/             # metadata, data, attachments, sync-units
    ├── loading/                 # DevRev → External System
    │   └── workers/             # load-data, load-attachments
    └── external-system/         # types, http-client, normalization
```

**Sync Phases:**

- Extraction: External Sync Units → Metadata → Data → Attachments
- Loading: Data → Attachments

## Critical Constraints

| Constraint         | Value      |
| ------------------ | ---------- |
| Max execution time | 13 minutes |
| Soft timeout       | 10 minutes |
| Max state size     | 1 MB       |
| SDK version        | Latest     |

## Review Findings Format

Structure all review findings using this simple, actionable format:

```markdown
## Review: [Connector Name]

### Scope

- Phases: [list of phases reviewed]
- Files: [count]

### Address Issue

**[Issue 1 Title]**

- **Location**: `file.ts:line` or `file.ts:startLine-endLine`
- **Problem**: [What's wrong]
- **Fix**: [How to fix it]
- **Root guideline**: [which rule/instruction flagged this error]

**[Issue 2 Title]**

- **Location**: `file.ts:line`
- **Problem**: [What's wrong]
- **Root guideline**: [which rule/instruction flagged this error]
```

**CRITICAL OUTPUT RULES:**

- ❌ DO NOT include "Strengths", "Good patterns", or positive feedback sections
- ❌ DO NOT list what's working correctly
- ❌ DO NOT include summary statistics or counts of good/bad
- ✅ ONLY report issues that require changes
- ✅ Be concise - one issue per finding with location, problem, fix
- ✅ Focus on what's broken, not what's working

**Example of what NOT to do:**
```
✅ Strengths:
1. Well-structured manifest
2. Proper OAuth2 configuration
```

**Example of what TO do:**
```
### Address Issue

**Naming Inconsistency**
- **Location**: `manifest.yaml:14`
- **Problem**: Developer keyring named google-drive-oauth-secret for Calendar connector
- **Fix**: Rename to google-calendar-oauth-secret
```

## Review Process

1. **Identify scope**: Full review, phase-specific, security scan, or anti-pattern check
2. **Load reference docs**: Consult appropriate phase documentation from `references/`
3. **Read files**: Use Read tool for manifest, workers, http-client, etc.
4. **Run mandatory checks**: For manifest reviews, follow the checklist in `references/manifest-reference/03-anti-patterns.md` (Detection Priority Guide)
5. **Format findings**: Use the findings format above

## Reference Documentation

Detailed review criteria organized by phase:

**Project & Structure:**

- `references/01-project-structure.md` - Manifest, package.json, directory structure
- `references/manifest-reference/` - Detailed manifest.yaml configuration guides

**Extraction Phases:**

- `references/02-metadata-extraction.md` - Schema definition, field types
- `references/03-data-extraction.md` - Pagination, state, event emission
- `references/04-attachments-extraction.md` - File streaming, progress
- `references/05-external-sync-units.md` - Sync boundaries

**Loading Phases:**

- `references/06-data-loading.md` - Denormalization, item creation
- `references/07-attachments-loading.md` - File upload, validation

**Implementation:**

- `references/08-http-client.md` - Authentication, retry logic, rate limiting
- `references/09-normalization.md` - Data transformation, validation
- `references/10-state-management.md` - State structure, persistence
- `references/11-error-handling.md` - Error classification, retry strategies

**Security & Patterns:**

- `references/12-security-checklist.md` - Credential security, PII handling
- `references/common-anti-patterns.md` - Quick detection, grep commands

## Example Workflows

**Full Review:**

1. Check SDK version: `npm view @devrev/ts-adaas version` vs `package.json`
2. Review `manifest.yaml` with `references/01-project-structure.md`
3. Review each worker file with corresponding phase reference
4. Run anti-pattern grep scans
5. Security scan with `references/12-security-checklist.md`

**Phase-Specific:**

1. Load relevant reference (e.g., `references/03-data-extraction.md`)
2. Read corresponding worker file
3. Format findings

**Security Audit:**

1. Load `references/12-security-checklist.md`
2. Scan all files for credential leaks, PII, HTTP usage
3. Check error messages and logging
4. Report security violations as MUST fix

## Tips

- **Use references**: Don't memorize - consult phase-specific docs
- **Be specific**: Provide file paths, line numbers, and code examples
- **Explain impact**: Don't just list problems - explain why they matter
- **Actionable fixes**: Give concrete recommendations, not just issues
- **For manifest reviews**: Always consult `references/manifest-reference/03-anti-patterns.md` Detection Priority Guide
