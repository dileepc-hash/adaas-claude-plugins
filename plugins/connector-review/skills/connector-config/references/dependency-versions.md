# Dependency Version Requirements

## @devrev/ts-adaas SDK

The primary SDK for building DevRev connectors. Should always be in its lastest version optionally beta versions ( including Major/Minor ).

### 1. Pin Major Versions, Allow Patches

**Recommended:**

```json
{
  "dependencies": {
    "@devrev/ts-adaas": "^1.14.0" // Allows ^1.14.x
  }
}
```

**Not recommended:**

```json
{
  "dependencies": {
    "@devrev/ts-adaas": "1.13.0" // Exact version - misses patches
  }
}
```

**Solution:**

1. Ask User to explictly to update the SDK to latest version
