import os
import json

STATE_FILE = "app/ai_agent/logs/index_state.json"
LOG_FILE = "app/ai_agent/logs/log_agents.jsonl"

def get_last_indexed_line():
    if not os.path.exists(STATE_FILE):
        return 0

    with open(STATE_FILE, "r") as f:
        return json.load(f).get("last_line", 0)


def update_last_indexed_line(line_no):
    with open(STATE_FILE, "w") as f:
        json.dump({"last_line": line_no}, f)

def clear_logs():
    with open(LOG_FILE, "w") as f:
        f.write("")