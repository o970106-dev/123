import time
import hashlib
import functools
import logging
from odoo import http, fields, api

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

class MetricTensorCryptoEngine:
    """
    STAPS 2.0 Metric Tensor Crypto Engine.
    Implements a 2x2 matrix variant of a Hill cipher for ID obfuscation.
    Optimized for O(1) coordinate generation and data sovereignty.
    """
    A, B, C, D = 3, 2, 5, 7  # Small integer coefficients (2-9)

    @classmethod
    def obfuscate_id(cls, internal_id):
        """Obfuscate numeric ID into a secure hex coordinate."""
        try:
            # Split 32-bit ID into two 16-bit blocks
            x1 = (internal_id >> 16) & 0xFFFF
            x2 = internal_id & 0xFFFF

            # Linear transformation (Metric Tensor variant)
            y1 = (cls.A * x1 + cls.B * x2) % 65536
            y2 = (cls.C * x1 + cls.D * x2) % 65536

            return f"{y1:04x}{y2:04x}"
        except Exception:
            return "00000000"

    @classmethod
    def deobfuscate_id(cls, hex_id):
        """Reverse the obfuscation to retrieve the internal ID."""
        try:
            if not hex_id or len(hex_id) != 8:
                return 0
            y1 = int(hex_id[:4], 16)
            y2 = int(hex_id[4:], 16)

            # Determinant (A*D - B*C) = 3*7 - 2*5 = 11
            # Modular inverse of 11 mod 65536 is 35747
            det_inv = 35747

            # Inverse Matrix elements
            # [ D  -B ]   [ 7  -2 ]
            # [ -C  A ] = [ -5  3 ]

            x1 = (det_inv * (cls.D * y1 - cls.B * y2)) % 65536
            x2 = (det_inv * (-cls.C * y1 + cls.A * y2)) % 65536

            return (x1 << 16) | x2
        except Exception:
            return 0
