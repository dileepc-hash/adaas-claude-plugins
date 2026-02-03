# AdaaS Connector Review Plugin

A comprehensive code review plugin for DevRev AdaaS (AirSync) connectors. Provides detailed review guidelines, best practices, anti-patterns, and security checklists covering all connector sync phases.

## Overview

This plugin helps review DevRev AirSync connector code against established patterns and best practices. It covers:

- **12 Review Phases**: Project structure, metadata extraction, data extraction, attachments, sync units, loading, HTTP client, normalization, state management, error handling, and security
- **Common Anti-Patterns**: Quick reference of critical mistakes to avoid
- **Security Checklist**: Credential security, data security, and common vulnerabilities
- **Runtime Constraints**: Execution time limits, state size, test coverage requirements

## Target Audience

- Code reviewers
- AI agents reviewing connector PRs
- Developers creating new connectors
- CI/CD pipelines

## Features

### Skill: AdaaS Connector Review

Auto-activates when discussing connector reviews, best practices, or analyzing connector code. Provides comprehensive knowledge of:

- Connector architecture and structure
- All sync phases (extraction and loading)
- Error handling and state management
- Security considerations
- Common anti-patterns

### Commands

#### `/review-connector`

Review an entire connector or specific phases.

**Usage:**
```bash
# Review entire connector (all phases)
/review-connector

# Review specific phases
/review-connector --phases=metadata-extraction,data-extraction

# Review only critical issues
/review-connector --severity=critical

# Combine filters
/review-connector --phases=security,error-handling --severity=critical
```

**Arguments:**
- `--phases`: Comma-separated list of phases to review (optional)
- `--severity`: Filter by severity level: `critical` (MUST only), `all` (MUST+SHOULD+NICE-TO-HAVE) (default: `all`)

#### `/review-phase`

Review a specific connector phase in detail.

**Usage:**
```bash
/review-phase metadata-extraction
/review-phase security
/review-phase data-extraction
```

**Available Phases:**
- `project-structure` - Project structure and manifest
- `metadata-extraction` - Metadata extraction phase
- `data-extraction` - Data extraction phase
- `attachments-extraction` - Attachments extraction
- `external-sync-units` - External sync units
- `data-loading` - Data loading phase
- `attachments-loading` - Attachments loading
- `http-client` - HTTP client implementation
- `normalization` - Data normalization/denormalization
- `state-management` - State management patterns
- `error-handling` - Error handling patterns
- `security` - Security checklist

## Installation

### Local Installation

```bash
# Copy plugin to Claude Code plugins directory
cp -r adaas-connector-review ~/.claude/plugins/

# Or use plugin in current project
mkdir -p .claude-plugin
ln -s /path/to/adaas-connector-review .claude-plugin/adaas-connector-review
```

### Development

```bash
# Test plugin locally
cc --plugin-dir /Users/dileepbc/code-base/platform/connectors/adaas-connector-review
```

## Usage Examples

### Interactive Review

```
You: Review this connector for best practices
Claude: [Skill auto-loads, performs comprehensive review]
```

### Command-Based Review

```
You: /review-connector --phases=metadata-extraction,data-extraction
Claude: [Reviews specified phases with MUST/SHOULD/NICE-TO-HAVE findings]
```

### Focused Security Review

```
You: /review-phase security
Claude: [Deep dive into security checklist and patterns]
```

## Review Output Format

Reviews provide findings organized by severity:

- **MUST** - Critical requirements that will break functionality
- **SHOULD** - Best practices that significantly impact quality/reliability
- **NICE-TO-HAVE** - Improvements that enhance maintainability/performance

## Runtime Constraints Reference

| Constraint | Value |
|-----------|-------|
| Max execution time | 13 minutes |
| Soft timeout (graceful exit) | 10 minutes |
| Max state size | 1 MB (~500,000 characters) |
| SDK version required | >= 1.13.0 |
| Test coverage (statements) | >= 60% |
| Test coverage (branches) | >= 80% |

## Critical Rules

1. **Progress events have NO parameters** - `emit(DataExtractionProgress)` only
2. **initialDomainMapping required** - Must be passed to `spawn()`
3. **Check `adapter.isTimeout` in loops** - Exit gracefully before hard timeout
4. **No manual data batching** - SDK handles batching internally

## Contributing

To update review guidelines:

1. Update reference documents in `skills/adaas-connector-review/references/`
2. Update SKILL.md if core guidelines change
3. Test with sample connectors
4. Update version in plugin.json

## License

MIT

## Version History

- **0.1.0** - Initial release with 12 review phases, anti-patterns, and security checklist
