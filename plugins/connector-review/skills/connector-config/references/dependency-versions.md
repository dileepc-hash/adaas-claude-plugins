# Dependency Version Requirements

## @devrev/ts-adaas SDK

The primary SDK for building DevRev connectors.

### Current Latest Version

**Latest Stable:** Check dynamically using:
```bash
npm view @devrev/ts-adaas version
```

**As of this document:** 1.13.0 (update this regularly)

### Version History and Important Changes

| Version | Release Date | Key Changes |
|---------|-------------|-------------|
| 1.13.0 | 2024-01 | - Improved error handling<br>- New progress event API<br>- Deprecated old message formats |
| 1.12.0 | 2023-12 | - TIME_SCOPED_SYNCS support<br>- Enhanced state management |
| 1.11.0 | 2023-11 | - Initial stable release |

### Checking Current Version

**In package.json:**
```bash
jq -r '.dependencies["@devrev/ts-adaas"]' code/package.json
```

**Expected output formats:**
- `^1.13.0` - Caret range (allows minor/patch updates)
- `~1.13.0` - Tilde range (allows patch updates only)
- `1.13.0` - Exact version

### Upgrading SDK

#### Option 1: Upgrade to Latest

```bash
cd code
npm install @devrev/ts-adaas@latest
```

This updates to the latest version and modifies package.json.

#### Option 2: Upgrade to Specific Version

```bash
cd code
npm install @devrev/ts-adaas@1.13.0
```

#### Post-Upgrade Steps

1. **Update lock file:**
   ```bash
   npm install
   ```

2. **Check for breaking changes:**
   ```bash
   npm run build
   ```

3. **Fix deprecation warnings:**
   ```bash
   npm run lint
   ```

4. **Test connector:**
   ```bash
   npm test
   ```

### Migration Guide: 1.11.x → 1.13.x

#### Breaking Changes

**1. Progress Event Parameters (CRITICAL)**

```typescript
// ❌ OLD (1.11.x) - Will break in 1.13.0
adapter.emitMessage({
  type: 'extraction-progress',
  data: { processed: 100 }  // Parameters not allowed
});

// ✅ NEW (1.13.0+)
adapter.emitProgress();  // No parameters
```

**2. Error Handling**

```typescript
// ❌ OLD (1.11.x) - Manual error wrapping
try {
  const data = await client.fetchData();
} catch (error) {
  adapter.emitError({ message: error.message });
}

// ✅ NEW (1.13.0+) - Automatic error handling
const data = await client.fetchData();  // Errors automatically emitted
```

#### Deprecated APIs (Fix Before 2.0)

| Deprecated API | Replacement | Since Version |
|---------------|-------------|---------------|
| `emitMessage({ type: 'progress' })` | `emitProgress()` | 1.12.0 |
| `processTask({ state: any })` | `processTask<StateType>()` | 1.12.0 |
| `adapter.config.raw` | `adapter.config.get()` | 1.11.0 |

### Dynamic Version Checking in Scripts

```bash
#!/bin/bash

# Get current version from package.json
CURRENT_VERSION=$(jq -r '.dependencies["@devrev/ts-adaas"]' code/package.json | sed 's/[\^~]//g')

# Get latest version from npm registry
LATEST_VERSION=$(npm view @devrev/ts-adaas version 2>/dev/null)

if [ -z "$LATEST_VERSION" ]; then
  echo "⚠️ Unable to fetch latest version from npm registry"
  exit 1
fi

# Compare versions
if [ "$CURRENT_VERSION" != "$LATEST_VERSION" ]; then
  echo "❌ @devrev/ts-adaas outdated"
  echo "   Current: $CURRENT_VERSION"
  echo "   Latest:  $LATEST_VERSION"
  echo "   Fix: cd code && npm install @devrev/ts-adaas@$LATEST_VERSION"
  exit 1
else
  echo "✅ @devrev/ts-adaas is up to date ($CURRENT_VERSION)"
fi
```

## Other Important @devrev Dependencies

### @devrev/airdrop-sdk

**Purpose:** File upload and attachment handling

**Latest version check:**
```bash
npm view @devrev/airdrop-sdk version
```

**When to use:**
- Attachment extraction phase
- Uploading files to DevRev
- Processing binary data

### @devrev/api-client

**Purpose:** Direct DevRev API access (use sparingly)

