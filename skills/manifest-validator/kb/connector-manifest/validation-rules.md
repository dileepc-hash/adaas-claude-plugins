# Validation Rules

## How to Use This

1. **Read manifest.yaml** first
2. **Run checks** in order: CRITICAL → HIGH → MEDIUM
3. **Reference patterns** when needed:
   - Auth issues → auth-patterns.md
   - Config issues → config-patterns.md
   - Examples → anti-patterns.md
4. **Output results** with line numbers and specific fixes

---

## CRITICAL Checks (Must Pass)

### C1: Template Defaults
**What to check:**
- [ ] `name` is not "Todo" or template default
- [ ] `external_system_name` is not "Todo"
- [ ] `slug` is not "airdrop-todo-*"

**How to detect:**
```yaml
# Look for these patterns:
name: Todo
external_system_name: Todo
slug: airdrop-todo-snap-in
```

**Why it matters:** Template defaults break snap-in activation and make connector unidentifiable.

**Reference:** anti-patterns.md #1

---

### C2: Version
**What to check:**
- [ ] `version: "2"` (must be string "2")

**How to detect:**
```yaml
version: "2"  # ✅ Correct
version: 2    # ❌ Wrong (not string)
```

**Reference:** auth-patterns.md "Basic Information"

---

### C3: Function Name Consistency
**What to check:**
- [ ] All `functions[].name` values match their references in `imports`
- [ ] `imports.extractor_function` exists in `functions[].name`
- [ ] `imports.loader_function` exists in `functions[].name` (if present)

**How to detect:**
1. Extract all `functions[].name` values
2. Extract all `imports.extractor_function` and `imports.loader_function` values
3. Verify every import reference has matching function declaration

**Why it matters:** Snap-in fails to execute because function reference is invalid.

**Reference:** anti-patterns.md #2

---

### C4: Connection Types Defined
**What to check:**
- [ ] Every ID in `imports.allowed_connection_types[]` exists in `keyring_types[].id`

**How to detect:**
1. Extract all `imports.allowed_connection_types[]` values
2. Extract all `keyring_types[].id` values
3. Verify every allowed_connection_type has matching keyring_type

**Why it matters:** Users cannot create connections because keyring type doesn't exist.

**Reference:** anti-patterns.md #3

---

### C5: Subdomain Configuration
**What to check:**
- [ ] If `is_subdomain: true` → URLs must contain `[SUBDOMAIN]` placeholder
- [ ] If `is_subdomain: false` → must have `organization_data` section

**How to detect:**
```yaml
# Pattern 1: Subdomain-based
is_subdomain: true
token_verification:
  url: "https://[SUBDOMAIN].example.com/api"  # Must have [SUBDOMAIN]

# Pattern 2: Non-subdomain
is_subdomain: false
organization_data:  # Must be present
  type: "config"
  url: "https://api.example.com/org"
```

**Why it matters:** Connector fails because it expects subdomain that doesn't exist, or cannot identify organization.

**Reference:** anti-patterns.md #4, #5

---

### C6: Organization Data Stability ⚠️ MOST CRITICAL
**What to check:**
- [ ] `organization_data.response_jq` `id` is NOT `workspace_name`
- [ ] `organization_data.response_jq` `id` is NOT team name
- [ ] `organization_data.response_jq` `id` is NOT public email domain (gmail.com, yahoo.com)
- [ ] `organization_data.response_jq` `id` is organization-level (not workspace/team level)
- [ ] Same org always gets same ID (stable across workspaces)
- [ ] Different orgs get different IDs (unique)

**How to detect:**
```yaml
# ❌ BAD - Workspace level (same org can have N workspaces)
response_jq: '{"id": .workspace_name, "name": .workspace_name}'

# ❌ BAD - Team level (org can have N teams)
response_jq: '{"id": .team.name, "name": .team.name}'

# ❌ BAD - Public email domain (N orgs share gmail.com)
response_jq: '{"id": (.email | split("@")[1]), "name": ...}'

# ✅ GOOD - Organization level
response_jq: '{"id": .organization.id, "name": .organization.name}'
response_jq: '{"id": .hub_id, "name": .hub_domain}'
```

