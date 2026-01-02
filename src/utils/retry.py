"""Retry utilities with exponential backoff."""

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)


def create_retry_decorator(
    max_attempts: int = 3,
    min_wait_seconds: int = 1,
    max_wait_seconds: int = 10,
    exceptions: tuple[type[Exception], ...] = (Exception,),
):
    """
    Create a retry decorator with exponential backoff.

    Args:
        max_attempts: Maximum number of retry attempts
        min_wait_seconds: Minimum wait time between retries
        max_wait_seconds: Maximum wait time between retries
        exceptions: Tuple of exceptions to retry on

    Returns:
        Configured retry decorator
    """
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(
            multiplier=1,
            min=min_wait_seconds,
            max=max_wait_seconds,
        ),
        retry=retry_if_exception_type(exceptions),
        reraise=True,
    )
