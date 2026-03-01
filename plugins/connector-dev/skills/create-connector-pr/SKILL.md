---
name: create-connector-pr
description: Create pull requests for ADaaS connector repositories following DevRev standards. This skill should be used when the user asks to "create a PR", "create a pull request", "make a PR for connector", "submit changes", or any request to create a pull request for connector code changes.
---

# Create Connector PR

Create pull requests for ADaaS connector repositories following DevRev branch naming conventions and PR template standards.

## Overview

This skill provides an interactive workflow for creating properly formatted pull requests for connector repositories:

1. Checks for existing branch or creates a new one with work item prefix
2. Analyzes changes and generates PR title and description
3. Follows the standard connector PR template format
4. Includes full DevRev work item URLs

**When to use:** User says "create a PR", "create pull request for [connector]", or similar requests to submit changes.

## Workflow

### Phase 1: Branch Management

**Step 1:** Check the current git state

Run git commands to understand the current state:

```bash
# Check current branch
git branch --show-current

# Check git status
git status

# Check if changes are committed
git diff HEAD
```

**Step 2:** Determine if branch needs to be created

**Scenario A: Already on a feature branch**

If the current branch follows the work item naming pattern (e.g., `ISS-252455-*`):

- Extract work item ID from branch name
- Proceed to Phase 2 (PR creation)

**Scenario B: On main/master or wrong branch**

If on `main`, `master`, or a branch without work item prefix:

- Prompt user for work item ID (e.g., "ISS-252455")
- Create a new branch with proper naming

**Step 3:** Prompt for work item ID (if needed)

Ask the user for the DevRev work item ID:

```
To create a properly named branch, I need the DevRev work item ID.

Please provide the work item ID (e.g., ISS-252455):
```

**Important:** Only the ID is needed at this point, not the full URL.

**Step 4:** Create branch with proper naming (if needed)

**Branch naming pattern:** `ISS-{NUMBER}-{short-description}`

To create the branch name:

1. Start with the work item ID (e.g., `ISS-252455`)
2. Add a short description based on the changes (2-5 words)
3. Use kebab-case (lowercase with hyphens)

**Examples:**

- Security fixes: `ISS-252455-fix-security-vulnerabilities`
- SDK update: `ISS-123456-update-sdk-version`
- New feature: `ISS-789012-add-attachment-extraction`
- Bug fix: `ISS-456789-fix-data-sync-error`

To analyze changes and generate description:

```bash
# View uncommitted changes
git diff

# View committed changes (if any)
git log --oneline -5

# View changed files
git status --short
```

Generate a concise description based on:

- File changes (e.g., `package.json` → "update-dependencies")
- Code modifications (e.g., new extraction phase → "add-extraction-phase")
- Commit messages (if already committed)

**Step 5:** Create and switch to the new branch

```bash
git checkout -b ISS-{NUMBER}-{short-description}
```

**Step 6:** Ensure changes are committed

If there are uncommitted changes, commit them:

```bash
# Stage all changes
git add .

# Commit with descriptive message
git commit -m "Brief description of changes"
```

If changes are already committed, proceed to next phase.

### Phase 2: Analyze Changes

**Step 7:** Gather change information

Run git commands to understand what changed:

```bash
# View commits since branching from main
git log main..HEAD --oneline

# View full diff since main
git diff main...HEAD

# List changed files
git diff --name-only main...HEAD
```

**Step 8:** Categorize the changes

Analyze the changes and identify the type:

**Common change types:**

- **Security fixes:** Updates to dependencies, vulnerability fixes, SDK updates for security
- **Feature/Enhancement:** New functionality, new extraction phases, new configuration options
- **Bug fix:** Fixes to existing functionality, error handling improvements
- **Configuration:** Manifest updates, connection parameter changes
- **Refactoring:** Code restructuring without functionality changes
- **Documentation:** README updates, code comments

### Phase 3: Generate PR Content

**Step 9:** Create PR title

**Format:** Brief, active voice description (50-72 characters recommended)

**Patterns by change type:**

- **Security:** "Fix security vulnerabilities in dependencies"
- **SDK Update:** "Update @devrev/ts-adaas to v1.15.0"
- **Feature:** "Add attachment extraction support"
- **Bug Fix:** "Fix data sync error for large events"
- **Config:** "Update manifest to version 2.0"
- **Multiple changes:** "Update SDK and fix security issues"

