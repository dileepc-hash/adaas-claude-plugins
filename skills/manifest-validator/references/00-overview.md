# Connector Manifest Validation - Overview

Quick navigation for Claude when validating manifest.yaml files.

## File Structure

- **auth-patterns.md**: Secret, OAuth2, Keyrings V2 authentication patterns
- **config-patterns.md**: Functions, imports, inputs, hooks configuration patterns
- **anti-patterns.md**: Common mistakes with BAD/GOOD examples
- **validation-rules.md**: Structured checklist with all validation checks

## Validation Priority

CRITICAL → HIGH → MEDIUM (see validation-rules.md)

## Quick Reference

- Authentication issues → auth-patterns.md + anti-patterns.md #4-8
- Configuration issues → config-patterns.md + anti-patterns.md #1-3
- Organization data (CRITICAL) → auth-patterns.md + anti-patterns.md #7
- OAuth scopes → auth-patterns.md + anti-patterns.md #8
- TIME_SCOPED_SYNCS → config-patterns.md

## Most Critical Issues to Check

1. **Organization Data Stability (C6)** - Most frequently missed
2. **Template Defaults (C1)** - Common oversight
3. **Function Mismatches (C3)** - Breaks execution
4. **Subdomain Configuration (C5)** - Connection failures
