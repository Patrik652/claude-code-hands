# Intelligent Workflow Examples

Complete examples demonstrating the integration of Vision AI, Browser Automation, and Persistent Memory.

## Overview

These examples show how to build intelligent AI agents that:
- **Learn from experience** using persistent memory
- **Analyze screens** with vision AI (Gemini)
- **Automate tasks** with browser and desktop control
- **Make decisions** based on past interactions

## Quick Start

```bash
# Run the main example
cd ~/claude-vision-hands/examples
python3 intelligent_workflow_example.py
```

## Examples Included

### Example 1: Basic Website Analysis with Memory

Demonstrates:
- Navigating to a website
- Analyzing screen content with AI
- Storing analysis in persistent memory
- Searching for similar past experiences

```python
agent = IntelligentWorkflowAgent()

# Analyze and remember
result = await agent.navigate_and_analyze(
    url="https://example.com/login",
    analysis_prompt="What forms are visible?"
)

# Search past experiences
memories = await agent.search_past_experiences("login forms")
```

### Example 2: Intelligent Form Filling

Demonstrates:
- Remembering form structures
- Auto-filling forms based on memory
- Tracking actions for future reference

```python
# First visit - analyze and remember
await agent.navigate_and_analyze(
    url="https://example.com/login",
    analysis_prompt="Identify all form fields"
)

# Second visit - intelligent auto-fill
await agent.intelligent_form_fill("login")
```

### Example 3: Complex Multi-Step Workflow

Demonstrates:
- Executing multi-step workflows
- Error handling and recovery
- Workflow memory for future optimization

```python
# Define workflow steps
async def step_1_navigate():
    return await agent.navigate_and_analyze(...)

async def step_2_authenticate():
    return await agent.intelligent_form_fill("login")

# Execute workflow
result = await agent.execute_workflow(
    workflow_name="user_authentication",
    steps=[step_1_navigate, step_2_authenticate, ...]
)
```

### Example 4: Learning from Experience

Demonstrates:
- Pattern recognition across multiple interactions
- Optimizing future tasks based on past successes
- Building knowledge base over time

```python
# Perform task multiple times
for i in range(10):
    await agent.navigate_and_analyze(...)

# Agent learns:
# - Common screen patterns
# - Optimal interaction sequences
# - Error recovery strategies
```

## Architecture

```
┌─────────────────────────────────────────┐
│     IntelligentWorkflowAgent            │
│  (Orchestrates all components)          │
└────────┬────────────────────┬───────────┘
         │                    │
    ┌────▼─────┐        ┌────▼─────┐
    │ Vision   │        │ Browser  │
    │ AI       │        │ Control  │
    │ (Gemini) │        │ (Hands)  │
    └────┬─────┘        └────┬─────┘
         │                   │
         └───────┬───────────┘
                 │
          ┌──────▼──────┐
          │   Memory    │
          │   System    │
          │  (ChromaDB) │
          └─────────────┘
```

## Integration Points

### Vision AI Integration

Replace simulation with real AI:
```python
# Current (simulation)
analysis = {
    'raw_text': "Simulated text",
    'analysis': "Simulated analysis"
}

# Real integration
from vision_mcp.analyzers import GeminiVisionAnalyzer
analyzer = GeminiVisionAnalyzer()
analysis = await analyzer.analyze_screen(
    screenshot_path,
    prompt=analysis_prompt
)
```

### Browser Control Integration

Replace simulation with real automation:
```python
# Current (simulation)
# await browser_navigate(url)

# Real integration
from browser_mcp import BrowserController
browser = BrowserController()
await browser.navigate(url)
await browser.screenshot("/tmp/screenshot.png")
```

### Desktop Control Integration

For form filling and interactions:
```python
# Real integration
from hands_mcp import HandsController
hands = HandsController()
await hands.click(x=245, y=678)
await hands.type_text("username")
```

## Memory System Features

All examples use persistent memory that:

1. **Stores experiences**
   - Screen analyses
   - Action results
   - Workflow outcomes

2. **Enables semantic search**
   - Natural language queries
   - Similarity-based retrieval
   - Context-aware results

3. **Tracks sessions**
   - Session-based filtering
   - Activity summaries
   - Usage statistics

## Use Cases