**Rules:**

- Use imperative mood ("Fix", "Add", "Update", not "Fixed", "Added", "Updated")
- Be specific but concise
- Don't include issue numbers in title

**Step 10:** Generate PR description

Follow the standard connector PR template structure. Reference `references/pr_template.md` for the complete template format.

**Required sections:**

1. **Description**: Active voice explanation of what the PR does
2. **Connected Issues**: Full DevRev work item URL(s)
3. **Changes** (optional but recommended): Bullet list of specific changes
4. **How to test** (if applicable): Numbered steps to verify the changes
5. **Checklist**: Standard checklist items

**Example structure:**

```markdown
# Description

This PR [active voice description of what changed].

## Connected Issues

https://app.devrev.ai/devrev/works/ISS-{NUMBER}

## Changes

- [Specific change 1]
- [Specific change 2]
- [Specific change 3]

## How to test

1. [Step 1]
2. [Step 2]
3. [Expected outcome]

## Checklist

- [x] Tests added/updated and ran with `npm run test` OR no tests needed.
- [x] Code formatted and checked with `npm run lint`.
- [x] Added "How to test" section to the description OR this section is not needed.
```

**Description section guidelines:**

Based on change type:

**For security fixes:**

```markdown
This PR addresses security vulnerabilities identified in the [connector-name] connector by updating dependencies and fixing SAST issues.
```

**For SDK updates:**

```markdown
This PR updates the @devrev/ts-adaas SDK from [old-version] to [new-version], bringing [key improvements/fixes].
```

**For features:**

```markdown
This PR adds [feature name] to enable [capability/use case].
```

**For bug fixes:**

```markdown
This PR fixes [specific issue] that was causing [problem description].
```

**Connected Issues section:**

Always use full DevRev URLs:

- ✅ Correct: `https://app.devrev.ai/devrev/works/ISS-252455`
- ❌ Incorrect: `ISS-252455` or `#ISS-252455`

If multiple work items:

```markdown
## Connected Issues

https://app.devrev.ai/devrev/works/ISS-252455
https://app.devrev.ai/devrev/works/ISS-252456
```

**Changes section (optional):**

Include for PRs with multiple modifications:

- Dependency updates
- Code changes
- Configuration changes
- File additions/deletions

**How to test section:**

Include when changes need verification:

1. Clear, numbered steps
2. Expected outcomes
3. Any prerequisites (test accounts, data, environment)

Omit for obvious changes (typo fixes, comment updates) but mark checklist item as done.

**Checklist:**

Mark applicable items with `[x]`:

- Always mark first item (tests) as done, explain if tests not needed
- Always mark second item (lint) if you've run linting
- Mark third item if "How to test" is included OR not needed

**Step 11:** Present PR content to user

Show the proposed PR title and description to the user:

```markdown
## Proposed PR

**Title:** [Generated title]

**Description:**
[Full PR description following template]

---

Should I create this PR? (yes/no/edit)
```

Wait for user response:

- **"yes"** or approval: Proceed to create PR
- **"no"** or rejection: Stop and ask what to change
- **"edit"**: Ask what needs to be modified

### Phase 4: Create PR

**Step 12:** Push branch to remote

```bash
# Push branch and set upstream
git push -u origin HEAD
```

**Step 13:** Create PR using GitHub CLI

Use `gh pr create` with the approved title and description:

```bash
gh pr create --title "PR title" --body "$(cat <<'EOF'
# Description
[Full description content]

## Connected Issues
https://app.devrev.ai/devrev/works/ISS-{NUMBER}

## Changes
- Change 1
- Change 2

## How to test
1. Step 1
2. Step 2

## Checklist
- [x] Tests added/updated and ran with `npm run test` OR no tests needed.
- [x] Code formatted and checked with `npm run lint`.
- [x] Added "How to test" section to the description OR this section is not needed.
EOF
)"
```

**Important:**

- Always use HEREDOC format for the body to preserve formatting
- Include all sections from the template
- Use the full work item URL in Connected Issues section

**Step 14:** Report PR URL

After successful creation, display the PR URL to the user:

```markdown
✅ PR created successfully!

**PR URL:** [GitHub PR URL]

**Branch:** ISS-{NUMBER}-{description}
**Work Item:** https://app.devrev.ai/devrev/works/ISS-{NUMBER}
```

