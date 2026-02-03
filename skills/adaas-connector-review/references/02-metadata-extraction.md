# Metadata Extraction Phase Review

## Overview

The metadata extraction phase provides the `external_domain_metadata.json` file to AirSync, describing the external system's domain model including entities, types, relationships, and field definitions.

**Triggering Event:** `ExtractorEventType.MetadataExtractionStart`
**Success Event:** `ExtractorEventType.MetadataExtractionDone`
**Error Event:** `ExtractorEventType.MetadataExtractionError`

**Special Error Events (ExtractionCommonError):**
Use these for proper UI translation when external system supports detecting these scenarios:

- `EXTERNAL_SYNC_UNIT_DELETED` - Sync unit no longer exists in external system
- `EXTERNAL_SYNC_UNIT_DEACTIVATED` - Sync unit is deactivated/archived
- `USER_DELETED` - User account deleted or unauthorized

---

## File: `external_domain_metadata.json`

### MUST Follow

- [ ] **`schema_version` is set** - Currently `v0.2.0`
- [ ] **All extracted record types declared** - Must match `itemType` in repos
- [ ] **Required fields marked with `is_required: true`**
- [ ] **Field types match actual data types** - bool, int, float, text, rich_text, reference, enum, date, timestamp
- [ ] **ID, created_date, modified_date NOT declared** - These are implicit
- [ ] **Reference fields specify `refers_to`** - With `#record:` or `#category:` notation
- [ ] **Enum values defined for enum fields** - With all possible values
- [ ] **Field keys are case-sensitive and match extracted data**

### SHOULD Follow

- [ ] **Human-readable `name` for record types** - For UI display
- [ ] **Human-readable `name` for fields** - For UI display
- [ ] **Categories assigned to related record types** - For mapping flexibility
- [ ] **`is_loadable: true` for 2-way sync record types**
- [ ] **Deprecated enum values marked** - `is_deprecated: true`
- [ ] **Dynamic metadata fetched at runtime** - For customizable external systems
- [ ] **Stage diagrams configured** - For records with state transitions
- [ ] **Collections marked with `collection` key** - For array fields

### Nice-to-Have

- [ ] Custom link types declared with `link_naming_data`
- [ ] Field attributes set: `is_read_only`, `is_indexed`, `is_filterable`
- [ ] `reference_type` set for parent-child relationships

---

## File: `metadata-extraction.ts`

### MUST Follow

- [ ] **Uses `processTask` from SDK** - Standard worker pattern
- [ ] **Initializes repos correctly** - `adapter.initializeRepos(repos)`
- [ ] **Pushes metadata to repo** - `adapter.getRepo('external_domain_metadata')?.push([...])`
- [ ] **Emits single message** - Either done or error
- [ ] **Implements `onTimeout` callback** - Handles graceful exit
- [ ] **4xx errors emit error with message** - Client errors are non-retryable, emit error immediately (exceptions need comment explaining why)
- [ ] **5xx errors retry with warn log** - Server errors are retryable, log warning and retry (exceptions need comment explaining why)

### SHOULD Follow

- [ ] **Fetches dynamic metadata from API** - For custom fields/enums
- [ ] **Validates metadata before pushing** - Use chef-cli patterns
- [ ] **Uses ExtractionCommonError for special cases** - If external system supports detecting deleted/deactivated resources
- [ ] **No PII in logs** - Never log user emails, names, or sensitive data

### Nice-to-Have

- [ ] Error messages include context
- [ ] Handles API pagination for metadata endpoints

---

## Review Questions

```
Q1: Record Type Coverage
    - Are ALL entity types from the external system declared?
    - Are custom/user-defined record types handled?
    - Do record type names match exactly with itemType in data extraction?

Q2: Field Completeness
    - Are all fields that will be extracted declared?
    - Are required fields correctly identified?
    - Are optional fields handled (can be null)?

Q3: Reference Accuracy
    - Do reference fields point to correct record types?
    - Are bidirectional references handled?
    - Are parent-child relationships marked with reference_type?

Q4: Enum Values
    - Are enum values fetched dynamically if they're customizable?
    - Are deprecated values marked?
    - Do enum keys match actual data values?

Q5: Type Correctness
    - Are dates using 'date' type (YYYY-MM-DD)?
    - Are timestamps using 'timestamp' type (RFC3339)?
    - Are numbers declared as int/float, not text?
    - Are arrays marked as collections?

Q6: 2-Way Sync Readiness
    - Are loadable record types marked?
    - Are read-only fields marked?
    - Are stage diagrams defined for stateful records?

Q7: Special Error Handling
    - Does external system support detecting deleted/deactivated sync units?
    - Is ExtractionCommonError used for proper UI messaging?
```

