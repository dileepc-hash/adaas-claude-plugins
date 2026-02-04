# Project Structure and Manifest Review

## Overview

This document covers the review of connector project structure, manifest.yaml configuration, and overall setup.

---

## Expected Directory Structure

```
connector-name/
├── .circleci/config.yml          # CI/CD configuration
├── .devrev/repo.yml              # DevRev repo configuration
├── .gitignore
├── Makefile                      # Build and deployment automation (only local setup)
├── README.md                     # Documentation
├── manifest.yaml                 # Snap-in configuration
└── code/
    ├── package.json
    ├── package-lock.json
    ├── tsconfig.json
    ├── eslint.config.mts
    ├── jest.config.js
    ├── scripts/
    │   ├── deploy.sh
    │   └── cleanup.sh
    └── src/
        ├── index.ts
        ├── main.ts
        ├── function-factory.ts
        └── functions/
            ├── extraction/
            ├── loading/
            └── external-system/
```

---

## Review Checklist

### manifest.yaml

#### MUST Follow

- [ ] **`name` and `description` are set** - Not left as template defaults
- [ ] **`slug` is unique and descriptive** - Follows naming convention `airdrop-[service]-snap-in`
- [ ] **`extractor_function` matches function name** - Must correspond with `functions` section
- [ ] **`loader_function` matches (if 2-way sync)** - Must correspond with `functions` section
- [ ] **`keyring_types` properly configured** - Authentication method defined
- [ ] **`external_system_name` is unique in External System** - Starts with capital letter (e.g., "Asana", "Confluence Cloud","Google Calendar")
- [ ] **`token_verification` endpoint defined** - For secret-type keyrings
- [ ] **`allowed_connection_types` references valid keyring** - Must match keyring ID

#### SHOULD Follow

- [ ] **`is_subdomain` correctly set** - True if API URLs contain org subdomain
- [ ] **`organization_data` configured** - Required if `is_subdomain: false`, returns unique `id` and `name` in External System
- [ ] **`capabilities` declared if needed** - e.g., `TIME_SCOPED_SYNCS`
- [ ] **Service account properly named** - Descriptive name for DevRev operations
- [ ] **No `loader_function` if loading not implemented** - Remove unused loader_function
- [ ] **OAuth scopes have clear descriptions** - Explain what functionality each scope enables
- [ ] Comments explaining non-obvious configurations
- [ ] Clear, concise description

### Review Questions - manifest.yaml

```
Q1: Is the keyring type appropriate for this external system?
    - Does the external system support OAuth2? (preferred)
    - Is PAT/API key the only option?

Q2: Is subdomain handling correct?
    - Does the external system use subdomain-based URLs (e.g., org.service.com)?
    - Is organization_data configured if no subdomain?

Q3: Are all connection fields necessary?
    - Can any optional fields be removed?
    - Are field descriptions clear for end users?

Q4: Is token verification endpoint correct?
    - Does it actually validate the token?
    - Does it return appropriate status codes?

Q5: Is external_system_name unique in External System?
    - Different variants need different names (e.g., "Confluence Cloud" vs "Confluence Datacenter")

Q6: Is organization_data returning unique id and name?
    - Dynamic from API: `{ id: .gid, name: .name }`
    - Static: `{ id: "static-id", name: "Org Name" }`
```

---

### Package Configuration

#### MUST Follow (Critical)

- [ ] **@devrev/ts-adaas version should be latest** - **CRITICAL**: Check with `npm view @devrev/ts-adaas version` (minimum 1.13.0)
- [ ] **@devrev/typescript-sdk dependency present** - DevRev SDK
- [ ] **Version numbers are explicit** - Not using `*` or `latest`
- [ ] **package-lock.json committed** - Reproducible builds
- [ ] **TypeScript strict mode enabled** - `strict: true` in tsconfig.json
- [ ] **ESLint configured with strict rules** - Error on `any` usage, deprecation warnings

#### SHOULD Follow

- [ ] Prettier configured for formatting

#### Nice-to-Have

- [ ] Pre-commit hooks set up

### Review Questions - Package Config

```
Q1: Are all dependencies necessary?
    - Check for unused packages
    - Check for duplicate functionality

Q2: Are SDK versions up to date?
    - Run: npm view @devrev/ts-adaas version
    - Compare with version in package.json
    - Recommend upgrade if outdated
    - Check changelog for breaking changes
```

---

### File Organization

#### MUST Follow

- [ ] **Extraction workers in correct location** - `functions/extraction/workers/`
- [ ] **Loading workers in correct location** - `functions/loading/workers/`
- [ ] **External system code isolated** - `functions/external-system/`
- [ ] **Types defined in types.ts** - Not scattered across files
- [ ] **function-factory.ts exports both functions** - Extraction and loading

#### SHOULD Follow

- [ ] **Clear file naming** - Follows template convention
- [ ] **No business logic in index.ts** - Only routing/orchestration
- [ ] **Separation of concerns** - HTTP client, types, normalization separate

#### Nice-to-Have

- [ ] Test files alongside source files
- [ ] Consistent file naming (kebab-case)
- [ ] README in complex subdirectories

---

## Common Anti-Patterns

### 1. Template Defaults Not Updated

```yaml
# BAD - Template defaults left in place
name: Todo
external_system_name: Todo
slug: airdrop-todo-snap-in

# GOOD - Properly customized
name: Asana
external_system_name: "Asana"
slug: airdrop-asana-extractor
```

### 2. Mismatched Function Names

```yaml
# BAD - Function names don't match
functions:
  - name: extract
imports:
  - extractor_function: extraction  # Mismatch!

# GOOD - Consistent naming
functions:
  - name: extraction
imports:
  - extractor_function: extraction
```

### 3. Missing Connection Types

```yaml
# BAD - Connection type not defined
imports:
  - allowed_connection_types:
      - my-connection  # Not in keyring_types!

# GOOD - Properly linked
keyring_types:
  - id: my-connection
imports:
  - allowed_connection_types:
      - my-connection
```

### 4. Hardcoded URLs in Manifest

```yaml
# BAD - Environment-specific URLs
token_verification:
  url: https://api.staging.service.com/verify

# GOOD - Production URLs or configurable
token_verification:
  url: https://api.service.com/verify
```

### 5. Generic OAuth Scope Descriptions

```yaml
# BAD - Generic, unclear scope descriptions
keyring_types:
  - id: oauth
    type: oauth2
    oauth_scopes:
      - scope: read
        description: Read access
      - scope: write
        description: Write access

# GOOD - Specific descriptions explaining functionality
keyring_types:
  - id: oauth
    type: oauth2
    oauth_scopes:
      - scope: tasks:read
        description: Read tasks and task lists to sync into DevRev
      - scope: tasks:write
        description: Create and update tasks when syncing from DevRev
      - scope: users:read
        description: Read user information to map assignees
```
