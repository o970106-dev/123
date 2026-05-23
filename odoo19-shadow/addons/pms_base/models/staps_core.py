import time
import hashlib
import functools
import logging
from odoo import http, fields, api

_logger = logging.getLogger(__name__)

class MetricTensorCryptoEngine:
    """
    STAPS 2.0 Metric Tensor Cryptography Engine.
    Implements a row-major 2x2 Hill cipher for O(1) ID obfuscation.
    Matrix: [[3, 2], [5, 7]], INV_MATRIX: [[53621, 59578], [17873, 41705]], Mod: 65536
    """
    MATRIX = [[3, 2], [5, 7]]
    INV_MATRIX = [[53621, 59578], [17873, 41705]]
    MOD = 65536

    @classmethod
    def encrypt(cls, numeric_id):
        """Obfuscate numeric ID into 8-char hex coordinate."""
        v1 = numeric_id & 0xFFFF
        v2 = (numeric_id >> 16) & 0xFFFF

        c1 = (v1 * cls.MATRIX[0][0] + v2 * cls.MATRIX[1][0]) % cls.MOD
        c2 = (v1 * cls.MATRIX[0][1] + v2 * cls.MATRIX[1][1]) % cls.MOD

        return f"{c1:04x}{c2:04x}"

    @classmethod
    def decrypt(cls, coord):
        """Reverse 8-char hex coordinate back to numeric ID."""
        try:
            c1 = int(coord[0:4], 16)
            c2 = int(coord[4:8], 16)

            v1 = (c1 * cls.INV_MATRIX[0][0] + c2 * cls.INV_MATRIX[1][0]) % cls.MOD
            v2 = (c1 * cls.INV_MATRIX[0][1] + c2 * cls.INV_MATRIX[1][1]) % cls.MOD

            return v1 | (v2 << 16)
        except Exception:
            return 0

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
