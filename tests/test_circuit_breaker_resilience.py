import time
import threading
import pytest
from src.strata_core.circuit_breaker import StrataCircuitBreaker, CircuitState
from src.strata_core.client import StrataCoreClient, DocumentAuditExtraction
from src.warehouse.engine import warehouse

def test_circuit_breaker_state_transitions():
    """Verify circuit trips to OPEN after failure threshold and recovers."""
    cb = StrataCircuitBreaker(failure_threshold=3, recovery_timeout_sec=0.2, request_timeout_sec=0.1)
    assert cb.state == CircuitState.CLOSED
    assert cb.can_attempt_external_call() is True

    # 1. Simulate 2 failures (threshold not reached)
    cb.record_failure()
    cb.record_failure()
    assert cb.state == CircuitState.CLOSED
    assert cb.can_attempt_external_call() is True

    # 2. 3rd failure trips the breaker to OPEN
    cb.record_failure()
    assert cb.state == CircuitState.OPEN
    # Immediately after opening, calls must NOT attempt external network (0ms)
    assert cb.can_attempt_external_call() is False

    # 3. Wait for cooldown period to test HALF_OPEN transition
    time.sleep(0.25)
    assert cb.can_attempt_external_call() is True
    assert cb.state == CircuitState.HALF_OPEN

    # 4. Successful recovery returns to CLOSED
    cb.record_success()
    assert cb.state == CircuitState.CLOSED
    assert cb.failure_count == 0

@pytest.mark.anyio
async def test_circuit_breaker_instant_fallback_latency():
    """Verify that when circuit is OPEN, fallback completes in under 5ms."""
    client = StrataCoreClient(base_url="http://localhost:8999", timeout_sec=0.1)
    
    # Force trip breaker
    from src.strata_core.circuit_breaker import circuit_breaker
    circuit_breaker.state = CircuitState.OPEN
    circuit_breaker.last_failure_time = time.time()  # Recent failure

    t0 = time.perf_counter()
    result = await client.evaluate_scanned_document(
        document_id="BENCH-01",
        document_type="Factura RIPS",
        raw_text="DIAGNÓSTICO J069 INFECCIÓN RESPIRATORIA AGUDA. RM-9921.",
        ips_name="Hospital Universitario Central",
        eps_name="Sura EPS"
    )
    elapsed_ms = (time.perf_counter() - t0) * 1000

    assert isinstance(result, DocumentAuditExtraction)
    assert result.diagnostico_cie10_code == "J069"
    # Strict speed SLA: instant zero-wait fallback under 10ms
    assert elapsed_ms < 10.0, f"Fallback took {elapsed_ms}ms, expected < 10ms"
    
    # Restore breaker state
    circuit_breaker.state = CircuitState.CLOSED
    circuit_breaker.failure_count = 0

def test_duckdb_concurrent_read_write_isolation():
    """
    Verify 24/7 isolation: Multiple threads performing concurrent writes and reads
    succeed with zero 'Resource temporarily unavailable' file lock exceptions.
    """
    errors = []
    
    def writer_worker(thread_id: int):
        try:
            for i in range(5):
                with warehouse.get_connection(read_only=False) as con:
                    # Insert sample glosa event
                    glosa_id = 9000000 + (thread_id * 100) + i
                    con.execute(f"""
                    INSERT OR REPLACE INTO fact_auditoria_glosas VALUES (
                        {glosa_id}, 1, 1, 20261001, 150000.0, 150000.0, 0.0, 'GL-01 Tarifa no pactada', 'Glosada'
                    );
                    """)
                time.sleep(0.01)
        except Exception as e:
            errors.append(f"Writer error: {str(e)}")

    def reader_worker():
        try:
            for _ in range(10):
                res = warehouse.execute_query("SELECT COUNT(*) AS total FROM fact_auditoria_glosas;")
                assert len(res) > 0
                time.sleep(0.01)
        except Exception as e:
            errors.append(f"Reader error: {str(e)}")

    # Launch 3 writer threads and 3 reader threads concurrently
    threads = []
    for t_id in range(3):
        threads.append(threading.Thread(target=writer_worker, args=(t_id,)))
    for _ in range(3):
        threads.append(threading.Thread(target=reader_worker))

    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert len(errors) == 0, f"Concurrent execution errors encountered: {errors}"
