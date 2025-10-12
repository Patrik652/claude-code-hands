FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV DISPLAY=:99

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-tk \
    python3-dev \
    xvfb \
    x11vnc \
    openbox \
    scrot \
    xdotool \
    wget \
    curl \
    git \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Copy MCP servers
COPY mcp-servers /app/mcp-servers

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    -r /app/mcp-servers/vision-mcp/requirements.txt \
    -r /app/mcp-servers/hands-mcp/requirements.txt \
    -r /app/mcp-servers/integration-mcp/requirements.txt

# Create startup script
RUN echo '#!/bin/bash\n\
Xvfb :99 -screen 0 1920x1080x24 &\n\
sleep 2\n\
openbox &\n\
x11vnc -display :99 -forever -nopw -quiet &\n\
echo "Display ready on :99"\n\
echo "VNC available on port 5900"\n\
tail -f /dev/null\n\
' > /app/start.sh && chmod +x /app/start.sh

EXPOSE 5900

CMD ["/app/start.sh"]
