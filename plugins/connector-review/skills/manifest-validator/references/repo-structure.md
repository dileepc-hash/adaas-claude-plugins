# Connector Project Structure and Phases

## Directory Structure

### Root Level

```
connector-name/
├── manifest.yaml              # Connector configuration
├── marketplace.yaml           # Marketplace metadata
├── Makefile                   # Build automation
├── code/                      # TypeScript implementation
└── .github/workflows/
```

### Code Structure

```

code/
├── package.json
├── tsconfig.json
├── src/
│ ├── index.ts # Entry point
│ ├── function-factory.ts # Function registry
│ └── functions/
│ ├── extraction/
│ │ ├── index.ts
│ │ └── workers/ # Phase workers (4 files)
│ ├── loading/ # Bidirectional only
│ │ ├── index.ts
│ │ └── workers/ # Load workers (2 files)
│ └── [connector-name]/
│ ├── client.ts # API wrapper
│ ├── types.ts
│ ├── initial_domain_mapping.json
│ └── external_domain_metadata.json

```

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
