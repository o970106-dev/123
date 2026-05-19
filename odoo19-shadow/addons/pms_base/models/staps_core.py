import time
import hashlib
import functools
import logging
from odoo import http, fields, api

_logger = logging.getLogger(__name__)

class MetricTensorCryptoEngine:
    """
    Metric Tensor Cryptography Engine using a 2x2 Hill cipher variant.
    Used for obfuscating numeric data for privacy during cloud transmission.
    """
    def __init__(self, key=None):
        # Default key matrix (Hill cipher 2x2) with coefficients 2-9
        self.matrix = key or [[3, 7], [5, 8]]

    def encrypt_pair(self, x, y):
        """Linear transformation using the metric tensor matrix."""
        c1 = self.matrix[0][0] * x + self.matrix[0][1] * y
        c2 = self.matrix[1][0] * x + self.matrix[1][1] * y
        return c1, c2

    def obfuscate_value(self, val):
        """Obfuscate a single numeric value."""
        return (val * self.matrix[0][0]) + (self.matrix[1][1] * 17)

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

                # Telemetry Payload
                telemetry_data = {
                    'name': func.__name__,
                    'duration': duration_ms,
                    'coordinate': coordinate,
                    'persist': persist,
                    'error': error
                }

                # Log the telemetry
                _logger.info(f"[STAPS] {coordinate} | {func.__name__} | {duration_ms:.4f}ms")

                # Persistent recording if requested and environment available
                if persist:
                    try:
                        # Attempt to find environment from args (self) or http request
                        env = None
                        if args and hasattr(args[0], 'env'):
                            env = args[0].env
                        elif hasattr(http, 'request') and http.request and hasattr(http.request, 'env'):
                            env = http.request.env

                        if env:
                            # Auto-capture resident_id from context
                            resident_id = False
                            if args and hasattr(args[0], '_name') and args[0]._name == 'res.users':
                                resident_id = args[0].id
                            elif hasattr(http, 'request') and http.request and http.request.env.user:
                                resident_id = http.request.env.user.id

                            # Use existing cursor for telemetry persistence to optimize connection usage
                            env['pms.telemetry'].sudo().create({
                                'name': telemetry_data['name'],
                                'duration': telemetry_data['duration'],
                                'error': telemetry_data['error'],
                                'coordinate': telemetry_data['coordinate'],
                                'resident_id': resident_id,
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
