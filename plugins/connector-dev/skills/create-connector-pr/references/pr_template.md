# Connector PR Template Reference

This document describes the standard PR template format used for ADaaS connector repositories.

## Standard PR Template Structure

All connector PRs should follow this structure:

```markdown
# Description

<!--
    A brief description of what the PR does/changes.
    Use active voice and present tense, e.g., This PR fixes ...
-->

## Connected Issues

<!--
    DevRev issue(s) full link(s) (e.g. https://app.devrev.ai/devrev/works/ISS-123).
-->

## Checklist

- [ ] Tests added/updated and ran with `npm run test` OR no tests needed.
- [ ] Code formatted and checked with `npm run lint`.
- [ ] Added "How to test" section to the description OR this section is not needed.
```

## Work Item URL Format

Work items should always be referenced with full URLs, not just issue numbers:

- ✅ Correct: `https://app.devrev.ai/devrev/works/ISS-252455`
- ❌ Incorrect: `ISS-252455` or `#ISS-252455`

## Branch Naming Convention

All branches should be prefixed with the work item ID:

**Pattern:** `ISS-{NUMBER}-{short-description}`

**Examples:**

- `ISS-252455-fix-security-vulnerabilities`
- `ISS-123456-update-sdk-version`
- `ISS-789012-add-new-extraction-phase`

**Rules:**

- Use lowercase for the description part
- Separate words with hyphens (kebab-case)
- Keep description concise (2-5 words)
- Description should summarize the main change

## Common PR Types and Examples

### Security Fix PR

```markdown
# Description

This PR addresses security vulnerabilities identified in the health report by updating dependencies and fixing SAST issues.

## Connected Issues

https://app.devrev.ai/devrev/works/ISS-252455

## Changes

- Updated @devrev/ts-adaas from 1.14.0 to 1.15.0
- Fixed 3 high-severity npm audit vulnerabilities
- Resolved prototype pollution issue in data extraction

## How to test

1. Run `npm install` and verify no security warnings
2. Run `npm audit` and confirm reduced vulnerability count
3. Run `npm test` to ensure all tests pass
4. Build the connector with `npm run build`

## Checklist

- [x] Tests added/updated and ran with `npm run test` OR no tests needed.
- [x] Code formatted and checked with `npm run lint`.
- [x] Added "How to test" section to the description OR this section is not needed.
```

### Feature/Enhancement PR

```markdown
# Description

This PR adds support for extracting attachments from Outlook Calendar events.

## Connected Issues

https://app.devrev.ai/devrev/works/ISS-123456

## Changes

- Implemented attachment extraction worker
- Added attachment metadata mapping
- Updated manifest.yaml with new extraction phase

## How to test

1. Configure the connector with a test account that has calendar events with attachments
2. Run extraction and verify attachments are synced
3. Check DevRev to confirm attachment metadata is correct

## Checklist

- [x] Tests added/updated and ran with `npm run test` OR no tests needed.
- [x] Code formatted and checked with `npm run lint`.
- [x] Added "How to test" section to the description OR this section is not needed.
```

### Configuration/Manifest Update PR

```markdown
# Description

This PR updates the connector configuration to use the latest manifest version and adds new connection parameters.

## Connected Issues

https://app.devrev.ai/devrev/works/ISS-789012

## Changes

- Updated manifest.yaml to version 2.0
- Added new connection fields for API rate limiting
- Updated README with new configuration instructions

## How to test

1. Validate manifest with DevRev CLI tools
2. Deploy to staging and test connection configuration
3. Verify backward compatibility with existing installations

## Checklist

- [x] Tests added/updated and ran with `npm run test` OR no tests needed.
- [x] Code formatted and checked with `npm run lint`.
- [x] Added "How to test" section to the description OR this section is not needed.
```

## Best Practices

### Description Section

- Use active voice and present tense
- Start with "This PR..."
- Be specific about what changed, not why (the issue explains why)
- Include a "Changes" subsection for longer PRs with multiple modifications

### Connected Issues Section

- Always include the full DevRev work item URL
- Multiple issues can be listed, one per line
- The work item should provide context about why the change is needed

### How to Test Section

- Include clear, numbered steps
- Assume reviewer has basic connector development knowledge
- Include expected outcomes
- Mention any prerequisites (test accounts, specific data, etc.)

### Checklist

- Mark all items that apply with `[x]`
- If tests aren't needed, keep the first item checked and explain in description
- If "How to test" isn't needed (obvious changes), keep the third item checked
