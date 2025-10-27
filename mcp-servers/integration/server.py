#!/usr/bin/env python3
"""
Integration MCP Server
Provides unified MCP tools for autonomous AI automation
"""

import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# MCP SDK imports (would be from actual MCP SDK)
# For now, we'll create a simple implementation

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MCPServer:
    """Simple MCP Server implementation"""

    def __init__(self):
        self.tools = {}
        self.orchestrator = None
        self.agent = None

    def tool(self):
        """Decorator for registering tools"""
        def decorator(func):
            self.tools[func.__name__] = func
            return func
        return decorator

    async def initialize(self):
        """Initialize server components"""
        from integration.orchestrator import AIOrchestrator
        from integration.autonomous_agent import AutonomousAgent

        self.orchestrator = AIOrchestrator()
        self.agent = AutonomousAgent()

        logger.info("Integration MCP Server initialized")


# Create server instance
server = MCPServer()


@server.tool()
async def start_recording(workflow_name: str, metadata: Optional[Dict] = None) -> dict:
    """
    Start recording user actions

    Args:
        workflow_name: Name for the workflow
        metadata: Optional metadata dictionary

    Returns:
        dict with session_id and status
    """
    try:
        if not server.orchestrator:
            await server.initialize()

        session_id = server.orchestrator.start_recording(
            workflow_name,
            metadata or {}
        )

        return {
            'success': True,
            'session_id': session_id,
            'workflow_name': workflow_name,
            'message': f'Recording started: {session_id}'
        }

    except Exception as e:
        logger.error(f"Error starting recording: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def stop_recording() -> dict:
    """
    Stop recording and save workflow

    Returns:
        dict with session_id and saved workflow path
    """
    try:
        if not server.orchestrator:
            return {
                'success': False,
                'error': 'No active recording session'
            }

        session_id = server.orchestrator.stop_recording()

        if not session_id:
            return {
                'success': False,
                'error': 'No active recording to stop'
            }

        return {
            'success': True,
            'session_id': session_id,
            'message': f'Recording stopped: {session_id}',
            'workflow_path': f'~/.claude-vision-hands/recordings/{session_id}.json'
        }

    except Exception as e:
        logger.error(f"Error stopping recording: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def replay_workflow(
    workflow_name: str,
    variables: Optional[Dict] = None
) -> dict:
    """
    Replay a recorded workflow

    Args:
        workflow_name: Name of workflow to replay
        variables: Optional variable substitutions

    Returns:
        dict with replay results
    """
    try:
        # Load workflow from storage
        from recorder.capture import WorkflowCapture

        recorder = WorkflowCapture()
        session = recorder.load_session(workflow_name)

        if not session:
            return {
                'success': False,
                'error': f'Workflow not found: {workflow_name}'
            }

        # Execute each action from the workflow
        results = []
        for action in session.actions:
            # Substitute variables if provided
            params = action.parameters.copy()
            if variables:
                for key, value in params.items():
                    if isinstance(value, str) and value.startswith('${'):
                        var_name = value[2:-1]  # Extract variable name
                        if var_name in variables:
                            params[key] = variables[var_name]

            # Execute action
            result = await server.orchestrator.execute_secure_action(
                action_type=action.action_type,
                tool_name=action.tool_name,
                parameters=params
            )

            results.append(result)

            # Stop if action failed
            if not result.get('success', False):
                break

        return {
            'success': True,
            'workflow_name': workflow_name,
            'actions_executed': len(results),
            'results': results
        }

    except Exception as e:
        logger.error(f"Error replaying workflow: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def security_scan(target: str, scan_type: str = 'comprehensive') -> dict:
    """
    Scan for security vulnerabilities

    Args:
        target: Target to scan (URL, command, input, etc.)
        scan_type: Type of scan (comprehensive, quick, specific)

    Returns:
        dict with scan results
    """
    try:
        from security.validator import SecurityValidator
        from security.prompt_guard import PromptGuard

        validator = SecurityValidator()
        guard = PromptGuard()

        results = {
            'target': target,
            'scan_type': scan_type,
            'vulnerabilities': [],
            'warnings': [],
            'passed': []
        }

        # Run different security checks based on scan type
        checks = []

        if scan_type in ('comprehensive', 'quick'):
            checks.extend([
                ('command', validator.validate_input(target, 'command')),
                ('path', validator.validate_input(target, 'path')),
                ('url', validator.validate_input(target, 'url')),
                ('sql', validator.validate_input(target, 'sql')),
                ('html', validator.validate_input(target, 'html')),
            ])

        if scan_type in ('comprehensive', 'prompt'):
            checks.append(('prompt_injection', guard.validate_prompt(target)))

        # Process check results
        for check_name, (is_valid, reason) in checks:
            if not is_valid:
                results['vulnerabilities'].append({
                    'type': check_name,
                    'reason': reason,
                    'severity': 'high' if 'injection' in reason.lower() else 'medium'
                })
            else:
                results['passed'].append(check_name)

        # Calculate risk score if comprehensive
        if scan_type == 'comprehensive':
            risk_score = guard.get_risk_score(target)
            results['risk_score'] = risk_score

            if risk_score > 0.7:
                results['overall_risk'] = 'high'
            elif risk_score > 0.4:
                results['overall_risk'] = 'medium'
            else:
                results['overall_risk'] = 'low'

        results['success'] = True
        results['vulnerabilities_found'] = len(results['vulnerabilities'])

        return results

    except Exception as e:
        logger.error(f"Error in security scan: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def validate_input(
    input_text: str,
    input_type: str = 'general'
) -> dict:
    """
    Validate user input for security

    Args:
        input_text: Input to validate
        input_type: Type of input (command, path, url, sql, html, general)

    Returns:
        dict with validation result
    """
    try:
        from security.validator import SecurityValidator

        validator = SecurityValidator()
        is_valid, reason = validator.validate_input(input_text, input_type)

        return {
            'success': True,
            'valid': is_valid,
            'input_type': input_type,
            'reason': reason if not is_valid else 'Input validated successfully',
            'sanitized': validator.sanitize_input(input_text, input_type) if not is_valid else input_text
        }

    except Exception as e:
        logger.error(f"Error validating input: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def autonomous_task(
    task_description: str,
    screenshot_path: Optional[str] = None,
    max_iterations: int = 10,
    confidence_threshold: float = 0.7
) -> dict:
    """
    Execute task autonomously using AI

    Args:
        task_description: Description of the task to accomplish
        screenshot_path: Optional path to initial screenshot
        max_iterations: Maximum iterations to attempt
        confidence_threshold: Minimum confidence to proceed

    Returns:
        dict with task execution results
    """
    try:
        if not server.agent:
            await server.initialize()

        # Update agent settings
        server.agent.confidence_threshold = confidence_threshold
        server.agent.max_retries = 3

        # Execute task autonomously
        if screenshot_path:
            result = await server.agent.analyze_and_act(
                screenshot_path=screenshot_path,
                goal=task_description
            )
        else:
            result = await server.agent.execute_goal_autonomously(
                goal=task_description,
                max_iterations=max_iterations
            )

        return {
            'success': True,
            'task': task_description,
            'result': result,
            'iterations': result.get('iterations', 1),
            'goal_achieved': result.get('success', False)
        }

    except Exception as e:
        logger.error(f"Error executing autonomous task: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def get_agent_status() -> dict:
    """
    Get status of the autonomous agent and orchestrator

    Returns:
        dict with detailed status information
    """
    try:
        if not server.agent:
            await server.initialize()

        agent_stats = server.agent.get_agent_stats()
        orchestrator_status = server.orchestrator.get_status()

        return {
            'success': True,
            'agent': agent_stats,
            'orchestrator': orchestrator_status,
            'recording': orchestrator_status['recording']
        }

    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {
            'success': False,
            'error': str(e)
        }


@server.tool()
async def search_memory(
    query: str,
    limit: int = 10,
    min_score: float = 0.5
) -> dict:
    """
    Search memory for past experiences

    Args:
        query: Search query
        limit: Maximum results to return
        min_score: Minimum similarity score

    Returns:
        dict with search results
    """
    try:
        result = await server.orchestrator.execute_secure_action(
            action_type='memory',
            tool_name='search',
            parameters={
                'query': query,
                'limit': limit,
                'min_score': min_score
            }
        )

        if result.get('success'):
            search_results = result.get('results', {})
            return {
                'success': True,
                'query': query,
                'total_count': getattr(search_results, 'total_count', 0),
                'results': getattr(search_results, 'results', [])[:limit]
            }
        else:
            return result

    except Exception as e:
        logger.error(f"Error searching memory: {e}")
        return {
            'success': False,
            'error': str(e)
        }


async def main():
    """Main server loop"""
    await server.initialize()

    print("=" * 70)
    print("  Integration MCP Server - Ready")
    print("=" * 70)
    print("\nAvailable Tools:")
    for tool_name in server.tools.keys():
        print(f"  - {tool_name}")
    print("\nServer is running... Press Ctrl+C to stop")

    # Keep server running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\nShutting down server...")


if __name__ == "__main__":
    asyncio.run(main())
