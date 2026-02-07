---
name: connector-config
description: Validate connector code quality configuration including TypeScript strict mode, latest DevRev SDK versions, and ESLint rules. Use when the user asks to "check code quality", "validate TypeScript config", "check SDK versions", "validate ESLint", "review code configuration", or any request to validate code quality setup.
argument-hint: [path/to/connector-root]
allowed-tools: Read, Bash(*), Glob, Grep
---

# Code Quality Configuration Validator

Validates code quality configuration for DevRev connectors, ensuring TypeScript strict mode, latest SDK versions, and proper ESLint rules are in place.

## Workflow

### 1. Locate Configuration Files

**Auto-Discovery Pattern:**

```bash
# Find code/package.json
find . -path "*/code/package.json" -not -path "*/node_modules/*" 2>/dev/null | head -1

# Find code/tsconfig.json
find . -path "*/code/tsconfig.json" -not -path "*/node_modules/*" 2>/dev/null | head -1

# Find ESLint config (.eslintrc.json, .eslintrc.js, or eslintConfig in package.json)
find . -path "*/code/.eslintrc.*" -not -path "*/node_modules/*" 2>/dev/null | head -1
```

**Fallback:** If user provides connector root path, look in `<path>/code/` directory.

### 2. Load Validation Rules (REQUIRED)

**MUST read these KB files:**

1. `${CLAUDE_PLUGIN_ROOT}/skills/connector-config/references/overview.md` - Validation overview
2. `${CLAUDE_PLUGIN_ROOT}/skills/connector-config/references/dependency-versions.md` - SDK version requirements
3. `${CLAUDE_PLUGIN_ROOT}/skills/connector-config/references/eslint-rules.md` - ESLint configuration requirements

### 3. Execute Validation

Run checks in priority order: CRITICAL only (focused scope)

**CRITICAL Checks (C1-C6)** - Must all pass:

- **C1: code/package.json exists**
- **C2: @devrev/ts-adaas SDK is at latest version** ⚠️ CHECK VERSION
- **C3: code/tsconfig.json exists**
- **C4: TypeScript strict mode is enabled**
- **C5: ESLint configured to error on `any` type usage**
- **C6: ESLint configured to error on deprecated code usage**

### 4. Automated Detection (Optional)

For quick validation, use the detection script:

```bash
bash ${CLAUDE_PLUGIN_ROOT}/skills/connector-config/references/detection-script.sh <connector-root>
```

This script checks all 6 validations automatically and provides pass/fail results.

### 5. Output Results

**Format:**

```markdown
# Code Quality Validation Results

## Connector: <connector-name>

### CRITICAL Issues ❌

[C1] @devrev/ts-adaas SDK version outdated
Current: x.yy.zz
Latest: x.zz.xx
Fix: cd code && npm install @devrev/ts-adaas@latest

[C2] TypeScript strict mode not enabled
File: code/tsconfig.json
Fix: Set "strict": true in compilerOptions

[C3] ESLint not configured to error on 'any' type`
Fix: Add to .eslintrc.json rules:
"@typescript-eslint/no-explicit-any": "error"
```

## Key Enforcement Rules

**STOP if CRITICAL fails** - All 6 checks must pass for production readiness
**Check latest SDK version** - Use `npm view @devrev/ts-adaas version`
**Support multiple ESLint configs** - .eslintrc.json, .eslintrc.js, eslint.config.mts or eslintConfig in package.json

## Cross-References

This validator focuses on code quality configuration. Also use:

- **validate-manifest** - For manifest.yaml configuration
- **validate-data-extraction** - For data extraction logic implementation
- **validate-attachment-extraction** - For attachment extraction logic

## References

All rules and examples: `${CLAUDE_PLUGIN_ROOT}/skills/connector-config/references/`

- `overview.md` - Quick reference and validation overview
- `dependency-versions.md` - SDK version tracking and upgrade guidance
- `eslint-rules.md` - Required ESLint rules and examples
- `detection-script.sh` - Automated validation script
