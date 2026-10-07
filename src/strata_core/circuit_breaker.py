import time
from enum import Enum
from typing import Optional, Dict, Any

class CircuitState(str, Enum):
    CLOSED = "CLOSED"        # Normal state: calls are routed to Strata Core
    OPEN = "OPEN"            # Tripped state: calls immediately short-circuit to local fallback (0ms)
    HALF_OPEN = "HALF_OPEN"  # Probe state: testing if Strata Core has recovered

class StrataCircuitBreaker:
    """
    High-Resilience Circuit Breaker for Strata Core perception engine (:8001).
    Guarantees 0ms fallback execution when the external service is down or degraded,
    preventing UI freezes or downtime for hospital auditing personnel.
    """
    def __init__(
        self,
        failure_threshold: int = 3,
        recovery_timeout_sec: float = 10.0,
        request_timeout_sec: float = 2.0
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec
        self.request_timeout_sec = request_timeout_sec
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.fallback_served_count = 0
        self.last_failure_time: Optional[float] = None
        self.last_state_change_time = time.time()

    def can_attempt_external_call(self) -> bool:
        """
        Determines whether to attempt calling Strata Core at :8001.
        Returns False immediately (0ms) if the circuit is OPEN, preventing network hangs.
        """
        now = time.time()
        
        if self.state == CircuitState.OPEN:
            # Check if cooldown recovery period has elapsed
            if self.last_failure_time and (now - self.last_failure_time) >= self.recovery_timeout_sec:
                self.state = CircuitState.HALF_OPEN
                self.last_state_change_time = now
                return True
            return False

        return True

    def record_success(self):
        """Called when Strata Core responds successfully with HTTP 200."""
        self.success_count += 1
        self.failure_count = 0
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.last_state_change_time = time.time()

    def record_failure(self):
        """Called when Strata Core times out, connects refused, or errors."""
        now = time.time()
        self.failure_count += 1
        self.last_failure_time = now
        
        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            self.last_state_change_time = now

    def record_fallback(self):
        """Increments counter of requests seamlessly fulfilled by local perception engine."""
        self.fallback_served_count += 1

    def get_status(self) -> Dict[str, Any]:
        """Returns live observability metrics for the circuit breaker."""
        return {
            "state": self.state.value,
            "failure_count": self.failure_count,
            "failure_threshold": self.failure_threshold,
            "success_count": self.success_count,
            "fallback_served_count": self.fallback_served_count,
            "recovery_timeout_sec": self.recovery_timeout_sec,
            "request_timeout_sec": self.request_timeout_sec,
            "is_degraded": self.state != CircuitState.CLOSED
        }

circuit_breaker = StrataCircuitBreaker()