---

## Supported Field Types Reference

| Type         | Description                   | Example                  |
| ------------ | ----------------------------- | ------------------------ |
| `bool`       | Boolean value                 | `true`, `false`          |
| `int`        | Integer                       | `42`                     |
| `float`      | Floating point                | `3.14`                   |
| `text`       | Plain text                    | `"Hello"`                |
| `rich_text`  | Formatted text (CommonMark)   | Markdown content         |
| `reference`  | ID pointing to another record | `"user-123"`             |
| `enum`       | Value from predefined set     | `"high"`, `"low"`        |
| `date`       | Date only                     | `"2024-01-15"`           |
| `timestamp`  | Full timestamp (RFC3339)      | `"2024-01-15T10:30:00Z"` |
| `struct`     | Complex nested object         | `{...}`                  |
| `permission` | Article permission            | See permissions doc      |
| `type_key`   | Type key mapping              | See permissions doc      |

---

## Common Anti-Patterns

### 1. Declaring Implicit Fields

```json
// BAD - id, created_date, modified_date should NOT be declared
{
  "record_types": {
    "issues": {
      "fields": {
        "id": { "type": "text" },           // WRONG!
        "created_date": { "type": "timestamp" },  // WRONG!
        "title": { "type": "text" }
      }
    }
  }
}

// GOOD - Only declare actual data fields
{
  "record_types": {
    "issues": {
      "fields": {
        "title": { "type": "text" }
      }
    }
  }
}
```

### 2. String Numbers Instead of Numeric Types

```json
// BAD - Numeric fields declared as text
{
  "priority": { "type": "text" }  // If values are 1, 2, 3

// GOOD - Use appropriate numeric type
{
  "priority": { "type": "int" }
}
```

### 3. Missing Reference Declarations

```json
// BAD - Reference without refers_to
{
  "owner": {
    "type": "reference"
    // Missing reference configuration!
  }
}

// GOOD - Complete reference declaration
{
  "owner": {
    "type": "reference",
    "reference": {
      "refers_to": {
        "#record:users": {}
      }
    }
  }
}
```

### 4. Hardcoded Enum Values for Dynamic Systems

```typescript
// BAD - Hardcoded enum values
const metadata = {
  fields: {
    status: {
      type: "enum",
      enum: { values: [{ key: "open" }, { key: "closed" }] }, // Might change!
    },
  },
};

// GOOD - Fetch from API
const statuses = await client.getStatuses();
const metadata = {
  fields: {
    status: {
      type: "enum",
      enum: {
        values: statuses.map((s) => ({ key: s.id, name: s.name })),
      },
    },
  },
};
```

### 5. Case Sensitivity Issues

```json
// BAD - Metadata key doesn't match data
{
  "fields": {
    "Title": { "type": "text" }  // Capital T
  }
}
// But extracted data has:
{ "data": { "title": "..." } }   // Lowercase t

// GOOD - Exact case match
{
  "fields": {
    "title": { "type": "text" }  // Matches data
  }
}
```

### 6. Missing Category for Similar Record Types

```json
// BAD - No category grouping
{
  "record_types": {
    "bug": { "fields": {...} },
    "feature": { "fields": {...} },
    "task": { "fields": {...} }
  }
}

// GOOD - Grouped by category
{
  "record_types": {
    "bug": { "category": "work_item", "fields": {...} },
    "feature": { "category": "work_item", "fields": {...} },
    "task": { "category": "work_item", "fields": {...} }
  },
  "record_type_categories": {
    "work_item": { "are_record_type_conversions_possible": true }
  }
}
```

### 7. Not Using ExtractionCommonError for Special Cases

```typescript
import { ExtractionCommonError, ExtractorEventType } from "@devrev/ts-adaas";

// BAD - Generic error for deleted sync unit
try {
  await client.getProject(projectId);
} catch (error) {
  if (error.response?.status === 404) {
    await adapter.emit(ExtractorEventType.ExtractionMetadataError, {
      error: { message: "Project not found" }, // Generic message
    });
  }
}

// GOOD - Use ExtractionCommonError for proper UI translation
try {
  await client.getProject(projectId);
} catch (error) {
  // Sync unit deleted
  if (error.response?.status === 404) {
    await adapter.emit(ExtractorEventType.ExtractionMetadataError, {
      error: { message: ExtractionCommonError.EXTERNAL_SYNC_UNIT_DELETED },
    });
    return;
  }
  // User unauthorized/deleted
  if (error.response?.status === 401 || error.response?.status === 403) {
    await adapter.emit(ExtractorEventType.ExtractionMetadataError, {
      error: { message: ExtractionCommonError.USER_DELETED },
    });
    return;
  }
}
```
