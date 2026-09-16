# PRC-010 Tools Reference

## Browser Automation (Chrome MCP)

STEP-007: Product Walkthrough uses browser automation to verify documentation against the live product. The AI agent controls a Chrome browser through the Claude-in-Chrome MCP extension.

### Available Tools

| Tool | Purpose |
|---|---|
| `tabs_context_mcp` | List open tabs and get current browser state. **Always call first** at the start of a session. |
| `tabs_create_mcp` | Open a new tab. Use instead of reusing existing tabs. |
| `navigate` | Go to a URL in a specific tab. |
| `read_page` | Read the visible content of a page (text, links, structure). |
| `find` | Search for text or UI elements on the page. Returns coordinates for clicking. |
| `computer` | Perform mouse/keyboard actions: click, type, scroll, take screenshots. |
| `form_input` | Fill form fields by selector. |
| `javascript_tool` | Run JavaScript on the page for inspection or interaction. |
| `get_page_text` | Extract all text content from the page. |
| `read_console_messages` | Read browser console output. Use `pattern` parameter to filter. |
| `read_network_requests` | Inspect network traffic (useful for API verification). |
| `gif_creator` | Record multi-step interactions as animated GIFs for documentation screenshots. |
| `upload_image` | Upload an image file to a page (e.g., for form uploads). |

### Workflow

1. **Start session**: Call `tabs_context_mcp` to see current browser state.
2. **Open product**: Use `tabs_create_mcp` to open a new tab, then `navigate` to the product URL.
3. **Verify UI labels**: Use `read_page` or `find` to locate elements mentioned in the docs.
4. **Walk through procedures**: Use `computer` (click, type) and `navigate` to follow each documented step.
5. **Capture screenshots**: Use `gif_creator` to record interactions, or `computer` with `screenshot` action for static captures. Save to the doc's `images/` directory.
6. **Verify URLs**: Use `navigate` and confirm the page loads correctly.
7. **Verify API**: Use `read_network_requests` to inspect API calls, or `javascript_tool` to make test requests.

### Screenshot Capture

**Static screenshots**:
- Use `computer` with screenshot action to capture the current page state
- Save with a descriptive filename (e.g., `signup-page.png`, `dashboard-create-link.png`)

**Animated GIFs** (for multi-step flows):
- Start `gif_creator` recording before performing the steps
- Capture extra frames before and after actions for smooth playback
- Name meaningfully (e.g., `create-link-flow.gif`)
- Use `download: true` to save to disk

### Constraints

- **No alerts/dialogs**: Avoid triggering `alert()`, `confirm()`, or `prompt()` — these block the browser extension.
- **Tab IDs are session-scoped**: Never reuse tab IDs from a previous session. Call `tabs_context_mcp` if a tab ID stops working.
- **Stay focused**: If browser tools fail after 2-3 attempts, stop and ask the user for guidance.
- **Console debugging**: Use `javascript_tool` with `console.log()` and read via `read_console_messages` instead of triggering dialogs.
