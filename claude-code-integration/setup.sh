#!/bin/bash
# Claude Code Integration Setup Script

set -e

echo "🤖 Claude Vision & Hands - Setup Script"
echo "========================================"

# Get project root
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
echo "📁 Project root: $PROJECT_ROOT"

# Install Vision MCP
echo ""
echo "📦 Installing Vision MCP..."
cd "$PROJECT_ROOT/mcp-servers/vision-mcp"
pip3 install -r requirements.txt --yes

# Install Hands MCP
echo ""
echo "📦 Installing Hands MCP..."
cd "$PROJECT_ROOT/mcp-servers/hands-mcp"
pip3 install -r requirements.txt --yes

# Install Integration MCP
echo ""
echo "📦 Installing Integration MCP..."
cd "$PROJECT_ROOT/mcp-servers/integration-mcp"
pip3 install -r requirements.txt --yes

# Create Claude config directory
CLAUDE_CONFIG_DIR="$HOME/.claude"
mkdir -p "$CLAUDE_CONFIG_DIR"

# Backup existing config
if [ -f "$CLAUDE_CONFIG_DIR/mcp_servers.json" ]; then
    echo ""
    echo "💾 Backing up existing config..."
    cp "$CLAUDE_CONFIG_DIR/mcp_servers.json" "$CLAUDE_CONFIG_DIR/mcp_servers.json.backup.$(date +%Y%m%d_%H%M%S)"
fi

# Create or update MCP servers config
echo ""
echo "⚙️ Configuring MCP servers..."

cat > "$CLAUDE_CONFIG_DIR/mcp_servers.json" << EOF
{
  "mcpServers": {
    "vision": {
      "command": "python3",
      "args": ["$PROJECT_ROOT/mcp-servers/vision-mcp/server.py"],
      "env": {
        "DISPLAY": "${DISPLAY:-:0}"
      }
    },
    "hands": {
      "command": "python3",
      "args": ["$PROJECT_ROOT/mcp-servers/hands-mcp/server.py"],
      "env": {
        "PYAUTOGUI_FAILSAFE": "1"
      }
    },
    "integration": {
      "command": "python3",
      "args": ["$PROJECT_ROOT/mcp-servers/integration-mcp/server.py"]
    }
  }
}
EOF

echo "✅ MCP servers configured at: $CLAUDE_CONFIG_DIR/mcp_servers.json"

# Test servers
echo ""
echo "🧪 Testing servers..."

echo "  Testing Vision MCP..."
timeout 5 python3 "$PROJECT_ROOT/mcp-servers/vision-mcp/server.py" &
VISION_PID=$!
sleep 2
if ps -p $VISION_PID > /dev/null; then
    echo "  ✅ Vision MCP running"
    kill $VISION_PID 2>/dev/null || true
else
    echo "  ❌ Vision MCP failed to start"
fi

echo "  Testing Hands MCP..."
timeout 5 python3 "$PROJECT_ROOT/mcp-servers/hands-mcp/server.py" &
HANDS_PID=$!
sleep 2
if ps -p $HANDS_PID > /dev/null; then
    echo "  ✅ Hands MCP running"
    kill $HANDS_PID 2>/dev/null || true
else
    echo "  ❌ Hands MCP failed to start"
fi

echo "  Testing Integration MCP..."
timeout 5 python3 "$PROJECT_ROOT/mcp-servers/integration-mcp/server.py" &
INTEGRATION_PID=$!
sleep 2
if ps -p $INTEGRATION_PID > /dev/null; then
    echo "  ✅ Integration MCP running"
    kill $INTEGRATION_PID 2>/dev/null || true
else
    echo "  ❌ Integration MCP failed to start"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Restart Claude Code"
echo "  2. Try: 'capture screen' or 'click at 500 300'"
echo "  3. Check logs at ~/.claude-vision-cache/ and ~/.claude-hands-logs/"
echo ""
echo "Documentation: $PROJECT_ROOT/docs/"
echo "Examples: $PROJECT_ROOT/examples/"
