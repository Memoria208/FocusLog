# Learning Tracker

A lightweight personal desktop app for logging and visualizing work and learning sessions. Built with Python and tkinter — no server, no account, no internet required.

---

## Features

- **Start/stop sessions** with a single click from the desktop shortcut
- **Topic picker** — choose from your saved categories or type a custom topic
- **Optional session notes** — captured when you stop a session
- **SQLite storage** — all sessions saved locally in `sessions.db`
- **Dashboard** — two charts rendered with matplotlib:
  - Line chart: minutes logged over time
  - Pie chart: time breakdown by topic
- **Category management** — add, remove, or reset your topic categories via Settings

---

## Project Structure

```
time-tracker/
├── tracker.py          # Main application
├── sessions.db         # SQLite database (auto-created on first run)
├── config.json         # Saved categories (auto-created on first run)
├── session_state.json  # Temp file tracking an active session (deleted on stop)
└── README.md
```

---

## Requirements

- Python 3.x (developed on Python 3.14)
- `matplotlib` — install with:

```
pip install matplotlib
```

All other dependencies (`tkinter`, `sqlite3`, `json`, `os`, `datetime`) are part of the Python standard library.

---

## Running the App

### From the desktop shortcut

The shortcut is configured to launch with `pythonw` (no console window) and the "Start in" field set to the project directory:

- **Target:** `C:\Users\tamsl\AppData\Local\Programs\Python\Python314\pythonw.exe tracker.py`
- **Start in:** `C:\Users\tamsl\dev\projects\time-tracker\`

### From the terminal

```
cd C:\Users\tamsl\dev\projects\time-tracker
python tracker.py
```

---

## How It Works

1. **Launch the app.** If no session is active, the main menu appears.
2. **Start a Session.** Pick a topic from your categories (or type a custom one). The start time is saved to `session_state.json`.
3. **Launch the app again to stop.** The app detects the active session and asks if you want to stop and log it.
4. **Add optional notes**, then confirm. The session is written to `sessions.db` and the state file is deleted.
5. **View Dashboard** to see your progress charts.

> The app uses a single-click launch model — each launch either starts or stops a session depending on whether one is already in progress.

---

## Data Storage

| File | Purpose |
|---|---|
| `sessions.db` | SQLite database; stores all completed sessions |
| `config.json` | Stores your custom category list |
| `session_state.json` | Tracks an active session; deleted after logging |

All files are stored in the project directory alongside `tracker.py`.

---

## Known Limitations

- **Hard power-offs cannot be intercepted.** If the machine loses power mid-session, the active session state will remain in `session_state.json` and prompt you on next launch.
- The dashboard opens in a separate matplotlib window (not embedded in the app UI).
- No multi-user support — designed for a single local user.
