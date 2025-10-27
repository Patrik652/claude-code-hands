"""
Browser MCP Integration for Hands MCP Server
Adds browser control capabilities alongside PyAutoGUI
"""

import asyncio
import logging
from typing import Optional, Dict, Any
from pathlib import Path

from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types

# Import browser controller
from browser_mcp import BrowserController
from browser_automation import BrowserAutomation

logger = logging.getLogger("hands-mcp-browser")

class BrowserIntegration:
    """
    Integrates browser control into existing Hands MCP
    Provides both PyAutoGUI (desktop) and Playwright (browser) control
    """
    
    def __init__(self, server: Server):
        self.server = server
        self.browser = BrowserController()
        self.automation = BrowserAutomation(self.browser)
        self.mode = "hybrid"  # hybrid, browser_only, desktop_only
        
    async def initialize(self):
        """Initialize browser integration"""
        success = await self.browser.initialize(headless=False)
        if success:
            logger.info("✅ Browser integration initialized")
            # Load sample workflows
            for name, workflow in SAMPLE_WORKFLOWS.items():
                self.automation.workflows[name] = workflow
        return success
    
    def register_tools(self):
        """Register browser tools with MCP server"""
        
        @self.server.tool()
        async def browser_navigate(url: str, wait_for: str = "domcontentloaded") -> dict:
            """Navigate browser to URL"""
            return await self.browser.navigate(url, wait_for)
        
        @self.server.tool()
        async def browser_click(
            selector: Optional[str] = None,
            text: Optional[str] = None,
            aria_label: Optional[str] = None
        ) -> dict:
            """Click element in browser"""
            return await self.browser.click_element(selector, text, aria_label)
        
        @self.server.tool()
        async def browser_fill(
            selector: str,
            value: str,
            press_enter: bool = False
        ) -> dict:
            """Fill form input in browser"""
            return await self.browser.fill_form(selector, value, press_enter)
        
        @self.server.tool()
        async def browser_extract_aria() -> dict:
            """Extract ARIA accessibility tree"""
            return await self.browser.extract_aria_tree()
        
        @self.server.tool()
        async def browser_find_element(
            selector: Optional[str] = None,
            text: Optional[str] = None,
            aria_label: Optional[str] = None,
            role: Optional[str] = None
        ) -> dict:
            """Find element in browser"""
            return await self.browser.find_element(selector, text, aria_label, role)
        
        @self.server.tool()
        async def browser_screenshot(full_page: bool = False) -> dict:
            """Take browser screenshot"""
            return await self.browser.screenshot(full_page)
        
        @self.server.tool()
        async def browser_extract_content() -> dict:
            """Extract structured content from page"""
            return await self.browser.extract_page_content()
        
        @self.server.tool()
        async def browser_execute_workflow(
            workflow_name: str,
            context: Optional[dict] = None
        ) -> dict:
            """Execute predefined workflow"""
            return await self.automation.execute_workflow(workflow_name, context or {})
        
        @self.server.tool()
        async def browser_smart_fill(
            form_data: dict,
            submit_button: Optional[str] = None
        ) -> dict:
            """Smart form filling with multiple fields"""
            return await self.automation.smart_form_fill(form_data, submit_button)
        
        @self.server.tool()
        async def browser_intelligent_nav(
            target_text: str,
            max_depth: int = 3
        ) -> dict:
            """Intelligently navigate to find target"""
            return await self.automation.intelligent_navigation(target_text, max_depth)
        
        @self.server.tool()
        async def switch_control_mode(mode: str) -> dict:
            """Switch between hybrid/browser_only/desktop_only modes"""
            if mode in ["hybrid", "browser_only", "desktop_only"]:
                self.mode = mode
                return {"success": True, "mode": mode}
            return {"success": False, "error": "Invalid mode"}
        
        @self.server.tool()
        async def get_control_status() -> dict:
            """Get status of all control systems"""
            return {
                "mode": self.mode,
                "browser": {
                    "initialized": self.browser.browser is not None,
                    "current_url": self.browser.current_url,
                    "history_length": len(self.browser.page_history)
                },
                "automation": {
                    "workflows_loaded": len(self.automation.workflows),
                    "action_history": len(self.automation.action_history),
                    "current_workflow": self.automation.current_workflow
                }
            }
        
        logger.info(f"✅ Registered {12} browser control tools")


