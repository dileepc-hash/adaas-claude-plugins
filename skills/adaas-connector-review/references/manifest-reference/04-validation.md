# Pre-Deployment Validation

## Overview

Automated testing and validation for manifest.yaml before deployment. For detailed feature checks, see [02-configuration.md](./02-configuration.md). For common mistakes, see [03-anti-patterns.md](./03-anti-patterns.md).

---

## Critical Checks (Required Before Merge)

These checks are mandatory and must pass before the connector can be deployed.

- [ ] Version is "2"
- [ ] Name is not template default (e.g., not "Todo")
- [ ] Description is not template default
- [ ] external_system_name is unique and starts with capital letter
- [ ] Function names match between functions and imports sections
- [ ] All allowed_connection_types reference defined keyrings
- [ ] is_subdomain correctly reflects API URL structure
- [ ] organization_data configured when is_subdomain is false
- [ ] organization_data returns `{id, name}` structure
- [ ] organization_data `id` is stable (same org always gets same ID, even across different workspaces)
- [ ] organization_data `id` is organization-level (not workspace/team level)
- [ ] organization_data `id` is NOT workspace name, public email domain (gmail.com/yahoo.com), or team name
- [ ] If using email domain: validated against public domains or provide fallback for public domain users
- [ ] secret_transform has valid jq syntax
- [ ] Token verification endpoint is correct and working
- [ ] OAuth2 has developer_keyrings declared
- [ ] OAuth2 oauth_secret references declared keyring
- [ ] All placeholders use correct format: [PLACEHOLDER]
- [ ] No hardcoded staging/test URLs
- [ ] No incorrect placeholder formats ({}, ())
- [ ] If TIME_SCOPED_SYNCS enabled: state tracks lastSuccessfulSyncStarted (REQUIRED)
- [ ] If TIME_SCOPED_SYNCS enabled: implements extract_from/reset_extract_from OR documents alternative
- [ ] If TIME_SCOPED_SYNCS enabled: handles incremental vs initial sync modes

---

## Important Checks (Recommended)

These checks improve connector quality and user experience.

- [ ] Sensitive fields use input_type: password
- [ ] OAuth scopes have descriptive, specific explanations
- [ ] Input descriptions explain impact clearly
- [ ] Default values are safe and reasonable
- [ ] service_account.display_name is meaningful
- [ ] loader_function removed if loading not implemented
- [ ] Enum values are comprehensive
- [ ] Boolean inputs have clear true/false implications
- [ ] Organization vs user input scope is correct
- [ ] Multiple connection types supported (API key + OAuth) when possible

---

## Automated Detection Commands

### Anti-Pattern Detection

Run these commands to catch common mistakes:

```bash
# 1. Template defaults not updated
grep -E "(name: Todo|Todo Connector|airdrop-todo)" manifest.yaml

# 2. Function name mismatches
diff <(grep "name:" manifest.yaml | grep -A1 "^functions:" | awk '{print $3}' | sort) \
     <(grep -E "extractor_function:|loader_function:" manifest.yaml | awk '{print $2}' | sort)

# 3. Missing connection types
comm -13 \
  <(grep "id:" manifest.yaml | grep -B2 "keyring_types:" | awk '{print $3}' | sort) \
  <(grep "allowed_connection_types:" -A5 manifest.yaml | grep "^      -" | awk '{print $2}' | sort)

# 4. Wrong is_subdomain setting (true but no SUBDOMAIN placeholder)
if grep -q "is_subdomain: true" manifest.yaml && ! grep -q "\[SUBDOMAIN\]" manifest.yaml; then
  echo "ERROR: is_subdomain is true but no [SUBDOMAIN] placeholder found"
fi

# 5. Missing organization_data when required (false but no organization_data)
if grep -q "is_subdomain: false" manifest.yaml && ! grep -q "organization_data:" manifest.yaml; then
  echo "ERROR: is_subdomain is false but no organization_data configured"
fi

# 6. Invalid secret_transform syntax
TRANSFORM=$(grep "secret_transform:" manifest.yaml | sed 's/.*secret_transform: //')
if [ -n "$TRANSFORM" ]; then
  echo '{"email":"test@example.com","token":"abc123"}' | jq "$TRANSFORM" || echo "ERROR: Invalid jq syntax"
fi

# 7. Incorrect placeholder format
grep -E "\{[A-Z_]+\}|\([A-Z_]+\)" manifest.yaml

# 8. Staging/test URLs
grep -i "staging\|test\|dev\|localhost" manifest.yaml | grep "url:"

# 9. OAuth2 without developer keyring
if grep -q "kind: \"Oauth2\"" manifest.yaml && ! grep -q "developer_keyrings:" manifest.yaml; then
  echo "ERROR: OAuth2 configured but no developer_keyrings declared"
fi

# 10. Generic OAuth scope descriptions
grep -A2 "description:" manifest.yaml | grep -E "(Read access|Write access|Generic)"

# 11. Non-stable organization_data identifiers (id must be stable and organization-level)
if grep -q "organization_data:" manifest.yaml; then
  RESPONSE_JQ=$(grep "response_jq:" manifest.yaml | grep -A1 "organization_data:" | tail -1 | sed 's/.*response_jq: //')

  # Check if id and name use identical expressions
  if echo "$RESPONSE_JQ" | grep -q '"id":.*"name":.*' && \
     echo "$RESPONSE_JQ" | grep -oP '(?<="id":)[^,}]*' | \
     diff - <(echo "$RESPONSE_JQ" | grep -oP '(?<="name":)[^,}]*') >/dev/null 2>&1; then
    echo "ERROR: organization_data uses same value for id and name"
  fi

  # Check for workspace/team level identifiers (not stable - org can have N workspaces)
  if echo "$RESPONSE_JQ" | grep -qE '(workspace_name|team.*name)'; then
    echo "ERROR: organization_data id uses workspace/team name (not stable - org can have multiple workspaces)"
  fi

  # Check for email domains (warn - could be public domains shared by N orgs)
  if echo "$RESPONSE_JQ" | grep -qE '(split.*@|emailAddress)'; then
    echo "WARNING: organization_data id uses email domain - ensure validation against public domains (gmail.com, yahoo.com, etc.)"
  fi

  # Check for hardcoded values
  if echo "$RESPONSE_JQ" | grep -qE '"id":\s*"[^[.]+".*"name":\s*"[^[.]+"'; then
    echo "ERROR: organization_data has hardcoded identical values"
  fi
fi
```

