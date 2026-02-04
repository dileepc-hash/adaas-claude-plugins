# Data Extraction Validation Skill

## Overview

This skill validates the data extraction phase implementation for DevRev connectors. It provides comprehensive code review with 3-tier validation (CRITICAL/HIGH/MEDIUM) and actionable fixes.

## Implementation Status

✅ **COMPLETE** - Ready for use

## Structure

```
skills/validate-data-extraction/
├── SKILL.md                              # Main skill definition with frontmatter + workflow
├── README.md                             # This file
└── kb/                                   # Knowledge base
    ├── overview.md                       # Skill-specific introduction
    ├── data-extraction.md                # Symlink → ../../../../references/03-data-extraction.md
    ├── state-management.md               # Symlink → ../../../../references/10-state-management.md
    └── common-anti-patterns.md           # Symlink → ../../../../references/common-anti-patterns.md
```

## Skill Capabilities

### Validation Coverage

**CRITICAL Checks (14):**
- C1: Progress events have NO parameters (most frequent violation)
- C2: Uses `processTask<ExtractorState>` pattern
- C3: Checks `adapter.isTimeout` in loops
- C4: Single message emission per invocation
- C5: State tracks pagination/completion
- C6: Implements `onTimeout` callback
- C7: Required fields present (id, created_date, modified_date)
- C8: Work items include `item_url_field`
- C9: No manual data batching
- C10: 4xx errors emit error immediately
- C11: 5xx errors retry with warning
- C12: Initializes repos before use
- C13: Repo `itemType` matches metadata `record_type`
- C14: Provides `initialDomainMapping` to spawn()

**HIGH Priority Checks (9):**
- H1: Rate limiting with Delay event
- H2: Pagination with reasonable batch sizes (50-100)
- H3: TIME_SCOPED_SYNCS support (extract_from/reset_extract_from)
- H4: State persistence before timeout
- H5: Handles `EXTRACTION_DATA_CONTINUE` event
- H6: Distinguishes initial vs incremental sync
- H7: Updates `lastSuccessfulSyncStarted` after success
- H8: External API errors logged clearly
- H9: No PII in logs

**MEDIUM Priority Checks (3):**
- M1: Configurable batch sizes
- M2: Extraction statistics
- M3: Parallel extraction

### Anti-Pattern Detection

Automated grep patterns detect:
- Progress with parameters (C1)
- Missing timeout checks (C3)
- Multiple emissions (C4)
- Missing onTimeout (C6)
- Manual batching (C9)
- Rate limit handling (H1)
- PII in logs (H9)
- Hardcoded batch sizes (M1)

## Usage

### Invocation Methods

**1. Slash Command:**
```
/validate-data-extraction path/to/data-extraction.ts
```

**2. Natural Language:**
- "review data extraction"
- "validate data extraction implementation"
- "check extraction phase"
- "review data-extraction.ts"
- "validate extraction worker"

**3. Auto-Discovery:**
If no path provided, automatically finds:
- `**/functions/extraction/workers/data-extraction.ts`
- `**/functions/extraction/index.ts`

### Example Workflow

1. User invokes: `/validate-data-extraction`
2. Skill auto-discovers target file
3. Loads validation rules from KB
4. Executes CRITICAL → HIGH → MEDIUM checks
5. Runs anti-pattern detection greps
6. Outputs structured report with:
   - Line numbers for each issue
   - Problem description
   - Specific fix with code
   - KB reference for context

## Output Format

```markdown
# Data Extraction Validation Results

## File: functions/extraction/workers/data-extraction.ts

### CRITICAL Issues ❌
[Issues with line numbers, fixes, KB references]

### HIGH Priority Issues ⚠️
[Issues with line numbers, fixes, KB references]

### MEDIUM Priority Issues ℹ️
[Issues with line numbers, fixes, KB references]

### Summary
✅ PASSED: X checks
❌ CRITICAL: X issues (MUST FIX before deployment)
⚠️ HIGH: X issues (RECOMMENDED fix)
ℹ️ MEDIUM: X issues (OPTIONAL improvement)
```

## Knowledge Base

The skill uses symbolic links to maintain a single source of truth:

1. **data-extraction.md** (591 lines)
   - Complete validation rules
   - TIME_SCOPED_SYNCS implementation guide
   - Data normalization requirements
   - 10 anti-pattern examples

2. **state-management.md** (118 lines)
   - State interface requirements
   - lastSuccessfulSyncStarted usage
   - Pagination tracking patterns
   - Serialization rules

3. **common-anti-patterns.md** (83 lines)
   - Quick reference tables
   - Detection commands
   - Pre-merge checklist

## Testing

### Test Files Available

Sample connector implementations:
```
/Users/dileepbc/code-base/platform/connectors/adaas-connectors/airdrop-sharepoint-tcc-global-snap-in/code/src/functions/extraction/workers/data-extraction.ts
/Users/dileepbc/code-base/platform/connectors/adaas-connectors/airdrop-devrev-snap-in/code/src/functions/extraction/workers/data-extraction.ts
/Users/dileepbc/code-base/platform/connectors/adaas-connectors/airdrop-slack-snap-in/code/src/functions/slack_extractor/workers/data-extraction.ts
```

