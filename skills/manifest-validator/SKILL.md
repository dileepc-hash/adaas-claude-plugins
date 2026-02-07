---
name: validate-manifest
description: Validate connector manifest.yaml against DevRev standards. Use when the user asks to "review manifest", "validate manifest", "check manifest", "validate connector manifest file", "review connector manifest", or any request to validate or check a manifest.yaml file.
argument-hint: [path/to/manifest.yaml]
allowed-tools: Read, Bash(*)
---

# Connector Manifest Validator

Validates `manifest.yaml` files for DevRev connectors.

## Workflow

### 1. Read Manifest

- Locate manifest.yaml (ask user if needed)
- Read entire file

### 2. Load Validation Rules (REQUIRED)

**MUST read this first:**

- `${CLAUDE_PLUGIN_ROOT}/skills/manifest-validator/references/connector-manifest/validation-rules.md`

**Reference as needed:**

- `${CLAUDE_PLUGIN_ROOT}/skills/manifest-validator/references/connector-manifest/anti-patterns.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/manifest-validator/references/connector-manifest/auth-patterns.md`
- `${CLAUDE_PLUGIN_ROOT}/skills/manifest-validator/references/connector-manifest/config-patterns.md`

### 3. Execute Validation

**CRITICAL Checks (C1-C10)** - Must all pass:

- C1: Template Defaults
- C2: Version
- C3: Function Name Consistency
- C4: Connection Types Defined
- C5: Subdomain Configuration
- **C6: Organization Data Stability** ⚠️ CHECK FIRST
- C7: Secret Transform Syntax
- C8: OAuth Configuration
- C9: Placeholder Format
- C10: Production URLs

**HIGH Checks (H1-H4)** - Strongly recommended:

- H1: External System Name Format
- H2: OAuth Scope Descriptions
- H3: Sensitive Field Protection
- H4: TIME_SCOPED_SYNCS Implementation

**MEDIUM Checks (M1-M4)** - Recommended:

- M1: Input Descriptions
- M2: Default Values Safety
- M3: Service Account Display Name
- M4: Multiple Auth Methods

### 4. Output Results

**Format** (from validation-rules.md):

```
# Manifest Validation Results

## File: manifest.yaml

### CRITICAL Issues ❌
C6: [issue] (line X)
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
⚠️  HIGH: X issues (RECOMMENDED)
ℹ️  MEDIUM: X issues (OPTIONAL)
```

### 5. Implementation Check (If Applicable)

If TIME_SCOPED_SYNCS found, ask: "Validate code implementation?"

## Key Enforcement Rules

**ALWAYS check C6 first** - Most critical, frequently missed
**STOP if CRITICAL fails** - Must fix before deployment
**Include line numbers** - For every issue
**Provide specific fixes** - With code examples
**Reference KB sections** - For detailed context

## References

All rules: `${CLAUDE_PLUGIN_ROOT}/references/connector-manifest/validation-rules.md`