**Latest version check:**
```bash
npm view @devrev/api-client version
```

**When to use:**
- Custom API calls not covered by ts-adaas
- Advanced integrations

**Note:** Prefer ts-adaas SDK methods over direct API calls when possible.

## Validation Script: Check All Versions

```bash
#!/bin/bash
# check-all-versions.sh

echo "Checking @devrev dependency versions..."
echo

# Check ts-adaas
echo "1. @devrev/ts-adaas"
CURRENT=$(jq -r '.dependencies["@devrev/ts-adaas"]' code/package.json | sed 's/[\^~]//g')
LATEST=$(npm view @devrev/ts-adaas version 2>/dev/null)
if [ "$CURRENT" = "$LATEST" ]; then
  echo "   ✅ $CURRENT (latest)"
else
  echo "   ❌ $CURRENT (latest: $LATEST)"
  echo "      Fix: npm install @devrev/ts-adaas@$LATEST"
fi
echo

# Check airdrop-sdk (if used)
if jq -e '.dependencies["@devrev/airdrop-sdk"]' code/package.json >/dev/null 2>&1; then
  echo "2. @devrev/airdrop-sdk"
  CURRENT=$(jq -r '.dependencies["@devrev/airdrop-sdk"]' code/package.json | sed 's/[\^~]//g')
  LATEST=$(npm view @devrev/airdrop-sdk version 2>/dev/null)
  if [ "$CURRENT" = "$LATEST" ]; then
    echo "   ✅ $CURRENT (latest)"
  else
    echo "   ❌ $CURRENT (latest: $LATEST)"
    echo "      Fix: npm install @devrev/airdrop-sdk@$LATEST"
  fi
  echo
fi

# Check api-client (if used)
if jq -e '.dependencies["@devrev/api-client"]' code/package.json >/dev/null 2>&1; then
  echo "3. @devrev/api-client"
  CURRENT=$(jq -r '.dependencies["@devrev/api-client"]' code/package.json | sed 's/[\^~]//g')
  LATEST=$(npm view @devrev/api-client version 2>/dev/null)
  if [ "$CURRENT" = "$LATEST" ]; then
    echo "   ✅ $CURRENT (latest)"
  else
    echo "   ❌ $CURRENT (latest: $LATEST)"
    echo "      Fix: npm install @devrev/api-client@$LATEST"
  fi
fi
```

## Best Practices

### 1. Pin Major Versions, Allow Patches

**Recommended:**
```json
{
  "dependencies": {
    "@devrev/ts-adaas": "^1.13.0"  // Allows 1.13.x, 1.14.x, etc.
  }
}
```

**Not recommended:**
```json
{
  "dependencies": {
    "@devrev/ts-adaas": "1.13.0"  // Exact version - misses patches
  }
}
```

### 2. Update Regularly

**Schedule:**
- Check for updates **monthly**
- Review changelog before upgrading
- Test thoroughly after major version bumps

### 3. Lock File Management

Always commit both files:
- `package.json` - Dependency ranges
- `package-lock.json` - Exact versions installed

This ensures reproducible builds.

### 4. CI/CD Version Checks

Add to your CI pipeline:
```yaml
- name: Check Dependency Versions
  run: |
    LATEST=$(npm view @devrev/ts-adaas version)
    CURRENT=$(jq -r '.dependencies["@devrev/ts-adaas"]' code/package.json | sed 's/[\^~]//g')
    if [ "$CURRENT" != "$LATEST" ]; then
      echo "::warning::@devrev/ts-adaas is outdated ($CURRENT vs $LATEST)"
    fi
```

## Troubleshooting

### Issue: npm view fails

**Problem:**
```bash
npm view @devrev/ts-adaas version
# Error: 404 Not Found
```

**Solutions:**
1. Check npm registry access
2. Verify package name spelling
3. Check if behind corporate proxy

### Issue: Version conflict after upgrade

**Problem:**
```bash
npm install @devrev/ts-adaas@1.13.0
# Error: Peer dependency conflict
```

**Solution:**
```bash
npm install @devrev/ts-adaas@1.13.0 --legacy-peer-deps
```

### Issue: Build breaks after upgrade

**Problem:**
```bash
npm run build
# Error: Type 'X' is not assignable to type 'Y'
```

**Solution:**
1. Read SDK changelog for breaking changes
2. Update type definitions
3. Fix deprecated API usage
