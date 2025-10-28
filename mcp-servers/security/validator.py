"""
Security Validator - Input Sanitization and Validation
Protects against injection attacks, malicious commands, and unsafe operations
"""

import re
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from urllib.parse import urlparse
import html

logger = logging.getLogger(__name__)


class SecurityValidator:
    """
    Comprehensive security validation for all user inputs and system operations

    Protects against:
    - Command injection
    - Path traversal
    - SQL injection
    - XSS attacks
    - Malicious file operations
    - Unsafe URL access
    """

    # Dangerous command patterns
    DANGEROUS_COMMANDS = [
        r'\b(rm|del|format|mkfs|dd)\b.*-[rf]',  # Destructive file operations
        r'\b(sudo|su|doas)\b',  # Privilege escalation
        r'[:,;|&`$]',  # Command chaining
        r'\$\(',  # Command substitution
        r'eval\s*\(',  # Code evaluation
        r'exec\s*\(',  # Code execution
        r'__import__',  # Dynamic imports
        r'compile\s*\(',  # Code compilation
        r'>\s*/dev/',  # Device file access
        r'/proc/',  # Process file system
        r'/sys/',  # System file system
        r'/etc/(passwd|shadow|sudoers)',  # Sensitive system files
        r'\bcat\b.*(/etc/|/var/log/)',  # Reading sensitive files
    ]

    # SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|#|/\*|\*/)",  # SQL comments
        r"('\s*(OR|AND)\s*'?\d)",  # OR/AND injection
        r"(UNION\s+SELECT)",  # UNION injection
        r"(;|\|\||&&)",  # Statement terminators
    ]

    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",  # Event handlers
        r"<iframe",
        r"<object",
        r"<embed",
        r"eval\s*\(",
    ]

    # Path traversal patterns
    PATH_TRAVERSAL_PATTERNS = [
        r"\.\./",  # Parent directory
        r"\.\.",  # Double dot
        r"~",  # Home directory
        r"/etc/",  # System config
        r"/var/",  # System var
        r"/root/",  # Root home
        r"C:\\",  # Windows root
    ]

    # Allowed URL schemes
    ALLOWED_URL_SCHEMES = {'http', 'https', 'file'}

    # Blocked file extensions
    DANGEROUS_EXTENSIONS = {
        '.exe', '.dll', '.so', '.dylib',  # Executables
        '.sh', '.bat', '.cmd', '.ps1',  # Scripts
        '.vbs', '.js', '.jar',  # More scripts
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize security validator

        Args:
            config: Security configuration dict
        """
        self.config = config or {}
        self.strict_mode = self.config.get('strict_mode', True)
        self.allow_file_operations = self.config.get('allow_file_operations', False)
        self.allowed_domains = set(self.config.get('allowed_domains', []))
        self.blocked_domains = set(self.config.get('blocked_domains', []))

        logger.info(f"Security Validator initialized (strict_mode={self.strict_mode})")

    def validate_input(
        self,
        input_text: str,
        input_type: str = "general"
    ) -> Tuple[bool, str]:
        """
        Validate user input against various attack vectors

        Args:
            input_text: Input to validate
            input_type: Type of input (general, command, path, url, sql)

        Returns:
            Tuple of (is_valid, reason)
        """
        if not input_text:
            return True, "Empty input"

        # Check based on input type
        validators = {
            'command': self._validate_command,
            'path': self._validate_path,
            'url': self._validate_url,
            'sql': self._validate_sql,
            'html': self._validate_html,
            'general': self._validate_general,
        }

        validator = validators.get(input_type, self._validate_general)
        return validator(input_text)

    def _validate_command(self, command: str) -> Tuple[bool, str]:
        """Validate command for dangerous patterns"""
        # Check for dangerous command patterns
        for pattern in self.DANGEROUS_COMMANDS:
            if re.search(pattern, command, re.IGNORECASE):
                logger.warning(f"Dangerous command blocked: {command[:100]}")
                return False, f"Dangerous command pattern detected: {pattern}"

        # Check for shell metacharacters
        dangerous_chars = ['|', '&', ';', '$', '`', '\n', '<', '>']
        for char in dangerous_chars:
            if char in command:
                logger.warning(f"Shell metacharacter '{char}' in command: {command[:100]}")
                return False, f"Shell metacharacter '{char}' not allowed"

        return True, "Command validated"

    def _validate_path(self, path: str) -> Tuple[bool, str]:
        """Validate file path for traversal attacks"""
        # Check for path traversal patterns
        for pattern in self.PATH_TRAVERSAL_PATTERNS:
            if re.search(pattern, path):
                logger.warning(f"Path traversal attempt blocked: {path}")
                return False, f"Path traversal pattern detected: {pattern}"

        # Check for dangerous extensions
        path_obj = Path(path)
        if path_obj.suffix.lower() in self.DANGEROUS_EXTENSIONS:
            logger.warning(f"Dangerous file extension: {path}")
            return False, f"File extension {path_obj.suffix} not allowed"

        # Resolve path and check if it's within allowed directories
        try:
            resolved = Path(path).resolve()

            # In strict mode, only allow paths within project directory
            if self.strict_mode:
                project_root = Path.cwd().resolve()
                if not str(resolved).startswith(str(project_root)):
                    logger.warning(f"Path outside project root: {path}")
                    return False, "Path must be within project directory"

        except Exception as e:
            logger.error(f"Path validation error: {e}")
            return False, f"Invalid path: {str(e)}"

        return True, "Path validated"

    def _validate_url(self, url: str) -> Tuple[bool, str]:
        """Validate URL for malicious content"""
        try:
            parsed = urlparse(url)

            # Check scheme
            if parsed.scheme not in self.ALLOWED_URL_SCHEMES:
                logger.warning(f"Invalid URL scheme: {parsed.scheme}")
                return False, f"URL scheme '{parsed.scheme}' not allowed"

            # Check for blocked domains
            if parsed.netloc in self.blocked_domains:
                logger.warning(f"Blocked domain: {parsed.netloc}")
                return False, f"Domain '{parsed.netloc}' is blocked"

            # If allowed domains specified, enforce whitelist
            if self.allowed_domains and parsed.netloc not in self.allowed_domains:
                logger.warning(f"Domain not in whitelist: {parsed.netloc}")
                return False, f"Domain '{parsed.netloc}' not in allowed list"

            # Check for javascript: or data: URLs
            if parsed.scheme in ('javascript', 'data'):
                logger.warning(f"Dangerous URL scheme: {parsed.scheme}")
                return False, "javascript: and data: URLs not allowed"

        except Exception as e:
            logger.error(f"URL validation error: {e}")
            return False, f"Invalid URL: {str(e)}"

        return True, "URL validated"

    def _validate_sql(self, query: str) -> Tuple[bool, str]:
        """Validate SQL for injection attempts"""
        for pattern in self.SQL_INJECTION_PATTERNS:
            if re.search(pattern, query, re.IGNORECASE):
                logger.warning(f"SQL injection attempt blocked: {query[:100]}")
                return False, f"SQL injection pattern detected: {pattern}"

        return True, "SQL validated"

    def _validate_html(self, html_content: str) -> Tuple[bool, str]:
        """Validate HTML for XSS attacks"""
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, html_content, re.IGNORECASE):
                logger.warning(f"XSS attempt blocked: {html_content[:100]}")
                return False, f"XSS pattern detected: {pattern}"

        return True, "HTML validated"

    def _validate_general(self, text: str) -> Tuple[bool, str]:
        """General validation for unknown input types"""
        # Run all validations in non-strict mode
        checks = [
            self._validate_command(text),
            self._validate_sql(text),
            self._validate_html(text),
        ]

        for is_valid, reason in checks:
            if not is_valid:
                return is_valid, reason

        return True, "Input validated"

    def sanitize_input(
        self,
        input_text: str,
        input_type: str = "general"
    ) -> str:
        """
        Sanitize input by removing dangerous content

        Args:
            input_text: Input to sanitize
            input_type: Type of input

        Returns:
            Sanitized input
        """
        if not input_text:
            return input_text

        sanitized = input_text

        # HTML escape
        if input_type in ('html', 'general'):
            sanitized = html.escape(sanitized)

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        # Remove control characters (except newline and tab)
        sanitized = ''.join(char for char in sanitized
                           if char >= ' ' or char in '\n\t')

        # Normalize whitespace
        sanitized = ' '.join(sanitized.split())

        return sanitized

    def validate_action(
        self,
        action: str,
        params: Dict[str, Any]
    ) -> Tuple[bool, str]:
        """
        Validate an action with its parameters

        Args:
            action: Action name
            params: Action parameters

        Returns:
            Tuple of (is_valid, reason)
        """
        logger.info(f"Validating action: {action}")

        # Validate action name
        if not re.match(r'^[a-zA-Z0-9_]+$', action):
            return False, "Invalid action name format"

        # Validate each parameter
        for key, value in params.items():
            if not isinstance(value, (str, int, float, bool, list, dict, type(None))):
                return False, f"Invalid parameter type for {key}"

            # Validate string parameters
            if isinstance(value, str):
                # Auto-detect type
                if key in ('command', 'cmd', 'exec'):
                    is_valid, reason = self._validate_command(value)
                elif key in ('path', 'file', 'directory'):
                    is_valid, reason = self._validate_path(value)
                elif key in ('url', 'link', 'href'):
                    is_valid, reason = self._validate_url(value)
                else:
                    is_valid, reason = self._validate_general(value)

                if not is_valid:
                    return False, f"Parameter '{key}' validation failed: {reason}"

        return True, "Action validated"

    def is_safe_file_operation(
        self,
        operation: str,
        path: str
    ) -> Tuple[bool, str]:
        """
        Check if file operation is safe

        Args:
            operation: Type of operation (read, write, delete, execute)
            path: File path

        Returns:
            Tuple of (is_safe, reason)
        """
        # Check if file operations are allowed
        if not self.allow_file_operations:
            return False, "File operations are disabled"

        # Validate path
        is_valid, reason = self._validate_path(path)
        if not is_valid:
            return False, reason

        # Additional checks for dangerous operations
        if operation in ('delete', 'execute'):
            logger.warning(f"Dangerous file operation requested: {operation} on {path}")
            if self.strict_mode:
                return False, f"Operation '{operation}' not allowed in strict mode"

        return True, "File operation is safe"

    def get_security_report(self) -> Dict[str, Any]:
        """
        Get security configuration report

        Returns:
            Security status dict
        """
        return {
            'strict_mode': self.strict_mode,
            'file_operations_allowed': self.allow_file_operations,
            'allowed_domains_count': len(self.allowed_domains),
            'blocked_domains_count': len(self.blocked_domains),
            'validation_rules': {
                'command_patterns': len(self.DANGEROUS_COMMANDS),
                'sql_patterns': len(self.SQL_INJECTION_PATTERNS),
                'xss_patterns': len(self.XSS_PATTERNS),
                'path_patterns': len(self.PATH_TRAVERSAL_PATTERNS),
            }
        }
