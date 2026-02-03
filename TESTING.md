# Testing Guide for AdaaS Connector Review Plugin

## Installation for Testing

### Option 1: Test with --plugin-dir (Recommended for Development)

```bash
# From any directory, point to the plugin
cc --plugin-dir /Users/dileepbc/code-base/platform/connectors/adaas-connector-review

# Or use relative path if you're in the parent directory
cc --plugin-dir ./adaas-connector-review
```

### Option 2: Copy to Global Plugins Directory

```bash
# Copy plugin to Claude Code's plugins directory
cp -r /Users/dileepbc/code-base/platform/connectors/adaas-connector-review ~/.claude/plugins/

# Start Claude Code normally
cc
```

### Option 3: Link for Project-Specific Testing

```bash
# Navigate to a connector project
cd /Users/dileepbc/code-base/platform/connectors/adaas-connectors

# Create plugin directory if it doesn't exist
mkdir -p .claude-plugin

# Link the plugin
ln -s /Users/dileepbc/code-base/platform/connectors/adaas-connector-review .claude-plugin/adaas-connector-review

# Start Claude Code
cc
```

## Verification Checklist

### 1. Plugin Loads Successfully

**Test:**
```bash
cc --plugin-dir /Users/dileepbc/code-base/platform/connectors/adaas-connector-review
```

**Expected:**
- Claude Code starts without errors
- No plugin loading errors in startup output

**Status:** [ ]

---

### 2. Commands Appear in Help

**Test:**
```
/help
```

**Expected Output:**
Should see both commands listed:
- `/review-connector` - Review DevRev AdaaS connector code for best practices, anti-patterns, and security issues
- `/review-phase` - Review a specific phase of DevRev AdaaS connector implementation

**Status:** [ ]

---

### 3. Skill Triggers on Relevant Queries

**Test 1: Direct connector review request**
```
User: "Can you review this connector for best practices?"
```

**Expected:**
- Skill loads automatically (may see "Loading skill: AdaaS Connector Review" or similar)
- Claude responds with connector review guidance

**Status:** [ ]

**Test 2: Anti-patterns query**
```
User: "What are common connector anti-patterns I should avoid?"
```

**Expected:**
- Skill loads automatically
- Claude references anti-patterns from the skill knowledge

**Status:** [ ]

**Test 3: Security check request**
```
User: "Check this connector for security issues"
```

**Expected:**
- Skill loads automatically
- Claude applies security checklist from skill

**Status:** [ ]

---

### 4. Command: /review-connector

**Test 1: Full review (no arguments)**

Navigate to a connector directory:
```bash
cd /Users/dileepbc/code-base/platform/connectors/adaas-connectors/airdrop-asana-snap-in
```

Run command:
```
/review-connector
```

**Expected:**
- Command executes
- Locates manifest.yaml and code/src/ directory
- Reviews all phases
- Outputs findings organized by severity (MUST/SHOULD/NICE-TO-HAVE)
- Provides actionable recommendations

**Status:** [ ]

**Test 2: Phase-filtered review**
```
/review-connector --phases=metadata-extraction,security
```

**Expected:**
- Reviews only metadata-extraction and security phases
- Skips other phases
- Outputs findings for selected phases only

**Status:** [ ]

**Test 3: Severity-filtered review**
```
/review-connector --severity=critical
```

**Expected:**
- Reviews all phases
- Shows only MUST fix issues (critical)
- Skips SHOULD and NICE-TO-HAVE findings

**Status:** [ ]

**Test 4: Combined filters**
```
/review-connector --phases=data-extraction --severity=critical
```

**Expected:**
- Reviews only data-extraction phase
- Shows only critical issues for that phase

**Status:** [ ]

---

### 5. Command: /review-phase

**Test 1: Specific phase review**
```
/review-phase metadata-extraction
```

**Expected:**
- Loads references/02-metadata-extraction.md
- Reviews metadata-extraction.ts and related files
- Provides comprehensive phase-specific findings
- Includes code snippets and line numbers
- Answers review questions from phase documentation

**Status:** [ ]

**Test 2: Security phase review**
```
/review-phase security
```

**Expected:**
- Loads references/12-security-checklist.md
- Scans all files for security issues
- Checks credentials, PII, HTTPS usage
- Provides security-focused findings

**Status:** [ ]

**Test 3: Invalid phase name**
```
/review-phase invalid-phase-name
```

**Expected:**
- Shows error message about invalid phase
- Lists valid phase names
- Provides usage example

**Status:** [ ]

**Test 4: Missing argument**
```
/review-phase
```

**Expected:**
- Prompts for phase name
- Shows available phases
- Provides usage guidance

**Status:** [ ]

---

### 6. Skill Content Accessibility

**Test: Reference documents load when needed**

```
User: "What should I check in the data extraction phase?"
```

**Expected:**
- Skill loads
- Claude can access and reference content from references/03-data-extraction.md
- Provides specific checklist items (MUST/SHOULD/NICE-TO-HAVE)
- Mentions critical rules like progress event parameters, timeout handling