**Verification tests:**
1. ❌ Could same org get different IDs? (e.g., N workspaces) → WRONG
2. ❌ Could different orgs get same ID? (e.g., gmail.com) → WRONG
3. ✅ Each org always gets same unique ID? → CORRECT

**Why it matters:** Non-stable IDs cause connection conflicts and data isolation issues.

**Reference:** anti-patterns.md #7, auth-patterns.md "Organization Data Configuration"

---

### C7: Secret Transform Syntax
**What to check:**
- [ ] `secret_transform` uses valid jq syntax
- [ ] Transform matches what API expects (e.g., includes Base64 if needed)

**How to detect:**
Test with sample JSON:
```bash
echo '{"email":"test@example.com","token":"abc123"}' | jq '<secret_transform>'
```

**Common mistakes:**
- Missing `| @base64` when API requires Base64
- Invalid jq syntax (missing quotes, wrong operators)
- Referencing non-existent fields

**Reference:** anti-patterns.md #6, auth-patterns.md "Secret Authentication"

---

### C8: OAuth Configuration
**What to check:**
- [ ] If `kind: "Oauth2"` → `developer_keyrings` section must exist
- [ ] `oauth_secret` references a declared developer keyring name

**How to detect:**
```yaml
# Must have developer_keyrings when using OAuth2
developer_keyrings:
  - name: gong_oauth_secret
    display_name: Gong OAuth Secret

keyring_types:
  - kind: "Oauth2"
    oauth_secret: gong_oauth_secret  # Must match developer_keyrings.name
```

**Why it matters:** OAuth flow fails without client credentials storage.

**Reference:** auth-patterns.md "OAuth2 Authentication"

---

### C9: Placeholder Format
**What to check:**
- [ ] All placeholders use `[BRACKET]` format
- [ ] No `{BRACE}` or `(PAREN)` placeholders

**Valid placeholders:**
- `[API_KEY]`, `[ACCESS_TOKEN]`, `[SUBDOMAIN]`, `[ORGANIZATION_ID]`
- `[CLIENT_ID]`, `[CLIENT_SECRET]`, `[REFRESH_TOKEN]`
- `[SCOPES]`, `[CLIENT_CREDENTIALS_BASE64]`

**How to detect:**
```yaml
# ✅ Correct
Authorization: "Bearer [API_KEY]"

# ❌ Wrong
Authorization: "Bearer {API_KEY}"
Authorization: "Bearer (API_KEY)"
```

**Reference:** auth-patterns.md "OAuth2 Placeholders"

---

### C10: Production URLs
**What to check:**
- [ ] No staging/test/dev/localhost URLs in production manifest

**How to detect:**
Look for these patterns in `url` fields:
- `staging.`, `test.`, `dev.`, `localhost`
- `-staging`, `-test`, `-dev`

**Why it matters:** Production connectors must use production endpoints.

---

## HIGH Priority Checks

### H1: External System Name Format
**What to check:**
- [ ] `external_system_name` starts with capital letter
- [ ] Name is unique and recognizable

**How to detect:**
```yaml
external_system_name: GitHub   # ✅ Correct
external_system_name: github   # ❌ Wrong (lowercase)
```

**Reference:** auth-patterns.md "Name and Description"

---

### H2: OAuth Scope Descriptions
**What to check:**
- [ ] Each `scopes[].description` is at least 5 words
- [ ] Descriptions explain specific functionality (not generic)
- [ ] No single-word descriptions

**How to detect:**
```yaml
# ❌ BAD - Generic
scopes:
  - name: read
    description: Read access  # Too generic, < 5 words

# ✅ GOOD - Specific
scopes:
  - name: contacts_read
    description: Read contact information including names, emails, and phone numbers
```

**Generic terms to flag:**
- "Read access", "Write access", "Full access" (without context)
- "Data", "API", "Permissions" (standalone)
- Single words: "Read", "Write", "Admin"

**Reference:** anti-patterns.md #8, auth-patterns.md "OAuth Scope Description Quality"

---

### H3: Sensitive Field Protection
**What to check:**
- [ ] Token/password/key/secret fields use `input_type: password`

**How to detect:**
```yaml
fields:
  - id: token
    name: API Token
    input_type: password  # ✅ Required for sensitive fields
```

