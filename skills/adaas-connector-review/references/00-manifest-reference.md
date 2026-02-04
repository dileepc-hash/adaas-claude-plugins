# Manifest.yaml Reference Guide

## Overview

The `manifest.yaml` file is the configuration foundation of every AirSync connector. It defines authentication methods, functions, inputs, and all components required for data synchronization between DevRev and external systems.

**Location:** `<connector-root>/manifest.yaml`

---

## Navigation

This reference is organized into focused topic guides:

1. **[Authentication](./manifest-reference/01-authentication.md)** - Secret, OAuth2, and Keyrings V2 patterns
2. **[Configuration](./manifest-reference/02-configuration.md)** - Functions, imports, inputs, and hooks
3. **[Anti-Patterns](./manifest-reference/03-anti-patterns.md)** - Common mistakes with examples
4. **[Validation](./manifest-reference/04-validation.md)** - Final validation checklist

---

## Complete Manifest Structure

```yaml
version: "2"

name: <Connector Name>
description: <Connector Description>

service_account:
  display_name: <Bot Display Name>

# Optional: Developer-provided credentials for OAuth2
developer_keyrings:
  - name: <keyring_name>
    description: <description>
    display_name: <display_name>

# Authentication configuration
keyring_types:
  - id: <connection_id>
    name: <connection_name>
    description: <description>
    kind: "Secret" | "Oauth2"
    is_subdomain: true | false
    external_system_name: <External System Name>
    secret_config: {...}      # For Secret type
    scopes: [...]             # For OAuth2 type
    authorize: {...}          # For OAuth2 type
    refresh: {...}            # For OAuth2 type
    revoke: {...}             # Optional for OAuth2

# Alternative V2 pattern (organization keyrings)
keyrings:
  organization:
    - name: <keyring_name>
      description: <description>
      display_name: <display_name>
      types:
        - <predefined_keyring_type>

# Function definitions
functions:
  - name: extraction
    description: <description>
  - name: loading            # Optional
    description: <description>

# Import configuration
imports:
  - slug: <unique_identifier>
    display_name: <display_name>
    description: <description>
    extractor_function: extraction
    loader_function: loading  # Optional
    allowed_connection_types:
      - <connection_id>
    capabilities:             # Optional
      - TIME_SCOPED_SYNCS
      - COMPUTER_READY

# User-configurable inputs
inputs:
  organization:
    - name: <input_name>
      description: <description>
      field_type: bool | text | enum | int | float
      default_value: <value>
      is_required: true | false
      ui:
        display_name: <display_name>
  user:                       # Optional
    - name: <input_name>
      # Same structure as organization inputs

# Optional: Lifecycle hooks
hooks:
  - type: validate | activate | update
    function: <function_name>
```

---

## Quick Reference: Placeholder Syntax

| Placeholder                      | Usage                          | Context              |
| -------------------------------- | ------------------------------ | -------------------- |
| `[API_KEY]`                      | Transformed secret value       | Secret keyrings      |
| `[ACCESS_TOKEN]`                 | OAuth access token             | OAuth2 keyrings      |
| `[REFRESH_TOKEN]`                | OAuth refresh token            | OAuth2 refresh       |
| `[CLIENT_ID]`                    | OAuth client ID                | OAuth2 authorize     |
| `[CLIENT_SECRET]`                | OAuth client secret            | OAuth2 refresh       |
| `[CLIENT_CREDENTIALS_BASE64]`    | Base64(client_id:client_secret)| OAuth2 Basic Auth    |
| `[SCOPES]`                       | Space/comma-joined scopes      | OAuth2 authorize     |
| `[SUBDOMAIN]`                    | User-provided subdomain        | is_subdomain: true   |
| `[ORGANIZATION_ID]`              | Fetched organization ID        | organization_data    |

---

## Examples by Authentication Type

### Secret - Simple Token
- **GitHub**, Slack, Notion, Linear, Intercom

### Secret - Email + Token (Base64)
- **Confluence**, Jira, Freshdesk

### Secret - Multi-field JSON
- **Snowflake**, MS Fabric, Workday

### OAuth2 - Space-delimited Scopes
- **Gong**, Azure DevOps, Outlook, SharePoint

### OAuth2 - Comma-delimited Scopes
- **Linear**, HubSpot

### OAuth2 - URL Scopes
- **Google Drive**, Google Calendar, Google Docs

---

## Related Documents

- [01-project-structure.md](./01-project-structure.md) - Project structure and manifest validation
- [02-metadata-extraction.md](./02-metadata-extraction.md) - Metadata phase implementation
- [12-security-checklist.md](./12-security-checklist.md) - Security considerations

---

## Summary

The manifest.yaml is critical for connector functionality:

1. **Authentication** - Properly configure Secret or OAuth2 keyrings
2. **Functions** - Ensure extraction is defined, loading only if implemented
3. **Imports** - Link functions to connection types with correct slug
4. **Inputs** - Provide user-configurable options with safe defaults
5. **Validation** - Use checklist to catch common mistakes

**Most common mistakes:**
- Template defaults not updated
- is_subdomain incorrectly set
- Missing organization_data
- Mismatched function names
- Invalid secret_transform syntax

For detailed guidance on each section, see the topic-specific guides in [manifest-reference/](./manifest-reference/).