### Basic Information Checks

```bash
# Check version
grep "^version:" manifest.yaml | grep -q "\"2\"" || echo "ERROR: Version must be \"2\""

# Check external_system_name starts with capital
grep "external_system_name:" manifest.yaml | grep -qE ": [A-Z]" || echo "ERROR: external_system_name must start with capital letter"

# Verify no template defaults
grep -E "(name: Todo|Todo Connector)" manifest.yaml && echo "ERROR: Template defaults found"
```

### Authentication Checks

```bash
# Verify keyring configuration
grep -A5 "keyring_types:" manifest.yaml

# Check secret_transform syntax
grep "secret_transform:" manifest.yaml

# OAuth2 specific checks
if grep -q "kind: \"Oauth2\"" manifest.yaml; then
  # Verify developer keyring
  grep "developer_keyrings:" manifest.yaml || echo "ERROR: Missing developer_keyrings"

  # Verify oauth_secret reference
  OAUTH_SECRET=$(grep "oauth_secret:" manifest.yaml | awk '{print $2}')
  grep "name: $OAUTH_SECRET" manifest.yaml || echo "ERROR: oauth_secret references undefined keyring"
fi
```

### TIME_SCOPED_SYNCS Implementation Checks

```bash
# If TIME_SCOPED_SYNCS capability is enabled
if grep -q "TIME_SCOPED_SYNCS" manifest.yaml; then
  echo "Checking TIME_SCOPED_SYNCS implementation..."

  # Find the actual data extraction file (path varies by connector)
  EXTRACTION_FILE=$(find code/src/functions/extraction -name "*extraction*.ts" -o -name "*sync*.ts" 2>/dev/null | head -1)

  if [ -z "$EXTRACTION_FILE" ]; then
    echo "ERROR: No extraction file found in code/src/functions/extraction/"
  else
    echo "Checking implementation in: $EXTRACTION_FILE"

    # CRITICAL: State tracking (required for 83% of connectors)
    if ! grep -q "lastSuccessfulSyncStarted" "$EXTRACTION_FILE"; then
      echo "ERROR: lastSuccessfulSyncStarted not tracked in state (REQUIRED)"
    fi

    # Check for standard TIME_SCOPED_SYNCS parameters
    if grep -q "extract_from" "$EXTRACTION_FILE" && grep -q "reset_extract_from" "$EXTRACTION_FILE"; then
      echo "✓ Standard TIME_SCOPED_SYNCS parameters found (extract_from, reset_extract_from)"
    else
      # Check for alternative implementations
      if grep -q "extractionStartTime" "$EXTRACTION_FILE"; then
        echo "ℹ Alternative implementation using extractionStartTime (valid for some connectors)"
      else
        echo "WARNING: No extract_from/reset_extract_from or alternative time parameters found"
      fi
    fi

    # Verify sync mode handling
    if grep -q "SyncMode.INCREMENTAL" "$EXTRACTION_FILE"; then
      echo "✓ Incremental sync mode handling found"
    else
      echo "WARNING: No explicit SyncMode.INCREMENTAL handling found"
    fi
  fi
fi
```

### Alternative TIME_SCOPED_SYNCS Patterns

Some connectors use valid alternative implementations:

**Azure/Outlook pattern** (extractionStartTime):

