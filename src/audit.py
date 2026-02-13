import json
import os
from datetime import datetime

class AuditLogger:
    def __init__(self, log_file="data/audit_log.json"):
        self.log_file = log_file
        self._ensure_log_file()

    def _ensure_log_file(self):
        if not os.path.exists(os.path.dirname(self.log_file)):
            os.makedirs(os.path.dirname(self.log_file))
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w') as f:
                json.dump([], f)

    def log_event(self, event_type, user, details):
        """
        Logs an event to the audit trail.
        event_type: "Generation", "Edit", "View", "Approval"
        user: "Analyst_Name" (or ID)
        details: dict containing relevant context (e.g., specific changes, reasoning)
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user": user,
            "details": details
        }
        
        try:
            with open(self.log_file, 'r') as f:
                logs = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            logs = []
            
        logs.append(entry)
        
        with open(self.log_file, 'w') as f:
            json.dump(logs, f, indent=4)
            
    def get_logs(self):
        try:
            with open(self.log_file, 'r') as f:
                return json.load(f)
        except:
            return []
