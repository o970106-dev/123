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

def staps_timed(action_name, persist=True):
    """
    STAPS 2.0 High-Precision Telemetry Decorator.
    :param persist: If True, saves telemetry to database. Set False for high-frequency polling.
    """
    def decorator(func):
        def wrapper(self, *args, **kwargs):
            start = time.perf_counter()
            try:
                result = func(self, *args, **kwargs)
            finally:
                duration = (time.perf_counter() - start) * 1000  # ms
                coord = get_staps_coordinate(action_name)

                # Log to server logs (Ultra-fast)
                _logger.info(f"[STAPS] {action_name} | {duration:.6f}ms | {coord[:8]}")

                # Optional persistent telemetry
                if persist:
                    env = None
                    try:
                        env = getattr(self, 'env', None)
                        if not env and http.request:
                            env = getattr(http.request, 'env', None)
                    except Exception:
                        pass

                    if env:
                        try:
                            # Use a lighter check or batching if needed in real production
                            env['pms.telemetry'].sudo().create({
                                'name': action_name,
                                'duration': duration,
                                'staps_coordinate': coord,
                                'source_node': 'pms_base',
                            })
                        except Exception as e:
                            _logger.error(f"STAPS Telemetry Creation Failed: {e}")

            return result
        return wrapper
    return decorator
