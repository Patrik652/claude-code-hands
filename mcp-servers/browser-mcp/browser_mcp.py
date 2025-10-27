#!/usr/bin/env python3
"""
Browser MCP Server - Playwright-based browser automation
Similar to OpenAI Atlas browser control capabilities
"""

import asyncio
import json
import os
import base64
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List, Tuple
from pathlib import Path
import re

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from playwright.async_api import async_playwright, Page, Browser, ElementHandle
from PIL import Image
import io

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("browser-mcp")

class BrowserController:
    """
    Advanced browser automation controller
    Provides Atlas-like capabilities for web interaction
    """
    
    def __init__(self):
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.context = None
        self.current_url = None
        self.page_history = []
        self.element_cache = {}
        self.aria_tree = None
        
    async def initialize(self, headless: bool = False):
        """Initialize Playwright and browser"""
        try:
            self.playwright = await async_playwright().start()
            
            # Launch browser with optimized settings
            self.browser = await self.playwright.chromium.launch(
                headless=headless,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu' if headless else '',
                ]
            )
            
            # Create context with permissions
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            # Create page
            self.page = await self.context.new_page()
            
            # Enable console logging
            self.page.on("console", lambda msg: logger.info(f"Browser console: {msg.text}"))
            
            logger.info("✅ Browser initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    async def navigate(self, url: str, wait_for: str = "domcontentloaded") -> Dict[str, Any]:
        """Navigate to URL with smart waiting"""
        try:
            if not self.page:
                await self.initialize()
            
            # Navigate to URL
            response = await self.page.goto(url, wait_until=wait_for)
            
            # Update state
            self.current_url = self.page.url
            self.page_history.append({
                'url': self.current_url,
                'timestamp': datetime.now().isoformat(),
                'title': await self.page.title()
            })
            
            # Clear element cache for new page
            self.element_cache.clear()
            
            # Extract page info
            return {
                'success': True,
                'url': self.current_url,
                'title': await self.page.title(),
                'status': response.status if response else None,
                'history_length': len(self.page_history)
            }
            
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def extract_aria_tree(self) -> Dict[str, Any]:
        """
        Extract accessibility tree (ARIA) like Atlas
        This is how Atlas understands page structure
        """
        try:
            if not self.page:
                return {'success': False, 'error': 'No page loaded'}
            
            # Get accessibility tree
            aria_snapshot = await self.page.accessibility.snapshot()
            
            # Cache the tree
            self.aria_tree = aria_snapshot
            
            # Parse and structure the tree
            structured = self._parse_aria_tree(aria_snapshot)
            
            return {
                'success': True,
                'tree': structured,
                'elements_count': self._count_elements(structured),
                'interactive_elements': self._find_interactive_elements(structured)
            }
            
        except Exception as e:
            logger.error(f"ARIA extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def _parse_aria_tree(self, node: Dict, depth: int = 0) -> Dict[str, Any]:
        """Parse ARIA tree into structured format"""
        if not node:
            return {}
        
        result = {
            'role': node.get('role', 'unknown'),
            'name': node.get('name', ''),
            'description': node.get('description', ''),
            'value': node.get('value', ''),
            'level': depth
        }
        
        # Add state information
        if 'checked' in node:
            result['checked'] = node['checked']
        if 'disabled' in node:
            result['disabled'] = node['disabled']
        if 'expanded' in node:
            result['expanded'] = node['expanded']
        if 'selected' in node:
            result['selected'] = node['selected']
        
        # Process children
        children = []
        for child in node.get('children', []):
            parsed_child = self._parse_aria_tree(child, depth + 1)
            if parsed_child:
                children.append(parsed_child)
        
        if children:
            result['children'] = children
        
        return result
    
    def _count_elements(self, tree: Dict) -> int:
        """Count total elements in ARIA tree"""
        if not tree:
            return 0
        
        count = 1  # Count current node
        for child in tree.get('children', []):
            count += self._count_elements(child)
        
        return count
    
    def _find_interactive_elements(self, tree: Dict, elements: List = None) -> List[Dict]:
        """Find all interactive elements in ARIA tree"""
        if elements is None:
            elements = []
        
        # Interactive roles
        interactive_roles = [
            'button', 'link', 'textbox', 'checkbox', 'radio',
            'combobox', 'menuitem', 'tab', 'slider', 'switch'
        ]
        
        if tree.get('role') in interactive_roles:
            elements.append({
                'role': tree['role'],
                'name': tree.get('name', ''),
                'description': tree.get('description', ''),
                'disabled': tree.get('disabled', False)
            })
        
        # Recursively check children
        for child in tree.get('children', []):
            self._find_interactive_elements(child, elements)
        
        return elements
    
    async def find_element(
        self,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        aria_label: Optional[str] = None,
        role: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Find element using multiple strategies
        Similar to Atlas element detection
        """
        try:
            element = None
            strategy_used = None
            
            # Try different strategies
            if selector:
                element = await self.page.query_selector(selector)
                strategy_used = "css_selector"
            
            elif text:
                element = await self.page.get_by_text(text).first
                strategy_used = "text_content"
            
            elif aria_label:
                element = await self.page.get_by_label(aria_label).first
                strategy_used = "aria_label"
            
            elif role:
                element = await self.page.get_by_role(role).first
                strategy_used = "aria_role"
            
            if element:
                # Get element details
                bbox = await element.bounding_box()
                is_visible = await element.is_visible()
                is_enabled = await element.is_enabled()
                
                # Get element properties
                tag_name = await element.evaluate("el => el.tagName")
                inner_text = await element.inner_text() if tag_name not in ['INPUT', 'IMG'] else ""
                
                return {
                    'success': True,
                    'found': True,
                    'strategy': strategy_used,
                    'element': {
                        'tag': tag_name,
                        'text': inner_text[:100],  # Limit text length
                        'visible': is_visible,
                        'enabled': is_enabled,
                        'bbox': bbox
                    }
                }
            else:
                return {
                    'success': True,
                    'found': False,
                    'strategy': strategy_used
                }
                
        except Exception as e:
            logger.error(f"Element search failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def click_element(
        self,
        selector: Optional[str] = None,
        text: Optional[str] = None,
        aria_label: Optional[str] = None
    ) -> Dict[str, Any]:
        """Click element with multiple targeting strategies"""
        try:
            clicked = False
            
            if selector:
                await self.page.click(selector)
                clicked = True
            elif text:
                await self.page.get_by_text(text).click()
                clicked = True
            elif aria_label:
                await self.page.get_by_label(aria_label).click()
                clicked = True
            
            if clicked:
                # Wait for any navigation or updates
                await self.page.wait_for_load_state('networkidle', timeout=5000)
                
                return {
                    'success': True,
                    'clicked': True,
                    'current_url': self.page.url
                }
            
            return {'success': False, 'error': 'No valid selector provided'}
            
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def fill_form(
        self,
        selector: str,
        value: str,
        press_enter: bool = False
    ) -> Dict[str, Any]:
        """Fill form input with value"""
        try:
            # Clear and fill
            await self.page.fill(selector, value)
            
            if press_enter:
                await self.page.press(selector, 'Enter')
            
            return {
                'success': True,
                'filled': True,
                'selector': selector,
                'value_length': len(value)
            }
            
        except Exception as e:
            logger.error(f"Form fill failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def extract_page_content(self) -> Dict[str, Any]:
        """Extract structured page content"""
        try:
            # Get page content
            content = await self.page.content()
            
            # Extract text
            text_content = await self.page.evaluate("""
                () => {
                    const walker = document.createTreeWalker(
                        document.body,
                        NodeFilter.SHOW_TEXT,
                        null,
                        false
                    );
                    const text = [];
                    let node;
                    while (node = walker.nextNode()) {
                        const trimmed = node.textContent.trim();
                        if (trimmed) text.push(trimmed);
                    }
                    return text.join(' ');
                }
            """)
            
            # Extract links
            links = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('a[href]')).map(a => ({
                    text: a.innerText,
                    href: a.href,
                    target: a.target
                }))
            """)
            
            # Extract forms
            forms = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('form')).map(form => ({
                    action: form.action,
                    method: form.method,
                    inputs: Array.from(form.querySelectorAll('input, select, textarea')).map(input => ({
                        name: input.name,
                        type: input.type || 'text',
                        required: input.required,
                        value: input.value
                    }))
                }))
            """)
            
            # Extract images
            images = await self.page.evaluate("""
                () => Array.from(document.querySelectorAll('img')).map(img => ({
                    src: img.src,
                    alt: img.alt,
                    width: img.width,
                    height: img.height
                }))
            """)
            
            return {
                'success': True,
                'title': await self.page.title(),
                'url': self.page.url,
                'text_length': len(text_content),
                'links_count': len(links),
                'forms_count': len(forms),
                'images_count': len(images),
                'content': {
                    'text': text_content[:1000],  # First 1000 chars
                    'links': links[:10],  # First 10 links
                    'forms': forms,
                    'images': images[:5]  # First 5 images
                }
            }
            
        except Exception as e:
            logger.error(f"Content extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def screenshot(self, full_page: bool = False) -> Dict[str, Any]:
        """Take screenshot of current page"""
        try:
            # Take screenshot
            screenshot_bytes = await self.page.screenshot(
                full_page=full_page,
                type='png'
            )
            
            # Convert to base64 for transport
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            # Also save to file
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            filepath = Path(f"/tmp/{filename}")
            
            with open(filepath, 'wb') as f:
                f.write(screenshot_bytes)
            
            return {
                'success': True,
                'base64': screenshot_b64,
                'filepath': str(filepath),
                'size': len(screenshot_bytes),
                'full_page': full_page
            }
            
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def execute_javascript(self, script: str) -> Dict[str, Any]:
        """Execute JavaScript in page context"""
        try:
            result = await self.page.evaluate(script)
            
            return {
                'success': True,
                'result': result
            }
            
        except Exception as e:
            logger.error(f"JavaScript execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def wait_for_element(
        self,
        selector: str,
        timeout: int = 30000,
        state: str = "visible"
    ) -> Dict[str, Any]:
        """Wait for element to appear/disappear"""
        try:
            locator = self.page.locator(selector)
            
            if state == "visible":
                await locator.wait_for(state="visible", timeout=timeout)
            elif state == "hidden":
                await locator.wait_for(state="hidden", timeout=timeout)
            elif state == "attached":
                await locator.wait_for(state="attached", timeout=timeout)
            
            return {
                'success': True,
                'selector': selector,
                'state': state
            }
            
        except Exception as e:
            logger.error(f"Wait failed: {e}")
            return {'success': False, 'error': str(e), 'timeout': timeout}
    
    async def get_cookies(self) -> Dict[str, Any]:
        """Get browser cookies"""
        try:
            cookies = await self.context.cookies()
            
            return {
                'success': True,
                'cookies': cookies,
                'count': len(cookies)
            }
            
        except Exception as e:
            logger.error(f"Cookie retrieval failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def set_cookie(self, cookie: Dict) -> Dict[str, Any]:
        """Set browser cookie"""
        try:
            await self.context.add_cookies([cookie])
            
            return {
                'success': True,
                'cookie_set': True
            }
            
        except Exception as e:
            logger.error(f"Cookie setting failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def cleanup(self):
        """Clean up browser resources"""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            if self.playwright:
                await self.playwright.stop()
            
            logger.info("Browser cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


# MCP Server setup
browser_controller = BrowserController()
server = Server("browser-mcp")

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """List all available browser tools"""
    return [
        types.Tool(
            name="browser_navigate",
            description="Navigate browser to URL",
            inputSchema={
                "type": "object",
                "properties": {
                    "url": {"type": "string", "description": "URL to navigate to"},
                    "wait_for": {"type": "string", "description": "Wait condition", "default": "domcontentloaded"}
                },
                "required": ["url"]
            }
        ),
        types.Tool(
            name="browser_click",
            description="Click element on page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"},
                    "text": {"type": "string", "description": "Text content"},
                    "aria_label": {"type": "string", "description": "ARIA label"}
                }
            }
        ),
        types.Tool(
            name="browser_fill",
            description="Fill form input",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Input selector"},
                    "value": {"type": "string", "description": "Value to fill"},
                    "press_enter": {"type": "boolean", "description": "Press Enter after filling"}
                },
                "required": ["selector", "value"]
            }
        ),
        types.Tool(
            name="browser_extract_aria",
            description="Extract ARIA accessibility tree",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="browser_find_element",
            description="Find element on page",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "CSS selector"},
                    "text": {"type": "string", "description": "Text content"},
                    "aria_label": {"type": "string", "description": "ARIA label"},
                    "role": {"type": "string", "description": "ARIA role"}
                }
            }
        ),
        types.Tool(
            name="browser_screenshot",
            description="Take screenshot of page",
            inputSchema={
                "type": "object",
                "properties": {
                    "full_page": {"type": "boolean", "description": "Capture full page", "default": False}
                }
            }
        ),
        types.Tool(
            name="browser_extract_content",
            description="Extract structured page content",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="browser_execute_js",
            description="Execute JavaScript in page",
            inputSchema={
                "type": "object",
                "properties": {
                    "script": {"type": "string", "description": "JavaScript code to execute"}
                },
                "required": ["script"]
            }
        ),
        types.Tool(
            name="browser_wait_for",
            description="Wait for element",
            inputSchema={
                "type": "object",
                "properties": {
                    "selector": {"type": "string", "description": "Element selector"},
                    "timeout": {"type": "integer", "description": "Timeout in ms", "default": 30000},
                    "state": {"type": "string", "description": "State to wait for", "default": "visible"}
                },
                "required": ["selector"]
            }
        ),
        types.Tool(
            name="browser_init",
            description="Initialize browser",
            inputSchema={
                "type": "object",
                "properties": {
                    "headless": {"type": "boolean", "description": "Run headless", "default": False}
                }
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """Handle tool calls"""
    
    # Initialize browser if needed
    if not browser_controller.browser and name != "browser_init":
        await browser_controller.initialize()
    
    result = {}
    
    if name == "browser_init":
        success = await browser_controller.initialize(
            headless=arguments.get("headless", False)
        )
        result = {"success": success}
    
    elif name == "browser_navigate":
        result = await browser_controller.navigate(
            url=arguments["url"],
            wait_for=arguments.get("wait_for", "domcontentloaded")
        )
    
    elif name == "browser_click":
        result = await browser_controller.click_element(
            selector=arguments.get("selector"),
            text=arguments.get("text"),
            aria_label=arguments.get("aria_label")
        )
    
    elif name == "browser_fill":
        result = await browser_controller.fill_form(
            selector=arguments["selector"],
            value=arguments["value"],
            press_enter=arguments.get("press_enter", False)
        )
    
    elif name == "browser_extract_aria":
        result = await browser_controller.extract_aria_tree()
    
    elif name == "browser_find_element":
        result = await browser_controller.find_element(
            selector=arguments.get("selector"),
            text=arguments.get("text"),
            aria_label=arguments.get("aria_label"),
            role=arguments.get("role")
        )
    
    elif name == "browser_screenshot":
        result = await browser_controller.screenshot(
            full_page=arguments.get("full_page", False)
        )
    
    elif name == "browser_extract_content":
        result = await browser_controller.extract_page_content()
    
    elif name == "browser_execute_js":
        result = await browser_controller.execute_javascript(
            script=arguments["script"]
        )
    
    elif name == "browser_wait_for":
        result = await browser_controller.wait_for_element(
            selector=arguments["selector"],
            timeout=arguments.get("timeout", 30000),
            state=arguments.get("state", "visible")
        )
    
    else:
        result = {"error": f"Unknown tool: {name}"}
    
    return [types.TextContent(
        type="text",
        text=json.dumps(result, indent=2)
    )]

async def main():
    """Main entry point"""
    logger.info("🌐 Browser MCP Server starting...")
    
    # Run server
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="browser-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    asyncio.run(main())
