from odoo import models, fields, api
import time
import functools
import hashlib
import logging

_logger = logging.getLogger(__name__)

def staps_timed(persist=False):
    """
    Decorator for high-precision STAPS timing.
    Captures telemetry and optionally persists to the database.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            coord = get_staps_coordinate(func.__name__)

            # Identify the environment
            env = None
            if args and hasattr(args[0], 'env'):
                env = args[0].env
            else:
                try:
                    from odoo.http import request
                    env = request.env
                except (ImportError, RuntimeError):
                    pass

            try:
                result = func(*args, **kwargs)
                status = 'SUCCESS'
                return result
            except Exception as e:
                status = 'ERROR'
                _logger.error("STAPS Execution Error in %s: %s", func.__name__, str(e))
                raise
            finally:
                end_time = time.perf_counter()
                duration = (end_time - start_time) * 1000  # ms

                _logger.info("[STAPS 2.0 CNS Broadcast] Action: %s | Coord: %s | Duration: %.4f ms",
                             func.__name__, coord[:16], duration)

                if persist and env:
                    try:
                        env['pms.telemetry'].sudo().create({
                            'name': func.__name__,
                            'duration': duration,
                            'staps_coordinate': coord,
                            'status': status,
                            'timestamp': fields.Datetime.now(),
                        })
                    except Exception as telemetry_error:
                        _logger.warning("Failed to persist STAPS telemetry: %s", str(telemetry_error))

        return wrapper
    return decorator

def get_staps_coordinate(input_str):
    """
    Returns the SHA-256 absolute coordinate for a given input,
    representing the O(1) Space-Time Absolute Position.
    """
    ts = str(time.time_ns())
    combined = f"{input_str}-{ts}"
    return hashlib.sha256(combined.encode()).hexdigest()

class PmsTelemetry(models.Model):
    _name = 'pms.telemetry'
    _description = 'PMS High-Precision Telemetry'
    _order = 'timestamp desc'

    name = fields.Char(string='Action Name', required=True)
    duration = fields.Float(string='Duration (ms)', digits=(16, 4))
    staps_coordinate = fields.Char(string='STAPS Coordinate', size=64)
    status = fields.Selection([('SUCCESS', 'Success'), ('ERROR', 'Error')], string='Status')
    timestamp = fields.Datetime(string='Timestamp', default=fields.Datetime.now)
    source_node = fields.Char(string='Source Node', default='CNS-Main')
