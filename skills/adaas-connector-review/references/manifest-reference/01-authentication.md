# Authentication

## Overview

This guide covers authentication configuration in `manifest.yaml`, including Secret (API key/token), OAuth2, and Keyrings V2 patterns. Authentication defines how connectors authenticate with external systems and fetch organization identity.

---

## Basic Information

### Version

Always use manifest version 2:

```yaml
version: "2"
```

### Name and Description

The `name` should be the external system name (not a template default), and `description` should clearly explain what data is synced.

```yaml
name: GitHub
description: GitHub connector for importing issues, markdown files, and users
```

### Service Account

The `service_account.display_name` identifies the bot in DevRev.

```yaml
service_account:
  display_name: GitHub Integration Bot
```

---

## Secret Authentication

Secret authentication uses API keys, tokens, or credentials that are transformed and used in API requests.

### Pattern 1: Simple Token

Most straightforward pattern - a single token field.

```yaml
keyring_types:
  - id: github-connection
    name: GitHub Connection
    description: GitHub Personal Access Token connection
    kind: "Secret"
    is_subdomain: true
    external_system_name: GitHub
    secret_config:
      # Transform extracts just the token field
      secret_transform: ".token"
      fields:
        - id: token
          name: GitHub PAT
          description: Personal Access Token with repo and read:user permissions
          input_type: password
      token_verification:
        url: "https://api.github.com/user/repos"
        method: "GET"
        headers:
          Authorization: "Bearer [API_KEY]"
          Accept: "application/vnd.github+json"
          X-GitHub-Api-Version: "2022-11-28"
```

### Pattern 2: Bearer Token with Prefix

Adds "Bearer " prefix to the token.

```yaml
keyring_types:
  - id: slack-connection
    name: Slack Connection
    kind: "Secret"
    external_system_name: Slack
    secret_config:
      # Adds "Bearer " prefix to token
      secret_transform: '"Bearer "+.token'
      fields:
        - id: token
          name: Slack Bot Token
          description: Bot token starting with xoxb-
          input_type: password
      token_verification:
        url: "https://slack.com/api/auth.test"
        method: "GET"
        headers:
          Authorization: "[API_KEY]"
```

### Pattern 3: Multi-Field with Base64 Encoding

Combines multiple fields (like email:token) and encodes to Base64.

```yaml
keyring_types:
  - id: atlassian-pat
    name: Atlassian PAT
    description: Atlassian Personal Access Token
    kind: "Secret"
    external_system_name: Confluence Cloud
    is_subdomain: true
    secret_config:
      # Combines email:token and encodes to Base64
      secret_transform: .email + ":" + .token | @base64
      fields:
        - id: email
          name: Email
          description: Atlassian account email
        - id: token
          name: PAT
          description: Atlassian Personal Access Token
          input_type: password
      token_verification:
        url: "https://[SUBDOMAIN]/wiki/api/v2/pages"
        method: GET
        headers:
          Authorization: "Basic [API_KEY]"
```

### Pattern 4: Complex JSON Transform

Creates a JSON object with multiple fields.

```yaml
keyring_types:
  - id: snowflake-connection
    name: Snowflake Key Pair Authentication
    kind: "Secret"
    external_system_name: Snowflake
    is_subdomain: false
    secret_config:
      # Creates JSON object with all fields
      secret_transform: "{username: .username, privateKey: .privateKey, privateKeyPassphrase: .privateKeyPassphrase, account_identifier: .account_identifier, warehouse_name: .warehouse_name, role: .role}"
      fields:
        - id: username
          name: Username
          description: Snowflake username
        - id: privateKey
          name: Private Key
          description: RSA private key in PEM format
          input_type: password
        - id: privateKeyPassphrase
          name: Private Key Passphrase
          description: Optional passphrase for encrypted private key
          input_type: password
          is_optional: true
        - id: account_identifier
          name: Account Identifier
          description: Format - <orgname>-<account_name>
        - id: warehouse_name
          name: Warehouse Name
          description: Snowflake warehouse name
        - id: role
          name: Role
          description: Optional role name
          is_optional: true
      token_verification:
        url: "https://[ORGANIZATION_ID].snowflakecomputing.com/api/v2/statements"
        method: POST
        headers:
          Content-Type: "application/json"
      organization_data:
        type: "config"
        url: "https://[API_KEY].snowflakecomputing.com/api/v2/databases"
        method: "GET"
        response_jq: "{id: .account_identifier, name: .account_identifier}"
```

### Pattern 5: GraphQL Token Verification

Uses GraphQL endpoint to verify token validity.

```yaml
keyring_types:
  - id: linear-connection
    name: Linear Connection
    kind: "Secret"
    external_system_name: Linear
    is_subdomain: false
    secret_config:
      secret_transform: ".token"
      fields:
        - id: token
          name: Linear API Key
          input_type: password
      token_verification:
        url: "https://api.linear.app/graphql"
        method: "POST"
        headers:
          Authorization: "Bearer [API_KEY]"
          Content-Type: "application/json"
        body: |
          {
            "query": "query { viewer { id name email } }"
          }
```

