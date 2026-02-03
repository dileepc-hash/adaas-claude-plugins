# Changelog

All notable changes to the AdaaS Connector Review plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-03

### Added
- Initial release of AdaaS Connector Review plugin
- Comprehensive skill with 12 phase-specific review documents
- Command `/review-connector` for full or filtered connector reviews
  - Support for `--phases` argument to review specific phases
  - Support for `--severity` argument to filter by critical/all issues
- Command `/review-phase` for deep-dive phase-specific reviews
- Reference documentation covering:
  - Project structure and manifest review (01-project-structure.md)
  - Metadata extraction phase (02-metadata-extraction.md)
  - Data extraction phase (03-data-extraction.md)
  - Attachments extraction phase (04-attachments-extraction.md)
  - External sync units (05-external-sync-units.md)
  - Data loading phase (06-data-loading.md)
  - Attachments loading phase (07-attachments-loading.md)
  - HTTP client implementation (08-http-client.md)
  - Data normalization (09-normalization.md)
  - State management patterns (10-state-management.md)
  - Error handling patterns (11-error-handling.md)
  - Security checklist (12-security-checklist.md)
  - Common anti-patterns quick reference
- Comprehensive README with usage examples
- Testing guide with verification checklist
- Git repository with .gitignore

### Features
- Auto-triggering skill for connector review questions
- MUST/SHOULD/NICE-TO-HAVE severity categorization
- Quick anti-pattern detection with grep commands
- Security-focused review capabilities
- Runtime constraints validation
- SDK version checking
- Progressive disclosure design (lean SKILL.md with detailed references)

### Documentation
- Complete plugin documentation in README.md
- Detailed testing guide in TESTING.md
- This changelog in CHANGELOG.md
- Command implementation guides in command files

## [Unreleased]

### Planned
- Additional example connectors showing good/bad patterns
- Utility scripts for automated anti-pattern detection
- Integration examples for CI/CD pipelines
- Marketplace submission

---

## Release Notes

### Version 0.1.0 (Initial Release)

This is the first release of the AdaaS Connector Review plugin. It provides comprehensive code review capabilities for DevRev AdaaS (AirSync) connectors.

**Key Features:**
- 12 detailed phase-specific review documents
- 2 slash commands for flexible review workflows
- Auto-activating skill for natural language queries
- Security-focused review capabilities
- Anti-pattern detection
- Severity-based filtering

**Target Audience:**
- Code reviewers
- AI agents in CI pipelines
- Developers creating connectors

**Installation:**
See README.md for installation instructions.

**Testing:**
See TESTING.md for comprehensive testing guide.

**Known Limitations:**
- None at this time

**Future Enhancements:**
- Example connector snippets
- Automated validation scripts
- CI/CD integration templates
