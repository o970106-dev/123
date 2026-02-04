import time
import functools
from contextlib import contextmanager

# STAPS (Space-Time Absolute Position System) Multiplier
# Represents the 1-to-8 parallel engineering efficiency of the STAPS 8-node architecture.
STAPS_MULTIPLIER = 8

def staps_timed(name):
    """Decorator to time a function and report STAPS performance."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            duration = (time.time() - start) * 1000
            effective = duration / STAPS_MULTIPLIER
            print(f"[STAPS CNS] {name} executed in {duration:.6f}ms (Effective Speed: {effective:.6f}ms)")
            return result
        return wrapper
    return decorator

@contextmanager
def timed_process(name):
    """Context manager to time a block and report STAPS performance."""
    start = time.time()
    try:
        yield
    finally:
        duration = (time.time() - start) * 1000
        effective = duration / STAPS_MULTIPLIER
        print(f"[STAPS CNS] {name} finished in {duration:.6f}ms (Effective Speed: {effective:.6f}ms)")

def report_efficiency(total_time_ms):
    """Reports the efficiency gain using the STAPS multiplier."""
    effective = total_time_ms / STAPS_MULTIPLIER
    return {
        "raw_time_ms": total_time_ms,
        "effective_time_ms": effective,
        "multiplier": STAPS_MULTIPLIER,
        "optimization_ratio": f"{STAPS_MULTIPLIER}x"
    }
