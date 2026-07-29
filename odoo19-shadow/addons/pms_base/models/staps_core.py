import time
import hashlib
import functools
import logging
from odoo import http, fields

_logger = logging.getLogger(__name__)

def get_staps_coordinate(func_name):
    """Generate O(1) unique coordinate using SHA-256 and nanoseconds."""
    ts = time.time_ns()
    seed = f"{func_name}-{ts}"
    return hashlib.sha256(seed.encode()).hexdigest()[:16]

def staps_timed(persist=False):
    """
    STAPS 2.0 High-Precision Timing Decorator.
    Captures telemetry via finally blocks to ensure logging even on failure.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_ns = time.time_ns()
            coordinate = get_staps_coordinate(func.__name__)
            error = None
            try:
                return func(*args, **kwargs)
            except Exception as e:
                error = str(e)
                raise
            finally:
                end_ns = time.time_ns()
                duration_ms = (end_ns - start_ns) / 1_000_000.0

                # Resident Attribution Logic
                resident_id = None
                env = None
                try:
                    if args and hasattr(args[0], 'env'):
                        env = args[0].env
                    elif hasattr(http, 'request') and http.request and hasattr(http.request, 'env'):
                        env = http.request.env

                    if env:
                        # If the first argument is a user record, use it
                        if args and hasattr(args[0], '_name') and args[0]._name == 'res.users':
                            resident_id = args[0].id
                        else:
                            resident_id = env.user.id
                except:
                    pass

                # Telemetry Payload
                telemetry_data = {
                    'name': func.__name__,
                    'duration': duration_ms,
                    'coordinate': coordinate,
                    'persist': persist,
                    'error': error,
                    'resident_id': resident_id
                }

                # Log the telemetry
                _logger.info(f"[STAPS] {coordinate} | {func.__name__} | {duration_ms:.4f}ms | Res: {resident_id}")

                # Persistent recording if requested and environment available
                if persist:
                    try:
                        if env:
                            env['pms.telemetry'].sudo().create({
                                'name': telemetry_data['name'],
                                'duration': telemetry_data['duration'],
                                'error': telemetry_data['error'],
                                'coordinate': telemetry_data['coordinate'],
                                'resident_id': telemetry_data['resident_id'],
                                'timestamp': fields.Datetime.now(),
                            })
                    except Exception as record_error:
                        _logger.error(f"Failed to persist telemetry: {record_error}")
        return wrapper
    return decorator

class TimedProcess:
    """Context manager for STAPS timing block."""
    def __init__(self, name, persist=True):
        self.name = name
        self.persist = persist
        self.start = 0
        self.coordinate = ""

    def __enter__(self):
        self.start = time.time_ns()
        self.coordinate = get_staps_coordinate(self.name)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.time_ns() - self.start) / 1_000_000.0
        _logger.info(f"[STAPS Context] {self.coordinate} | {self.name} | {duration_ms:.4f}ms")
