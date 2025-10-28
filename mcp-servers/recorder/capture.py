"""
Workflow Capture - Record user actions and system interactions
Hooks into all MCP tools to capture complete workflows
"""

import time
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict, field

logger = logging.getLogger(__name__)


@dataclass
class CapturedAction:
    """Represents a single captured action"""
    timestamp: float
    action_type: str  # 'vision', 'browser', 'hands', 'memory', 'security'
    tool_name: str
    parameters: Dict[str, Any]
    result: Optional[Dict[str, Any]] = None
    screenshot_path: Optional[str] = None
    duration_ms: Optional[float] = None
    success: bool = True
    error: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)


@dataclass
class RecordingSession:
    """Represents a recording session"""
    session_id: str
    name: str
    started_at: float = field(default_factory=time.time)
    ended_at: Optional[float] = None
    actions: List[CapturedAction] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.actions is None:
            self.actions = []
        if self.metadata is None:
            self.metadata = {}


class WorkflowCapture:
    """
    Captures user actions and system interactions

    Features:
    - Hook into all MCP tool calls
    - Record action parameters and results
    - Capture screenshots at each step
    - Track timing and performance
    - Store for later replay
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize workflow capture

        Args:
            config: Capture configuration
        """
        self.config = config or {}

        # Recording state
        self.is_recording = False
        self.current_session: Optional[RecordingSession] = None

        # Storage configuration (support both storage_dir and storage_path)
        storage_path = self.config.get('storage_dir') or self.config.get('storage_path', '~/.claude-vision-hands/recordings')
        self.storage_dir = Path(storage_path).expanduser()
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Screenshot configuration
        self.capture_screenshots = self.config.get('capture_screenshots', True)
        self.screenshot_dir = self.storage_dir / 'screenshots'
        self.screenshot_dir.mkdir(exist_ok=True)

        # Performance tracking
        self.action_start_times: Dict[str, float] = {}

        logger.info(f"Workflow Capture initialized (storage: {self.storage_dir})")

    def start_recording(self, name: str, metadata: Optional[Dict] = None) -> str:
        """
        Start a new recording session

        Args:
            name: Session name
            metadata: Optional metadata

        Returns:
            Session ID
        """
        if self.is_recording:
            logger.warning("Already recording, stopping previous session")
            self.stop_recording()

        session_id = f"session_{int(time.time())}_{name.replace(' ', '_')}"

        self.current_session = RecordingSession(
            session_id=session_id,
            name=name,
            started_at=time.time(),
            metadata=metadata or {}
        )

        self.is_recording = True

        logger.info(f"Started recording session: {session_id}")
        return session_id

    def stop_recording(self) -> Optional[str]:
        """
        Stop current recording session

        Returns:
            Session ID of stopped session
        """
        if not self.is_recording or not self.current_session:
            logger.warning("No active recording session")
            return None

        self.current_session.ended_at = time.time()
        self.is_recording = False

        # Save session
        session_file = self._save_session(self.current_session)

        session_id = self.current_session.session_id
        logger.info(f"Stopped recording session: {session_id} ({len(self.current_session.actions)} actions)")

        self.current_session = None
        return session_id

    def capture_action(
        self,
        action_type: str,
        tool_name: str,
        parameters: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error: Optional[str] = None
    ) -> Optional[str]:
        """
        Capture a single action

        Args:
            action_type: Type of action (vision, browser, hands, etc.)
            tool_name: Name of the tool being called
            parameters: Action parameters
            result: Action result
            success: Whether action succeeded
            error: Error message if failed

        Returns:
            Action ID
        """
        if not self.is_recording or not self.current_session:
            return None

        # Calculate duration if we tracked start time
        action_key = f"{action_type}:{tool_name}"
        duration_ms = None
        if action_key in self.action_start_times:
            duration_ms = (time.time() - self.action_start_times[action_key]) * 1000
            del self.action_start_times[action_key]

        # Capture screenshot if enabled
        screenshot_path = None
        if self.capture_screenshots and action_type in ('vision', 'browser', 'hands'):
            screenshot_path = self._capture_screenshot(action_type, tool_name)

        # Create action
        action = CapturedAction(
            timestamp=time.time(),
            action_type=action_type,
            tool_name=tool_name,
            parameters=parameters.copy(),
            result=result.copy() if result else None,
            screenshot_path=screenshot_path,
            duration_ms=duration_ms,
            success=success,
            error=error
        )

        # Add to session
        self.current_session.actions.append(action)

        action_id = f"action_{len(self.current_session.actions)}"
        logger.debug(f"Captured action: {action_type}.{tool_name}")

        return action_id

    def mark_action_start(self, action_type: str, tool_name: str):
        """
        Mark the start of an action for timing

        Args:
            action_type: Type of action
            tool_name: Name of tool
        """
        action_key = f"{action_type}:{tool_name}"
        self.action_start_times[action_key] = time.time()

    def _capture_screenshot(self, action_type: str, tool_name: str) -> Optional[str]:
        """
        Capture screenshot for action

        Args:
            action_type: Type of action
            tool_name: Tool name

        Returns:
            Path to screenshot
        """
        try:
            timestamp = int(time.time() * 1000)
            filename = f"{self.current_session.session_id}_{action_type}_{tool_name}_{timestamp}.png"
            screenshot_path = self.screenshot_dir / filename

            # Try to capture screenshot (implementation depends on available tools)
            # For now, we'll just return the path where it should be saved
            # The actual capture would be done by vision or browser tools

            return str(screenshot_path)
        except Exception as e:
            logger.error(f"Failed to capture screenshot: {e}")
            return None

    def _save_session(self, session: RecordingSession) -> Path:
        """
        Save session to disk

        Args:
            session: Session to save

        Returns:
            Path to saved session file
        """
        session_file = self.storage_dir / f"{session.session_id}.json"

        session_data = {
            'session_id': session.session_id,
            'name': session.name,
            'started_at': session.started_at,
            'ended_at': session.ended_at,
            'duration_seconds': (session.ended_at - session.started_at) if session.ended_at else None,
            'action_count': len(session.actions),
            'metadata': session.metadata,
            'actions': [action.to_dict() for action in session.actions]
        }

        with open(session_file, 'w') as f:
            json.dump(session_data, f, indent=2)

        logger.info(f"Saved recording session to {session_file}")
        return session_file

    def load_session(self, session_id: str) -> Optional[RecordingSession]:
        """
        Load a saved session

        Args:
            session_id: Session ID to load

        Returns:
            Loaded session or None
        """
        session_file = self.storage_dir / f"{session_id}.json"

        if not session_file.exists():
            logger.error(f"Session file not found: {session_file}")
            return None

        try:
            with open(session_file, 'r') as f:
                session_data = json.load(f)

            # Reconstruct session
            actions = [
                CapturedAction(**action_dict)
                for action_dict in session_data.get('actions', [])
            ]

            session = RecordingSession(
                session_id=session_data['session_id'],
                name=session_data['name'],
                started_at=session_data['started_at'],
                ended_at=session_data.get('ended_at'),
                actions=actions,
                metadata=session_data.get('metadata', {})
            )

            logger.info(f"Loaded session: {session_id} ({len(actions)} actions)")
            return session

        except Exception as e:
            logger.error(f"Failed to load session {session_id}: {e}")
            return None

    def list_sessions(self) -> List[Dict[str, Any]]:
        """
        List all saved sessions

        Returns:
            List of session summaries
        """
        sessions = []

        for session_file in self.storage_dir.glob("session_*.json"):
            try:
                with open(session_file, 'r') as f:
                    session_data = json.load(f)

                sessions.append({
                    'session_id': session_data['session_id'],
                    'name': session_data['name'],
                    'started_at': session_data['started_at'],
                    'duration_seconds': session_data.get('duration_seconds'),
                    'action_count': session_data.get('action_count', 0),
                    'file_path': str(session_file)
                })
            except Exception as e:
                logger.error(f"Failed to read session {session_file}: {e}")

        # Sort by timestamp (newest first)
        sessions.sort(key=lambda s: s['started_at'], reverse=True)

        return sessions

    def get_session_stats(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get statistics for a session

        Args:
            session_id: Session ID

        Returns:
            Session statistics
        """
        session = self.load_session(session_id)
        if not session:
            return None

        # Calculate statistics
        action_types = {}
        tools_used = {}
        total_duration = 0
        success_count = 0
        error_count = 0

        for action in session.actions:
            # Count by type
            action_types[action.action_type] = action_types.get(action.action_type, 0) + 1

            # Count by tool
            tools_used[action.tool_name] = tools_used.get(action.tool_name, 0) + 1

            # Duration
            if action.duration_ms:
                total_duration += action.duration_ms

            # Success/error
            if action.success:
                success_count += 1
            else:
                error_count += 1

        return {
            'session_id': session.session_id,
            'name': session.name,
            'total_actions': len(session.actions),
            'action_types': action_types,
            'tools_used': tools_used,
            'total_duration_ms': total_duration,
            'average_duration_ms': total_duration / len(session.actions) if session.actions else 0,
            'success_count': success_count,
            'error_count': error_count,
            'success_rate': success_count / len(session.actions) if session.actions else 0
        }