### Manual Test Cases

**Test 1: Valid Implementation**
- Run against well-structured connector
- Expected: All checks pass, no issues

**Test 2: Critical Violation (Progress with Parameters)**
- Find `emit(DataExtractionProgress, { ... })`
- Expected: C1 violation reported with line number

**Test 3: Missing Timeout Handling**
- Find loop without `adapter.isTimeout`
- Expected: C3 violation with specific fix

**Test 4: TIME_SCOPED_SYNCS Gap**
- Connector with capability but no extract_from handling
- Expected: H3 violation with implementation guide

**Test 5: PII in Logs**
- Find `console.log` with user data
- Expected: H9 violation with security warning

## Integration with Plugin

### Auto-Discovery

The plugin automatically discovers this skill via the `skills/` directory structure. No manual registration required in `plugin.json`.

### Allowed Tools

```yaml
allowed-tools: Read, Bash(*), Grep, Glob
```

- **Read**: Load KB files and target source files
- **Bash(*)**: Run grep patterns for anti-pattern detection, find files
- **Grep**: Search for specific patterns in code
- **Glob**: Find data-extraction.ts files by pattern

### Cross-References

Skill may recommend:
- `validate-manifest` - For TIME_SCOPED_SYNCS capability verification
- `validate-http-security` - For rate limiting and HTTP client issues
- `validate-state-error-handling` - For complex state management

## Extension Pattern

This skill serves as a **template for 7 additional skills**:

### Phase-Specific Skills
1. ✅ **validate-data-extraction** (this skill)
2. ⬜ **validate-metadata-extraction** - Schema definition validation
3. ⬜ **validate-data-loading** - 2-way sync implementation
4. ⬜ **validate-attachments** - File handling (extraction + loading)
5. ⬜ **validate-external-sync-units** - Sync boundary validation

### Cross-Cutting Skills
1. ⬜ **validate-http-security** - HTTP client + security checklist
2. ⬜ **validate-state-error-handling** - State + error patterns

### Replication Steps

To create a new skill following this pattern:

1. Copy `validate-data-extraction/` directory
2. Update `SKILL.md`:
   - Change name/description in frontmatter
   - Update trigger phrases
   - Replace validation checks from corresponding `/references/*.md`
   - Update anti-pattern grep patterns
3. Update `kb/overview.md` for the specific phase
4. Create symlinks to relevant `/references/*.md` files
5. Update README.md with phase-specific details
6. Test invocation and validation

## Design Decisions

### Symbolic Links vs Copy
**Decision:** Use symbolic links
**Rationale:** Single source of truth, automatic updates, no duplication
**Trade-off:** Requires symlink support (works on macOS/Linux)

### Auto-Discovery vs Explicit Paths
**Decision:** Support both
**Rationale:** Convenience for quick reviews, precision for specific files

### Grep-Based Anti-Pattern Detection
**Decision:** Include explicit grep patterns
**Rationale:** Fast detection, complements manual validation, provides line numbers

### KB Organization
**Decision:** Minimal skill-specific KB (overview.md), symlink to comprehensive references
**Rationale:** Avoid duplication, leverage existing comprehensive guides

### Validation Execution Order
**Decision:** CRITICAL → HIGH → MEDIUM (fail-fast)
**Rationale:** Prioritizes blockers, saves review time, matches manifest-validator

## Success Criteria

### Functional ✅
- Skill auto-discovers data-extraction.ts files
- Detects all 14 CRITICAL issues
- Detects all 9 HIGH issues
- Provides specific fixes with code examples
- References KB sections correctly
- Output format matches manifest-validator pattern

### Quality ✅
- No false positives expected (validation rules are comprehensive)
- Line numbers guide precise fixes
- Fixes are actionable (copy-pasteable)
- KB references resolve correctly via symlinks

### Performance ✅
- Symlinks resolve instantly
- KB files load quickly (under 1MB total)
- Grep patterns are efficient

### Usability ✅
- Natural language triggers work
- Can be invoked with or without file path
- Output is readable and scannable
- Severity tiers are clear (❌ ⚠️ ℹ️)

## Maintenance

### Updating Validation Rules

To update validation rules:
1. Edit `/references/03-data-extraction.md` (single source of truth)
2. Symlinks automatically reflect changes
3. No need to update skill KB files

### Adding New Checks

To add new validation checks:
1. Add check to `/references/03-data-extraction.md`
2. Update `SKILL.md` workflow with new check ID
3. Add grep pattern if auto-detectable
4. Update `kb/overview.md` quick reference if CRITICAL

### Version History

- **v0.1.0** (2025-02-04): Initial implementation
  - 14 CRITICAL checks
  - 9 HIGH priority checks
  - 3 MEDIUM priority checks
  - Automated anti-pattern detection
  - TIME_SCOPED_SYNCS validation

## Contributors

Created by: Dileep BC
Pattern based on: `validate-manifest` skill
Reference docs: `/references/03-data-extraction.md` (591 lines)

## License

Part of the adaas-connector-review plugin for Claude Code.
