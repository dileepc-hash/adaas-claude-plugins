# Configuration Patterns

## Overview

This guide covers configuration sections in `manifest.yaml`: functions, imports, inputs, and hooks. These sections define connector capabilities, user inputs, and lifecycle behaviors.

---

## Functions

Functions define the code entry points for extraction, loading, and lifecycle hooks.

### Basic Function Declaration

```yaml
functions:
  - name: extraction
    description: Extract calls, transcripts, participants, and users from Gong
  - name: loading
    description: Create and update calls in Gong from DevRev
  - name: validate_configuration
    description: Validates input configuration before sync
```

### Function Types

- **extraction** - Always required. Fetches data from external system.
- **loading** - Optional. Only include if bidirectional sync is implemented.
- **Hook functions** - validate, activate, update (see Hooks section below).

### Naming Conventions

Follow standard naming conventions:

- Use `extraction` (not `extract`, `extractor`)
- Use `loading` (not `load`, `loader`)
- Use descriptive names for hook functions

---

## Imports

The imports section defines snap-in configuration, linking functions to connection types.

### Basic Structure

```yaml
imports:
  - slug: airdrop-<service>-snap-in
    display_name: <Service Name>
    description: <What data is synced and direction>
    extractor_function: extraction
    loader_function: loading # Optional
    allowed_connection_types:
      - <connection_id>
    capabilities: # Optional
      - TIME_SCOPED_SYNCS
      - COMPUTER_READY
```

### Slug Naming Convention

The slug is a unique identifier following this pattern:

```
airdrop-<service>-snap-in
airdrop-<service>-extractor
airdrop-<service>-extractor-loader
```

Examples:

- `airdrop-github-extractor-loader`
- `airdrop-gong-extractor`
- `airdrop-hubspot-snap-in`

### Example: Extraction Only

```yaml
imports:
  - slug: airdrop-github-extractor-loader
    display_name: GitHub
    description: Import GitHub issues, markdown files, and users into DevRev
    extractor_function: extraction
    allowed_connection_types:
      - github-connection
    capabilities:
      - TIME_SCOPED_SYNCS
```

### Example: Bidirectional Sync

```yaml
imports:
  - slug: airdrop-hubspot-snap-in
    display_name: HubSpot
    description: Bidirectional sync of contacts, companies, and deals between HubSpot and DevRev
    extractor_function: extraction
    loader_function: loading
    allowed_connection_types:
      - hubspot-oauth-connection
    capabilities:
      - TIME_SCOPED_SYNCS
```

### Example: Multiple Connection Types

Support both API key and OAuth authentication:

```yaml
imports:
  - slug: airdrop-gong-extractor
    display_name: Gong
    description: Import Gong sales calls with recordings, transcripts, and participants
    extractor_function: extraction
    allowed_connection_types:
      - gong-api-key-connection
      - gong-oauth-connection
    capabilities:
      - TIME_SCOPED_SYNCS
```

### Capabilities Reference

| Capability        | Description                        | Usage                 |
| ----------------- | ---------------------------------- | --------------------- |
| TIME_SCOPED_SYNCS | Supports incremental sync          | Most connectors       |
| COMPUTER_READY    | Optional and Platform Feature flag | Slack, Notion, DevRev |

**TIME_SCOPED_SYNCS**: Enables custom timestamp control for extraction scope. When enabled:

- Extraction receives optional `extract_from` parameter (RFC3339 timestamp)
- Incremental syncs receive optional `reset_extract_from` flag
- Connector must implement proper timestamp-based filtering
- Must track `lastSuccessfulSyncStarted` in state

**Requirements:**

1. Handle `extract_from` parameter in both initial and incremental syncs
2. Handle `reset_extract_from` flag in incremental syncs
3. Maintain `lastSuccessfulSyncStarted` in adapter state
4. Pass timestamps to external API for filtering

Only include if connector actually implements this logic.

---

