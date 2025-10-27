"""
Prompt Guard - Protection Against Prompt Injection Attacks
Detects and prevents malicious prompt manipulation attempts
"""

import re
import logging
from typing import Dict, List, Tuple, Optional, Any

logger = logging.getLogger(__name__)


class PromptGuard:
    """
    Protects against prompt injection attacks

    Detects:
    - Direct instruction injection
    - Context boundary violations
    - Recursive injection
    - Jailbreak attempts
    - System prompt leakage
    """

    # Prompt injection patterns
    INJECTION_PATTERNS = [
        # Direct instruction attempts
        r"ignore\s+(previous|all|above)\s+instructions",
        r"disregard\s+(previous|all)\s+(instructions|commands)",
        r"forget\s+(everything|all|previous)",

        # Role manipulation
        r"you\s+are\s+now",
        r"act\s+as\s+(a|an)",
        r"pretend\s+(to\s+be|you)",
        r"role\s*:\s*system",
        r"new\s+instructions",

        # System prompt leakage
        r"show\s+(me\s+)?(your|the)\s+system\s+prompt",
        r"what\s+are\s+your\s+instructions",
        r"reveal\s+your\s+(instructions|prompt|rules)",

        # Jailbreak attempts
        r"DAN\s+mode",
        r"developer\s+mode",
        r"god\s+mode",
        r"jailbreak",
        r"unrestricted",

        # Context boundary violations
        r"</system>",
        r"<admin>",
        r"</instructions>",
        r"END_PROMPT",
    ]

    # Encoding/obfuscation patterns
    OBFUSCATION_PATTERNS = [
        r"base64",
        r"rot13",
        r"hex\s+encoded",
        r"unicode\s+escape",
    ]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize prompt guard

        Args:
            config: Security configuration
        """
        self.config = config or {}
        self.strict_mode = self.config.get('strict_mode', True)
        self.block_suspicious = self.config.get('block_suspicious', True)

        logger.info("Prompt Guard initialized")

    def validate_prompt(
        self,
        prompt: str,
        context: Optional[str] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate prompt for injection attempts

        Args:
            prompt: User prompt to validate
            context: Optional context for validation

        Returns:
            Tuple of (is_safe, reason_if_blocked)
        """
        if not prompt:
            return True, None

        # Check for direct injection patterns
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                logger.warning(f"Prompt injection detected: {pattern}")
                return False, f"Prompt injection detected: pattern '{pattern}'"

        # Check for obfuscation attempts
        if self.strict_mode:
            for pattern in self.OBFUSCATION_PATTERNS:
                if re.search(pattern, prompt, re.IGNORECASE):
                    logger.warning(f"Obfuscation detected: {pattern}")
                    return False, f"Suspicious obfuscation pattern: '{pattern}'"

        # Check for unusual character patterns
        if self._has_suspicious_patterns(prompt):
            if self.block_suspicious:
                return False, "Suspicious character patterns detected"

        return True, None

    def _has_suspicious_patterns(self, text: str) -> bool:
        """Check for suspicious character patterns"""
        # Excessive special characters
        special_char_ratio = sum(1 for c in text if not c.isalnum() and c != ' ') / max(len(text), 1)
        if special_char_ratio > 0.3:
            logger.warning(f"High special character ratio: {special_char_ratio:.2f}")
            return True

        # Repeated delimiters
        if re.search(r'([<>{}|\[\]])\1{3,}', text):
            logger.warning("Repeated delimiter pattern detected")
            return True

        # Excessive newlines
        if text.count('\n') > 20:
            logger.warning("Excessive newlines detected")
            return True

        return False

    def sanitize_prompt(self, prompt: str) -> str:
        """
        Sanitize prompt by removing dangerous patterns

        Args:
            prompt: Prompt to sanitize

        Returns:
            Sanitized prompt
        """
        sanitized = prompt

        # Remove system tags
        sanitized = re.sub(r'</?(system|admin|instructions)>', '', sanitized, flags=re.IGNORECASE)

        # Remove null bytes
        sanitized = sanitized.replace('\x00', '')

        # Normalize whitespace
        sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)

        return sanitized

    def get_risk_score(self, prompt: str) -> float:
        """
        Calculate risk score for prompt

        Args:
            prompt: Prompt to analyze

        Returns:
            Risk score (0.0 - 1.0)
        """
        score = 0.0

        # Check each pattern
        for pattern in self.INJECTION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += 0.2

        for pattern in self.OBFUSCATION_PATTERNS:
            if re.search(pattern, prompt, re.IGNORECASE):
                score += 0.1

        # Character pattern checks
        if self._has_suspicious_patterns(prompt):
            score += 0.3

        return min(score, 1.0)
