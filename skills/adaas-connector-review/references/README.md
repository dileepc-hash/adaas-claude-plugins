# Connector Review Guidelines

This document serves as a comprehensive guide for reviewing DevRev AirSync connectors. It covers all phases of connector development, common patterns, anti-patterns, and security considerations.

## Target Audience

- Code reviewers
- AI Agents reviewing connector PRs
- Developers creating new connectors

## Connector Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    CONNECTOR STRUCTURE                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌─────────────────────────────────────┐    │
│  │ manifest.yaml│    │            code/src/                │    │
│  └─────────────┘    ├─────────────────────────────────────┤    │
│                     │  functions/                          │    │
│                     │  ├── extraction/                     │    │
│                     │  │   ├── index.ts                    │    │
│                     │  │   └── workers/                    │    │
│                     │  │       ├── data-extraction.ts      │    │
│                     │  │       ├── metadata-extraction.ts  │    │
│                     │  │       ├── attachments-extraction.ts│   │
│                     │  │       └── external-sync-units.ts  │    │
│                     │  ├── loading/                        │    │
│                     │  │   ├── index.ts                    │    │
│                     │  │   └── workers/                    │    │
│                     │  │       ├── load-data.ts            │    │
│                     │  │       └── load-attachments.ts     │    │
│                     │  └── external-system/                │    │
│                     │      ├── types.ts                    │    │
│                     │      ├── http-client.ts              │    │
│                     │      ├── data-normalization.ts       │    │
│                     │      ├── data-denormalization.ts     │    │
│                     │      ├── initial_domain_mapping.json │    │
│                     │      └── external_domain_metadata.json│   │
│                     └─────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
```

## Sync Phases

### Extraction (External System → DevRev)

1. **External Sync Units Extraction** - Identify sync boundaries (initial sync only)
2. **Metadata Extraction** - Define external system schema
3. **Data Extraction** - Retrieve items from external system
4. **Attachments Extraction** - Download and upload file attachments

### Loading (DevRev → External System)

1. **Data Loading** - Create/update items in external system
2. **Attachments Loading** - Upload attachments to external system

## Review Documents

| Document                                                       | Description                           |
| -------------------------------------------------------------- | ------------------------------------- |
| [00-manifest-reference.md](./00-manifest-reference.md)         | Manifest overview and quick reference |
| [manifest-reference/](./manifest-reference/)                   | Detailed manifest.yaml configuration  |
| [01-project-structure.md](./01-project-structure.md)           | Project structure and manifest review |
| [02-metadata-extraction.md](./02-metadata-extraction.md)       | Metadata extraction phase             |
| [03-data-extraction.md](./03-data-extraction.md)               | Data extraction phase                 |
| [04-attachments-extraction.md](./04-attachments-extraction.md) | Attachments extraction phase          |
| [05-external-sync-units.md](./05-external-sync-units.md)       | External sync units extraction        |
| [06-data-loading.md](./06-data-loading.md)                     | Data loading phase                    |
| [07-attachments-loading.md](./07-attachments-loading.md)       | Attachments loading phase             |
| [08-http-client.md](./08-http-client.md)                       | HTTP client implementation            |
| [09-normalization.md](./09-normalization.md)                   | Data normalization/denormalization    |
| [10-state-management.md](./10-state-management.md)             | State management patterns             |
| [11-error-handling.md](./11-error-handling.md)                 | Error handling patterns               |
| [12-security-checklist.md](./12-security-checklist.md)         | Security considerations               |
| [common-anti-patterns.md](./common-anti-patterns.md)           | Common mistakes to avoid              |

### Manifest Reference Subdirectory

The `manifest-reference/` subdirectory provides focused guides on manifest.yaml configuration:

| Document                                                                      | Description                           |
| ----------------------------------------------------------------------------- | ------------------------------------- |
| [01-authentication.md](./manifest-reference/01-authentication.md)             | Secret, OAuth2, Keyrings V2 patterns  |
| [02-configuration.md](./manifest-reference/02-configuration.md)               | Functions, imports, inputs, hooks     |
| [03-anti-patterns.md](./manifest-reference/03-anti-patterns.md)               | Common manifest mistakes              |
| [04-validation.md](./manifest-reference/04-validation.md)                     | Final validation checklist            |

## Quick Reference: Runtime Constraints

| Constraint                        | Value                      |
| --------------------------------- | -------------------------- |
| Max execution time per invocation | 13 minutes                 |
| Soft timeout (graceful exit)      | 10 minutes                 |
| Hard timeout (forced termination) | 13 minutes                 |
| Max state size                    | 1 MB (~500,000 characters) |
| Single message emission           | Required per invocation    |
| SDK version required              | >= 1.13.0                  |
| Test coverage (statements)        | >= 60%                     |
| Test coverage (branches)          | >= 80%                     |

## Critical Rules

1. **Progress events have NO parameters** - `emit(DataExtractionProgress)` only, no data!
2. **initialDomainMapping required** - Must be passed to `spawn()`
3. **Check `adapter.isTimeout` in loops** - Exit gracefully before hard timeout
4. **No manual data batching** - SDK handles batching internally

## Review Priority Levels

- **MUST** - Critical requirements that will break functionality if not met
- **SHOULD** - Best practices that significantly impact quality/reliability
- **NICE-TO-HAVE** - Improvements that enhance maintainability/performance