### is_subdomain Configuration

The `is_subdomain` field determines how API URLs are constructed:

- **`is_subdomain: true`** - API URLs contain organization subdomain (e.g., `org.service.com`)
  - Use `[SUBDOMAIN]` placeholder in URLs
  - Example: Confluence Cloud, Jira Cloud, Asana

- **`is_subdomain: false`** - API URLs don't contain subdomain (e.g., `api.service.com`)
  - Must configure `organization_data` to fetch organization ID
  - Example: Linear, Gong, Notion

### Organization Data Configuration

Required when `is_subdomain: false`. Returns organization identifier and name in format `{id, name}`.

#### REST API Pattern

```yaml
organization_data:
  type: "config"
  url: "https://api.gong.io/v2/calls"
  method: "GET"
  headers:
    Authorization: "[API_KEY]"
    Content-Type: "application/json"
  # Extracts domain from first call's URL
  response_jq: "{id: (.calls[0].url | split(\"://\") | .[1] | split(\"/\") | .[0] | sub(\"app\\\\.gong\\\\.io\"; \"api.gong.io\")) , name: (.calls[0].url | split(\"://\") | .[1] | split(\"/\") | .[0] | sub(\"app\\\\.gong\\\\.io\"; \"api.gong.io\"))}"
```

#### GraphQL Pattern

```yaml
organization_data:
  type: "config"
  url: "https://api.linear.app/graphql"
  method: "POST"
  headers:
    Authorization: "Bearer [API_KEY]"
    Content-Type: "application/json"
  body: |
    {
      "query": "query { organization { id name } }"
    }
  response_jq: ".data.organization | {id:.id, name:.name}"
```

#### Static ID Pattern

For services without organization endpoints, use static identifier.

```yaml
organization_data:
  type: "config"
  url: "https://api.notion.com/v1/users/me"
  method: "GET"
  headers:
    Authorization: "Bearer [API_KEY]"
    Notion-Version: "2022-02-22"
  response_jq: "{id: \"notion-org\", name: \"Notion Workspace\"}"
```

---

## OAuth2 Authentication

OAuth2 provides secure authentication without sharing credentials. Requires developer keyring for client credentials.

### Developer Keyring Declaration

OAuth2 connectors must declare a developer keyring to store client ID and secret:

```yaml
developer_keyrings:
  - name: gong_oauth_secret
    description: Gong OAuth 2.0 client credentials
    display_name: Gong OAuth Secret
```

### Complete OAuth2 Example

```yaml
# Developer keyring for OAuth client credentials
developer_keyrings:
  - name: gong_oauth_secret
    description: Gong OAuth 2.0 client credentials
    display_name: Gong OAuth Secret

keyring_types:
  - id: gong-oauth-connection
    name: Gong OAuth Connection
    description: |
      Connect to Gong using OAuth 2.0 authentication. This provides secure access without sharing credentials.
      Required for accessing calls, transcripts, recordings, and user data.
    kind: "Oauth2"
    external_system_name: "Gong"

    # OAuth scopes with descriptive names
    scopes:
      - name: workspaces_read
        description: Read workspace information
        value: "api:workspaces:read"
      - name: calls_read_basic
        description: Read basic call information
        value: "api:calls:read:basic"
      - name: calls_read_extensive
        description: Read extensive call data including participants and content
        value: "api:calls:read:extensive"
      - name: calls_read_transcript
        description: Read call transcripts
        value: "api:calls:read:transcript"
      - name: calls_read_media
        description: Access call recordings
        value: "api:calls:read:media"
      - name: users_read
        description: Read user information
        value: "api:users:read"

    scope_delimiter: " "
    oauth_secret: gong_oauth_secret

    # Authorization configuration
    authorize:
      type: "config"
      auth_url: "https://app.gong.io/oauth2/authorize"
      token_url: "https://app.gong.io/oauth2/generate-customer-token"
      grant_type: "authorization_code"
      auth_query_parameters:
        "client_id": "[CLIENT_ID]"
        "scope": "[SCOPES]"
        "response_type": "code"
      token_headers:
        "Authorization": "Basic [CLIENT_CREDENTIALS_BASE64]"
      token_query_parameters:
        "client_id": "[CLIENT_ID]"

    # Token refresh configuration
    refresh:
      type: "config"
      url: "https://app.gong.io/oauth2/generate-customer-token"
      method: "POST"
      headers:
        "Authorization": "Basic [CLIENT_CREDENTIALS_BASE64]"
      query_parameters:
        "grant_type": "refresh_token"
        "refresh_token": "[REFRESH_TOKEN]"

    # Organization data fetching
    organization_data:
      type: "config"
      url: "https://api.gong.io/v2/calls"
      method: "GET"
      headers:
        Authorization: "Bearer [ACCESS_TOKEN]"
        Content-Type: "application/json"
      response_jq: "{id: (.calls[0].url | split(\"://\") | .[1] | split(\"/\") | .[0] | sub(\"app\\\\.gong\\\\.io\"; \"api.gong.io\")) , name: (.calls[0].url | split(\"://\") | .[1] | split(\"/\") | .[0] | sub(\"app\\\\.gong\\\\.io\"; \"api.gong.io\"))}"
```

