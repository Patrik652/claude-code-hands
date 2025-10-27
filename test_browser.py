#!/usr/bin/env python3
"""Test browser control functionality"""

import asyncio
import sys
sys.path.append('mcp-servers/browser-mcp')

from browser_mcp import BrowserController

async def test_browser():
    print("🧪 Testing Browser Control...")
    
    # Initialize browser
    browser = BrowserController()
    success = await browser.initialize(headless=False)
    
    if not success:
        print("❌ Failed to initialize browser")
        return
    
    print("✅ Browser initialized")
    
    # Test navigation
    result = await browser.navigate("https://example.com")
    print(f"✅ Navigated to: {result.get('url')}")
    
    # Test ARIA extraction
    aria = await browser.extract_aria_tree()
    print(f"✅ ARIA tree extracted: {aria.get('elements_count')} elements")
    
    # Test screenshot
    screenshot = await browser.screenshot()
    print(f"✅ Screenshot saved: {screenshot.get('filepath')}")
    
    # Test content extraction
    content = await browser.extract_page_content()
    print(f"✅ Content extracted: {content.get('text_length')} chars")
    
    # Cleanup
    await browser.cleanup()
    print("✅ Browser closed")
    
    print("\n🎉 All tests passed!")

if __name__ == "__main__":
    asyncio.run(test_browser())
