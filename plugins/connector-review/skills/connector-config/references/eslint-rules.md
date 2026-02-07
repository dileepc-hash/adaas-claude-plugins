# ESLint Configuration Requirements

## Required ESLint Rules

DevRev connectors must configure ESLint to catch two critical issues:

1. **Usage of `any` type** - Breaks type safety
2. **Usage of deprecated code** - Will break in future SDK versions

## Complete ESLint Configuration

### Option 1: .eslintrc.json (Recommended)

Create `code/.eslintrc.json`:

```json
{
  "parser": "@typescript-eslint/parser",
  "parserOptions": {
    "ecmaVersion": 2020,
    "sourceType": "module",
    "project": "./tsconfig.json"
  },
  "plugins": [
    "@typescript-eslint",
    "deprecation"
  ],
  "extends": [
    "eslint:recommended",
    "plugin:@typescript-eslint/recommended"
  ],
  "rules": {
    "@typescript-eslint/no-explicit-any": "error",
    "@typescript-eslint/no-unsafe-assignment": "error",
    "@typescript-eslint/no-unsafe-member-access": "error",
    "@typescript-eslint/no-unsafe-call": "error",
    "@typescript-eslint/no-unsafe-return": "error",
    "deprecation/deprecation": "error"
  }
}
```

### Option 2: .eslintrc.js

Create `code/.eslintrc.js`:

```javascript
module.exports = {
  parser: '@typescript-eslint/parser',
  parserOptions: {
    ecmaVersion: 2020,
    sourceType: 'module',
    project: './tsconfig.json',
  },
  plugins: ['@typescript-eslint', 'deprecation'],
  extends: [
    'eslint:recommended',
    'plugin:@typescript-eslint/recommended',
  ],
  rules: {
    '@typescript-eslint/no-explicit-any': 'error',
    '@typescript-eslint/no-unsafe-assignment': 'error',
    '@typescript-eslint/no-unsafe-member-access': 'error',
    '@typescript-eslint/no-unsafe-call': 'error',
    '@typescript-eslint/no-unsafe-return': 'error',
    'deprecation/deprecation': 'error',
  },
};
```

### Option 3: eslintConfig in package.json

Add to `code/package.json`:

```json
{
  "eslintConfig": {
    "parser": "@typescript-eslint/parser",
    "parserOptions": {
      "ecmaVersion": 2020,
      "sourceType": "module",
      "project": "./tsconfig.json"
    },
    "plugins": [
      "@typescript-eslint",
      "deprecation"
    ],
    "extends": [
      "eslint:recommended",
      "plugin:@typescript-eslint/recommended"
    ],
    "rules": {
      "@typescript-eslint/no-explicit-any": "error",
      "@typescript-eslint/no-unsafe-assignment": "error",
      "@typescript-eslint/no-unsafe-member-access": "error",
      "@typescript-eslint/no-unsafe-call": "error",
      "@typescript-eslint/no-unsafe-return": "error",
      "deprecation/deprecation": "error"
    }
  }
}
```

## Required Dependencies

Install these dev dependencies:

```bash
cd code
npm install --save-dev \
  eslint \
  @typescript-eslint/parser \
  @typescript-eslint/eslint-plugin \
  eslint-plugin-deprecation
```

**Minimum versions:**
- `eslint`: ^8.0.0
- `@typescript-eslint/parser`: ^6.0.0
- `@typescript-eslint/eslint-plugin`: ^6.0.0
- `eslint-plugin-deprecation`: ^2.0.0

## Rule Explanations

### C5: Rules for `any` Type Usage

#### @typescript-eslint/no-explicit-any

**Purpose:** Prevent explicit use of `any` type

**Violation:**
```typescript
function processData(data: any) {  // ❌ ESLint error
  return data.items.map(item => item.id);
}
```

**Fix:**
```typescript
interface DataResponse {
  items: Array<{ id: string }>;
}

function processData(data: DataResponse) {  // ✅ Type safe
  return data.items.map(item => item.id);
}
```

#### @typescript-eslint/no-unsafe-assignment

**Purpose:** Prevent assigning `any` values to typed variables

