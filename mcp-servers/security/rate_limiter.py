"""
Rate Limiter - Prevents abuse through rate limiting
Protects against brute force, spam, and resource exhaustion
"""

import time
import logging
from typing import Dict, Optional, Tuple
from collections import defaultdict, deque
from threading import Lock

logger = logging.getLogger(__name__)


class RateLimiter:
    """
    Token bucket rate limiter with multiple strategies

    Supports:
    - Per-user rate limiting
    - Per-IP rate limiting
    - Per-action rate limiting
    - Burst handling
    - Sliding window
    """

    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize rate limiter

        Args:
            config: Rate limiting configuration
        """
        self.config = config or {}

        # Rate limit settings
        self.default_rate = self.config.get('default_rate', 60)  # requests per minute
        self.default_burst = self.config.get('default_burst', 10)  # burst size
        self.window_size = self.config.get('window_size', 60)  # seconds

        # Storage for rate limit data
        self.buckets = defaultdict(lambda: {
            'tokens': self.default_burst,
            'last_update': time.time(),
            'requests': deque()
        })

        # Thread safety
        self.lock = Lock()

        # Custom limits per action
        self.action_limits = self.config.get('action_limits', {
            'login': {'rate': 5, 'window': 300},  # 5 per 5 minutes
            'api_call': {'rate': 100, 'window': 60},  # 100 per minute
            'file_operation': {'rate': 50, 'window': 60},  # 50 per minute
        })

        logger.info("Rate Limiter initialized")

    def check_rate_limit(
        self,
        identifier: str,
        action: str = 'default'
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if request is allowed under rate limit

        Args:
            identifier: Unique identifier (user ID, IP, etc.)
            action: Action type for custom limits

        Returns:
            Tuple of (is_allowed, message)
        """
        with self.lock:
            # Get limits for this action
            limits = self.action_limits.get(action, {
                'rate': self.default_rate,
                'window': self.window_size
            })

            rate = limits['rate']
            window = limits['window']

            # Get or create bucket
            bucket_key = f"{identifier}:{action}"
            bucket = self.buckets[bucket_key]

            current_time = time.time()

            # Clean old requests outside window
            while bucket['requests'] and bucket['requests'][0] < current_time - window:
                bucket['requests'].popleft()

            # Check if under limit
            if len(bucket['requests']) < rate:
                bucket['requests'].append(current_time)
                return True, None
            else:
                # Calculate when next request will be allowed
                oldest_request = bucket['requests'][0]
                wait_time = window - (current_time - oldest_request)

                logger.warning(
                    f"Rate limit exceeded for {identifier} on {action}. "
                    f"Wait {wait_time:.1f}s"
                )

                return False, f"Rate limit exceeded. Try again in {wait_time:.1f} seconds"

    def consume_tokens(
        self,
        identifier: str,
        tokens: int = 1,
        action: str = 'default'
    ) -> Tuple[bool, Optional[str]]:
        """
        Token bucket algorithm implementation

        Args:
            identifier: Unique identifier
            tokens: Number of tokens to consume
            action: Action type

        Returns:
            Tuple of (success, message)
        """
        with self.lock:
            bucket_key = f"{identifier}:{action}"
            bucket = self.buckets[bucket_key]

            current_time = time.time()

            # Refill tokens based on time passed
            time_passed = current_time - bucket['last_update']
            refill_rate = self.default_rate / self.window_size  # tokens per second

            bucket['tokens'] = min(
                self.default_burst,
                bucket['tokens'] + time_passed * refill_rate
            )
            bucket['last_update'] = current_time

            # Try to consume tokens
            if bucket['tokens'] >= tokens:
                bucket['tokens'] -= tokens
                return True, None
            else:
                wait_time = (tokens - bucket['tokens']) / refill_rate
                return False, f"Insufficient tokens. Wait {wait_time:.1f} seconds"

    def reset_limit(self, identifier: str, action: str = 'default'):
        """
        Reset rate limit for identifier

        Args:
            identifier: Unique identifier
            action: Action type
        """
        bucket_key = f"{identifier}:{action}"
        with self.lock:
            if bucket_key in self.buckets:
                del self.buckets[bucket_key]
                logger.info(f"Reset rate limit for {identifier}:{action}")

    def get_remaining(
        self,
        identifier: str,
        action: str = 'default'
    ) -> Dict:
        """
        Get remaining rate limit info

        Args:
            identifier: Unique identifier
            action: Action type

        Returns:
            Dict with remaining requests and reset time
        """
        bucket_key = f"{identifier}:{action}"
        bucket = self.buckets[bucket_key]

        limits = self.action_limits.get(action, {
            'rate': self.default_rate,
            'window': self.window_size
        })

        current_time = time.time()

        # Clean old requests
        while bucket['requests'] and bucket['requests'][0] < current_time - limits['window']:
            bucket['requests'].popleft()

        remaining = limits['rate'] - len(bucket['requests'])

        reset_time = None
        if bucket['requests']:
            reset_time = bucket['requests'][0] + limits['window']

        return {
            'remaining': max(0, remaining),
            'limit': limits['rate'],
            'reset_time': reset_time,
            'window': limits['window']
        }

    def cleanup(self):
        """Clean up old bucket data"""
        with self.lock:
            current_time = time.time()
            expired = []

            for bucket_key, bucket in self.buckets.items():
                # Remove buckets with no recent activity
                if current_time - bucket['last_update'] > self.window_size * 2:
                    expired.append(bucket_key)

            for key in expired:
                del self.buckets[key]

            if expired:
                logger.info(f"Cleaned up {len(expired)} expired rate limit buckets")
