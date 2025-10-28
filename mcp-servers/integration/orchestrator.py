"""
AI Orchestrator - Central coordination for all automation components
Connects Vision AI, Memory, Security, Browser Control, and Workflow Recording
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """
    Central orchestrator that coordinates all automation components

    Features:
    - Unified API for all tools
    - Automatic security validation
    - Memory integration
    - Workflow recording
    - Error handling and recovery
    - Performance tracking
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize AI Orchestrator

        Args:
            config: Orchestrator configuration
        """
        self.config = config or {}

        # Initialize components (lazy loading)
        self._vision = None
        self._memory = None
        self._security = None
        self._recorder = None
        self._browser = None  # To be implemented

        # State
        self.is_recording = False
        self.current_session_id = None

        logger.info("AI Orchestrator initialized")

    @property
    def vision(self):
        """Lazy load vision analyzer"""
        if self._vision is None:
            try:
                import sys
                import signal
                from pathlib import Path

                # Timeout handler for slow initialization
                def timeout_handler(signum, frame):
                    raise TimeoutError("Vision analyzer initialization timed out")

                # Add vision-mcp to path
                vision_path = Path(__file__).parent.parent / 'vision-mcp'
                if str(vision_path) not in sys.path:
                    sys.path.insert(0, str(vision_path))

                # Set 5 second timeout for initialization (PaddleOCR can be slow)
                signal.signal(signal.SIGALRM, timeout_handler)
                signal.alarm(5)

                try:
                    from analyzers.gemini_analyzer import GeminiVisionAnalyzer
                    self._vision = GeminiVisionAnalyzer()
                    logger.info("Vision AI loaded")
                finally:
                    signal.alarm(0)  # Cancel alarm

            except Exception as e:
                logger.error(f"Failed to load Vision AI: {e}")
        return self._vision

    @property
    def memory(self):
        """Lazy load memory manager"""
        if self._memory is None:
            try:
                from memory.manager import MemoryManager
                self._memory = MemoryManager()
                logger.info("Memory Manager loaded")
            except Exception as e:
                logger.error(f"Failed to load Memory Manager: {e}")
        return self._memory

    @property
    def security(self):
        """Lazy load security validator"""
        if self._security is None:
            try:
                from security.validator import SecurityValidator
                self._security = SecurityValidator()
                logger.info("Security Validator loaded")
            except Exception as e:
                logger.error(f"Failed to load Security Validator: {e}")
        return self._security

    @property
    def recorder(self):
        """Lazy load workflow recorder"""
        if self._recorder is None:
            try:
                from recorder.capture import WorkflowCapture
                self._recorder = WorkflowCapture()
                logger.info("Workflow Recorder loaded")
            except Exception as e:
                logger.error(f"Failed to load Workflow Recorder: {e}")
        return self._recorder

    @property
    def recording(self):
        """Alias for is_recording (for backwards compatibility with tests)"""
        return self.is_recording

    @property
    def validator(self):
        """Alias for security (for backwards compatibility with tests)"""
        return self.security

    async def execute_secure_action(
        self,
        action_type: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute an action with security validation, memory storage, and recording

        Args:
            action_type: Type of action (vision, browser, hands, memory)
            tool_name: Specific tool to use
            parameters: Action parameters

        Returns:
            Action result with metadata
        """
        try:
            # 1. Security Validation
            if self.security:
                is_valid, reason = await self._validate_action(action_type, tool_name, parameters)
                if not is_valid:
                    logger.warning(f"Action blocked by security: {reason}")
                    return {
                        'success': False,
                        'error': f'Security validation failed: {reason}',
                        'blocked': True
                    }

            # 2. Mark recording start if recording
            if self.recorder and self.is_recording:
                self.recorder.mark_action_start(action_type, tool_name)

            # 3. Execute action
            result = await self._execute_action(action_type, tool_name, parameters)

            # 4. Record action if recording
            if self.recorder and self.is_recording:
                self.recorder.capture_action(
                    action_type=action_type,
                    tool_name=tool_name,
                    parameters=parameters,
                    result=result,
                    success=result.get('success', True),
                    error=result.get('error')
                )

            # 5. Store in memory if successful
            if self.memory and result.get('success', True):
                self._store_in_memory(action_type, tool_name, parameters, result)

            return result

        except Exception as e:
            logger.error(f"Error executing action {action_type}.{tool_name}: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _validate_action(
        self,
        action_type: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate action with security layer

        Args:
            action_type: Action type
            tool_name: Tool name
            parameters: Parameters

        Returns:
            Tuple of (is_valid, reason)
        """
        try:
            # Validate each parameter
            for param_name, param_value in parameters.items():
                if isinstance(param_value, str):
                    # Determine input type based on parameter name
                    input_type = self._detect_input_type(param_name)

                    is_valid, reason = self.security.validate_input(param_value, input_type)
                    if not is_valid:
                        return False, f"Parameter '{param_name}' validation failed: {reason}"

            return True, None

        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False, str(e)

    def _detect_input_type(self, param_name: str) -> str:
        """Detect input type from parameter name"""
        param_lower = param_name.lower()

        if 'url' in param_lower or 'link' in param_lower:
            return 'url'
        elif 'path' in param_lower or 'file' in param_lower:
            return 'path'
        elif 'command' in param_lower or 'cmd' in param_lower:
            return 'command'
        elif 'query' in param_lower or 'sql' in param_lower:
            return 'sql'
        elif 'html' in param_lower or 'content' in param_lower:
            return 'html'
        else:
            return 'general'

    async def _execute_action(
        self,
        action_type: str,
        tool_name: str,
        parameters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute the actual action

        Args:
            action_type: Action type
            tool_name: Tool name
            parameters: Parameters

        Returns:
            Action result
        """
        try:
            if action_type == 'vision':
                return await self._execute_vision_action(tool_name, parameters)
            elif action_type == 'memory':
                return await self._execute_memory_action(tool_name, parameters)
            elif action_type == 'browser':
                return await self._execute_browser_action(tool_name, parameters)
            elif action_type == 'hands':
                return await self._execute_hands_action(tool_name, parameters)
            else:
                return {
                    'success': False,
                    'error': f'Unknown action type: {action_type}'
                }

        except Exception as e:
            logger.error(f"Action execution error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    async def _execute_vision_action(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute vision action"""
        if not self.vision:
            return {'success': False, 'error': 'Vision AI not available'}

        if tool_name == 'analyze_screen':
            result = self.vision.analyze_screen(
                screenshot_path=parameters.get('screenshot_path'),
                prompt=parameters.get('prompt')
            )
            return {'success': True, 'result': result}

        return {'success': False, 'error': f'Unknown vision tool: {tool_name}'}

    async def _execute_memory_action(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute memory action"""
        if not self.memory:
            return {'success': False, 'error': 'Memory system not available'}

        if tool_name == 'search':
            results = self.memory.search_memories(
                query=parameters.get('query'),
                limit=parameters.get('limit', 10)
            )
            return {'success': True, 'results': results}

        elif tool_name == 'store_screen':
            mem_id = self.memory.store_screen_memory(
                content=parameters.get('content'),
                ai_provider=parameters.get('ai_provider', 'gemini'),
                ai_analysis=parameters.get('ai_analysis')
            )
            return {'success': True, 'memory_id': mem_id}

        return {'success': False, 'error': f'Unknown memory tool: {tool_name}'}

    async def _execute_browser_action(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute browser action (placeholder)"""
        # TODO: Implement when browser control is ready
        return {'success': False, 'error': 'Browser control not yet implemented'}

    async def _execute_hands_action(self, tool_name: str, parameters: Dict) -> Dict:
        """Execute hands/desktop control action (placeholder)"""
        # TODO: Implement when hands control is ready
        return {'success': False, 'error': 'Desktop control not yet implemented'}

    def _store_in_memory(
        self,
        action_type: str,
        tool_name: str,
        parameters: Dict,
        result: Dict
    ):
        """Store successful action in memory"""
        if not self.memory:
            return

        try:
            self.memory.store_action_memory(
                content=f"{action_type}.{tool_name}: {parameters}",
                action_type=tool_name,
                success=result.get('success', True),
                mcp_server=action_type
            )
        except Exception as e:
            logger.error(f"Failed to store action in memory: {e}")

    def start_recording(self, session_name: str, metadata: Optional[Dict] = None) -> str:
        """
        Start recording workflow

        Args:
            session_name: Name for the recording session
            metadata: Optional metadata

        Returns:
            Session ID
        """
        if not self.recorder:
            raise RuntimeError("Workflow recorder not available")

        session_id = self.recorder.start_recording(session_name, metadata)
        self.is_recording = True
        self.current_session_id = session_id

        logger.info(f"Started recording: {session_id}")
        return session_id

    def stop_recording(self) -> Optional[str]:
        """
        Stop recording workflow

        Returns:
            Session ID
        """
        if not self.recorder or not self.is_recording:
            logger.warning("No active recording")
            return None

        session_id = self.recorder.stop_recording()
        self.is_recording = False
        self.current_session_id = None

        logger.info(f"Stopped recording: {session_id}")
        return session_id

    def get_status(self) -> Dict[str, Any]:
        """
        Get orchestrator status

        Returns:
            Status information
        """
        return {
            'components': {
                'vision': self._vision is not None,
                'memory': self._memory is not None,
                'security': self._security is not None,
                'recorder': self._recorder is not None,
                'browser': self._browser is not None
            },
            'recording': {
                'is_recording': self.is_recording,
                'session_id': self.current_session_id
            },
            # Backwards compatibility with tests
            'memory_initialized': self._memory is not None,
            'vision_initialized': self._vision is not None
        }
