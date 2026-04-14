import json
import os
from datetime import datetime

BASE_DIR = os.path.dirname(__file__)
LOG_FILE = os.path.join(BASE_DIR, "logs", "log_agents.jsonl")
def log_event(event_type, data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    log = {
        "timestamp": str(datetime.utcnow()),
        "type": event_type,
        "data": data
    }
    
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")
