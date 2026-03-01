---
name: security-remediation
description: Propose and apply security fixes for ADaaS connectors based on health reports. This skill should be used when the user asks to "address security findings", "fix security issues", "remediate vulnerabilities", or "fix security report" for a connector. The skill runs the health script, analyzes the report, proposes a fix plan, gets user approval, and executes the fixes.
---

# Security Remediation for ADaaS Connectors

Propose and apply security fixes for ADaaS connector repositories based on automated health reports.

## Overview

This skill provides an **interactive, user-guided workflow** for remediating security vulnerabilities in TypeScript ADaaS connectors:

1. Generates a fresh security health report
2. Analyzes findings and proposes specific fix actions
3. Gets user approval before making changes
4. Applies fixes interactively with verification

**When to use:** User says "Address security findings for [connector-name]" or similar requests to fix security issues.

## Workflow

### Phase 1: Generate Health Report

**Step 1:** Determine the connector repository path

- If user specifies connector name (e.g., "airdrop-outlook-calendar"), locate the repository
- Common locations: `../airdrop-connectors/[connector-name]` or working directory
- Verify path exists and contains the connector structure

**Important:** ADaaS connector structure:

- Repository root: Contains the connector repository
- Code location: `code/*` folder (where `package.json` and source code reside)
- All npm commands must be run from the `code/*` directory

**Step 2:** Run the health script to generate a fresh report

The health script is bundled with this skill at `scripts/adaas_health.py`.

```bash
python3 scripts/adaas_health.py [REPO_PATH] security_reports
```

**Important paths:**

- Health script: `scripts/adaas_health.py` (bundled with this skill)
- Report output: `security_reports/[connector-name]/report_[timestamp].md`

**Note:** If running from a different location, you may need to reference the script using the skill's path or ensure it's available in the workspace.

**Step 3:** Read and analyze the generated report

- SDK version status (@devrev/ts-adaas)
- npm audit findings (dependency vulnerabilities)
- Snyk test findings (dependency vulnerabilities)
- Snyk code findings (SAST issues in source code)

### Phase 2: Propose Fix Plan

#### Migration Guide Detection

**When proposing SDK updates, check for migration requirements:**

**Step 4A:** Detect if update crosses v1.13.0 boundary

- Parse current SDK version and latest version from the health report
- If current < 1.13.0 and latest >= 1.13.0: Migration required (v1.13.0 introduced breaking changes)
- If both current and latest are >= 1.13.2: Non-breaking (v1.13.2 → v1.14.0 → v1.15.0 are non-breaking)

**Step 4B:** Fetch migration guide when crossing v1.13.0 boundary

```bash
gh release view v1.13.2 --repo devrev/adaas-sdk --json body,url
```

**Step 4C:** Parse migration guide content

- Extract "Migration guide from the previous versions" section from the release body
- Identify before/after code patterns (workerPath → baseWorkerPath, getWorkerPath removal)
- Extract list of files typically needing updates: `functions/extraction/index.ts`, `functions/*/index.ts`

**Step 4D:** Document required connector changes when migration is needed

- Spawn function: `workerPath` parameter deprecated → use `baseWorkerPath`
- Remove manual `getWorkerPath()` helper function
- Affected files: `functions/extraction/index.ts`, `functions/*/index.ts`

**Step 4:** Categorize findings into actionable items

Analyze each finding and categorize:

**A. SDK Updates**

- ✅ Patch updates (1.14.0 → 1.14.3): Safe to apply
- ✅ Minor within v1.13.2+ (1.14.0 → 1.15.0): Safe to apply (non-breaking)
- ⚠️ Crossing v1.13.0 boundary (1.12.x → 1.13.0+): Requires code migration; include migration guidance in proposal
- ⚠️ Major updates (1.x → 2.x): Requires manual review, skip

**B. Dependency Vulnerabilities (npm audit + Snyk)**

- ✅ Auto-fixable: Can use `npm audit fix` (without --force)
- ✅ Direct updates: Specific package versions available
- ❌ Unfixable: Requires `--force`, breaking changes, or no fix available

