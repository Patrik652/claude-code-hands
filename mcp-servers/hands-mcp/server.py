#!/usr/bin/env python3
"""
Hands MCP Server - Ruky pre Claude Code
MIT License - Open Source
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

# Core dependencies
import pyautogui
from pynput import mouse, keyboard as pynput_keyboard

# MCP dependencies
from fastmcp import FastMCP, Context
from pydantic import BaseModel, Field

# Initialize MCP server
app = FastMCP("hands-mcp")

# Safety configuration
pyautogui.FAILSAFE = True  # Move mouse to corner to stop
pyautogui.PAUSE = 0.1  # Pause between actions

# Logging
LOG_DIR = Path.home() / ".claude-hands-logs"
LOG_DIR.mkdir(exist_ok=True)

def log_action(action: str, details: Dict[str, Any]):
    """Log all control actions for security and debugging"""
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "details": details
    }
    log_file = LOG_DIR / f"hands_log_{datetime.now().strftime('%Y%m%d')}.jsonl"
    with open(log_file, 'a') as f:
        f.write(json.dumps(log_entry) + '\n')

# Safety checks
def check_bounds(x: int, y: int) -> bool:
    """Verify coordinates are within screen bounds"""
    screen_width, screen_height = pyautogui.size()
    return 0 <= x < screen_width and 0 <= y < screen_height

def check_forbidden_area(x: int, y: int) -> bool:
    """Check if coordinates are in forbidden areas"""
    # Add forbidden areas here (password managers, banking apps, etc.)
    FORBIDDEN_AREAS = []

    for area in FORBIDDEN_AREAS:
        if (area["x"] <= x <= area["x"] + area["width"] and
            area["y"] <= y <= area["y"] + area["height"]):
            return True
    return False

# Rate limiting
class RateLimiter:
    def __init__(self, max_actions: int = 100, window_seconds: int = 60):
        self.max_actions = max_actions
        self.window_seconds = window_seconds
        self.actions = []

    def check(self) -> bool:
        """Check if action is allowed"""
        now = time.time()
        # Remove old actions
        self.actions = [t for t in self.actions if now - t < self.window_seconds]

        if len(self.actions) >= self.max_actions:
            return False

        self.actions.append(now)
        return True

rate_limiter = RateLimiter()

# MCP Tools - Mouse Control

@app.tool()
async def mouse_move(
    x: int,
    y: int,
    duration: float = 0.5
) -> Dict[str, Any]:
    """
    Move mouse to position

    Args:
        x, y: Target coordinates
        duration: Movement duration in seconds

    Returns:
        Dictionary with final position
    """
    try:
        # Safety checks
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        if not check_bounds(x, y):
            raise ValueError(f"Coordinates out of bounds: ({x}, {y})")

        if check_forbidden_area(x, y):
            raise ValueError("Attempting to access forbidden area")

        # Move mouse
        pyautogui.moveTo(x, y, duration=duration)

        # Log action
        log_action("mouse_move", {
            "x": x,
            "y": y,
            "duration": duration
        })

        return {
            "status": "success",
            "position": {"x": x, "y": y}
        }

    except Exception as e:
        log_action("mouse_move_error", {"error": str(e)})
        raise Exception(f"Mouse move failed: {str(e)}")

@app.tool()
async def mouse_click(
    x: Optional[int] = None,
    y: Optional[int] = None,
    button: str = "left",
    clicks: int = 1,
    interval: float = 0.1
) -> Dict[str, Any]:
    """
    Click mouse at position

    Args:
        x, y: Click coordinates (current position if not provided)
        button: Mouse button (left, right, middle)
        clicks: Number of clicks
        interval: Interval between clicks

    Returns:
        Dictionary with click details
    """
    try:
        # Safety checks
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        if x is not None and y is not None:
            if not check_bounds(x, y):
                raise ValueError(f"Coordinates out of bounds: ({x}, {y})")

            if check_forbidden_area(x, y):
                raise ValueError("Attempting to access forbidden area")

            # Move to position first
            pyautogui.moveTo(x, y, duration=0.2)
        else:
            x, y = pyautogui.position()

        # Perform click
        pyautogui.click(button=button, clicks=clicks, interval=interval)

        # Log action
        log_action("mouse_click", {
            "x": x,
            "y": y,
            "button": button,
            "clicks": clicks
        })

        return {
            "status": "success",
            "position": {"x": x, "y": y},
            "button": button,
            "clicks": clicks
        }

    except Exception as e:
        log_action("mouse_click_error", {"error": str(e)})
        raise Exception(f"Mouse click failed: {str(e)}")

@app.tool()
async def mouse_drag(
    start_x: int,
    start_y: int,
    end_x: int,
    end_y: int,
    duration: float = 0.5,
    button: str = "left"
) -> Dict[str, Any]:
    """
    Drag mouse from start to end position

    Args:
        start_x, start_y: Starting coordinates
        end_x, end_y: Ending coordinates
        duration: Drag duration
        button: Mouse button to hold

    Returns:
        Dictionary with drag details
    """
    try:
        # Safety checks
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        if not check_bounds(start_x, start_y) or not check_bounds(end_x, end_y):
            raise ValueError("Coordinates out of bounds")

        # Move to start position
        pyautogui.moveTo(start_x, start_y, duration=0.2)

        # Perform drag
        pyautogui.drag(end_x - start_x, end_y - start_y, duration=duration, button=button)

        # Log action
        log_action("mouse_drag", {
            "start": {"x": start_x, "y": start_y},
            "end": {"x": end_x, "y": end_y},
            "duration": duration
        })

        return {
            "status": "success",
            "start": {"x": start_x, "y": start_y},
            "end": {"x": end_x, "y": end_y}
        }

    except Exception as e:
        log_action("mouse_drag_error", {"error": str(e)})
        raise Exception(f"Mouse drag failed: {str(e)}")

@app.tool()
async def mouse_scroll(
    clicks: int,
    direction: str = "down"
) -> Dict[str, Any]:
    """
    Scroll mouse wheel

    Args:
        clicks: Number of scroll clicks
        direction: Scroll direction (up or down)

    Returns:
        Dictionary with scroll details
    """
    try:
        # Safety check
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        scroll_amount = clicks if direction == "up" else -clicks
        pyautogui.scroll(scroll_amount)

        # Log action
        log_action("mouse_scroll", {
            "clicks": clicks,
            "direction": direction
        })

        return {
            "status": "success",
            "clicks": clicks,
            "direction": direction
        }

    except Exception as e:
        log_action("mouse_scroll_error", {"error": str(e)})
        raise Exception(f"Mouse scroll failed: {str(e)}")

# MCP Tools - Keyboard Control

@app.tool()
async def keyboard_type(
    text: str,
    interval: float = 0.05
) -> Dict[str, Any]:
    """
    Type text on keyboard

    Args:
        text: Text to type
        interval: Interval between keystrokes

    Returns:
        Dictionary with typing details
    """
    try:
        # Safety check
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        # Type text
        pyautogui.write(text, interval=interval)

        # Log action (don't log sensitive data)
        log_action("keyboard_type", {
            "length": len(text),
            "interval": interval
        })

        return {
            "status": "success",
            "characters_typed": len(text)
        }

    except Exception as e:
        log_action("keyboard_type_error", {"error": str(e)})
        raise Exception(f"Keyboard typing failed: {str(e)}")

@app.tool()
async def keyboard_press(
    key: str,
    presses: int = 1,
    interval: float = 0.1
) -> Dict[str, Any]:
    """
    Press keyboard key

    Args:
        key: Key to press (e.g., 'enter', 'esc', 'tab')
        presses: Number of presses
        interval: Interval between presses

    Returns:
        Dictionary with press details
    """
    try:
        # Safety check
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        # Press key
        pyautogui.press(key, presses=presses, interval=interval)

        # Log action
        log_action("keyboard_press", {
            "key": key,
            "presses": presses
        })

        return {
            "status": "success",
            "key": key,
            "presses": presses
        }

    except Exception as e:
        log_action("keyboard_press_error", {"error": str(e)})
        raise Exception(f"Keyboard press failed: {str(e)}")

@app.tool()
async def keyboard_hotkey(
    keys: List[str]
) -> Dict[str, Any]:
    """
    Press keyboard hotkey combination

    Args:
        keys: List of keys to press together (e.g., ['ctrl', 's'])

    Returns:
        Dictionary with hotkey details
    """
    try:
        # Safety check
        if not rate_limiter.check():
            raise Exception("Rate limit exceeded")

        # Press hotkey
        pyautogui.hotkey(*keys)

        # Log action
        log_action("keyboard_hotkey", {
            "keys": keys
        })

        return {
            "status": "success",
            "keys": keys
        }

    except Exception as e:
        log_action("keyboard_hotkey_error", {"error": str(e)})
        raise Exception(f"Keyboard hotkey failed: {str(e)}")

# System Information

@app.tool()
async def get_mouse_position() -> Dict[str, Any]:
    """
    Get current mouse position

    Returns:
        Dictionary with mouse coordinates
    """
    x, y = pyautogui.position()
    return {
        "x": x,
        "y": y
    }

@app.tool()
async def get_screen_size() -> Dict[str, Any]:
    """
    Get screen dimensions

    Returns:
        Dictionary with screen size
    """
    width, height = pyautogui.size()
    return {
        "width": width,
        "height": height
    }

# Emergency stop
@app.tool()
async def emergency_stop() -> Dict[str, Any]:
    """
    Emergency stop all automation

    Returns:
        Dictionary with stop status
    """
    log_action("emergency_stop", {"timestamp": datetime.now().isoformat()})

    # Clear rate limiter
    rate_limiter.actions.clear()

    return {
        "status": "stopped",
        "message": "All automation halted. Move mouse to corner for failsafe."
    }

# Health check
@app.tool()
async def health_check() -> Dict[str, Any]:
    """
    Check hands system health

    Returns:
        System status and capabilities
    """
    try:
        screen_width, screen_height = pyautogui.size()
        mouse_x, mouse_y = pyautogui.position()

        return {
            "status": "healthy",
            "capabilities": {
                "mouse_control": True,
                "keyboard_control": True,
                "failsafe": pyautogui.FAILSAFE,
                "pause": pyautogui.PAUSE
            },
            "screen": {
                "width": screen_width,
                "height": screen_height
            },
            "mouse": {
                "x": mouse_x,
                "y": mouse_y
            },
            "rate_limit": {
                "current_actions": len(rate_limiter.actions),
                "max_actions": rate_limiter.max_actions
            },
            "logs": {
                "directory": str(LOG_DIR)
            },
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# Main entry point
if __name__ == "__main__":
    # Print startup info
    print("🖐️ Hands MCP Server starting...")
    print(f"📁 Log directory: {LOG_DIR}")
    print(f"⚠️ Failsafe: {pyautogui.FAILSAFE}")

    # Check dependencies
    try:
        import pyautogui
        from pynput import mouse, keyboard
        print("✅ All dependencies loaded")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        sys.exit(1)

    # Run server
    print("🚀 Server ready on stdio")
    app.run()