**Violation:**
```typescript
const result: any = await client.fetchData();
const items: Item[] = result.items;  // ❌ Unsafe assignment
```

**Fix:**
```typescript
interface FetchResult {
  items: Item[];
}

const result: FetchResult = await client.fetchData();
const items: Item[] = result.items;  // ✅ Type safe
```

#### @typescript-eslint/no-unsafe-member-access

**Purpose:** Prevent accessing properties on `any` typed values

**Violation:**
```typescript
function process(data: any) {
  return data.items.length;  // ❌ Unsafe access
}
```

**Fix:**
```typescript
interface Data {
  items: unknown[];
}

function process(data: Data) {
  return data.items.length;  // ✅ Type safe
}
```

#### @typescript-eslint/no-unsafe-call

**Purpose:** Prevent calling functions with `any` type

**Violation:**
```typescript
function execute(fn: any) {
  return fn();  // ❌ Unsafe call
}
```

**Fix:**
```typescript
function execute(fn: () => void) {
  return fn();  // ✅ Type safe
}
```

#### @typescript-eslint/no-unsafe-return

**Purpose:** Prevent returning `any` from typed functions

**Violation:**
```typescript
function getData(): string {
  const result: any = fetchData();
  return result;  // ❌ Unsafe return
}
```

**Fix:**
```typescript
function getData(): string {
  const result: string = fetchData();
  return result;  // ✅ Type safe
}
```

### C6: Rules for Deprecated Code

#### deprecation/deprecation

**Purpose:** Catch usage of deprecated APIs at compile time

**Violation:**
```typescript
import { OldAPI } from '@devrev/ts-adaas';

// ❌ ESLint error: 'OldAPI' is deprecated
const client = new OldAPI();
```

**Fix:**
```typescript
import { NewAPI } from '@devrev/ts-adaas';

// ✅ Using current API
const client = new NewAPI();
```

**How it works:**
- Detects `@deprecated` JSDoc tags
- Flags usage of deprecated functions, classes, types
- Shows deprecation message in IDE

## Validation Scripts

### Check if ESLint is Configured

```bash
#!/bin/bash

# Check for ESLint config files
if [ -f "code/.eslintrc.json" ]; then
  echo "✅ Found .eslintrc.json"
  ESLINT_CONFIG="code/.eslintrc.json"
elif [ -f "code/.eslintrc.js" ]; then
  echo "✅ Found .eslintrc.js"
  ESLINT_CONFIG="code/.eslintrc.js"
elif jq -e '.eslintConfig' code/package.json >/dev/null 2>&1; then
  echo "✅ Found eslintConfig in package.json"
  ESLINT_CONFIG="code/package.json"
else
  echo "❌ No ESLint configuration found"
  exit 1
fi
```

### Check Required Rules (for .eslintrc.json)

```bash
#!/bin/bash

ESLINT_CONFIG="code/.eslintrc.json"

# Check C5: no-explicit-any rule
NO_EXPLICIT_ANY=$(jq -r '.rules["@typescript-eslint/no-explicit-any"]' "$ESLINT_CONFIG")

if [ "$NO_EXPLICIT_ANY" = "error" ] || [ "$NO_EXPLICIT_ANY" = "2" ]; then
  echo "✅ C5: ESLint configured to error on 'any' type"
else
  echo "❌ C5: ESLint not configured to error on 'any' type"
  echo "   Fix: Add to .eslintrc.json rules:"
  echo '   "@typescript-eslint/no-explicit-any": "error"'
fi

# Check C6: deprecation rule
DEPRECATION=$(jq -r '.rules["deprecation/deprecation"]' "$ESLINT_CONFIG" 2>/dev/null)

if [ "$DEPRECATION" = "error" ] || [ "$DEPRECATION" = "2" ]; then
  echo "✅ C6: ESLint configured to error on deprecated code"
else
  echo "❌ C6: ESLint not configured to error on deprecated code"
  echo "   Fix: Install plugin and add rule:"
  echo "   npm install --save-dev eslint-plugin-deprecation"
  echo '   Add to .eslintrc.json: "deprecation/deprecation": "error"'
fi
```

### Check Required Rules (for package.json eslintConfig)

