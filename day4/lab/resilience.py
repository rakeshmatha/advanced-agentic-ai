"""Offline resilience patterns for Day 4 (IN06).

Timeouts are implemented with daemon worker threads because Python cannot
forcibly cancel an arbitrary running thread. A timed-out operation may continue
in the background. Use this wrapper only for safe/idempotent demo operations;
production clients should use their native cancellation/timeout support.
"""

from __future__ import annotations

import queue
import random
import threading
import time
from contextvars import copy_context
from collections.abc import Callable
from enum import Enum
from typing import TypeVar

T = TypeVar("T")


class TransientServiceError(RuntimeError):
    """A simulated dependency error that is safe to retry."""


class CircuitOpenError(RuntimeError):
    """Raised when a circuit breaker is not accepting calls."""


class CircuitState(str, Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF-OPEN"


def call_with_timeout(operation: Callable[[], T], timeout_seconds: float) -> T:
    """Run an operation and raise ``TimeoutError`` when its budget expires."""
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be greater than zero")

    result_queue: queue.Queue[tuple[bool, object]] = queue.Queue(maxsize=1)
    worker_context = copy_context()

    def worker() -> None:
        try:
            result_queue.put((True, worker_context.run(operation)))
        except BaseException as error:  # propagate worker exceptions to caller
            result_queue.put((False, error))

    thread = threading.Thread(target=worker, name="day4-timeout-worker", daemon=True)
    thread.start()
    try:
        succeeded, value = result_queue.get(timeout=timeout_seconds)
    except queue.Empty as error:
        raise TimeoutError(f"operation exceeded {timeout_seconds:.3f}s budget") from error

    if succeeded:
        return value  # type: ignore[return-value]
    raise value  # type: ignore[misc]


def retry_call(
    operation: Callable[[], T],
    *,
    attempts: int = 3,
    base_delay_seconds: float = 0.05,
    max_delay_seconds: float = 1.0,
    retryable: tuple[type[Exception], ...] = (TransientServiceError, TimeoutError),
    sleeper: Callable[[float], None] = time.sleep,
    random_value: Callable[[], float] = random.random,
    jitter_ratio: float = 0.0,
) -> T:
    """Retry a transient operation with capped exponential backoff and jitter.

    Set ``jitter_ratio=0`` for deterministic tests. Do not retry non-idempotent
    actions without an idempotency key: a timed-out request may still complete.
    """
    if attempts < 1:
        raise ValueError("attempts must be at least one")
    if base_delay_seconds < 0 or max_delay_seconds < 0:
        raise ValueError("backoff delays cannot be negative")
    if jitter_ratio < 0:
        raise ValueError("jitter_ratio cannot be negative")

    for attempt in range(attempts):
        try:
            return operation()
        except retryable:
            if attempt + 1 == attempts:
                raise
            delay = min(max_delay_seconds, base_delay_seconds * (2**attempt))
            if jitter_ratio:
                delay = min(max_delay_seconds, delay * (1 + jitter_ratio * random_value()))
            sleeper(delay)
    raise AssertionError("retry loop ended unexpectedly")


class CircuitBreaker:
    """Thread-safe CLOSED/OPEN/HALF-OPEN breaker for a single dependency."""

    def __init__(
        self,
        *,
        failure_threshold: int = 3,
        recovery_timeout_seconds: float = 10.0,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        if failure_threshold < 1:
            raise ValueError("failure_threshold must be at least one")
        if recovery_timeout_seconds < 0:
            raise ValueError("recovery_timeout_seconds cannot be negative")
        self.failure_threshold = failure_threshold
        self.recovery_timeout_seconds = recovery_timeout_seconds
        self._clock = clock
        self._state = CircuitState.CLOSED
        self._consecutive_failures = 0
        self._opened_at: float | None = None
        self._probe_in_flight = False
        self._lock = threading.RLock()

    @property
    def state(self) -> CircuitState:
        with self._lock:
            if (
                self._state is CircuitState.OPEN
                and self._opened_at is not None
                and self._clock() - self._opened_at >= self.recovery_timeout_seconds
            ):
                self._state = CircuitState.HALF_OPEN
            return self._state

    def call(self, operation: Callable[[], T]) -> T:
        with self._lock:
            current_state = self.state
            if current_state is CircuitState.OPEN:
                raise CircuitOpenError("dependency circuit is open")
            if current_state is CircuitState.HALF_OPEN:
                if self._probe_in_flight:
                    raise CircuitOpenError("half-open recovery probe is already running")
                self._probe_in_flight = True

        try:
            result = operation()
        except Exception:
            with self._lock:
                self._consecutive_failures += 1
                self._probe_in_flight = False
                if (
                    current_state is CircuitState.HALF_OPEN
                    or self._consecutive_failures >= self.failure_threshold
                ):
                    self._state = CircuitState.OPEN
                    self._opened_at = self._clock()
            raise

        with self._lock:
            self._consecutive_failures = 0
            self._probe_in_flight = False
            self._state = CircuitState.CLOSED
            self._opened_at = None
        return result


def validate_sku(sku: str, allowed_skus: set[str] | frozenset[str]) -> str:
    """Validate an extracted SKU against trusted application data."""
    normalized = sku.strip().upper()
    if not normalized or normalized not in allowed_skus:
        raise ValueError(f"SKU is not in the trusted catalog: {normalized!r}")
    return normalized


def demo_inventory_lookup(
    sku: str,
    *,
    allowed_skus: set[str] | frozenset[str] = frozenset({"SKU-100", "SKU-200"}),
    lookup: Callable[[str], int] | None = None,
    timeout_seconds: float = 0.2,
) -> dict[str, object]:
    """Validate, time-bound, and safely retry a read-only demo inventory call."""
    validated_sku = validate_sku(sku, allowed_skus)
    lookup_fn = lookup or (lambda item: {"SKU-100": 12, "SKU-200": 0}[item])
    try:
        stock = retry_call(
            lambda: call_with_timeout(lambda: lookup_fn(validated_sku), timeout_seconds),
            attempts=2,
            base_delay_seconds=0.01,
            max_delay_seconds=0.02,
        )
    except (TransientServiceError, TimeoutError):
        return {"sku": validated_sku, "available": None, "source": "safe_fallback"}
    return {"sku": validated_sku, "available": stock, "source": "live_demo"}