**Status:** [ ]

---

### 7. Anti-Pattern Detection

**Test: Quick anti-pattern reference**

```
User: "What are the critical anti-patterns I should check first?"
```

**Expected:**
- Skill loads
- Claude references common-anti-patterns.md
- Provides critical anti-patterns table
- May suggest grep commands for detection

**Status:** [ ]

---

### 8. Integration Test: Full Workflow

**Scenario: New connector review**

1. Navigate to a connector:
   ```bash
   cd /Users/dileepbc/code-base/platform/connectors/adaas-connectors/airdrop-github-snap-in
   ```

2. Start broad review:
   ```
   /review-connector --severity=critical
   ```

3. Follow up with phase-specific deep dive:
   ```
   /review-phase data-extraction
   ```

4. Ask clarifying question:
   ```
   User: "Why is checking adapter.isTimeout important?"
   ```

**Expected:**
- All commands execute successfully
- Findings are consistent across commands
- Skill provides context for follow-up questions
- Review is comprehensive and actionable

**Status:** [ ]

---

## Common Issues and Troubleshooting

### Plugin Not Loading

**Symptom:** Plugin doesn't appear in `/help` or skill doesn't trigger

**Checks:**
1. Verify plugin.json exists and is valid JSON:
   ```bash
   cat /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/.claude-plugin/plugin.json | jq .
   ```

2. Check directory structure:
   ```bash
   ls -la /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/
   ```

3. Verify SKILL.md has valid YAML frontmatter:
   ```bash
   head -5 /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/skills/adaas-connector-review/SKILL.md
   ```

### Commands Not Found

**Symptom:** `/review-connector` command not recognized

**Checks:**
1. Verify command files exist:
   ```bash
   ls -la /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/commands/
   ```

2. Check command frontmatter is valid YAML:
   ```bash
   head -10 /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/commands/review-connector.md
   ```

### Skill Not Triggering

**Symptom:** Skill doesn't load when asking connector review questions

**Checks:**
1. Verify skill description in SKILL.md includes trigger phrases
2. Try more specific queries that match description exactly:
   - "review this connector"
   - "check connector security"
   - "analyze AdaaS connector"

### Reference Files Not Accessible

**Symptom:** Skill loads but can't find reference documentation

**Checks:**
1. Verify references directory exists:
   ```bash
   ls -la /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/skills/adaas-connector-review/references/
   ```

2. Check reference files are readable:
   ```bash
   wc -l /Users/dileepbc/code-base/platform/connectors/adaas-connector-review/skills/adaas-connector-review/references/*.md
   ```

---

## Performance Testing

### Skill Load Time

**Test:** Measure time for skill to load

```
User: "Review this connector"
```

**Expected:**
- Skill loads within 1-2 seconds
- SKILL.md is accessed immediately
- Reference files loaded as needed (not all at once)

**Status:** [ ]

### Command Execution Time

**Test:** Time a full connector review

```
time echo "/review-connector" | cc --plugin-dir /path/to/plugin
```

**Expected:**
- Completes within reasonable time (depends on connector size)
- For typical connector: 30-90 seconds
- For large connector with many files: 2-5 minutes

**Status:** [ ]

---

## Test Data

### Sample Connectors for Testing

Good test subjects in your repository:

1. **Simple connector**: `airdrop-template-snapin`
   - Basic structure, good for quick tests

2. **Full-featured connector**: `airdrop-github-snap-in`
   - Has all phases implemented
   - Good for comprehensive testing

3. **Complex connector**: `airdrop-devrev-snap-in-effortless-feb25`
   - Large codebase
   - Tests performance and detailed review

### Test Scenarios

**Scenario 1: Perfect Connector**
- All MUST criteria met
- No critical issues
- Expected: Positive review with only minor suggestions

**Scenario 2: Common Issues**
- Missing adapter.isTimeout checks
- Progress events with parameters
- Expected: Multiple MUST fix issues identified

**Scenario 3: Security Issues**
- Hardcoded credentials in logs
- HTTP instead of HTTPS
- Expected: Security checklist violations flagged

---

## Sign-Off Checklist

Before considering testing complete:

- [ ] Plugin loads without errors
- [ ] Both commands appear in `/help`
- [ ] Skill triggers on relevant queries
- [ ] `/review-connector` executes successfully
- [ ] `/review-connector` with filters works
- [ ] `/review-phase` executes for all phases
- [ ] Reference documents are accessible
- [ ] Anti-pattern detection works
- [ ] Security checklist accessible
- [ ] Full workflow test passes
- [ ] Error messages are clear and helpful
- [ ] Performance is acceptable

---

## Next Steps After Testing

If all tests pass:
1. Document any issues found during testing
2. Update version to 1.0.0 for production release
3. Consider adding to marketplace
4. Create CI/CD integration examples

If issues found:
1. Document specific failures
2. Debug and fix issues
3. Re-run affected tests
4. Update documentation if behavior changes
