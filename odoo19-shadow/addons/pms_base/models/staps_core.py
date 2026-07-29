import time
import hashlib
import logging
from functools import wraps

try:
    from odoo.http import request
except ImportError:
    request = None

_logger = logging.getLogger(__name__)

class STAPSCore:
    @staticmethod
    def get_staps_coordinate(function_name):
        """Generates a SHA-256 hash based on function name and nanosecond timestamp."""
        ts = time.time_ns()
        seed = f"{function_name}-{ts}"
        return hashlib.sha256(seed.encode()).hexdigest()

    @staticmethod
    def record_telemetry(env, action_name, duration_ms, coord):
        """Records telemetry to Odoo model if env is available."""
        if env and hasattr(env, 'cr') and env.cr:
            try:
                env['pms.telemetry'].sudo().create({
                    'action_name': action_name,
                    'duration_ms': duration_ms,
                    'staps_coordinate': coord,
                })
            except Exception as e:
                _logger.error(f"Failed to record STAPS telemetry: {e}")

def staps_timed(func):
    """Decorator for automated execution timing and O(1) telemetry broadcast."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        coord = STAPSCore.get_staps_coordinate(func.__name__)
        _logger.info(f"[STAPS 2.0] Starting {func.__name__} | Coord: {coord}")

        result = func(*args, **kwargs)

        duration = (time.perf_counter() - start) * 1000 # to ms
        _logger.info(f"[STAPS 2.0] Completed {func.__name__} | Coord: {coord} | Duration: {duration:.4f}ms")

        # Try to find env for telemetry recording
        env = None
        if args and hasattr(args[0], 'env'):
            env = args[0].env
        elif request and hasattr(request, 'env'):
            env = request.env

        STAPSCore.record_telemetry(env, func.__name__, duration, coord)

        return result
    return wrapper

class timed_process:
    """Context manager for high-precision timing of blocks."""
    def __init__(self, process_name, env=None):
        self.process_name = process_name
        self.env = env
        self.start = 0

    def __enter__(self):
        self.start = time.perf_counter()
        self.coord = STAPSCore.get_staps_coordinate(self.process_name)
        _logger.info(f"[STAPS-BLOCK] Enter: {self.process_name} | Coord: {self.coord}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = (time.perf_counter() - self.start) * 1000
        _logger.info(f"[STAPS-BLOCK] Exit: {self.process_name} | Coord: {self.coord} | Duration: {duration:.4f}ms")

        env = self.env
        if not env and request and hasattr(request, 'env'):
            env = request.env

        STAPSCore.record_telemetry(env, self.process_name, duration, self.coord)
