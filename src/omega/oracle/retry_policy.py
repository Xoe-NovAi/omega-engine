"""tenacity retry policy for provider calls. M1-compliant (AnyIO-native)."""
import logging
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type, before_sleep_log

logger = logging.getLogger(__name__)

class TransientProviderError(Exception):
    """Retryable: timeout, 429, 5xx, network errors."""

class PermanentProviderError(Exception):
    """Non-retryable: 401, 403, bad request. Fail fast."""

# Default config — providers can override per call
DEFAULT_RETRY = dict(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=30),
    retry=retry_if_exception_type(TransientProviderError),
    reraise=True,
    before_sleep=before_sleep_log(logger, logging.WARNING),
)

async def call_with_retry(coro, **retry_kwargs):
    """Wrap an async provider call with tenacity retry logic."""
    cfg = {**DEFAULT_RETRY, **retry_kwargs}
    @retry(**cfg)
    async def _call():
        return await coro
    return await _call()
