# Security Checklist

## Credential Security

### MUST Follow

- [ ] **No hardcoded credentials** - All from `event.payload.connection_data`
- [ ] **No credentials in logs** - Redact before logging
- [ ] **No credentials in error messages** - Sanitize exceptions
- [ ] **No credentials in state** - State is persisted/logged
- [ ] **HTTPS only** - No HTTP connections to external systems
- [ ] **No credentials in URLs** - Use headers/body instead

### SHOULD Follow

- [ ] **Token refresh implemented** - For OAuth2
- [ ] **Credential validation on start** - Fail fast on bad creds

---

## Data Security

### MUST Follow

- [ ] **No PII logged** - No emails, names, passwords, tokens
- [ ] **Input validation** - Don't trust external API responses
- [ ] **No arbitrary code execution** - Never `eval()` external data

### SHOULD Follow

- [ ] **Data minimization** - Only extract needed fields
- [ ] **Error data sanitization** - Don't leak internal data

---

## Common Security Anti-Patterns

| Anti-Pattern           | BAD                                    | GOOD                                          |
| ---------------------- | -------------------------------------- | --------------------------------------------- |
| Hardcoded credentials  | `const API_KEY = "sk-xxx"`             | `event.payload.connection_data.key`           |
| Credentials in logs    | `console.log(headers)`                 | `{ ...headers, Authorization: "[REDACTED]" }` |
| Credentials in errors  | `throw new Error(\`Token: ${token}\`)` | `throw new Error(\`Status: ${status}\`)`      |
| Credentials in state   | `adapter.state.apiKey = key`           | Store only pagination/progress                |
| HTTP instead of HTTPS  | `http://api.service.com`               | `https://api.service.com`                     |
| Credentials in URL     | `?api_key=${key}`                      | `headers: { Authorization }`                  |
| Logging full responses | `console.log(response.data)`           | `console.log(items.length)`                   |

---

## Review Questions

```
Q1: Could credentials be leaked in logs or errors?
Q2: Is HTTPS enforced for all external calls?
Q3: Are credentials passed in headers (not URLs)?
Q4: Is state free of credentials?
Q5: Is external API data validated before use?
```