### Automated Testing
```python
# Remember test scenarios
agent.store_workflow_memory(
    workflow_name="checkout_test",
    steps=[...],
    success=True
)

# Replay similar scenarios
memories = agent.search_past_experiences("checkout test")
```

### Form Automation
```python
# Learn form structures
agent.navigate_and_analyze("https://form.com", "Identify fields")

# Auto-fill on next visit
agent.intelligent_form_fill("registration")
```

### Web Scraping with Memory
```python
# Remember page structures
agent.store_screen_memory(
    content="Product page layout",
    ai_analysis="Price in top-right, specs in table"
)

# Optimize future scraping
memories = agent.search_past_experiences("product page")
```

### Customer Support Bot
```python
# Remember customer interactions
agent.store_action_memory(
    content="Helped customer with login issue",
    success=True
)

# Learn from past solutions
solutions = agent.search_past_experiences("login issue")
```

## Advanced Features

### Pattern Recognition

The agent learns patterns automatically:
```python
# After multiple login attempts
memories = agent.search_past_experiences("login")

# Agent now knows:
# - Where login buttons typically are
# - Common form field names
# - Successful interaction sequences
```

### Context-Aware Decisions

Make intelligent decisions based on history:
```python
# Check if we've seen this screen before
similar = agent.search_past_experiences(
    f"screen at {current_url}",
    min_score=0.8
)

if similar.total_count > 0:
    # Use known strategy
    await execute_remembered_workflow(similar.results[0])
else:
    # Explore and learn new approach
    await analyze_and_learn(current_url)
```

### Workflow Optimization

Optimize workflows over time:
```python
# Find successful workflows
successful = agent.memory.search_memories(
    query="checkout workflow",
    success_only=True
)

# Use best-performing approach
best_workflow = max(successful.results,
                    key=lambda m: m.memory.metadata.get('success_rate', 0))
```

## Configuration

Memory system can be configured via `config/memory_config.yaml`:

```yaml
memory:
  enabled: true
  storage:
    path: "~/.claude-vision-hands/memory"
    max_size_mb: 500

  embeddings:
    model: "sentence-transformers/all-MiniLM-L6-v2"
    device: "cpu"  # or "cuda" for GPU

  auto_capture:
    enabled: true
    triggers:
      ai_analysis: true
      successful_actions: true
      workflow_completion: true
```

## Best Practices

1. **Start sessions properly**
   ```python
   agent.memory.start_session("unique_session_id")
   ```

2. **Use descriptive content**
   ```python
   agent.store_screen_memory(
       content="Detailed description of what you saw",
       ai_analysis="AI's interpretation and insights"
   )
   ```

3. **Search before acting**
   ```python
   # Check if we've done this before
   memories = agent.search_past_experiences("similar task")
   if memories.total_count > 0:
       # Use learned approach
   ```

4. **Track workflow success**
   ```python
   agent.store_workflow_memory(
       workflow_name="descriptive_name",
       success=True,  # Important for learning!
       duration_seconds=2.5
   )
   ```

5. **Monitor usage**
   ```python
   stats = agent.memory.get_stats()
   if stats.usage_percent > 75:
       # Consider cleanup
       agent.memory.cleanup_old_memories(days=14)
   ```

## Troubleshooting

### Memory search returns no results
- Lower `min_score` threshold (default 0.5)
- Check if memories were actually stored
- Verify embedding model is loaded

### Slow performance
- Use GPU for embeddings (set `device: "cuda"`)
- Increase cache size in config
- Consider batch operations

### Storage quota exceeded
- Run cleanup: `agent.memory.cleanup_old_memories(days=7)`
- Increase quota in config
- Delete unnecessary memories

## Next Steps

1. **Integrate real AI vision** (vision-mcp)
2. **Integrate browser automation** (browser-mcp)
3. **Integrate desktop control** (hands-mcp)
4. **Build custom workflows** for your use cases
5. **Deploy in production** with error handling

## Resources

- Memory System Documentation: `../mcp-servers/memory/README.md`
- Vision AI Documentation: `../mcp-servers/vision-mcp/README.md`
- Browser Control: `../mcp-servers/browser-mcp/README.md`
- Hands Control: `../mcp-servers/hands-mcp/README.md`

## License

Part of Claude Vision & Hands project.
