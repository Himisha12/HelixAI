import pytest
from app.config import settings
from app.core.exceptions import RateLimitExceededException
from app.services.rate_limiter import AIRateLimiter


def test_rate_limiter_rpm_exceeded():
    limiter = AIRateLimiter()
    user_id = "test_rate_user"

    # Fill up to max RPM
    for _ in range(settings.RATE_LIMIT_REQUESTS_PER_MINUTE):
        limiter.check_rate_limit(user_id, estimated_tokens=10)
        limiter.record_usage(user_id, actual_tokens=10)

    # Next attempt should raise RateLimitExceededException
    with pytest.raises(RateLimitExceededException):
        limiter.check_rate_limit(user_id, estimated_tokens=10)


def test_rate_limiter_tpm_exceeded():
    limiter = AIRateLimiter()
    user_id = "test_tpm_user"

    # Single request exceeding token limit
    with pytest.raises(RateLimitExceededException):
        limiter.check_rate_limit(user_id, estimated_tokens=settings.RATE_LIMIT_TOKENS_PER_MINUTE + 100)
