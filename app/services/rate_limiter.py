import time
from collections import defaultdict
from typing import Dict, List, Tuple
from app.config import settings
from app.core.exceptions import RateLimitExceededException


class AIRateLimiter:
    """
    AI-Specific Usage and Rate Controller implementing a sliding-window tracker
    for both Requests-per-Minute (RPM) and Tokens-per-Minute (TPM).
    """

    def __init__(self) -> None:
        # Stores (timestamp, token_count) tuples for each user
        self._request_history: Dict[str, List[Tuple[float, int]]] = defaultdict(list)

    def _clean_old_records(self, user_id: str, current_time: float) -> None:
        """Remove timestamps older than 60 seconds (sliding 1-minute window)."""
        window_start = current_time - 60.0
        self._request_history[user_id] = [
            (ts, tokens)
            for ts, tokens in self._request_history[user_id]
            if ts > window_start
        ]

    def check_rate_limit(self, user_id: str, estimated_tokens: int = 100) -> None:
        """
        Check if the user has exceeded Request-per-Minute or Token-per-Minute limits.
        Raises RateLimitExceededException if limit reached.
        """
        current_time = time.time()
        self._clean_old_records(user_id, current_time)

        history = self._request_history[user_id]
        current_rpm = len(history)
        current_tpm = sum(tokens for _, tokens in history)

        max_rpm = settings.RATE_LIMIT_REQUESTS_PER_MINUTE
        max_tpm = settings.RATE_LIMIT_TOKENS_PER_MINUTE

        if current_rpm >= max_rpm:
            raise RateLimitExceededException(
                detail=f"RPM limit reached ({current_rpm}/{max_rpm} req/min). Please slow down."
            )

        if current_tpm + estimated_tokens > max_tpm:
            raise RateLimitExceededException(
                detail=f"TPM quota exceeded ({current_tpm}/{max_tpm} tokens/min)."
            )

    def record_usage(self, user_id: str, actual_tokens: int) -> None:
        """Record an executed request with actual consumed tokens into sliding window."""
        current_time = time.time()
        self._request_history[user_id].append((current_time, actual_tokens))

    def get_usage_metrics(self, user_id: str) -> Dict[str, int]:
        """Get current window usage stats for UI dashboard."""
        current_time = time.time()
        self._clean_old_records(user_id, current_time)
        history = self._request_history[user_id]
        return {
            "current_rpm": len(history),
            "max_rpm": settings.RATE_LIMIT_REQUESTS_PER_MINUTE,
            "current_tpm": sum(tokens for _, tokens in history),
            "max_tpm": settings.RATE_LIMIT_TOKENS_PER_MINUTE,
        }


# Global rate limiter instance
rate_limiter = AIRateLimiter()
