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

class MetricTensorCryptoEngine:
    """
    STAPS 2.0 Metric Tensor Cryptography.
    Uses a 2x2 matrix Hill cipher variant to obfuscate internal IDs.
    Matrix: [[3, 2], [5, 7]], Modulo: 65536
    """
    MATRIX = [[3, 2], [5, 7]]
    INV_MATRIX = [[53621, 59578], [17873, 41705]]  # Modular inverse components
    MOD = 65536

    @classmethod
    def encrypt(cls, internal_id):
        """Encrypts a numeric ID into an 8-character hex coordinate."""
        if not isinstance(internal_id, int):
            try:
                internal_id = int(internal_id)
            except:
                return "00000000"

        # Split 32-bit ID into two 16-bit blocks
        x1 = (internal_id >> 16) & 0xFFFF
        x2 = internal_id & 0xFFFF

        # Matrix multiplication (Row-major)
        y1 = (cls.MATRIX[0][0] * x1 + cls.MATRIX[0][1] * x2) % cls.MOD
        y2 = (cls.MATRIX[1][0] * x1 + cls.MATRIX[1][1] * x2) % cls.MOD

        # Combine and hexify
        encrypted_val = (y1 << 16) | y2
        return f"{encrypted_val:08x}"

    @classmethod
    def decrypt(cls, coord):
        """Decrypts an 8-character hex coordinate back to a numeric ID."""
        try:
            encrypted_val = int(coord, 16)
        except:
            return 0

        y1 = (encrypted_val >> 16) & 0xFFFF
        y2 = encrypted_val & 0xFFFF

        # Inverse matrix multiplication (Row-major)
        x1 = (cls.INV_MATRIX[0][0] * y1 + cls.INV_MATRIX[0][1] * y2) % cls.MOD
        x2 = (cls.INV_MATRIX[1][0] * y1 + cls.INV_MATRIX[1][1] * y2) % cls.MOD

        return (x1 << 16) | x2

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