```typescript
// Alternative to extract_from parameter
const startTime = state.extractionStartTime || event.payload.extract_from;
```

**API-level filtering** (no extract_from needed):
Some APIs handle time filtering directly without requiring explicit parameters.

**When alternatives are acceptable:**

- API provides built-in incremental sync mechanisms
- Connector uses different state management approach
- Architecture justifies deviation (document in code comments)

**When standard pattern is required:**

- New connectors should follow standard pattern unless justified
- Must still track lastSuccessfulSyncStarted in state

### YAML Syntax Validation

```bash
# Validate YAML syntax
python3 -c "import yaml; yaml.safe_load(open('manifest.yaml'))" || echo "ERROR: Invalid YAML syntax"

# Find all placeholders
echo "Placeholders found:"
grep -o "\[[A-Z_]*\]" manifest.yaml | sort -u
```

---

## Common Failure Points

### 1. Template Defaults

**Check**: Are name, description, and slug customized?

```bash
grep -E "(Todo|template|example)" manifest.yaml
```

### 2. Function Mismatches

**Check**: Do function names in `functions` match `imports` references?

```bash
diff <(grep "^  - name:" manifest.yaml | awk '{print $3}' | sort) \
     <(grep -E "extractor_function:|loader_function:" manifest.yaml | awk '{print $2}' | sort)
```

### 3. Missing Keyrings

**Check**: Are all `allowed_connection_types` defined in `keyring_types`?

```bash
comm -13 \
  <(grep "^  - id:" manifest.yaml | awk '{print $3}' | sort) \
  <(grep "allowed_connection_types:" -A5 manifest.yaml | grep "^      -" | awk '{print $2}' | sort)
```

### 4. Subdomain Mismatch

**Check**: If `is_subdomain: true`, are there `[SUBDOMAIN]` placeholders?

```bash
grep "is_subdomain: true" -A20 manifest.yaml | grep -c "\[SUBDOMAIN\]"
```

### 5. Missing organization_data

**Check**: If `is_subdomain: false`, is `organization_data` configured?

```bash
grep "is_subdomain: false" -A20 manifest.yaml | grep -c "organization_data:"
```

---

## TIME_SCOPED_SYNCS Examples from Production

**Fully compliant connectors** (recommended reference):

- airdrop-github-snap-in
- airdrop-google-drive-snap-in
- airdrop-hubspot-snap-in
- airdrop-linear-snap-in
- airdrop-slack-snap-in

**Alternative implementations** (valid but different):

- airdrop-azure-devops-kb-snap-in (uses extractionStartTime)
- airdrop-outlook-calendar (API-level filtering)

**Reference these connectors before implementing TIME_SCOPED_SYNCS in new connectors.**

---

## Pre-Deployment Checklist

Before deploying the connector:

1. **Run all critical checks** - Must pass 100%
2. **Test token verification** - Create test connection
3. **Validate jq syntax** - Test secret_transform with sample data
4. **Review scope descriptions** - Ensure they're clear and specific
5. **Check placeholder format** - All use [BRACKET] syntax
6. **Verify production URLs** - No staging/test endpoints
7. **Test incremental sync** - If TIME_SCOPED_SYNCS enabled
8. **Verify OAuth flow** - If OAuth2 configured

---

## Pre-Deployment Testing Workflow

### Step 1: Test Token Verification

```bash
# Test secret_transform with sample data
TRANSFORM=$(grep "secret_transform:" manifest.yaml | sed 's/.*secret_transform: //')
echo '{"email":"test@example.com","token":"abc123"}' | jq "$TRANSFORM"

# Test organization_data response_jq (if applicable)
RESPONSE_JQ=$(grep "response_jq:" manifest.yaml | sed 's/.*response_jq: //')
echo '{"organization":{"id":"org-123","name":"Acme Corp"}}' | jq "$RESPONSE_JQ"
```

### Step 2: Verify Implementation

```bash
# Check TIME_SCOPED_SYNCS implementation (if enabled)
if grep -q "TIME_SCOPED_SYNCS" manifest.yaml; then
  echo "Verifying TIME_SCOPED_SYNCS implementation..."
  grep -l "extract_from\|reset_extract_from\|lastSuccessfulSyncStarted" \
    code/src/functions/extraction/workers/data-extraction.ts
fi

# Verify all item types from metadata are extracted
echo "Check extraction logic matches metadata record types"
```

### Step 3: Create Test Connection

1. Deploy connector to staging environment
2. Create test connection with valid credentials
3. Verify token verification succeeds
4. Run initial sync and verify data extraction
5. Run incremental sync and verify TIME_SCOPED_SYNCS logic

---

---

## Related Documents

- [01-authentication.md](./01-authentication.md) - Authentication patterns and configuration
- [02-configuration.md](./02-configuration.md) - Detailed feature checks and comprehensive validation
- [03-anti-patterns.md](./03-anti-patterns.md) - BAD/GOOD examples of common mistakes
