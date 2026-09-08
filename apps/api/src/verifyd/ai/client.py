import os
import re
import time
import random
import asyncio
from typing import Any, Dict, Optional, Tuple, Type, TypeVar
import httpx
from pydantic import BaseModel
from verifyd.config import get_settings
from verifyd.core.errors import ProviderError, TransientAIError
from verifyd.core.logging import get_logger

logger = get_logger("ai.client")
settings = get_settings()

T = TypeVar("T", bound=BaseModel)

# Approximate Pricing Constants (USD per 1M tokens / minute)
COST_TABLE = {
    "gemini-2.0-flash": {"prompt_1m": 0.10, "completion_1m": 0.40},
    "whisper-large-v3": {"per_minute": 0.006},
}


class CircuitBreaker:
    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: float = 60.0):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.failure_count = 0
        self.last_failure_time = 0.0
        self.is_open = False

    def record_success(self):
        self.failure_count = 0
        self.is_open = False

    def record_failure(self):
        self.failure_count += 1
        self.last_failure_time = time.time()
        if self.failure_count >= self.failure_threshold:
            self.is_open = True
            logger.warning("AI circuit breaker opened", failure_count=self.failure_count)

    def can_execute(self) -> bool:
        if not self.is_open:
            return True
        if time.time() - self.last_failure_time > self.recovery_timeout_sec:
            logger.info("AI circuit breaker attempting half-open recovery")
            return True
        return False


_circuit_breakers: Dict[str, CircuitBreaker] = {}


def get_circuit_breaker(provider: str) -> CircuitBreaker:
    if provider not in _circuit_breakers:
        _circuit_breakers[provider] = CircuitBreaker()
    return _circuit_breakers[provider]


def load_prompt_template(filename: str) -> Tuple[str, str]:
    """Reads prompt file from ai/prompts/ and returns (prompt_text, prompt_version)"""
    prompt_path = os.path.join(os.path.dirname(__file__), "prompts", filename)
    if not os.path.exists(prompt_path):
        raise FileNotFoundError(f"Prompt template {filename} not found at {prompt_path}")

    with open(prompt_path, "r", encoding="utf-8") as f:
        content = f.read()

    # Extract version header
    version_match = re.search(r"<!--\s*prompt_version:\s*(v[0-9.]+)\s*-->", content)
    version = version_match.group(1) if version_match else "v1.0.0"
    return content, version


async def execute_ai_call_with_retry(
    provider: str,
    call_fn,
    max_retries: int = 3,
    initial_delay: float = 1.0,
) -> Any:
    cb = get_circuit_breaker(provider)
    if not cb.can_execute():
        raise ProviderError(f"AI Circuit breaker is active for provider '{provider}'. Requests temporarily blocked.")

    attempt = 0
    start_time = time.time()

    while attempt < max_retries:
        attempt += 1
        try:
            result = await call_fn()
            cb.record_success()
            return result
        except (httpx.TimeoutException, httpx.NetworkError) as e:
            logger.warning("AI network/timeout error", provider=provider, attempt=attempt, error=str(e))
            if attempt >= max_retries:
                cb.record_failure()
                raise TransientAIError(f"AI Provider {provider} timed out after {max_retries} attempts.")
            # Exponential backoff with jitter
            delay = (initial_delay * (2 ** (attempt - 1))) + random.uniform(0.1, 0.5)
            await asyncio.sleep(delay)
        except httpx.HTTPStatusError as e:
            status_code = e.response.status_code
            logger.warning("AI HTTP error", provider=provider, status_code=status_code, attempt=attempt)
            if status_code in (429, 500, 502, 503, 504):
                if attempt >= max_retries:
                    cb.record_failure()
                    raise TransientAIError(f"AI Provider {provider} returned status {status_code}.")
                delay = (initial_delay * (2 ** (attempt - 1))) + random.uniform(0.2, 0.8)
                await asyncio.sleep(delay)
            else:
                cb.record_failure()
                raise ProviderError(f"AI Provider {provider} rejected request with code {status_code}: {e.response.text}")
        except Exception as e:
            if isinstance(e, (TransientAIError, ProviderError)):
                raise e
            cb.record_failure()
            logger.error("AI unexpected error", provider=provider, error=str(e))
            raise ProviderError(f"AI execution error for {provider}: {str(e)}")
