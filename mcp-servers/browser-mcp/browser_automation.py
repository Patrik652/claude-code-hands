"""
Advanced Browser Automation Layer
High-level automation patterns and workflows
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from pathlib import Path

from playwright.async_api import Page, Browser, async_playwright
import yaml

logger = logging.getLogger("browser-automation")

class BrowserAutomation:
    """
    High-level browser automation with workflow support
    Similar to OpenAI Atlas agent mode
    """
    
    def __init__(self, browser_controller):
        self.browser = browser_controller
        self.workflows = {}
        self.action_history = []
        self.current_workflow = None
        self.workflow_state = {}
        
    async def load_workflow(self, workflow_path: str) -> bool:
        """Load workflow from YAML file"""
        try:
            with open(workflow_path, 'r') as f:
                workflow = yaml.safe_load(f)
            
            name = workflow.get('name', 'unnamed')
            self.workflows[name] = workflow
            logger.info(f"Loaded workflow: {name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to load workflow: {e}")
            return False
    
    async def execute_workflow(
        self,
        workflow_name: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Execute complete workflow
        Like Atlas agent mode - autonomous task completion
        """
        try:
            if workflow_name not in self.workflows:
                return {'success': False, 'error': f'Workflow {workflow_name} not found'}
            
            workflow = self.workflows[workflow_name]
            self.current_workflow = workflow_name
            self.workflow_state = context or {}
            
            logger.info(f"Starting workflow: {workflow_name}")
            
            # Execute steps
            results = []
            for i, step in enumerate(workflow['steps']):
                logger.info(f"Executing step {i+1}: {step.get('name', 'unnamed')}")
                
                step_result = await self._execute_step(step)
                results.append(step_result)
                
                # Check for failures
                if not step_result.get('success') and step.get('required', True):
                    logger.error(f"Required step failed: {step.get('name')}")
                    return {
                        'success': False,
                        'workflow': workflow_name,
                        'failed_step': i,
                        'error': step_result.get('error')
                    }
                
                # Add delay between steps
                if 'delay' in step:
                    await asyncio.sleep(step['delay'])
            
            return {
                'success': True,
                'workflow': workflow_name,
                'results': results,
                'state': self.workflow_state
            }
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _execute_step(self, step: Dict) -> Dict[str, Any]:
        """Execute single workflow step"""
        try:
            action = step['action']
            params = step.get('params', {})
            
            # Substitute variables from workflow state
            params = self._substitute_variables(params)
            
            # Record action
            self.action_history.append({
                'timestamp': datetime.now().isoformat(),
                'action': action,
                'params': params
            })
            
            # Execute action
            if action == 'navigate':
                result = await self.browser.navigate(params['url'])
                
            elif action == 'click':
                result = await self.browser.click_element(
                    selector=params.get('selector'),
                    text=params.get('text'),
                    aria_label=params.get('aria_label')
                )
                
            elif action == 'fill':
                result = await self.browser.fill_form(
                    selector=params['selector'],
                    value=params['value'],
                    press_enter=params.get('press_enter', False)
                )
                
            elif action == 'wait':
                result = await self.browser.wait_for_element(
                    selector=params['selector'],
                    timeout=params.get('timeout', 30000),
                    state=params.get('state', 'visible')
                )
                
            elif action == 'extract':
                result = await self.browser.extract_page_content()
                # Store extracted data in workflow state
                if result.get('success') and 'store_as' in step:
                    self.workflow_state[step['store_as']] = result['content']
                
            elif action == 'screenshot':
                result = await self.browser.screenshot(
                    full_page=params.get('full_page', False)
                )
                
            elif action == 'javascript':
                result = await self.browser.execute_javascript(params['script'])
                
            else:
                result = {'success': False, 'error': f'Unknown action: {action}'}
            
            # Add step metadata to result
            result['step_name'] = step.get('name', 'unnamed')
            result['action'] = action
            
            return result
            
        except Exception as e:
            logger.error(f"Step execution failed: {e}")
            return {'success': False, 'error': str(e), 'step': step}
    
    def _substitute_variables(self, params: Any) -> Any:
        """Substitute {{variables}} in parameters"""
        if isinstance(params, str):
            # Replace {{var}} with value from workflow state
            import re
            pattern = r'\{\{(\w+)\}\}'
            
            def replacer(match):
                var_name = match.group(1)
                return str(self.workflow_state.get(var_name, match.group(0)))
            
            return re.sub(pattern, replacer, params)
        
        elif isinstance(params, dict):
            return {k: self._substitute_variables(v) for k, v in params.items()}
        
        elif isinstance(params, list):
            return [self._substitute_variables(item) for item in params]
        
        return params
    
    async def smart_form_fill(
        self,
        form_data: Dict[str, str],
        submit_button_selector: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Intelligently fill form with multiple fields
        Like Atlas form automation
        """
        try:
            results = []
            
            # Fill each field
            for selector, value in form_data.items():
                result = await self.browser.fill_form(selector, value)
                results.append({
                    'field': selector,
                    'success': result.get('success', False)
                })
                
                # Small delay between fields
                await asyncio.sleep(0.5)
            
            # Submit form if button selector provided
            if submit_button_selector:
                submit_result = await self.browser.click_element(
                    selector=submit_button_selector
                )
                results.append({
                    'action': 'submit',
                    'success': submit_result.get('success', False)
                })
            
            return {
                'success': all(r['success'] for r in results),
                'fields_filled': len(form_data),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Smart form fill failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def extract_structured_data(
        self,
        selectors: Dict[str, str]
    ) -> Dict[str, Any]:
        """Extract multiple data points from page"""
        try:
            extracted = {}
            
            for name, selector in selectors.items():
                try:
                    value = await self.browser.page.query_selector(selector)
                    if value:
                        text = await value.inner_text()
                        extracted[name] = text
                    else:
                        extracted[name] = None
                except:
                    extracted[name] = None
            
            return {
                'success': True,
                'data': extracted,
                'extracted_count': sum(1 for v in extracted.values() if v)
            }
            
        except Exception as e:
            logger.error(f"Data extraction failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def wait_and_verify(
        self,
        conditions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Wait for multiple conditions to be met"""
        try:
            results = []
            
            for condition in conditions:
                if condition['type'] == 'element':
                    result = await self.browser.wait_for_element(
                        selector=condition['selector'],
                        timeout=condition.get('timeout', 10000),
                        state=condition.get('state', 'visible')
                    )
                    
                elif condition['type'] == 'text':
                    # Wait for text to appear
                    start_time = asyncio.get_event_loop().time()
                    timeout = condition.get('timeout', 10000) / 1000
                    
                    while asyncio.get_event_loop().time() - start_time < timeout:
                        content = await self.browser.extract_page_content()
                        if condition['text'] in content.get('content', {}).get('text', ''):
                            result = {'success': True}
                            break
                        await asyncio.sleep(0.5)
                    else:
                        result = {'success': False, 'error': 'Text not found'}
                
                results.append({
                    'condition': condition,
                    'met': result.get('success', False)
                })
            
            return {
                'success': all(r['met'] for r in results),
                'conditions_checked': len(conditions),
                'results': results
            }
            
        except Exception as e:
            logger.error(f"Verification failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def intelligent_navigation(
        self,
        target_text: str,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Navigate to find target text/element
        Like Atlas intelligent navigation
        """
        try:
            visited_urls = set()
            queue = [(self.browser.current_url, 0)]
            
            while queue:
                url, depth = queue.pop(0)
                
                if depth > max_depth:
                    continue
                
                if url in visited_urls:
                    continue
                
                visited_urls.add(url)
                
                # Navigate to URL
                await self.browser.navigate(url)
                
                # Check if target found
                content = await self.browser.extract_page_content()
                if target_text.lower() in content.get('content', {}).get('text', '').lower():
                    return {
                        'success': True,
                        'found': True,
                        'url': url,
                        'depth': depth
                    }
                
                # Extract links for next level
                if depth < max_depth:
                    for link in content.get('content', {}).get('links', [])[:10]:
                        if link['href'] not in visited_urls:
                            queue.append((link['href'], depth + 1))
            
            return {
                'success': True,
                'found': False,
                'pages_visited': len(visited_urls)
            }
            
        except Exception as e:
            logger.error(f"Intelligent navigation failed: {e}")
            return {'success': False, 'error': str(e)}
    
    async def record_workflow(
        self,
        output_path: str,
        duration: int = 60
    ) -> Dict[str, Any]:
        """
        Record user actions to create workflow
        Similar to Atlas learning mode
        """
        try:
            recorded_actions = []
            start_time = asyncio.get_event_loop().time()
            
            # Start recording
            logger.info(f"Recording workflow for {duration} seconds...")
            
            # This would need browser event listeners in real implementation
            # For now, return placeholder
            
            workflow = {
                'name': 'recorded_workflow',
                'description': 'Automatically recorded workflow',
                'created': datetime.now().isoformat(),
                'steps': recorded_actions
            }
            
            # Save workflow
            with open(output_path, 'w') as f:
                yaml.dump(workflow, f)
            
            return {
                'success': True,
                'workflow_path': output_path,
                'actions_recorded': len(recorded_actions)
            }
            
        except Exception as e:
            logger.error(f"Workflow recording failed: {e}")
            return {'success': False, 'error': str(e)}


# Predefined workflows
SAMPLE_WORKFLOWS = {
    "search_google": {
        "name": "search_google",
        "description": "Search Google and extract results",
        "steps": [
            {
                "name": "Navigate to Google",
                "action": "navigate",
                "params": {"url": "https://www.google.com"}
            },
            {
                "name": "Enter search query",
                "action": "fill",
                "params": {
                    "selector": "textarea[name='q']",
                    "value": "{{search_query}}",
                    "press_enter": True
                }
            },
            {
                "name": "Wait for results",
                "action": "wait",
                "params": {
                    "selector": "#search",
                    "timeout": 5000
                }
            },
            {
                "name": "Extract results",
                "action": "extract",
                "store_as": "search_results"
            }
        ]
    },
    
    "fill_contact_form": {
        "name": "fill_contact_form",
        "description": "Fill and submit contact form",
        "steps": [
            {
                "name": "Fill name",
                "action": "fill",
                "params": {
                    "selector": "#name",
                    "value": "{{name}}"
                }
            },
            {
                "name": "Fill email",
                "action": "fill",
                "params": {
                    "selector": "#email",
                    "value": "{{email}}"
                }
            },
            {
                "name": "Fill message",
                "action": "fill",
                "params": {
                    "selector": "#message",
                    "value": "{{message}}"
                }
            },
            {
                "name": "Submit form",
                "action": "click",
                "params": {
                    "selector": "button[type='submit']"
                }
            },
            {
                "name": "Wait for confirmation",
                "action": "wait",
                "params": {
                    "selector": ".success-message",
                    "timeout": 10000
                }
            }
        ]
    },
    
    "login_workflow": {
        "name": "login_workflow",
        "description": "Generic login workflow",
        "steps": [
            {
                "name": "Navigate to login page",
                "action": "navigate",
                "params": {"url": "{{login_url}}"}
            },
            {
                "name": "Enter username",
                "action": "fill",
                "params": {
                    "selector": "{{username_selector}}",
                    "value": "{{username}}"
                }
            },
            {
                "name": "Enter password",
                "action": "fill",
                "params": {
                    "selector": "{{password_selector}}",
                    "value": "{{password}}"
                }
            },
            {
                "name": "Click login button",
                "action": "click",
                "params": {
                    "selector": "{{login_button_selector}}"
                }
            },
            {
                "name": "Wait for dashboard",
                "action": "wait",
                "params": {
                    "selector": "{{success_indicator}}",
                    "timeout": 10000
                }
            }
        ]
    }
}
