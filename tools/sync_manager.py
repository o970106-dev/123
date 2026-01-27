import json
import os
import time
from .space_time_algo import SpaceTimeSystem

LOG_FILE = "collaboration_log.json"
SYNC_STATE = "sync_state.json"

class DoubleJSyncManager:
    def __init__(self, time_window_seconds=86400): # Default 24h window
        self.now = time.time()
        self.st_system = SpaceTimeSystem(self.now - time_window_seconds, self.now + 600) # Buffer for future
        self.last_sync_time = self._load_last_sync()

    def _load_last_sync(self):
        if os.path.exists(SYNC_STATE):
            with open(SYNC_STATE, "r") as f:
                return json.load(f).get("last_sync_time", 0)
        return 0

    def _save_last_sync(self):
        with open(SYNC_STATE, "w") as f:
            json.dump({"last_sync_time": self.now}, f)

    def load_and_index_logs(self):
        if not os.path.exists(LOG_FILE):
            return []

        with open(LOG_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)

        for log in logs:
            # We assume the log has a 'timestamp_unix' field
            t = log.get("timestamp_unix", 0)
            if t:
                self.st_system.insert(t, log)
        return logs

    def get_pending_actions(self):
        # Efficiently query actions from last_sync_time to now
        return self.st_system.query(self.last_sync_time + 0.001, self.now)

    def perform_sync(self):
        self.load_and_index_logs()
        pending = self.get_pending_actions()

        if pending:
            print(f"[Sync] Found {len(pending)} new actions to synchronize.")
            for action in pending:
                print(f"  - [{action['agent']}] {action['action']}: {action['details']}")
        else:
            print("[Sync] System is already up to date.")

        self._save_last_sync()
        return pending

if __name__ == "__main__":
    # Note: This is intended to be imported, but can be run for testing
    manager = DoubleJSyncManager()
    manager.perform_sync()
