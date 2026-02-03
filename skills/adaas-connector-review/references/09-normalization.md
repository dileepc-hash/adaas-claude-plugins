# Data Normalization & Denormalization Review

## Overview

- **Normalization**: External → DevRev (extraction)
- **Denormalization**: DevRev → External (loading)

---

## Normalization (Extraction)

### MUST Follow

- [ ] **Returns correct structure** - `{ id, created_date, modified_date, data: {...} }`
- [ ] **ID is string** - Even if external ID is numeric
- [ ] **Timestamps are RFC3339** - `"2024-01-15T10:30:00Z"`
- [ ] **Dates are YYYY-MM-DD** - `"2024-01-15"`
- [ ] **Null values are null** - Not `""`, `-1`, or `"null"`
- [ ] **References are string IDs** - Not objects
- [ ] **Numbers stay numbers** - Not stringified
- [ ] **Arrays stay arrays** - Not comma-separated strings
- [ ] **HTML fields sanitized** - Omit `<script>` tags to prevent XSS

### SHOULD Follow

- [ ] **Work items have `item_url_field`** - URL to external item
- [ ] **Field names match metadata exactly** - Case-sensitive
- [ ] **Rich text is CommonMark** - If markdown field

---

## Denormalization (Loading)

### MUST Follow

- [ ] **Resolves DevRev ID references to external IDs** - Via object mapper
- [ ] **Maps enum values correctly** - DevRev enum → external enum
- [ ] **Converts timestamps to external format** - If different from RFC3339

### SHOULD Follow

- [ ] **Validates required fields** - Before API call
- [ ] **Handles missing optional fields** - Doesn't include undefined

---

## Normalized Item Structure

```typescript
{
  id: "ext-123",                              // String ID
  created_date: "2024-01-15T10:30:00Z",       // RFC3339
  modified_date: "2024-01-15T10:30:00Z",      // RFC3339
  data: {
    title: "Issue title",
    owner: "user-456",                        // Reference as string
    priority: 2,                              // Number, not string
    tags: ["bug", "urgent"],                  // Array, not CSV
    due_date: "2024-02-01",                   // Date (YYYY-MM-DD)
    item_url_field: "https://ext.com/issue/123"
  }
}
```

---

## Common Anti-Patterns

| Anti-Pattern | BAD | GOOD |
|--------------|-----|------|
| Wrong timestamp | `1705315800` or `"Jan 15"` | `new Date(item.createdAt).toISOString()` |
| Empty string for null | `description: ""` | `description: null` |
| Stringified numbers | `priority: String(item.p)` | `priority: item.p` |
| Object references | `owner: item.owner` | `owner: String(item.owner.id)` |
| CSV arrays | `tags: tags.join(",")` | `tags: tags` |
| Numeric IDs | `id: item.id` (number) | `id: String(item.id)` |
| Case mismatch | `Status: item.status` | `status: item.status` |

### Denormalization Anti-Patterns

```typescript
// BAD - Using DevRev ID directly
return { owner: data.owner };

// GOOD - Resolve to external ID
return { owner: await adapter.objectMapper.getByTargetId(data.owner) };

// BAD - Wrong enum value
return { priority: data.priority };  // "p0" (DevRev)

// GOOD - Map to external enum
const priorityMap = { p0: "critical", p1: "high" };
return { priority: priorityMap[data.priority] };
```

---

## Review Questions

```
Q1: Are timestamps RFC3339 and dates YYYY-MM-DD?
Q2: Are numeric IDs converted to strings?
Q3: Are missing values null (not empty strings)?
Q4: Are references string IDs (not objects)?
Q5: Is item_url_field present for work items?
Q6: Do field names match metadata exactly (case-sensitive)?
Q7: Are DevRev IDs resolved via objectMapper in denormalization?
```