```bash
#!/bin/bash

# Check if eslintConfig exists in package.json
if ! jq -e '.eslintConfig' code/package.json >/dev/null 2>&1; then
  echo "❌ No eslintConfig found in package.json"
  exit 1
fi

# Check C5
NO_EXPLICIT_ANY=$(jq -r '.eslintConfig.rules["@typescript-eslint/no-explicit-any"]' code/package.json)

if [ "$NO_EXPLICIT_ANY" = "error" ] || [ "$NO_EXPLICIT_ANY" = "2" ]; then
  echo "✅ C5: ESLint configured to error on 'any' type"
else
  echo "❌ C5: Missing rule in package.json eslintConfig"
fi

# Check C6
DEPRECATION=$(jq -r '.eslintConfig.rules["deprecation/deprecation"]' code/package.json)

if [ "$DEPRECATION" = "error" ] || [ "$DEPRECATION" = "2" ]; then
  echo "✅ C6: ESLint configured to error on deprecated code"
else
  echo "❌ C6: Missing deprecation rule in package.json eslintConfig"
fi
```

## Adding Rules to Existing Config

### If .eslintrc.json exists

```bash
# Install deprecation plugin if not already installed
cd code
npm install --save-dev eslint-plugin-deprecation

# Add rules using jq
jq '.plugins += ["deprecation"] | .rules["@typescript-eslint/no-explicit-any"] = "error" | .rules["deprecation/deprecation"] = "error"' .eslintrc.json > .eslintrc.json.tmp
mv .eslintrc.json.tmp .eslintrc.json
```

### If using package.json eslintConfig

```bash
# Install deprecation plugin
cd code
npm install --save-dev eslint-plugin-deprecation

# Manually add rules to package.json eslintConfig section
```

## Running ESLint

### Command Line

```bash
cd code
npm run lint  # If lint script is configured

# Or run directly
npx eslint src/ --ext .ts
```

### In package.json scripts

```json
{
  "scripts": {
    "lint": "eslint src/ --ext .ts",
    "lint:fix": "eslint src/ --ext .ts --fix"
  }
}
```

### In CI/CD

```yaml
- name: Run ESLint
  run: |
    cd code
    npm run lint
```

## IDE Integration

### VS Code

Install extension: `dbaeumer.vscode-eslint`

**Settings:**
```json
{
  "eslint.validate": ["typescript"],
  "eslint.workingDirectories": ["./code"]
}
```

### IntelliJ/WebStorm

ESLint support is built-in. Enable in:
Settings → Languages & Frameworks → JavaScript → Code Quality Tools → ESLint

## Troubleshooting

### Issue: deprecation/deprecation rule not working

**Problem:**
```bash
npm run lint
# No deprecation warnings shown
```

**Solution:**
Ensure `parserOptions.project` is set:
```json
{
  "parserOptions": {
    "project": "./tsconfig.json"  // Required for deprecation plugin
  }
}
```

### Issue: Too many false positives

**Problem:**
Every `any` usage is flagged, even when necessary (e.g., JSON.parse)

**Solution:**
Use `unknown` type instead:
```typescript
// Instead of:
const data: any = JSON.parse(str);

// Use:
const data: unknown = JSON.parse(str);
// Then validate and narrow type
if (isValidData(data)) {
  const validData: DataType = data;
}
```

### Issue: Legacy code has too many violations

**Problem:**
Hundreds of ESLint errors in existing connector

**Solution:**
1. Add rules as "warn" first:
   ```json
   {
     "rules": {
       "@typescript-eslint/no-explicit-any": "warn"
     }
   }
   ```

2. Fix violations incrementally

3. Change to "error" once all fixed

## Best Practices

1. **Run ESLint before commits**
   ```bash
   # Add to .husky/pre-commit or package.json scripts
   npm run lint
   ```

2. **Fix violations immediately**
   - Don't accumulate technical debt
   - Types are easier to add when code is fresh

3. **Use `unknown` instead of `any`**
   - Forces type validation
   - Maintains type safety

4. **Keep ESLint plugins updated**
   ```bash
   npm update @typescript-eslint/parser @typescript-eslint/eslint-plugin eslint-plugin-deprecation
   ```
