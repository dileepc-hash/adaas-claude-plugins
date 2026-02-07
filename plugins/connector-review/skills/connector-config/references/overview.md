# Code Quality Validation Overview

## Purpose

Ensure DevRev connectors maintain high code quality standards through proper configuration of:

1. **Latest SDK versions** - Get bug fixes and new features
2. **TypeScript strict mode** - Catch type errors at compile time
3. **ESLint rules** - Prevent common issues like `any` type usage and deprecated code

## Quick Reference: All Checks

### CRITICAL Checks (All Must Pass)

| Check  | What It Validates                  | Why It Matters                            |
| ------ | ---------------------------------- | ----------------------------------------- |
| **C1** | code/package.json exists           | Foundation for dependency management      |
| **C2** | @devrev/ts-adaas at latest version | Bug fixes, security patches, new features |
| **C3** | code/tsconfig.json exists          | TypeScript compiler configuration         |
| **C4** | TypeScript strict mode enabled     | Prevents runtime type errors              |
| **C5** | ESLint errors on `any` type        | Maintains type safety                     |
| **C6** | ESLint errors on deprecated code   | Prevents use of outdated APIs             |

## Validation Workflow

```
Start
  ↓
[1] Find package.json, tsconfig.json, ESLint config
  ↓
[2] Check C1: package.json exists?
  ↓ YES
[3] Check C2: Latest SDK version?
  ↓ YES
[4] Check C3: tsconfig.json exists?
  ↓ YES
[5] Check C4: Strict mode enabled?
  ↓ YES
[6] Check C5: ESLint errors on 'any'?
  ↓ YES
[7] Check C6: ESLint errors on deprecated code?
  ↓ YES
✅ ALL CHECKS PASSED
```

### Fix C6: Missing Deprecation Rule

```bash
# Install plugin
cd code
npm install --save-dev eslint-plugin-deprecation

# Add to .eslintrc.json
{
  "plugins": ["deprecation"],
  "rules": {
    "deprecation/deprecation": "error"
  }
}

```

## Related Validators

- `/validate-manifest` - Validates manifest.yaml configuration
- `/validate-data-extraction` - Validates data extraction implementation
- `/validate-attachment-extraction` - Validates attachment extraction implementation

This validator focuses purely on code quality **configuration**, not implementation logic.