**Reference:** auth-patterns.md "Secret Authentication"

---

### H4: TIME_SCOPED_SYNCS Implementation
**What to check:**
- [ ] If `capabilities` includes `TIME_SCOPED_SYNCS`:
  - Code tracks `lastSuccessfulSyncStarted` in state (REQUIRED)
  - Handles `extract_from` parameter OR documents alternative
  - Handles `reset_extract_from` flag OR documents alternative

**How to detect:**
1. Check manifest for `TIME_SCOPED_SYNCS` capability
2. If present, ask user if they want code validation
3. Check extraction function for required patterns

**Reference:** config-patterns.md "TIME_SCOPED_SYNCS"

---

## MEDIUM Priority Checks

### M1: Input Descriptions
**What to check:**
- [ ] Input descriptions explain impact clearly
- [ ] Boolean inputs show what happens when true/false
- [ ] Descriptions provide examples where helpful

**Reference:** config-patterns.md "Inputs"

---

### M2: Default Values Safety
**What to check:**
- [ ] Default values are safe (won't cause unintended data exposure)
- [ ] Default values are reasonable for first-time setup

**Example concerns:**
```yaml
# ⚠️ Check this carefully
- name: import_as_public
  default_value: true  # Could expose private data!
```

**Reference:** config-patterns.md "Inputs"

---

### M3: Service Account Display Name
**What to check:**
- [ ] `service_account.display_name` clearly identifies the external system

**Reference:** auth-patterns.md "Service Account"

---

### M4: Multiple Auth Methods
**What to check:**
- [ ] Connector supports both API key and OAuth when possible

**How to detect:**
```yaml
imports:
  - allowed_connection_types:
      - service-api-key
      - service-oauth-connection  # Support both when possible
```

**Reference:** config-patterns.md "Multiple Connection Types"

---

## Validation Output Format

When outputting results, use this format:

```
# Manifest Validation Results

## File: manifest.yaml

### CRITICAL Issues (Must Fix) ❌

**C6: organization_data.id uses workspace_name** (line 145)
Problem: Same org can have multiple workspaces, causing different IDs
Fix: Use organization-level identifier (hub_id, organization.id, account_id)
Example:
```yaml
# Replace this:
response_jq: '{"id": .workspace_name, "name": .workspace_name}'

# With this:
response_jq: '{"id": .organization.id, "name": .organization.name}'
```
Reference: anti-patterns.md #7

**C3: Function name mismatch** (line 23)
Problem: imports.extractor_function references "extract" but functions.name is "extraction"
Fix:
```yaml
functions:
  - name: extraction  # Match this
imports:
  - extractor_function: extraction  # With this
```
Reference: anti-patterns.md #2

---

### HIGH Priority Issues ⚠️

**H2: Generic OAuth scope description** (line 67)
Found: "Read access"
Fix: "Read contact information including names, emails, and phone numbers"
Reference: auth-patterns.md OAuth Scope Quality

---

### MEDIUM Priority Issues ℹ️

**M1: Input description could be clearer** (line 89)
Current: "Enable sync"
Better: "Import issues from GitHub. Disabling will only sync markdown files."
Reference: config-patterns.md Inputs

---

### Summary
✅ PASSED: 15 checks
❌ CRITICAL: 2 issues (MUST FIX BEFORE DEPLOYMENT)
⚠️  HIGH: 1 issue (STRONGLY RECOMMENDED)
ℹ️  MEDIUM: 1 issue (OPTIONAL IMPROVEMENT)
```

---

## Implementation Check Scripts

### For C7: Secret Transform
```bash
# Test secret_transform with sample data
echo '{"email":"test@example.com","token":"abc123"}' | jq '<secret_transform_value>'
```

### For C6: Organization Data
```bash
# Test response_jq with sample API response
echo '<sample_response>' | jq '<response_jq_value>'
```

### For H4: TIME_SCOPED_SYNCS
If enabled, check extraction function code for:
```typescript
// Required: State tracking
state.lastSuccessfulSyncStarted = new Date().toISOString();

// Standard pattern (or documented alternative):
const extractFrom = event.payload.extract_from;
const resetExtractFrom = event.payload.reset_extract_from;
```
