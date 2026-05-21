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
    Highest Degree Metric Tensor Crypto Engine.
    Implements a 2x2 Hill cipher to obfuscate internal IDs into coordinates.
    Matrix: [[3, 2], [5, 7]], Mod: 65536
    """
    MATRIX = [[3, 2], [5, 7]]
    INV_MATRIX = [[53621, 59578], [17873, 41705]]
    MOD = 65536

    @classmethod
    def encrypt(cls, numeric_id):
        """Encrypts a numeric ID into an 8-character hex coordinate."""
        # Split 32-bit ID into two 16-bit parts
        p1 = (numeric_id >> 16) & 0xFFFF
        p2 = numeric_id & 0xFFFF

        # Apply Matrix Transformation: V' = M * V mod 65536
        c1 = (cls.MATRIX[0][0] * p1 + cls.MATRIX[0][1] * p2) % cls.MOD
        c2 = (cls.MATRIX[1][0] * p1 + cls.MATRIX[1][1] * p2) % cls.MOD

        # Return as 8-character hex (4 chars per 16-bit block)
        return f"{c1:04x}{c2:04x}".upper()

    @classmethod
    def decrypt(cls, coordinate):
        """Decrypts an 8-character hex coordinate back to a numeric ID."""
        if not coordinate or len(coordinate) != 8:
            return None
        try:
            c1 = int(coordinate[:4], 16)
            c2 = int(coordinate[4:], 16)

            # Apply Inverse Matrix Transformation: V = M^-1 * V' mod 65536
            p1 = (cls.INV_MATRIX[0][0] * c1 + cls.INV_MATRIX[0][1] * c2) % cls.MOD
            p2 = (cls.INV_MATRIX[1][0] * c1 + cls.INV_MATRIX[1][1] * c2) % cls.MOD

            return (p1 << 16) | p2
        except (ValueError, TypeError):
            return None
