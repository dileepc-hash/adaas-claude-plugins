# Security Fix Patterns Reference

This reference provides common patterns for fixing security vulnerabilities in ADaaS connector repositories.

## SDK Updates (@devrev/ts-adaas)

### Pattern: Patch Version Update (Safe)

**When to apply:** Current version differs only in patch number (e.g., 1.14.0 → 1.14.3)

**How to fix:**
```bash
npm install @devrev/ts-adaas@latest
```

**Verification:**
- Check `package.json` shows updated version
- Run `npm install` to update `package-lock.json`
- Run `npm run build` to verify no breaking changes
- Run `npm test` if tests exist

### Pattern: Minor/Major Version Update (Requires Review)

**When to skip:** Minor (1.14.0 → 1.15.0) or major (1.14.0 → 2.0.0) version changes

**Reason:** May include breaking changes or require code modifications

**Action:** Document in PR as "Requires manual review"

---

## Dependency Vulnerabilities

### Pattern: Auto-fixable via npm audit fix

**When to apply:** npm audit indicates a fix is available

**How to fix:**
```bash
npm audit fix
```

**Rules:**
- ❌ NEVER use `npm audit fix --force` (can introduce breaking changes)
- ✅ Run without `--force` flag only
- ⚠️ If `--force` is suggested, it means breaking changes - skip and document

**Verification:**
- Run `npm audit` again to verify reduction in vulnerabilities
- Run `npm install && npm run build && npm test`

### Pattern: Direct Dependency Update

**When to apply:** 
- npm audit shows "Fix available via alternate source"
- Specific package version is outdated

**Example:** axios 1.13.2 → 1.13.5

**How to fix:**
```bash
npm install axios@1.13.5
```

Or for exact version:
```bash
npm install axios@^1.13.5
```

**Verification:**
- Verify `package.json` and `package-lock.json` updated
- Run `npm audit` to confirm vulnerability resolved
- Run tests and build

### Pattern: Transitive Dependency (No Direct Fix)

**When to skip:** 
- Vulnerability is in a dependency of a dependency
- No direct update path available
- Parent package hasn't released fix yet

**How to identify:**
```bash
npm audit
# Look for: "Fix available via `npm audit fix --force`"
```

**Action:** 
- Document as "No safe fix available"
- Note parent package and required version
- Check if parent package has updates: `npm outdated`

---

## SAST (Static Code Analysis) Issues

### Pattern: Prototype Pollution

**Common in:** Object manipulation, merging configurations

**Example Issue:**
```javascript
// Vulnerable
function merge(target, source) {
  for (let key in source) {
    target[key] = source[key];
  }
}
```

**Fix:**
```javascript
// Secure
function merge(target, source) {
  for (let key in source) {
    if (Object.prototype.hasOwnProperty.call(source, key)) {
      target[key] = source[key];
    }
  }
}
```

### Pattern: Command Injection

**Common in:** Shell command execution with user input

**Example Issue:**
```javascript
// Vulnerable
const result = execSync(`command ${userInput}`);
```

**Fix:**
```javascript
// Secure - use array arguments
const result = execSync('command', [userInput]);
```

### Pattern: Path Traversal

**Common in:** File operations with user-supplied paths

**Example Issue:**
```javascript
// Vulnerable
const filePath = path.join(baseDir, req.params.filename);
fs.readFile(filePath);
```

**Fix:**
```javascript
// Secure - validate path stays within base directory
const filePath = path.resolve(baseDir, req.params.filename);
if (!filePath.startsWith(baseDir)) {
  throw new Error('Invalid path');
}
fs.readFile(filePath);
```

### Pattern: SQL Injection (if using SQL)

**Example Issue:**
```javascript
// Vulnerable
const query = `SELECT * FROM users WHERE id = ${userId}`;
```

**Fix:**
```javascript
// Secure - use parameterized queries
const query = 'SELECT * FROM users WHERE id = ?';
db.query(query, [userId]);
```

---

## Common Unfixable Scenarios

### Scenario 1: Breaking Changes Required

**Symptom:** `npm audit fix` requires `--force`, or major version jump needed

**Action:**
- Document in PR: "Package X requires breaking changes (v1 → v2)"
- Note what would break: "Requires API migration"
- Suggest: "Manual review needed"

### Scenario 2: No Upstream Fix Available

**Symptom:** Vulnerability exists but package maintainer hasn't released fix

**Action:**
- Check package GitHub for issues/PRs
- Document: "Waiting for upstream fix in package X"
- Consider alternatives: "Consider replacing with package Y"

### Scenario 3: Development Dependency Only

**Symptom:** Vulnerability in devDependencies only (e.g., testing tools)

**Action:**
- Assess risk: "Low risk - development only"
- Document: "Dev dependency - no production impact"
- Update if easy, otherwise note and move on

---

## Verification Checklist

After any fixes, always verify:

```bash
# 1. Clean install
rm -rf node_modules package-lock.json
npm install

# 2. Check for remaining vulnerabilities
npm audit

# 3. Build the project
npm run build

# 4. Run tests (if available)
npm test

# 5. Check TypeScript (if applicable)
npm run type-check  # or tsc --noEmit
```

---

## Things to NEVER Do

❌ **NEVER** use `npm audit fix --force`
- Can introduce breaking changes
- May downgrade packages unexpectedly

❌ **NEVER** add `overrides` to package.json
- Bypasses dependency resolution
- Can mask compatibility issues
- Makes future updates harder

❌ **NEVER** edit files in `node_modules/`, `dist/`, or `build/`
- Changes will be lost on next install
- Fix source files instead

❌ **NEVER** ignore high/critical vulnerabilities without documentation
- Always document why unfixable
- Provide context and reasoning