**C. SAST Issues (Snyk code)**

- ✅ Fixable: Code changes in source files
- ⚠️ Review needed: Complex changes or architectural issues
- ❌ Skip: Issues in `node_modules/`, `dist/`, or generated files

**Step 5:** Present the fix plan to the user

Structure the proposal as follows:

````markdown
## Security Remediation Plan for [connector-name]

### Summary

- Total issues found: [count]
- Fixable automatically: [count]
- Requires manual review: [count]
- Cannot fix: [count]

### Proposed Actions

#### 1. SDK Update (@devrev/ts-adaas)

Use the appropriate template based on version analysis:

**Scenario A – Patch or non-breaking minor update** (e.g., 1.14.0 → 1.15.0, or 1.14.0 → 1.14.1):

- Current: [version]
- Latest: [version]
- Action: ✅ Apply update (patch / non-breaking minor release)
- **Changes in [latest]:** [Brief summary from release notes]
- No migration required.

**Scenario B – Crosses v1.13.0 boundary** (e.g., 1.12.x → 1.13.0+):

- Current: [version]
- Latest: [version]
- Action: ⚠️ Requires migration – v1.13.0 introduced breaking changes

**Migration Requirements:**

- v1.13.0+ requires code changes: `workerPath` deprecated in spawn(); use `baseWorkerPath`; remove manual `getWorkerPath()` helper.

**Required Connector Changes** (in `functions/extraction/index.ts` or `functions/*/index.ts`):

```typescript
// Before
const workerPath = getWorkerPath({ event, workerBasePath: __dirname });
await spawn({ event, workerPath, initialState, initialDomainMapping });

// After
await spawn({
  event,
  baseWorkerPath: __dirname,
  initialState,
  initialDomainMapping,
});
```
````

**Files needing updates:** `functions/extraction/index.ts`; remove `getWorkerPath()` helper.

**Migration Reference:** https://github.com/devrev/adaas-sdk/releases/tag/v1.13.2

**Scenario C – Already up to date:**

- Current: [version]
- Latest: [version]
- Action: Already up to date.

#### 2. Dependency Vulnerabilities

**Auto-fixable (via npm audit fix):**

- [package-name] ([severity]) - [description]
- ...

**Direct updates available:**

- [package-name]: [old-version] → [new-version] ([severity])
- ...

**Cannot fix:**

- [package-name] ([severity]) - [reason: no safe fix / breaking changes / etc.]
- ...

#### 3. SAST Issues (Source Code)

**Fixable:**

- [file:line] - [issue-type] - [description]
- ...

**Requires review:**

- [file:line] - [issue-type] - [description]
- ...

### Verification Steps

After applying fixes:

1. Clean install: `npm install`
2. Audit check: `npm audit`
3. Build: `npm run build`
4. Tests: `npm test` (if available)

### Estimated Changes

- Files to modify: [count]
- Dependencies to update: [count]

---

**Proceed with fixes? (yes/no/selective)**

````

**Step 6:** Wait for user input

- **"yes"** or approval: Proceed with all fixable items
- **"no"** or rejection: Stop and explain findings only
- **"selective"**: Ask which categories to apply (SDK / dependencies / SAST)

### Phase 3: Apply Fixes

**Only proceed after user approval from Phase 2.**

**Step 7:** Navigate to the connector code directory

ADaaS connectors have their `package.json` and source code in the `code/*` folder within the repository.

