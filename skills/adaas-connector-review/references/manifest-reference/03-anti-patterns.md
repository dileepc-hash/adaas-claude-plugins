# Common Anti-Patterns

## Overview

This guide identifies the most critical manifest.yaml mistakes with clear BAD/GOOD examples. For automated detection and testing, see [04-validation.md](./04-validation.md).

---

## 1. Template Defaults Not Updated

Using default values from connector templates without customization.

### BAD

```yaml
# Template defaults left in place
name: Todo
external_system_name: Todo
slug: airdrop-todo-snap-in
```

**Problem**: Template defaults make connector unidentifiable and break snap-in activation.

### GOOD

```yaml
# Properly customized
name: Asana
external_system_name: Asana
slug: airdrop-asana-extractor
```

---

## 2. Mismatched Function Names

Function names declared in `functions` section don't match references in `imports`.

### BAD

```yaml
# Function names don't match
functions:
  - name: extract
imports:
  - extractor_function: extraction # Mismatch!
```

**Problem**: Snap-in fails to execute because function reference is invalid.

### GOOD

```yaml
# Consistent naming
functions:
  - name: extraction
imports:
  - extractor_function: extraction
```

---

## 3. Missing Connection Types

`allowed_connection_types` references keyrings that aren't defined.

### BAD

```yaml
# Connection type not defined
imports:
  - allowed_connection_types:
      - my-connection # Not in keyring_types!
```

**Problem**: Users cannot create connections because keyring type doesn't exist.

### GOOD

```yaml
# Properly linked
keyring_types:
  - id: my-connection
imports:
  - allowed_connection_types:
      - my-connection
```

---

## 4. Wrong is_subdomain Setting

`is_subdomain` doesn't match API URL structure.

### BAD

```yaml
# is_subdomain: true but no subdomain in URL
keyring_types:
  - id: linear-connection
    is_subdomain: true # Linear uses api.linear.app (no subdomain!)
    token_verification:
      url: "https://api.linear.app/graphql" # No [SUBDOMAIN] placeholder
```

**Problem**: Connector fails because it expects subdomain that doesn't exist.

### GOOD

```yaml
# Correct configuration
keyring_types:
  - id: linear-connection
    is_subdomain: false
    token_verification:
      url: "https://api.linear.app/graphql"
    organization_data:
      type: "config"
      url: "https://api.linear.app/graphql"
      method: "POST"
      response_jq: ".data.organization | {id:.id, name:.name}"
```

**Rule**: If `is_subdomain: true`, URLs must contain `[SUBDOMAIN]` placeholder.

---

## 5. Missing organization_data When Required

`is_subdomain: false` but no `organization_data` configured.

### BAD

```yaml
# is_subdomain: false but no organization_data
keyring_types:
  - id: gong-connection
    is_subdomain: false
    # Missing organization_data!
```

**Problem**: Connector cannot identify organization without subdomain or organization_data.

### GOOD

```yaml
# organization_data configured
keyring_types:
  - id: gong-connection
    is_subdomain: false
    organization_data:
      type: "config"
      url: "https://api.gong.io/v2/calls"
      method: "GET"
      response_jq: "{id: .calls[0].url, name: .calls[0].url}"
```

**Rule**: If `is_subdomain: false`, must have `organization_data` configured.

---

## 6. Incorrect secret_transform Syntax

Invalid or incomplete jq syntax in `secret_transform` causes token verification failures.

### BAD

```yaml
# Invalid jq syntax
secret_config:
  secret_transform: .email + ":" + .token # Missing | @base64
```

**Problem**: Token verification fails because secret format is incorrect.

### GOOD

```yaml
# Complete transform
secret_config:
  secret_transform: .email + ":" + .token | @base64
```

### Common Mistakes

1. Missing Base64 encoding when required
2. Invalid jq syntax
3. Wrong field references
4. Missing quotes in string literals

---

## 7. Non-Unique organization_data Identifiers

Using values that aren't stable and unique at the organization level. The `id` must consistently identify ONE specific organization.

### BAD

```yaml
# Workspace name - same org can have multiple workspaces
organization_data:
  type: "config"
  url: "https://api.notion.com/v1/users/me"
  method: "GET"
  headers:
    "Authorization": "Bearer [ACCESS_TOKEN]"
  response_jq: '{"id": .bot.workspace_name, "name": .bot.workspace_name}'
```

```yaml
# Public email domain - multiple orgs share gmail.com
organization_data:
  type: "config"
  url: "https://www.googleapis.com/drive/v3/about?fields=user"
  method: "GET"
  headers:
    "Authorization": "Bearer [ACCESS_TOKEN]"
  response_jq: '{"id": (.user.emailAddress | split("@")[1]), "name": (.user.emailAddress | split("@")[1])}'
```

**Problem**: Non-stable IDs cause connection conflicts and data isolation issues. Same org gets different IDs (workspace-level), or different orgs get same ID (public domains).

### GOOD

```yaml
# Account-level identifier
organization_data:
  type: "config"
  url: "https://api.hubapi.com/oauth/v1/access-tokens/[ACCESS_TOKEN]"
  method: "GET"
  response_jq: '{"id": .hub_id, "name": .hub_domain}'
```

```yaml
# Organization entity from API
organization_data:
  type: "config"
  url: "https://api.linear.app/graphql"
  method: "POST"
  headers:
    "Authorization": "Bearer [ACCESS_TOKEN]"
    "Content-Type": "application/json"
  body: |
    {
      "query": "query { organization { id name } }"
    }
  response_jq: ".data.organization | {id:.id, name:.name}"
```

```yaml
# Corporate email domain (with validation)
organization_data:
  type: "config"
  url: "https://api.example.com/user/me"
  method: "GET"
  headers:
    "Authorization": "Bearer [ACCESS_TOKEN]"
  response_jq: '{"id": (.email | split("@")[1]), "name": .company_name}'
```

**Note**: Corporate domains (acme.com) are valid. Must validate against public domains (gmail.com, yahoo.com).

### Common Mistakes

1. **Workspace/team IDs** - Org can have multiple workspaces (same org → different IDs)
2. **Public email domains** - Multiple orgs share gmail.com, yahoo.com (different orgs → same ID)
3. **Same field for id and name** - Defeats purpose of separate fields
4. **Hard-coded values** - All orgs get same ID
5. **Not understanding hierarchy** - Some systems (Notion, Asana) have no org-level ID above workspaces

### Rule

- **`id`**: Must be stable and unique per organization
  - ✓ GOOD: Organization ID, account ID, hub ID, corporate domain (validated)
  - ✗ BAD: Workspace names/IDs, public domains, team names, user emails, hardcoded values

**Tests**:
- ❌ Same org gets different IDs? → WRONG
- ❌ Different orgs get same ID? → WRONG
- ✅ Each org always gets same unique ID? → CORRECT

---

## Related Documents

- [01-authentication.md](./01-authentication.md) - Authentication configuration patterns
- [02-configuration.md](./02-configuration.md) - Functions, imports, inputs with detailed checks
- [04-validation.md](./04-validation.md) - Automated detection and testing commands
