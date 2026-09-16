# Content Type Templates

Reference templates for each documentation content type. Use these as starting structures when drafting documents in STEP-004.

---

## 1. README

```markdown
# [Project Name]

A paragraph or two describing what the project does at a high level.

## Installation
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Examples

[Basic usage examples]

## Troubleshooting

[Common issues and quick fixes]

## Changelog

[Recent changes]

## Additional resources

- [Link to full documentation]
- [Link to API reference]

## License

[License information]
```

---

## 2. Getting Started

```markdown
# Getting Started with [Product]

[One paragraph: what the product is and what its core features do.]

## Prerequisites
- [Requirement 1]
- [Requirement 2]

## Quick Start

1. [First step to get up and running]
2. [Second step]
3. [Third step]

[Verification: how to confirm it's working]

## What's Next
- [Link to conceptual docs]
- [Link to first how-to guide]
- [Link to API reference]
```

---

## 3. Conceptual Documentation

```markdown
# [Concept Name]

[First paragraph introducing the concept and why it matters.]

## Overview

[Technical overview of how the concept works.]

### [Sub-concept 1]

[Explanation]

### [Sub-concept 2]

[Explanation]

## Additional resources
- [Link to related tutorial]
- [Link to related how-to guide]
```

---

## 4. How-To Guide

```markdown
# [How to Do X]

[First paragraph introducing core concepts and overview for this guide.]

## Prerequisites
- [Prerequisite 1]
- [Prerequisite 2]

## Steps

1. [Action step 1]
2. [Action step 2]
3. [Action step 3]
4. [Action step 4]
5. [Action step 5]

[Verification: how to confirm the procedure worked]

## Next steps
- [Link to related guide]
- [Link to advanced topic]
```

---

## 5. Tutorial

```markdown
# Tutorial: [Learning Goal]

[What the user will learn and build by the end of this tutorial.]

## Prerequisites
- [Prerequisite 1]
- [Prerequisite 2]

## What you'll build

[Brief description of the end result]

## Steps

### Step 1: [Setup]
[Instructions]

### Step 2: [Core action]
[Instructions]

### Step 3: [Verification]
[Instructions]

## Summary

[What the user accomplished and learned]

## Next steps
- [Link to more advanced tutorial]
- [Link to real-world how-to guide]
```

---

## 6. API Reference

```markdown
# [Product] API Reference

[Brief intro: API standards (e.g., REST, JSON), authentication method.]

## Authentication

[How to authenticate with the API]

## Endpoints

### [Resource Name]

#### [METHOD] /path/to/endpoint

[Brief description of what this endpoint does.]

**Parameters:**

| Name | Type | Required | Description |
|---|---|---|---|
| [param] | [type] | [Yes/No] | [Description] |

**Example request:**

\`\`\`shell
$ curl 'https://api.example.com/v1/resource' -i
\`\`\`

**Example response:**

\`\`\`json
{
  "id": 1,
  "name": "example"
}
\`\`\`

**Status codes:**

| Code | Description |
|---|---|
| 200 | Success |
| 400 | Bad request |
| 401 | Unauthorized |
| 404 | Not found |

## Error Messages

| Error Code | Message | Resolution |
|---|---|---|
| [code] | [message] | [how to fix] |
```

---

## 7. Troubleshooting

```markdown
# Troubleshooting [Topic]

## [Issue 1 Title]

**Description:** [What the user experiences]

**Steps to fix:**
1. [Step 1]
2. [Step 2]

## [Issue 2 Title]

**Description:** [What the user experiences]

**Steps to fix:**
1. [Step 1]
2. [Step 2]
```

Organize issues by: descending frequency (most common first) or chronological workflow order.

---

## 8. Glossary

```markdown
# Glossary

| Term | Definition |
|---|---|
| [Term 1] | [Definition] |
| [Term 2] | [Definition] |
| [Term 3] | [Definition] |
```

---

## 9. Release Notes

```markdown
# Release Notes

## YYYY-MM-DD

### [Item Title]
- **Summary**: [What changed]
- **Impact**: [Who is affected and how]
- **Reasoning**: [Why the change was made]
- **Actions required**: [What users need to do, if anything]
```

Entries include: new features, bug fixes, known bugs or limitations, migrations.

---

## 10. Changelog

```markdown
# Changelog

## [Version] - YYYY-MM-DD

### Added
- [New feature or capability]

### Changed
- [Modification to existing feature]

### Deprecated
- [Feature marked for future removal]

### Removed
- [Feature removed]

### Fixed
- [Bug fix]
```