## Bundled Resources

### references/pr_template.md

Complete reference for the connector PR template format, including:

- Standard template structure
- Work item URL format
- Branch naming conventions
- Common PR examples by type (security, feature, bug fix, config)
- Best practices for each section

**When to reference:**

- Need detailed examples of PR descriptions
- Unsure about template structure
- Want to see examples for specific change types

## Important Rules

### Branch Naming

**✅ DO:**

- Always prefix with work item ID: `ISS-{NUMBER}-{description}`
- Use kebab-case for description (lowercase with hyphens)
- Keep description concise (2-5 words)
- Base description on actual changes

**❌ NEVER:**

- Create branches without work item prefix
- Use camelCase or snake_case in branch names
- Use generic names like `ISS-123-updates` or `ISS-456-fixes`
- Skip asking for work item ID when needed

### Work Item References

**✅ DO:**

- Always use full DevRev URLs: `https://app.devrev.ai/devrev/works/ISS-{NUMBER}`
- Include work item URL in "Connected Issues" section
- Support multiple work items (one URL per line)

**❌ NEVER:**

- Use short references like `#ISS-123` or just `ISS-123`
- Omit the work item URL
- Use placeholder or made-up work item IDs

### PR Content

**✅ DO:**

- Follow the standard template structure
- Write description in active voice and present tense
- Include "How to test" for non-trivial changes
- Generate description based on actual changes
- Use HEREDOC format for `gh pr create --body`
- Present proposed PR content to user before creating
- Mark checklist items appropriately

**❌ NEVER:**

- Skip the PR template structure
- Create PR without user approval of content
- Use passive voice in description
- Include issue numbers in PR title
- Make up or guess at changes

### Git Operations

**✅ DO:**

- Check current branch before creating new one
- Verify changes are committed before pushing
- Use `git push -u origin HEAD` to push new branch
- Check for uncommitted changes

**❌ NEVER:**

- Create new branch if already on properly named feature branch
- Push without committing changes
- Force push without user approval
- Create PR from main/master branch

## Example Usage

**User request:**

> "Create a PR for the security fixes"

**Skill workflow:**

1. Check current branch: `git branch --show-current` → Returns `main`
2. Prompt: "To create a properly named branch, I need the DevRev work item ID. Please provide the work item ID (e.g., ISS-252455):"
3. User provides: "ISS-252455"
4. Analyze changes: `git diff`, `git status` → Identifies security-related dependency updates
5. Generate branch name: `ISS-252455-fix-security-vulnerabilities`
6. Create branch: `git checkout -b ISS-252455-fix-security-vulnerabilities`
7. Commit changes if needed
8. Analyze changes: Review diff since main
9. Generate PR content:
   - Title: "Fix security vulnerabilities in dependencies"
   - Description: Following template with security fix details
10. Present to user for approval
11. User approves
12. Push: `git push -u origin HEAD`
13. Create PR: `gh pr create` with generated content
14. Report PR URL to user

## Troubleshooting

### Work Item ID Format

**Issue:** User provides full URL instead of just ID
**Solution:** Extract ID from URL (e.g., `https://app.devrev.ai/devrev/works/ISS-252455` → `ISS-252455`)

### Already on Feature Branch

**Issue:** User is already on a branch with work item prefix
**Solution:** Skip branch creation, extract work item ID from branch name, proceed to PR creation

### No Changes to Commit

**Issue:** `git status` shows no changes
**Solution:** Inform user there are no changes to create a PR for; suggest committing changes first

### Branch Already Exists Remotely

**Issue:** `git push` fails because branch exists on remote
**Solution:** Inform user the branch exists; suggest using `git pull` or creating a different branch name

### gh CLI Not Authenticated

**Issue:** `gh pr create` fails with authentication error
**Solution:** Prompt user to run `gh auth login` first

### Multiple Work Items

**Issue:** Changes relate to multiple work items
**Solution:** Ask user which work item should be primary (for branch name), include all work items in "Connected Issues" section

## Related Tools

- **security-remediation skill:** Use before this skill to fix security issues, then use this skill to create the PR
- **Git:** Used for branch management and pushing changes
- **GitHub CLI (gh):** Used for creating pull requests