```bash
cd [REPO_PATH]/code/*
````

**Important:** All npm commands must be executed from within the `code/*` directory where `package.json` is located.

**Step 8:** Apply fixes in order

**8a. SDK Updates (if approved)**

Apply when the proposal indicated a safe update (patch, or non-breaking minor within v1.13.2+). Do not apply if the proposal indicated migration is required (crossing v1.13.0 boundary) until the user has applied the code migration.

From the `code/*` directory:

```bash
npm install @devrev/ts-adaas@latest
```

**8b. Dependency Fixes (if approved)**

First, try automatic fixes:

```bash
npm audit fix
```

Then, apply direct updates for specific packages:

```bash
npm install [package-name]@[target-version]
```

**Important rules:**

- ❌ NEVER use `npm audit fix --force`
- ❌ NEVER add `overrides` to package.json
- ✅ Document any skipped vulnerabilities

**8c. SAST Fixes (if approved)**

Apply code fixes to source files based on Snyk code findings:

- Fix prototype pollution issues
- Fix command injection vulnerabilities
- Fix path traversal issues
- Reference `references/fix_patterns.md` for common patterns

**Important rules:**

- ❌ NEVER edit files in `node_modules/`, `dist/`, or `build/`
- ✅ Only fix issues in source code within the `code/*` folder (typically `src/`, root `.ts` files, etc.)

**Step 9:** Verify the fixes

Run verification steps from the `code/*` directory:

```bash
# Clean install
rm -rf node_modules package-lock.json
npm install

# Check remaining vulnerabilities
npm audit

# Build
npm run build

# Test (if tests exist)
npm test
```

**Note:** All verification commands must be run from within the `code/*` directory where `package.json` is located.

Report verification results to the user:

- ✅ Build successful
- ✅ Tests passed
- ⚠️ Remaining vulnerabilities: [count] ([explain why unfixed])

**Step 10:** Summarize changes made

```markdown
## Changes Applied

### SDK Update

- @devrev/ts-adaas: [old-version] → [new-version]

### Dependencies Fixed

- [package-name]: [old-version] → [new-version] ([severity] vulnerability)
- ...

### SAST Issues Fixed

- [file:line]: [issue-type] - [fix description]
- ...

### Unfixed Issues

- [package-name] ([severity]): [reason]
- ...

### Verification Results

- ✅ Build: Passed
- ✅ Tests: Passed (or "No tests found")
- ⚠️ Remaining vulnerabilities: [count]

### Next Steps

To create a pull request for these changes, use the `create-connector-pr` skill.
```

## Using the Fix Patterns Reference

For detailed patterns on fixing specific vulnerability types, reference the bundled resource:

**File:** `references/fix_patterns.md`

**When to reference:**

- Need examples of common fixes (prototype pollution, command injection, etc.)
- Unsure whether to apply a fix or skip it
- Need verification checklist details
- Want to understand what NOT to do

**How to use:**

- Read relevant sections before applying fixes
- Copy verification commands from the checklist
- Reference unfixable scenarios when documenting skipped issues

## Bundled Resources

This skill includes the following bundled resources:

### scripts/adaas_health.py

The ADaaS connector health check script that generates comprehensive security reports.

**Purpose:** Analyzes ADaaS connector repositories for:

- SDK version status (@devrev/ts-adaas)
- npm audit findings (dependency vulnerabilities)
- Snyk test findings (dependency vulnerabilities)
- Snyk code findings (SAST issues in source code)

**Usage:**

```bash
python3 scripts/adaas_health.py [REPO_PATH] [OUTPUT_DIR]
```

**Output:** Generates a markdown report at `[OUTPUT_DIR]/[repo-name]/report_[timestamp].md`

### references/fix_patterns.md

Comprehensive reference guide for common security vulnerability fix patterns (see "Using the Fix Patterns Reference" section above).

## Important Rules

### SDK Update Rules

**Version boundary awareness:**

- v1.13.0 introduced breaking changes (workerPath → baseWorkerPath)
- v1.13.2 → v1.14.0 → v1.15.0 are non-breaking
- Always check if an update crosses the v1.13.0 boundary

**Migration detection:**

- Use `gh release view v1.13.2 --repo devrev/adaas-sdk` to fetch the migration guide when crossing v1.13.0
- Parse for "Migration guide from the previous versions" section
- Extract before/after code patterns for the proposal

**Safe to apply (after user approval):**

- Patch updates within the same minor version
- Minor updates within the v1.13.2+ range (non-breaking)

**Requires migration guidance (do not apply SDK update until user migrates code):**

- Updates crossing the v1.13.0 boundary (current < 1.13.0, latest >= 1.13.0)
- Include full migration instructions in the proposal
- Document specific file changes needed

**Never auto-apply:**

- Major version updates (1.x → 2.x)
- Any SDK update that requires code changes (crossing v1.13.0) until the user has applied the migration

### ✅ DO:

- Always run `scripts/adaas_health.py` first to get current state
- Navigate to the `code/*` directory before running any npm commands
- Present a clear fix plan before making changes
- Get user approval before applying fixes
- Verify with `npm install && npm audit && npm run build && npm test` (from `code/*` directory)
- Document all unfixed issues with reasons
- Apply patch-level and non-breaking minor (v1.13.2+) SDK updates when approved
- Check SDK release notes with `gh` and include migration guidance when crossing v1.13.0

### ❌ NEVER:

- Use `npm audit fix --force` (introduces breaking changes)
- Add `overrides` to package.json (bypasses resolution)
- Apply SDK updates that require migration (crossing v1.13.0) before the user has applied code changes
- Apply major version SDK updates without review
- Edit files in `node_modules/`, `dist/`, or `build/`
- Skip verification steps
- Assume fixes work without running build/tests

## Example Usage

**User request:**

> "Address security findings for airdrop-outlook-calendar"

**Skill workflow:**

1. Run: `python3 scripts/adaas_health.py ../airdrop-connectors/airdrop-outlook-calendar security_reports`
2. Read: `security_reports/airdrop-outlook-calendar/report_[latest].md`
3. Analyze: SDK status, npm audit, Snyk findings
4. Propose: Detailed fix plan with categories
5. Wait: User approval
6. Navigate: `cd ../airdrop-connectors/airdrop-outlook-calendar/code/*`
7. Apply: Approved fixes only (from `code/*` directory)
8. Verify: Build, test, audit (from `code/*` directory)
9. Report: Summary of changes and results

## Example Workflows (SDK Migration)

**Example A: Migration required (crosses v1.13.0 boundary)**

Connector on v1.12.0 → latest v1.15.0:

1. Detect versions from health report: current 1.12.0 &lt; 1.13.0, latest 1.15.0 — migration required
2. Fetch migration guide: `gh release view v1.13.2 --repo devrev/adaas-sdk --json body`
3. Parse: workerPath → baseWorkerPath pattern; remove getWorkerPath()
4. Present proposal with full migration instructions (Scenario B template)
5. Document affected files: `functions/extraction/index.ts`
6. Do not apply SDK update until the user has applied the code migration

**Example B: Non-breaking update (both v1.13.2+)**

Connector on v1.14.0 → latest v1.15.0:

1. Detect versions: both >= 1.13.2 → non-breaking
2. Fetch release notes: `gh release view v1.15.0 --repo devrev/adaas-sdk --json body`
3. Verify no migration guide needed
4. Present proposal: Safe to apply (Scenario A template)
5. After user approval, run `npm install @devrev/ts-adaas@latest` from `code/*`

## Troubleshooting

### Health script fails

**Error:** Script not found or execution error
**Solution:** Ensure running from `platform/connectors` directory with correct path

### npm commands fail

**Error:** `package.json` not found or npm commands fail
**Solution:** Ensure you're in the `code/*` directory within the connector repository where `package.json` is located

### npm audit fix makes no changes

**Explanation:** All vulnerabilities may require `--force` (breaking) or are transitive
**Action:** Document as unfixable and explain in PR

### Build fails after fixes

**Action:**

1. Review changes in `package.json` and `package-lock.json`
2. Check if any package introduced breaking changes
3. Revert specific package and document as unfixable
4. Re-run verification

### Tests fail after fixes

**Action:**

1. Identify which test is failing
2. Check if it's related to dependency changes
3. Consider if test needs updating or if fix introduced issue
4. Report to user for decision

## Related Tools

- **PR creation:** Use the `create-connector-pr` skill to create a pull request following DevRev standards
- **Reporting only:** Use the `security-audit` skill for read-only security analysis
