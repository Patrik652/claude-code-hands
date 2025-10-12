#!/usr/bin/env python3
"""
Basic automation example - Calculator demo
"""

import asyncio

# This would use the MCP client to communicate with servers
# For now, it's a template showing the workflow

async def calculator_demo():
    """Open calculator and perform calculation"""
    print("🧮 Calculator Demo")

    # 1. Capture screen to see what we're working with
    print("📸 Capturing screen...")
    # screenshot = await vision.capture_screen()

    # 2. Find calculator icon
    print("🔍 Finding calculator...")
    # calc_pos = await vision.find_element("templates/calculator_icon.png")

    # 3. Click to open
    print("🖱️ Opening calculator...")
    # await hands.mouse_click(calc_pos["x"], calc_pos["y"])

    # 4. Wait for window
    print("⏳ Waiting for window...")
    # await integration.wait_for_element("Calculator")

    # 5. Type calculation
    print("⌨️ Typing calculation...")
    # await hands.keyboard_type("2+2=")

    # 6. Extract result
    print("🔍 Reading result...")
    # result = await vision.extract_text(region="result_area")

    print("✅ Demo completed!")

if __name__ == "__main__":
    asyncio.run(calculator_demo())
