# HTTP Client Implementation Review

## Overview

The HTTP client handles all communication with the external system's API - authentication, error handling, rate limiting, and type-safe API methods.

---

## File: `http-client.ts`

### MUST Follow

- [ ] **Extracts credentials from event** - Uses `event.payload.connection_data`
- [ ] **Handles authentication correctly** - Headers, tokens, OAuth refresh
- [ ] **All API methods are typed** - Input parameters and return types
- [ ] **Handles rate limit responses (429)** - Detects and surfaces to caller
- [ ] **No hardcoded credentials** - All from keyring/connection
- [ ] **4xx errors surface to caller** - Client errors are non-retryable (exceptions need comment)
- [ ] **5xx errors retry with backoff** - Server errors are retryable (exceptions need comment)

### SHOULD Follow

- [ ] **Configures timeouts** - Per-request timeouts (30s typical)
- [ ] **Retries transient failures** - Network errors, 5xx with exponential backoff
- [ ] **Parses error responses** - Extract meaningful messages
- [ ] **Handles pagination** - Internally or exposes clear pagination API

---

## Authentication Patterns

| Pattern     | Connection Fields                                     | Base URL                              |
| ----------- | ----------------------------------------------------- | ------------------------------------- |
| API Key/PAT | `connection.key`                                      | Fixed URL                             |
| OAuth2      | `connection.access_token`, `connection.refresh_token` | Fixed URL                             |
| Subdomain   | `connection.org_name`                                 | `https://${org_name}.service.com/api` |

```typescript
// Example: API Key with subdomain
class HttpClient {
  constructor(event: AirdropEvent) {
    const connection = event.payload.connection_data;
    this.token = connection.key;
    this.baseUrl = `https://${connection.org_name}.service.com/api`;
  }
}
```

---

## Recommended Axios Configuration

```typescript
import axios from "axios";
import axiosRetry from "axios-retry";

const client = axios.create({
  baseURL: `https://${connection.org_name}.service.com/api`,
  timeout: 30000,
  headers: { Authorization: `Bearer ${connection.key}` },
});

axiosRetry(client, {
  retries: 3,
  retryDelay: axiosRetry.exponentialDelay,
  retryCondition: (error) => {
    if (!error.response) return true; // Network errors
    if (error.response.status >= 500) return true; // 5xx
    return false; // Don't retry 4xx or 429
  },
});
```

---

## Common Anti-Patterns

| Anti-Pattern          | Problem         | Fix                                                   |
| --------------------- | --------------- | ----------------------------------------------------- |
| Hardcoded credentials | Security risk   | Use `event.payload.connection_data`                   |
| Logging credentials   | Security risk   | Redact: `{ ...headers, Authorization: "[REDACTED]" }` |
| No timeout            | Requests hang   | Set `timeout: 30000`                                  |
| Retrying 429          | Wastes retries  | Exclude 429 from retry condition                      |
| Missing subdomain     | Wrong tenant    | Use `${connection.org_name}.service.com`              |
| Sync token refresh    | Race conditions | Use `async/await` for refresh                         |

### Rate Limit Handling

```typescript
// Detect and surface 429 to caller
if (error.response?.status === 429) {
  const retryAfter = error.response.headers["retry-after"] || 60;
  throw new RateLimitError(retryAfter);
}
```

---

## Review Questions

```
Q1: Are credentials from connection_data (not hardcoded)?
Q2: Is timeout configured (< 13 min lambda limit)?
Q3: Is 429 detected and Retry-After extracted?
Q4: Are 5xx errors retried?
Q5: Is subdomain handling correct (if applicable)?
Q6: Is OAuth token refresh async?
```

---

## RateLimitError Class

```typescript
export class RateLimitError extends Error {
  constructor(public readonly retryAfter: number) {
    super(`Rate limited. Retry after ${retryAfter} seconds`);
    this.name = "RateLimitError";
  }
}
```
