# 🤖 Claude Vision & Hands

> Give Claude Code eyes and hands - Open Source Computer Vision & Control System

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Protocol](https://img.shields.io/badge/MCP-1.0-purple.svg)](https://modelcontextprotocol.io)

## 🎯 Overview

Claude Vision & Hands je open-source systém, ktorý dáva Claude Code schopnosť vidieť obrazovku a ovládať počítač. 100% open source s MIT licenciou.

### Hlavné funkcie

- 👁️ **Vision MCP** - Zachytávanie obrazovky, OCR, detekcia UI elementov
- 🖱️ **Hands MCP** - Ovládanie myši a klávesnice
- 🔄 **Integration MCP** - Koordinácia komplexných workflow
- 🐳 **Docker ready** - Jednoduchý deployment
- 🔒 **Bezpečnostné mechanizmy** - Rate limiting, failsafe, audit logging

## 🚀 Quick Start

### Inštalácia

```bash
# Clone repository
git clone https://github.com/Patrik652/claude-code-hands
cd claude-code-hands

# Install dependencies
pip install -r mcp-servers/vision-mcp/requirements.txt
pip install -r mcp-servers/hands-mcp/requirements.txt
pip install -r mcp-servers/integration-mcp/requirements.txt

# Test servers
python3 mcp-servers/vision-mcp/server.py &
python3 mcp-servers/hands-mcp/server.py &
python3 mcp-servers/integration-mcp/server.py &
```

### Docker Setup

```bash
# Build and run
cd docker
docker-compose up -d

# Access VNC on port 5900
```

### Claude Code Integration

```bash
# Run setup script
./claude-code-integration/setup.sh

# Or manually add to ~/.claude/mcp_servers.json:
{
  "mcpServers": {
    "vision": {
      "command": "python3",
      "args": ["/path/to/mcp-servers/vision-mcp/server.py"]
    },
    "hands": {
      "command": "python3",
      "args": ["/path/to/mcp-servers/hands-mcp/server.py"]
    },
    "integration": {
      "command": "python3",
      "args": ["/path/to/mcp-servers/integration-mcp/server.py"]
    }
  }
}
```

## 📖 Usage Examples

### Basic Screen Capture

```python
# Capture screen
screenshot = await vision.capture_screen()

# Capture specific region
region = await vision.capture_region(x=100, y=100, width=500, height=300)

# Extract text with OCR
text = await vision.extract_text()
```

### Mouse & Keyboard Control

```python
# Move and click
await hands.mouse_move(x=500, y=300)
await hands.mouse_click(button="left")

# Type text
await hands.keyboard_type("Hello from Claude!")

# Keyboard shortcuts
await hands.keyboard_hotkey(["ctrl", "s"])
```

### Workflow Automation

```yaml
# workflow.yaml
name: "Open and edit document"
steps:
  - action: "vision.find"
    target: "editor_icon.png"
  - action: "hands.click"
    use_previous_result: true
  - action: "hands.type"
    text: "Automated text!"
```

```python
# Execute workflow
result = await integration.execute_workflow("workflow.yaml")
```

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│           Claude Code (Modified)                 │
├─────────────────────────────────────────────────┤
│                MCP Protocol Layer                │
├──────────┬──────────┬──────────┬────────────────┤
│  Vision  │  Hands   │  Memory  │  Browser       │
│   MCP    │   MCP    │   MCP    │ Automation     │
└──────────┴──────────┴──────────┴────────────────┘
```

### Vision MCP Features

- Screen capture (70-150 FPS)
- Template matching
- OCR with PaddleOCR
- Multi-monitor support
- GPU acceleration

### Hands MCP Features

- Mouse control (move, click, drag)
- Keyboard control (type, press, hotkeys)
- Safety features (failsafe, rate limiting)
- Forbidden area protection

### Integration MCP Features

- Workflow execution
- YAML-based workflows
- Step coordination
- Error recovery

## 🔒 Security

### Built-in Safety Features

1. **Failsafe** - Move mouse to corner to stop
2. **Rate Limiting** - Max 100 actions/minute
3. **Boundary Checks** - Verify coordinates
4. **Audit Logging** - All actions logged
5. **Forbidden Areas** - Protect sensitive UI

### Configuration

```python
# Customize safety settings
pyautogui.FAILSAFE = True
pyautogui.PAUSE = 0.1

# Define forbidden areas
FORBIDDEN_AREAS = [
    {"name": "password_field", "x": 100, "y": 200, "width": 300, "height": 50}
]
```

## 📊 Performance

| Operation | Latency | Throughput |
|-----------|---------|------------|
| Screen capture | 12-20ms | 70-150 FPS |
| OCR extraction | 50-200ms | 5-20 regions/s |
| Mouse click | 10-50ms | 20-100 clicks/s |
| Template match | 100-500ms | 2-10 matches/s |

## 🛠️ Development

### Project Structure

```
claude-code-hands/
├── mcp-servers/
│   ├── vision-mcp/         # Vision server
│   ├── hands-mcp/          # Control server
│   └── integration-mcp/    # Coordinator
├── docker/                 # Docker configs
├── examples/               # Usage examples
├── docs/                   # Documentation
└── claude-code-integration/ # Claude Code setup
```

### Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## 📄 License

MIT License - see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built on MCP Protocol
- Uses PaddleOCR, OpenCV, PyAutoGUI

## 📞 Support

- 🐛 [Issues](https://github.com/Patrik652/claude-code-hands/issues)
- 💬 [Discussions](https://github.com/Patrik652/claude-code-hands/discussions)
- 📖 [Documentation](docs/)

## ✅ Current Features

- ✅ **Screen capture** - Full screen, monitor, region capture
- ✅ **OCR text extraction** - PaddleOCR integration
- ✅ **UI element detection** - Template matching
- ✅ **Mouse/keyboard control** - PyAutoGUI automation
- ✅ **Multi-monitor support** - Capture from any display
- ✅ **Safety features** - Failsafe, rate limiting, audit logs
- ✅ **MCP Protocol** - Full Claude Code integration
- ✅ **Docker support** - Ready for deployment

## 💡 Potential Future Enhancements

Community contributions welcome for:
- AI vision models (YOLO, object detection)
- Workflow recorder/playback
- Wayland protocol improvements
- Mobile device control
- Browser extension

---

Made with ❤️ by the Claude Vision & Hands Team

**Star ⭐ this repo if you find it useful!**