# Integration helper functions
def integrate_with_hands_mcp(hands_server_path: str):
    """
    Generate integration code for existing hands-mcp server
    """
    integration_code = """
# Add to hands-mcp/server.py imports:
from browser_integration import BrowserIntegration

# Add to server initialization:
browser_integration = BrowserIntegration(server)
await browser_integration.initialize()
browser_integration.register_tools()

# Now you have both PyAutoGUI (desktop) and Playwright (browser) control!
# Use switch_control_mode() to change between:
# - "hybrid": Both systems active
# - "browser_only": Only browser control
# - "desktop_only": Only PyAutoGUI control
"""
    
    integration_file = Path(hands_server_path) / "browser_integration_snippet.py"
    with open(integration_file, 'w') as f:
        f.write(integration_code)
    
    print(f"Integration snippet saved to: {integration_file}")
    return str(integration_file)


# Hybrid control strategies
class HybridController:
    """
    Intelligent switching between browser and desktop control
    """
    
    def __init__(self, browser_controller, pyautogui_controller):
        self.browser = browser_controller
        self.desktop = pyautogui_controller
        self.current_context = "desktop"
        
    async def smart_click(self, target: str) -> Dict[str, Any]:
        """
        Intelligently decide whether to use browser or desktop click
        """
        # If browser is active and target looks like web element
        if self.browser.page and self._is_web_selector(target):
            result = await self.browser.click_element(selector=target)
            if result['success']:
                return result
        
        # Fallback to desktop click
        return self.desktop.click(target)
    
    def _is_web_selector(self, target: str) -> bool:
        """Check if target is likely a web selector"""
        web_indicators = ['#', '.', '[', '>', 'button', 'input', 'div', 'a']
        return any(indicator in target for indicator in web_indicators)
    
    async def smart_type(self, text: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Type text using appropriate method
        """
        # If target specified and browser active
        if target and self.browser.page:
            result = await self.browser.fill_form(target, text)
            if result['success']:
                return result
        
        # Use desktop typing
        return self.desktop.type_text(text)
    
    async def capture_context(self) -> Dict[str, Any]:
        """
        Capture both browser and desktop context
        """
        context = {
            'timestamp': datetime.now().isoformat()
        }
        
        # Browser context
        if self.browser.page:
            browser_content = await self.browser.extract_page_content()
            context['browser'] = {
                'url': self.browser.current_url,
                'title': browser_content.get('title'),
                'content_summary': browser_content
            }
        
        # Desktop context (screenshot via PyAutoGUI)
        desktop_screenshot = self.desktop.screenshot()
        context['desktop'] = {
            'screenshot': desktop_screenshot,
            'active_window': self.desktop.get_active_window()
        }
        
        return context


# Atlas-like features
class AtlasFeatures:
    """
    Advanced features similar to OpenAI Atlas
    """
    
    @staticmethod
    async def agent_mode(browser_controller, task_description: str) -> Dict[str, Any]:
        """
        Autonomous task completion mode
        """
        # This would use AI to break down task and execute
        # For now, returns structured plan
        return {
            'task': task_description,
            'plan': [
                'Analyze current page',
                'Identify required actions',
                'Execute step by step',
                'Verify completion'
            ],
            'status': 'ready'
        }
    
    @staticmethod
    async def memory_context(browser_controller) -> Dict[str, Any]:
        """
        Extract and store page context for memory
        """
        if not browser_controller.page:
            return {'error': 'No page loaded'}
        
        # Extract comprehensive context
        aria = await browser_controller.extract_aria_tree()
        content = await browser_controller.extract_page_content()
        screenshot = await browser_controller.screenshot()
        
        return {
            'url': browser_controller.current_url,
            'timestamp': datetime.now().isoformat(),
            'aria_tree': aria,
            'content': content,
            'screenshot_ref': screenshot.get('filepath'),
            'interactive_elements': aria.get('interactive_elements', [])
        }


from browser_automation import SAMPLE_WORKFLOWS
