# Browser Control Integration

To add browser control to hands-mcp, add these lines to server.py:

```python
# Import at top
import sys
sys.path.append('../browser-mcp')
from browser_integration import BrowserIntegration

# In server initialization
browser_integration = BrowserIntegration(server)
await browser_integration.initialize()
browser_integration.register_tools()
```

This adds these new tools:
- browser_navigate(url) - Navigate to URL
- browser_click(selector/text/aria_label) - Click element
- browser_fill(selector, value) - Fill form
- browser_extract_aria() - Get accessibility tree
- browser_screenshot() - Take screenshot
- browser_execute_workflow(name, context) - Run workflow
- And more...

## Usage Examples:

```python
# Navigate and interact
await browser_navigate("https://example.com")
await browser_fill("#search", "test query")
await browser_click("button[type='submit']")

# Extract ARIA tree (like Atlas)
aria = await browser_extract_aria()
print(f"Found {aria['elements_count']} elements")

# Run workflow
await browser_execute_workflow("google_search", {
    "search_query": "Claude AI"
})
```
