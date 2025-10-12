# 🚀 Quick Start Guide

## 5-Minute Setup

### 1. Install

```bash
cd ~/claude-code-hands
./claude-code-integration/setup.sh
```

### 2. Test

```bash
# Test Vision MCP
python3 mcp-servers/vision-mcp/server.py
# Press Ctrl+C to stop

# Test Hands MCP
python3 mcp-servers/hands-mcp/server.py
# Press Ctrl+C to stop
```

### 3. Use in Claude Code

Restart Claude Code, then try:

```
"Capture my screen"
"What's my screen resolution?"
"Move mouse to 500, 300"
```

## First Automation

Create a file `my_first_automation.py`:

```python
#!/usr/bin/env python3
import asyncio

async def main():
    # This is a template - actual MCP communication
    # happens through Claude Code
    print("🎯 Automation template ready!")
    print("Use Claude Code to execute vision & hands tools")

if __name__ == "__main__":
    asyncio.run(main())
```

## Common Commands

| What you want | Say to Claude |
|---------------|---------------|
| See screen | "Capture screen" |
| Find element | "Find the Firefox icon" |
| Click somewhere | "Click at 500, 300" |
| Type text | "Type 'Hello World'" |
| Save file | "Press Ctrl+S" |
| Run workflow | "Execute workflow examples/workflow-example.yaml" |

## Next Steps

1. Read [README.md](README.md) for full overview
2. Check [docs/INSTALLATION.md](docs/INSTALLATION.md) for detailed setup
3. See [examples/](examples/) for more examples
4. Review [claude-code-integration/CLAUDE_CODE_INSTRUCTIONS.md](claude-code-integration/CLAUDE_CODE_INSTRUCTIONS.md) for API reference

## Troubleshooting

**Server won't start?**
```bash
pip3 install --upgrade -r mcp-servers/vision-mcp/requirements.txt --yes
```

**Screen capture fails?**
```bash
echo $DISPLAY  # Should show :0 or :1
export DISPLAY=:0
```

**Permission denied?**
```bash
chmod +x claude-code-integration/setup.sh
```

## Get Help

- 📖 [Full Documentation](docs/)
- 🐛 [Report Issues](https://github.com/Patrik652/claude-code-hands/issues)
- 💬 [Discussions](https://github.com/Patrik652/claude-code-hands/discussions)

---

**Ready to automate? Let's go! 🚀**
