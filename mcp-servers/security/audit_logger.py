"""
Audit Logger - Comprehensive security and action logging
Tracks all system activities for compliance, security, and debugging
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from enum import Enum

logger = logging.getLogger(__name__)


class AuditLevel(Enum):
    """Audit event severity levels"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"
    SECURITY = "security"


class AuditCategory(Enum):
    """Audit event categories"""
    AUTHENTICATION = "authentication"
    AUTHORIZATION = "authorization"
    DATA_ACCESS = "data_access"
    DATA_MODIFICATION = "data_modification"
    SYSTEM_CHANGE = "system_change"
    SECURITY_EVENT = "security_event"
    USER_ACTION = "user_action"
    API_CALL = "api_call"


class AuditLogger:
    """
    Comprehensive audit logging system

    Features:
    - Structured logging
    - Multiple output formats (JSON, plain text)
    - Event categorization
    - Compliance reporting
    - Security event tracking
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize audit logger

        Args:
            config: Audit logging configuration
        """
        self.config = config or {}

        # Logging configuration
        self.log_dir = Path(self.config.get('log_dir', '~/.claude-vision-hands/logs')).expanduser()
        self.log_dir.mkdir(parents=True, exist_ok=True)

        self.log_file = self.log_dir / 'audit.log'
        self.security_log = self.log_dir / 'security.log'
        self.json_log = self.log_dir / 'audit.jsonl'

        # Logging levels
        self.min_level = AuditLevel[self.config.get('min_level', 'INFO')]

        # Event storage
        self.events = []
        self.max_events_memory = self.config.get('max_events_memory', 1000)

        logger.info(f"Audit Logger initialized (log_dir={self.log_dir})")

    def log_event(
        self,
        message: str,
        level: AuditLevel = AuditLevel.INFO,
        category: AuditCategory = AuditCategory.USER_ACTION,
        user: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """
        Log an audit event

        Args:
            message: Event description
            level: Event severity level
            category: Event category
            user: User identifier
            metadata: Additional event data
        """
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'level': level.value,
            'category': category.value,
            'message': message,
            'user': user,
            'metadata': metadata or {}
        }

        # Store in memory
        self.events.append(event)
        if len(self.events) > self.max_events_memory:
            self.events.pop(0)

        # Write to appropriate logs
        self._write_to_file(event)

        if level == AuditLevel.SECURITY or level == AuditLevel.CRITICAL:
            self._write_to_security_log(event)

        # Write JSON log
        self._write_to_json_log(event)

        # Log to Python logger
        log_method = getattr(logger, level.value.lower(), logger.info)
        log_method(f"[{category.value}] {message}")

    def log_authentication(
        self,
        user: str,
        success: bool,
        method: str = "password",
        ip: Optional[str] = None
    ):
        """Log authentication attempt"""
        self.log_event(
            message=f"Authentication {'succeeded' if success else 'failed'} for user {user}",
            level=AuditLevel.SECURITY if not success else AuditLevel.INFO,
            category=AuditCategory.AUTHENTICATION,
            user=user,
            metadata={
                'success': success,
                'method': method,
                'ip': ip
            }
        )

    def log_authorization(
        self,
        user: str,
        resource: str,
        action: str,
        granted: bool
    ):
        """Log authorization check"""
        self.log_event(
            message=f"Authorization {'granted' if granted else 'denied'} for {user} to {action} {resource}",
            level=AuditLevel.WARNING if not granted else AuditLevel.INFO,
            category=AuditCategory.AUTHORIZATION,
            user=user,
            metadata={
                'resource': resource,
                'action': action,
                'granted': granted
            }
        )

    def log_data_access(
        self,
        user: str,
        resource: str,
        operation: str = "read"
    ):
        """Log data access"""
        self.log_event(
            message=f"User {user} accessed {resource} ({operation})",
            level=AuditLevel.INFO,
            category=AuditCategory.DATA_ACCESS,
            user=user,
            metadata={
                'resource': resource,
                'operation': operation
            }
        )

    def log_security_event(
        self,
        event_type: str,
        description: str,
        severity: AuditLevel = AuditLevel.WARNING,
        user: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """Log security-related event"""
        self.log_event(
            message=f"Security event: {event_type} - {description}",
            level=severity,
            category=AuditCategory.SECURITY_EVENT,
            user=user,
            metadata={
                'event_type': event_type,
                **(metadata or {})
            }
        )

    def log_api_call(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        user: Optional[str] = None,
        duration_ms: Optional[float] = None
    ):
        """Log API call"""
        self.log_event(
            message=f"API {method} {endpoint} - {status_code}",
            level=AuditLevel.INFO if status_code < 400 else AuditLevel.WARNING,
            category=AuditCategory.API_CALL,
            user=user,
            metadata={
                'endpoint': endpoint,
                'method': method,
                'status_code': status_code,
                'duration_ms': duration_ms
            }
        )

    def get_events(
        self,
        level: Optional[AuditLevel] = None,
        category: Optional[AuditCategory] = None,
        user: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Retrieve audit events with filters

        Args:
            level: Filter by level
            category: Filter by category
            user: Filter by user
            limit: Maximum events to return

        Returns:
            List of matching events
        """
        events = self.events

        if level:
            events = [e for e in events if e['level'] == level.value]
        if category:
            events = [e for e in events if e['category'] == category.value]
        if user:
            events = [e for e in events if e['user'] == user]

        return events[-limit:]

    def get_security_summary(self) -> Dict[str, Any]:
        """
        Get summary of security events

        Returns:
            Security statistics
        """
        security_events = [
            e for e in self.events
            if e['level'] in (AuditLevel.SECURITY.value, AuditLevel.CRITICAL.value)
        ]

        return {
            'total_security_events': len(security_events),
            'failed_authentications': sum(
                1 for e in security_events
                if e['category'] == AuditCategory.AUTHENTICATION.value
                and not e['metadata'].get('success', False)
            ),
            'denied_authorizations': sum(
                1 for e in security_events
                if e['category'] == AuditCategory.AUTHORIZATION.value
                and not e['metadata'].get('granted', False)
            ),
            'recent_events': security_events[-10:]
        }

    def _write_to_file(self, event: Dict):
        """Write event to main log file"""
        try:
            with open(self.log_file, 'a') as f:
                timestamp = event['timestamp']
                level = event['level'].upper()
                category = event['category']
                message = event['message']

                f.write(f"[{timestamp}] [{level:8}] [{category:20}] {message}\n")
        except Exception as e:
            logger.error(f"Failed to write to audit log: {e}")

    def _write_to_security_log(self, event: Dict):
        """Write security event to dedicated security log"""
        try:
            with open(self.security_log, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to security log: {e}")

    def _write_to_json_log(self, event: Dict):
        """Write event to JSON lines log"""
        try:
            with open(self.json_log, 'a') as f:
                f.write(json.dumps(event) + '\n')
        except Exception as e:
            logger.error(f"Failed to write to JSON log: {e}")

    def export_audit_trail(
        self,
        output_file: Path,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ):
        """
        Export audit trail for compliance

        Args:
            output_file: Output file path
            start_time: Filter start time
            end_time: Filter end time
        """
        events = self.events

        if start_time:
            events = [
                e for e in events
                if datetime.fromisoformat(e['timestamp']) >= start_time
            ]

        if end_time:
            events = [
                e for e in events
                if datetime.fromisoformat(e['timestamp']) <= end_time
            ]

        with open(output_file, 'w') as f:
            json.dump({
                'export_time': datetime.utcnow().isoformat(),
                'event_count': len(events),
                'events': events
            }, f, indent=2)

        logger.info(f"Exported {len(events)} audit events to {output_file}")
