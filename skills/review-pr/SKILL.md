---
name: review-pr
description: Generate an HTML review page with C4 architecture diagrams and code walkthrough for the current git changes
disable-model-invocation: true
allowed-tools: Bash(git *), Bash(mkdir *), Read, Glob, Grep, Write, Edit
---

# PR Review Page Generator

Generate a self-contained HTML review page for the current uncommitted git changes (or a specified PR). Save it to `.review/index.html`.

## What to produce

The page must contain three sections:

### 1. System Architecture Diagram (C4 Container Level)

A single Mermaid flowchart showing the system architecture with the changed/new components highlighted:

- Use `flowchart TD` (top-down) for the diagram
- Show the request flow from user through frontend to backend
- Group unchanged peer components into a single summary node (e.g. "Other 5 scenarios")
- Highlight changed components with green fill/border: `fill:#d1fae5,stroke:#3fb950,stroke-width:3px`
- Highlight new components with green fill/border and a green circle emoji prefix
- Highlight data sources read by new code with blue: `fill:#dbeafe,stroke:#58a6ff,stroke-width:2px`
- Include a legend below the diagram

### 2. Component Detail Flowchart

A Mermaid flowchart showing the internal logic flow of the changed component:

- Show the decision tree / branching logic
- Mark new code paths with green: `fill:#d1fae5,stroke:#3fb950,stroke-width:2px` and green circle emoji
- Mark removed paths with red dashed: `fill:#fee2e2,stroke:#f85149,stroke-width:2px,stroke-dasharray:5 5` and red circle emoji
- Mark unchanged paths with grey: `fill:#f5f5f5,stroke:#999`
- Add a description table below the diagram explaining each node

### 3. Code Walkthrough

For each logical chunk of the change:
- A narrative step box explaining what the code does and why
- An inline diff block with syntax-highlighted added/removed/context lines

## Diagram guidelines

Keep Mermaid node labels SHORT (under 25 characters) to prevent text truncation. Use the description table below each diagram for detailed explanations. Avoid `\n` for line breaks in labels — use single-line text or unicode separators like `·` or `‹›`.

Always include this Mermaid init for responsive rendering:
```
%%{init: {'flowchart': {'useMaxWidth': true}} }%%
```

## HTML template requirements

- Use Mermaid v11 from CDN: `https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js`
- Dark theme (GitHub dark style): background `#0d1117`, surface `#161b22`, border `#30363d`
- Diagram containers should have white background for readability
- SVG scaling: `.diagram-container .mermaid svg { max-width: 100%; height: auto; }`
- Diff blocks styled with green background for added lines, red for removed, muted for context
- Max container width: 1200px, centered

## Steps

1. Run `git diff HEAD` and `git diff --stat HEAD` to understand the changes
2. Read the changed files and their surrounding architecture (imports, callers, class hierarchy)
3. Create `.review/` directory if it doesn't exist
4. Generate `.review/index.html` with all three sections
5. Open the file in the browser and take a screenshot to verify diagrams render correctly
6. If any diagram is clipped or text is truncated, shorten node labels and re-check

## Arguments

- `$ARGUMENTS` — optional: a git ref, PR number, or branch name to diff against (defaults to uncommitted changes vs HEAD)
