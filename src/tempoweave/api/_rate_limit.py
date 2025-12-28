from threading import Lock
import logging
import time

import httpx

logger = logging.getLogger(__name__)


class RetryRateLimitTransport(httpx.HTTPTransport):
    """A simple rate limiter."""

    RETRYABLE_EXCEPTIONS = (
        httpx.ReadError,
    )

    def __init__(self, requests_per_second: float = 1.0, **kwargs):
        super().__init__(**kwargs)
        self.delay = 1.0 / requests_per_second
        self.last_call = 0.0
        self.lock = Lock()
        self.retries = 3
        self.retry_backoff = 0.5

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        """Implement the rate limit."""
        for attempt in range(self.retries + 1):
            self._apply_rate_limit()

            try:
                return super().handle_request(request)

            except self.RETRYABLE_EXCEPTIONS as e:
                logger.warning(f"Exception trying {request.method} #{attempt + 1} {request.url}, retrying..")

                if attempt < self.retries:
                    time.sleep(self.retry_backoff * (2 ** attempt))
                    continue

                raise e

    def _apply_rate_limit(self) -> None:
        with self.lock:
            elapsed = time.time() - self.last_call

            if (wait := self.delay - elapsed) > 0:
                time.sleep(wait)

            self.last_call = time.time()