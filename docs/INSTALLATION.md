# Installation Guide

## Prerequisites

- Python 3.8+
- Linux (X11 or Wayland), Windows, or macOS
- Display server (for screen capture)
- 2GB RAM minimum
- Optional: GPU for acceleration

## Installation Methods

### Method 1: Direct Installation (Recommended)

```bash
# Clone repository
git clone https://github.com/yourusername/claude-vision-hands
cd claude-vision-hands

# Run setup script
./claude-code-integration/setup.sh
```

### Method 2: Manual Installation

#### 1. Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update -y
sudo apt install -y python3 python3-pip python3-tk xdotool scrot
```

**Fedora/RHEL:**
```bash
sudo dnf install -y python3 python3-pip python3-tkinter xdotool
```

**macOS:**
```bash
brew install python@3.11 tcl-tk
```

#### 2. Install Python Packages

```bash
# Vision MCP
cd mcp-servers/vision-mcp
pip3 install -r requirements.txt --yes

# Hands MCP
cd ../hands-mcp
pip3 install -r requirements.txt --yes

# Integration MCP
cd ../integration-mcp
pip3 install -r requirements.txt --yes
```

#### 3. Configure Claude Code

Create or edit `~/.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "vision": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp-servers/vision-mcp/server.py"]
    },
    "hands": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp-servers/hands-mcp/server.py"]
    },
    "integration": {
      "command": "python3",
      "args": ["/absolute/path/to/mcp-servers/integration-mcp/server.py"]
    }
  }
}
```

### Method 3: Docker Installation

```bash
# Build and run
cd docker
docker-compose up -d

# Access via VNC
# Connect to localhost:5900
```

## Verification

Test if servers are working:

```bash
# Test Vision MCP
python3 mcp-servers/vision-mcp/server.py

# Test Hands MCP
python3 mcp-servers/hands-mcp/server.py

# Test Integration MCP
python3 mcp-servers/integration-mcp/server.py
```

## Troubleshooting

### No screen capture

**Linux X11:**
```bash
echo $DISPLAY  # Should show :0 or similar
xhost +local:  # Allow local connections
```

**Linux Wayland:**
```bash
# Install additional tools
sudo apt install -y ydotool
```

### Permission errors

```bash
# Add user to input group
sudo usermod -a -G input $USER

# Logout and login again
```

### Import errors

```bash
# Reinstall dependencies
pip3 install --upgrade --force-reinstall -r requirements.txt --yes
```

### GPU acceleration not working

```bash
# Check CUDA
nvidia-smi

# Install CUDA-enabled packages
pip3 install opencv-python-headless --yes
pip3 install paddlepaddle-gpu --yes
```

## Next Steps

- Read [CONFIGURATION.md](CONFIGURATION.md) for customization
- See [examples/](../examples/) for usage examples
- Check [API_REFERENCE.md](API_REFERENCE.md) for API docs
