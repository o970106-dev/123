import time
import hashlib
import logging
import os
from functools import wraps

_logger = logging.getLogger(__name__)

# STAPS 2.0: Space-Time Absolute Position System
# The 'Double J' framework utilizes this for O(1) log indexing.

class STAPSCore:
    @staticmethod
    def get_staps_coordinate(function_name, node_id=None):
        """
        Generates a SHA-256 hash based on function name, nanosecond timestamp, and node ID.
        STAPS Coordinate = Hash(node_id + function_name + ns_timestamp)
        """
        ts = time.time_ns()
        node = node_id or os.getenv('PMS_NODE_ID', 'MASTER')
        seed = f"{node}-{function_name}-{ts}"
        return hashlib.sha256(seed.encode()).hexdigest()

    @staticmethod
    def record_telemetry(node_id, operation, coordinate, duration):
        """Records telemetry data into the PMS system."""
        # Attempt to record to Odoo if in request context
        try:
            from odoo.http import request
            if request and request.env:
                request.env['pms.telemetry'].sudo().create({
                    'node_id': node_id,
                    'operation': operation,
                    'coordinate': coordinate,
                    'duration': duration,
                })
        except Exception:
            # Fallback to logger if Odoo env is not available
            _logger.debug(f"Telemetry record failed for {operation}, fallback to log.")

def staps_timed(func):
    """Decorator for automated execution timing and telemetry broadcast with Node context."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        node = os.getenv('PMS_NODE_ID', 'MASTER')
        coord = STAPSCore.get_staps_coordinate(func.__name__, node)

        _logger.info(f"[STAPS][{node}] Starting {func.__name__} | Coord: {coord}")

        result = func(*args, **kwargs)

        duration_ms = (time.perf_counter() - start) * 1000

        _logger.info(f"[STAPS][{node}] Completed {func.__name__} | Coord: {coord} | Duration: {duration_ms:.4f}ms")

        STAPSCore.record_telemetry(node, func.__name__, coord, duration_ms)

        return result
    return wrapper

class timed_process:
    """Context manager for high-precision timing of blocks in the STAPS 2.0 framework."""
    def __init__(self, process_name, node_id=None):
        self.process_name = process_name
        self.node_id = node_id or os.getenv('PMS_NODE_ID', 'MASTER')
        self.start = 0

    def __enter__(self):
        self.start = time.perf_counter()
        self.coord = STAPSCore.get_staps_coordinate(self.process_name, self.node_id)
        _logger.info(f"[STAPS-BLOCK][{self.node_id}] Enter: {self.process_name} | Coord: {self.coord}")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration_ms = (time.perf_counter() - self.start) * 1000
        _logger.info(f"[STAPS-BLOCK][{self.node_id}] Exit: {self.process_name} | Coord: {self.coord} | Duration: {duration_ms:.4f}ms")
        STAPSCore.record_telemetry(self.node_id, self.process_name, self.coord, duration_ms)
