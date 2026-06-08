# shutdown_log.py
# This script is triggered by Windows Task Scheduler on shutdown.
# It checks if a session is in progress and auto-logs it.

import json
import os
import sqlite3
from datetime import datetime

# Must match the paths in tracker.py exactly

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "sessions.db")
STATE_FILE = os.path.join(BASE_DIR, "session_state.json")

def log_session(date, start_time, end_time, duration, topic, notes):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions (date, start_time, end_time, duration_min, topic, notes)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (date, start_time, end_time, duration, topic, notes))
    conn.commit()
    conn.close()

# Only does anything if a session is currently active
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        state json.load(f)
    
    now = datetime.now()
    start_dt = datetime.strptime(
        f"{state['date']} {state['start_time']}",
        "%Y-%m-%d %I:%M:%S %p"
    )
    duration = round((now - start_dt).total_seconds() / 60, 1)

    log_session(
        state["date"],
        state["start_time"],
        now.strftime("%I:%M:%S %p"),
        duration,
        state["topic"],
        "[Auto-logged on shutdown]"
    )
    os.remove(STATE_FILE)