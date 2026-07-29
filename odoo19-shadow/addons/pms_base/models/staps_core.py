import time
import hashlib
import logging
from odoo import models, fields, api, http

_logger = logging.getLogger(__name__)

def get_staps_coordinate(action_name):
    """Generate O(1) space-time coordinate using SHA-256."""
    ts = time.time_ns()
    raw = f"{action_name}-{ts}"
    return hashlib.sha256(raw.encode()).hexdigest()

def staps_timed(action_name):
    """STAPS 2.0 High-Precision Telemetry Decorator."""
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start = time.perf_counter()
            result = func(self, *args, **kwargs)
            duration = (time.perf_counter() - start) * 1000  # ms

            coord = get_staps_coordinate(action_name)

            # Persistent telemetry if env is available
            env = getattr(self, 'env', None) or getattr(http.request, 'env', None)
            if env:
                try:
                    env['pms.telemetry'].sudo().create({
                        'name': action_name,
                        'duration': duration,
                        'staps_coordinate': coord,
                        'source_node': 'pms_base',
                    })
                except Exception as e:
                    _logger.error(f"STAPS Telemetry Failed: {e}")

            _logger.info(f"[STAPS] {action_name} | {duration:.6f}ms | {coord[:8]}")
            return result
        return wrapper
    return decorator
