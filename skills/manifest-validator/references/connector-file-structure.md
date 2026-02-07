# Connector Project Structure and Phases

## Overview

Airdrop connectors follow a standardized architecture built on `@devrev/ts-adaas`. All connectors implement a phase-based approach:

- **Extraction-only**: Read data from external systems
- **Bidirectional**: Both extract and load data

Based on analysis of 10 representative connectors.

---

## Directory Structure

### Root Level

```
connector-name/
├── manifest.yaml              # Connector configuration
├── marketplace.yaml           # Marketplace metadata
├── Makefile                   # Build automation
├── code/                      # TypeScript implementation
└── .github/workflows/         # CI/CD
```

### Code Structure

```
code/
├── package.json
├── tsconfig.json
├── src/
│   ├── index.ts               # Entry point
│   ├── function-factory.ts    # Function registry
│   └── functions/
│       ├── extraction/
│       │   ├── index.ts
│       │   └── workers/       # Phase workers (4 files)
│       ├── loading/           # Bidirectional only
│       │   ├── index.ts
│       │   └── workers/       # Load workers (2 files)
│       └── [connector-name]/
│           ├── client.ts      # API wrapper
│           ├── types.ts
│           ├── initial_domain_mapping.json
│           └── external_domain_metadata.json
```

---

## Extraction Phases

### Phase 1: External Sync Units Extraction

- **Worker**: `workers/external-sync-units-extraction.ts`
- **Purpose**: Identify organizational units (projects, workspaces)
- **Events**: `ExtractionExternalSyncUnitsStart` → `ExtractionExternalSyncUnitsDone`
- **Action**: Query external system, call `adapter.registerExternalSyncUnit()` for each unit

### Phase 2: Metadata Extraction

- **Worker**: `workers/metadata-extraction.ts`
- **Purpose**: Define schema and initialize repositories
- **Events**: `ExtractionMetadataStart` → `ExtractionMetadataDone`
- **Actions**:
  - Load `external_domain_metadata.json`
  - Call `adapter.initializeRepos([{itemType: 'users'}, {itemType: 'tasks'}])`
  - Push metadata: `adapter.pushExternalDomainMetadata()`

### Phase 3: Data Extraction

- **Worker**: `workers/data-extraction.ts`
- **Purpose**: Extract primary data (users, tasks, issues)
- **Events**: `ExtractionDataStart/Continue` → `ExtractionDataProgress` → `ExtractionDataDone`
- **State Pattern**:

```typescript
interface State {
  users: { completed: boolean; offset: string; modifiedSince?: string };
  tasks: { completed: boolean; offset: string; modifiedSince?: string };
}
```

- **Actions**:
  - Fetch data with pagination
  - Push to repos: `adapter.getRepo('users')?.push({ external_id, name, email })`
  - Emit progress on pagination: `adapter.emit(ExtractionDataProgress, { state })`
  - Support incremental sync via `modifiedSince` timestamp

### Phase 4: Attachments Extraction

- **Worker**: `workers/attachments-extraction.ts`
- **Purpose**: Extract file attachments
- **Events**: `ExtractionAttachmentsStart/Continue` → `ExtractionAttachmentsProgress` → `ExtractionAttachmentsDone`
- **Actions**:
  - Download file content: `client.downloadFile(url)`
  - Push: `attachmentsRepo.push({ external_id, filename, file_data, parent_id })`

---

## Loading Phases (Bidirectional Only)

### Phase 1: Data Loading

- **Worker**: `workers/load-data.ts`
- **Purpose**: Create/update items in external system
- **Events**: `StartLoadingData/Continue` → `DataLoadingProgress` → `DataLoadingDone`
- **Pattern**: Define handlers with `create` and `update` functions, call `adapter.loadItemTypes()`

### Phase 2: Attachments Loading

- **Worker**: `workers/load-attachments.ts`
- **Purpose**: Upload attachments to external system
- **Events**: `StartLoadingAttachments/Continue` → `AttachmentsLoadingProgress` → `AttachmentsLoadingDone`
- **Actions**: Upload files, confirm with `adapter.confirmAttachmentLoaded()`

---

## Key Files

### function-factory.ts

Central registry exposing functions:

```typescript
export const functionFactory = {
  extraction,
  loading, // Bidirectional only
  install_initial_domain_mapping, // Bidirectional only
  validate_configuration, // Optional
} as const;
```

### extraction/index.ts

Routes events to workers:

```typescript
await spawn<State>({
  event,
  initialState,
  baseWorkerPath: __dirname,
  initialDomainMapping,
});
```

### client.ts

API wrapper for external system:

```typescript
export class ConnectorClient {
  constructor(event: AirdropEvent) {
    const { api_token, base_url } = event.input_data.keyrings.connection;
    this.httpClient = axios.create({ baseURL: base_url, headers: {...} });
  }
  async getProjects(options?: { offset?: string; limit?: number }) { ... }
  async getTasks(options?: { modifiedSince?: string; ... }) { ... }
  async createTask(task) { ... }
  async downloadFile(url): Promise<Buffer> { ... }
}
```

### initial_domain_mapping.json

Maps external fields to DevRev objects:

```json
{
  "additional_mappings": {
    "record_type_mappings": {
      "tasks": {
        "default_mapping": { "object_type": "issue" },
        "possible_record_type_mappings": [
          {
            "devrev_leaf_type": "issue",
            "shard": {
              "stock_field_mappings": {
                "title": { "from_path": "$.title" },
                "created_date": { "from_path": "$.created_at" }
              },
              "constructed_custom_fields": {
                "status": { "field_type": "text", "from_path": "$.status" }
              }
            }
          }
        ]
      }
    }
  }
}
```

### external_domain_metadata.json

Defines external system schema:

```json
{
  "external_schema_version": "1.0",
  "item_types": {
    "tasks": {
      "fields": {
        "id": { "type": "string", "required": true },
        "title": { "type": "string", "required": true },
        "status": { "type": "enum", "enum_values": ["open", "closed"] },
        "assignee_id": { "type": "string", "references": "users" }
      }
    }
  }
}
```
