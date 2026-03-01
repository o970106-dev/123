import time
import functools
import hashlib
import logging

_logger = logging.getLogger(__name__)

def staps_timed(func):
    """
    Decorator for high-precision STAPS 2.0 timing.
    Reports authentic real-time performance and logs to telemetry.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        result = func(*args, **kwargs)
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000  # ms
        coord = get_staps_coordinate(func.__name__)

        _logger.info("[STAPS 2.0 CNS] Action: %s | Duration: %.4f ms | Coord: %s",
                     func.__name__, duration, coord[:16])

        # Try to log to Odoo pms.telemetry model if env is available
        try:
            if args and hasattr(args[0], 'env'):
                self_obj = args[0]
                # Avoid infinite recursion if we are timing the telemetry creation itself
                if func.__name__ not in ['create', 'write'] or self_obj._name != 'pms.telemetry':
                    self_obj.env['pms.telemetry'].sudo().create({
                        'name': func.__name__,
                        'duration': duration,
                        'coordinate': coord,
                        'node_info': self_obj._name if hasattr(self_obj, '_name') else 'unknown'
                    })
        except Exception as e:
            _logger.debug("Telemetry logging failed: %s", e)

        return result
    return wrapper

def get_staps_coordinate(input_str):
    """
    Returns the SHA-256 absolute coordinate for a given input,
    representing the O(1) Space-Time Absolute Position.
    """
    ts = str(time.time_ns())
    combined = f"{input_str}-{ts}"
    return hashlib.sha256(combined.encode()).hexdigest()
