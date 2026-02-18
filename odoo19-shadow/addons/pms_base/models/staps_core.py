import time
import hashlib
import logging
from functools import wraps

_logger = logging.getLogger(__name__)

STAPS_MULTIPLIER = 8

class STAPSCore:
    @staticmethod
    def get_staps_coordinate(function_name):
        """Generates a SHA-256 hash based on function name and nanosecond timestamp."""
        ts = time.time_ns()
        seed = f"{function_name}-{ts}"
        return hashlib.sha256(seed.encode()).hexdigest()

def staps_timed(func):
    """Decorator for automated execution timing and telemetry broadcast."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        coord = STAPSCore.get_staps_coordinate(func.__name__)
        _logger.info(f"[STAPS] Starting {func.__name__} | Coord: {coord}")

        result = func(*args, **kwargs)

        duration = time.perf_counter() - start
        effective_speed = (duration * 1000) / STAPS_MULTIPLIER
        _logger.info(f"[STAPS] Completed {func.__name__} | Coord: {coord} | Duration: {duration*1000:.4f}ms | Effective: {effective_speed:.4f}ms")
        return result
    return wrapper

class timed_process:
    """Context manager for high-precision timing of blocks."""
    def __init__(self, process_name):
        self.process_name = process_name
        self.start = 0

    def __enter__(self):
        self.start = time.perf_counter()
        self.coord = STAPSCore.get_staps_coordinate(self.process_name)
        _logger.info(f"[STAPS-BLOCK] Enter: {self.process_name} | Coord: {self.coord}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.perf_counter() - self.start  # Fixed: correctly referencing self.start
        effective_speed = (duration * 1000) / STAPS_MULTIPLIER
        _logger.info(f"[STAPS-BLOCK] Exit: {self.process_name} | Coord: {self.coord} | Duration: {duration*1000:.4f}ms | Effective: {effective_speed:.4f}ms")