### Scope Configuration

Scopes define what data the connector can access. Always provide descriptive names and explanations.

#### Space-delimited (Most Common)

```yaml
scopes:
  - name: read
    value: "read"
  - name: write
    value: "write"
scope_delimiter: " "
```

#### Comma-delimited

```yaml
scopes:
  - name: read
    value: "read"
  - name: write
    value: "write"
scope_delimiter: ","
```

#### URL-based (Google, Azure)

```yaml
scopes:
  - name: drive
    value: "https://www.googleapis.com/auth/drive.readonly"
  - name: directory
    value: "https://www.googleapis.com/auth/admin.directory.user.readonly"
scope_delimiter: " "
```

### Token Revocation (Optional)

Allows users to revoke OAuth tokens when disconnecting.

```yaml
revoke:
  type: "config"
  url: "https://api.hubapi.com/oauth/v1/refresh-tokens"
  method: "DELETE"
  query_parameters:
    "token": "[REFRESH_TOKEN]"
  headers:
    "Content-type": "application/x-www-form-urlencoded"
```

### OAuth2 Placeholders

| Placeholder                      | Usage                          | Context              |
| -------------------------------- | ------------------------------ | -------------------- |
| `[ACCESS_TOKEN]`                 | OAuth access token             | OAuth2 keyrings      |
| `[REFRESH_TOKEN]`                | OAuth refresh token            | OAuth2 refresh       |
| `[CLIENT_ID]`                    | OAuth client ID                | OAuth2 authorize     |
| `[CLIENT_SECRET]`                | OAuth client secret            | OAuth2 refresh       |
| `[CLIENT_CREDENTIALS_BASE64]`    | Base64(client_id:client_secret)| OAuth2 Basic Auth    |
| `[SCOPES]`                       | Space/comma-joined scopes      | OAuth2 authorize     |

---

## Keyrings V2

Alternative pattern using pre-defined, reusable keyring types instead of declaring full configuration.

### Example

```yaml
keyrings:
  organization:
    - name: sharepoint-oauth-connection
      description: SharePoint OAuth connection
      display_name: SharePoint OAuth connection
      types:
        - devrev-microsoft-sharepoint-oauth
```

### When to Use

- When using pre-defined, reusable keyring types
- For Microsoft services (SharePoint, Outlook, etc.)
- When keyring definition is managed centrally by DevRev platform

### Scope Options

- **organization**: Shared across all users
- **user**: Per-user authentication

---

## Checks

- [ ] Version is "2"
- [ ] Name is not template default (e.g., not "Todo")
- [ ] Name is unique and recognizable (different variants need different names)
- [ ] Description explains what data is synced
- [ ] Description mentions bidirectional sync if applicable
- [ ] service_account.display_name clearly identifies the external system
- [ ] external_system_name is unique and starts with capital letter
- [ ] kind is "Secret" or "Oauth2" (correctly specified)
- [ ] secret_transform uses valid jq syntax
- [ ] secret_transform matches what the API expects (e.g., includes Base64 encoding if needed)
- [ ] All required fields are included in secret_transform
- [ ] Sensitive fields use input_type: password
- [ ] is_optional set for optional credential fields
- [ ] token_verification endpoint actually validates the token
- [ ] token_verification returns appropriate status codes (200 for valid, 401 for invalid)
- [ ] is_subdomain correctly reflects API URL structure (true if subdomain-based, false otherwise)
- [ ] organization_data configured when is_subdomain is false
- [ ] organization_data returns unique id and name
- [ ] organization_data jq filter is correct and handles API response structure
- [ ] All placeholders use correct format: [API_KEY], [SUBDOMAIN], [ORGANIZATION_ID]
- [ ] For OAuth2: developer_keyrings declared
- [ ] For OAuth2: oauth_secret references declared developer keyring
- [ ] For OAuth2: scopes defined with clear, descriptive names
- [ ] For OAuth2: scope descriptions explain what functionality each enables
- [ ] For OAuth2: scopes grant minimum necessary permissions
- [ ] For OAuth2: scope_delimiter is correct (check API docs - usually space " " or comma ",")
- [ ] For OAuth2: auth_url and token_url are correct (verify against API docs)
- [ ] For OAuth2: refresh configuration includes all required parameters
- [ ] For OAuth2: all OAuth placeholders use correct format
- [ ] For Keyrings V2: referenced keyring type exists (verify with DevRev platform team)
- [ ] For Keyrings V2: correct scope used (organization vs user)

---

## Related Documents

- [02-configuration.md](./02-configuration.md) - Functions, imports, inputs, and hooks
- [03-anti-patterns.md](./03-anti-patterns.md) - Common authentication mistakes
- [04-validation.md](./04-validation.md) - Final validation checklist
