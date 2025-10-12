# 🤖 Claude Code Vision & Hands - Integration Instructions

## For Claude Code Agent

### Your New Capabilities

You now have access to computer vision and control through MCP servers:

#### Vision Tools (mcp__vision__)
- `capture_screen()` - Capture full screen or specific monitor
- `capture_region(x, y, width, height)` - Capture screen region
- `find_element(template_path, confidence)` - Find UI element
- `extract_text(x, y, width, height)` - OCR text extraction
- `wait_for_element(template_path, timeout)` - Wait for element
- `get_screen_info()` - Get monitor information
- `health_check()` - Check system status

#### Hands Tools (mcp__hands__)
- `mouse_move(x, y, duration)` - Move mouse
- `mouse_click(x, y, button, clicks)` - Click mouse
- `mouse_drag(start_x, start_y, end_x, end_y)` - Drag mouse
- `mouse_scroll(clicks, direction)` - Scroll wheel
- `keyboard_type(text, interval)` - Type text
- `keyboard_press(key, presses)` - Press key
- `keyboard_hotkey(keys)` - Press key combination
- `get_mouse_position()` - Get cursor position
- `get_screen_size()` - Get screen dimensions
- `emergency_stop()` - Stop all automation

#### Integration Tools (mcp__integration__)
- `execute_workflow(workflow_path)` - Run YAML workflow
- `create_workflow(name, steps)` - Create workflow
- `list_workflows()` - List available workflows

### Usage Patterns

#### Pattern 1: Vision + Action
```python
# 1. See what's on screen
screenshot = await mcp__vision__capture_screen()

# 2. Find element
button = await mcp__vision__find_element("save_button.png", confidence=0.8)

# 3. Click it
if button and button["found"]:
    await mcp__hands__mouse_click(button["x"], button["y"])
```

#### Pattern 2: Wait and Interact
```python
# Wait for element to appear
element = await mcp__vision__wait_for_element("dialog.png", timeout=10)

if element:
    # Extract text from it
    text = await mcp__vision__extract_text(
        x=element["bbox"]["x"],
        y=element["bbox"]["y"],
        width=element["bbox"]["width"],
        height=element["bbox"]["height"]
    )

    # Respond based on text
    if "Error" in text["full_text"]:
        await mcp__hands__keyboard_press("escape")
```

#### Pattern 3: Workflow Automation
```python
# Execute pre-defined workflow
result = await mcp__integration__execute_workflow(
    "~/.claude-workflows/open_editor.yaml"
)

if result["success"]:
    print(f"Completed {result['completed_steps']} steps")
```

### Safety Rules

#### ⚠️ NEVER:
1. Click on password fields or sensitive areas
2. Exceed 100 actions per minute
3. Ignore boundary checks
4. Disable failsafe mechanisms
5. Run automation on banking/financial apps without explicit permission

#### ✅ ALWAYS:
1. Check bounds before clicking: `x, y < screen_size`
2. Use `wait_for_element()` instead of fixed delays
3. Handle errors gracefully with try/except
4. Log actions for debugging
5. Verify results after actions

### Example: Complete Automation

```python
async def automate_task(task_description):
    try:
        # 1. Get screen info
        screen = await mcp__hands__get_screen_size()
        print(f"Screen: {screen['width']}x{screen['height']}")

        # 2. Capture current state
        before = await mcp__vision__capture_screen()

        # 3. Find target element
        target = await mcp__vision__find_element(
            "target_icon.png",
            confidence=0.8
        )

        if not target or not target["found"]:
            print("Element not found")
            return False

        # 4. Click element
        await mcp__hands__mouse_click(
            target["x"],
            target["y"]
        )

        # 5. Wait for response
        await asyncio.sleep(1)

        # 6. Verify action
        after = await mcp__vision__capture_screen()

        # 7. Extract result
        result_text = await mcp__vision__extract_text()

        print(f"Result: {result_text['full_text']}")
        return True

    except Exception as e:
        print(f"Error: {e}")
        await mcp__hands__emergency_stop()
        return False
```

### Debugging

When something goes wrong:

```python
# Check system health
vision_health = await mcp__vision__health_check()
hands_health = await mcp__hands__health_check()

print(f"Vision status: {vision_health['status']}")
print(f"Hands status: {hands_health['status']}")

# Check logs
# Vision: ~/.claude-vision-cache/vision_log_*.jsonl
# Hands: ~/.claude-hands-logs/hands_log_*.jsonl

# Check cache
# Screenshots: ~/.claude-vision-cache/screen_*.png
# Debug images: ~/.claude-vision-cache/match_*.png
```

### Tips for Best Results

1. **Template Images**: Keep templates small (50x50 to 200x200 px)
2. **Confidence**: Use 0.8 for exact matches, 0.6 for fuzzy matches
3. **Timeouts**: Set reasonable timeouts (5-10s for most operations)
4. **Error Handling**: Always wrap automation in try/except
5. **Rate Limiting**: Space out actions with small delays

### Integration with Existing Tools

Combine with your other capabilities:

```python
# Use with memory system
await mcp__memory__store_memory({
    "type": "procedural",
    "action": "automated_task",
    "screenshot": screenshot,
    "success": True
})

# Use with browser automation
if is_browser_element:
    await browser_click(selector)
else:
    await mcp__hands__mouse_click(x, y)

# Use with Sage for analysis
screenshot = await mcp__vision__capture_screen()
analysis = await sage(
    mode="analyze",
    input=screenshot,
    prompt="What buttons are visible?"
)
```

### Quick Reference

| Task | Tool | Example |
|------|------|---------|
| See screen | vision | `capture_screen()` |
| Find button | vision | `find_element("btn.png")` |
| Read text | vision | `extract_text()` |
| Click | hands | `mouse_click(x, y)` |
| Type | hands | `keyboard_type("text")` |
| Save Ctrl+S | hands | `keyboard_hotkey(["ctrl", "s"])` |
| Run workflow | integration | `execute_workflow("task.yaml")` |

### Emergency Stop

If anything goes wrong:

```python
# Stop all automation
await mcp__hands__emergency_stop()

# Or move mouse to screen corner (failsafe)
```

## Testing Your Integration

Try these commands after setup:

```bash
# In Claude Code:
"Capture the screen"
"Find the Firefox icon"
"Click at coordinates 500, 300"
"Type 'Hello World'"
"Press Ctrl+S"
"Execute workflow examples/workflow-example.yaml"
```

---

**Remember**: With great power comes great responsibility!
Use these tools to help users, automate tasks, and make computing easier. 🚀