## Inputs

Inputs define user-configurable settings displayed in DevRev UI.

### Basic Structure

```yaml
inputs:
  organization: # Applies to all users
    - name: <input_name>
      description: <description>
      field_type: bool | text | enum | int | float
      default_value: <value>
      is_required: true | false
      ui:
        display_name: <display_name>

  user: # Optional - Per-user settings
    - name: <input_name>
      # Same structure as organization inputs
```

### Field Types

| Field Type | Description        | Example              |
| ---------- | ------------------ | -------------------- |
| `bool`     | Boolean toggle     | `true`, `false`      |
| `text`     | Free-form text     | `"Team A, Team B"`   |
| `enum`     | Dropdown selection | `["main", "master"]` |
| `int`      | Integer number     | `100`                |
| `float`    | Decimal number     | `3.14`               |

### Pattern 1: Boolean Input

```yaml
inputs:
  organization:
    - name: sync_issues
      description: Import issues from GitHub. Disabling will only sync markdown files.
      field_type: bool
      default_value: true
      is_required: true
      ui:
        display_name: Sync Issues
```

### Pattern 2: Enum Input

```yaml
inputs:
  organization:
    - name: branch
      description: Branch to fetch markdown files from
      field_type: enum
      allowed_values:
        - main
        - master
        - develop
      is_required: true
      default_value: main
      ui:
        display_name: Select Branch
```

### Pattern 3: Text Input

```yaml
inputs:
  organization:
    - name: team_names
      description: Comma-separated list of team names. Only issues from these teams will be imported.
      field_type: text
      default_value: ""
      is_required: false
      ui:
        display_name: Team Names Filter
```

### Pattern 4: Organization vs User Inputs

Organization inputs apply to all users, while user inputs are per-user settings.

```yaml
inputs:
  organization:
    - name: import_as_public
      description: |
        Enabling this toggle will make all imported content accessible to your entire organization.
        If disabled, the original permissions will be preserved.
      field_type: bool
      default_value: false
      is_required: true
      ui:
        display_name: Content Visibility

  user:
    - name: sync_private_files
      description: Import your private files. This setting is per-user.
      field_type: bool
      default_value: false
      ui:
        display_name: Sync Private Files
```

### Pattern 5: Complex JSON Input

For advanced configuration requiring JSON structure:

```yaml
inputs:
  organization:
    - name: items_to_extract
      description: |
        SELECTIVE MODE: Provide a JSON object with DON IDs to extract specific items.
        Format: {"work": ["don:core:dvrv-us-1:devo/1:issue/123"], "accounts": [...]}
      field_type: text
      is_required: false
      default_value: ""
      ui:
        display_name: Items to Extract (JSON)
```

---

## Hooks

Hooks allow running custom functions at specific lifecycle events.

### Hook Types

| Hook Type  | When Triggered                     | Use Case                      |
| ---------- | ---------------------------------- | ----------------------------- |
| `validate` | Before snap-in activation          | Validate configuration inputs |
| `activate` | After snap-in activation           | Initialize domain mapping     |
| `update`   | After snap-in configuration update | Refresh domain mapping        |

### Example: Validation Hook

```yaml
hooks:
  - type: validate
    function: validate_configuration

functions:
  - name: validate_configuration
    description: Validates input configuration before sync
```

### Example: Activation Hook

```yaml
hooks:
  - type: activate
    function: install_initial_domain_mapping
  - type: update
    function: install_initial_domain_mapping

functions:
  - name: install_initial_domain_mapping
    description: Create blueprint and install initial domain mapping
```

### Hook Implementation Notes

- **validate** - Must return boolean (true to proceed, false to block)
- **activate** - Runs once after initial snap-in activation
- **update** - Runs after snap-in configuration changes

---

## Related Documents

- auth-patterns.md - Authentication configuration
- anti-patterns.md - Common configuration mistakes
- validation-rules.md - Validation checklist
