[![Typing SVG](https://readme-typing-svg.demolab.com?font=Fira+Code&pause=1200&color=6B9FDD&width=500&lines=The+data+says+you're+doing+fine.;Productivity+tracking+for+people+who+know+better.;Hours+logged.+Sanity+optional.)](https://git.io/typing-svg)

# FocusLog

A lightweight desktop app for logging and visualizing work sessions. No server, no account, no internet required — just a single click to start tracking and another to stop.

![Python](https://img.shields.io/badge/Python_3-3776AB?style=flat-square&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=flat-square&logo=sqlite&logoColor=white)
![tkinter](https://img.shields.io/badge/tkinter-GUI-4479A1?style=flat-square)
![matplotlib](https://img.shields.io/badge/matplotlib-charts-11557c?style=flat-square)

---

## What it does

Launch the app to start a session. Launch it again to stop. Everything in between gets logged — topic, duration, and optional notes — to a local SQLite database. A built-in dashboard shows your time broken down by topic and plotted over time.

Designed for a single local user. All data stays on your machine.

---

## Features

- Start/stop sessions with a single click from a desktop shortcut
- Topic picker — choose from saved categories or type a custom one
- Optional session notes captured on stop
- SQLite storage — all sessions saved locally in `sessions.db`
- Dashboard with two charts:
  - Line chart: minutes logged over time
  - Pie chart: time breakdown by topic
- Category management — add, remove, or reset topics via Settings

---

## Project structure

```
focuslog/
├── tracker.py          # Main application
├── sessions.db         # SQLite database (auto-created on first run)
├── config.json         # Saved categories (auto-created on first run)
├── session_state.json  # Tracks an active session (deleted on stop)
└── README.md
```

---

## Requirements

- Python 3.x
- `matplotlib`

```bash
pip install matplotlib
```

All other dependencies (`tkinter`, `sqlite3`, `json`, `os`, `datetime`) are part of the Python standard library.

---

## Run it

```bash
cd focuslog
python tracker.py
```

To run without a console window (Windows), use `pythonw` instead of `python`.

---

## How it works

1. Launch the app. If no session is active, the main menu appears.
2. Pick a topic from your categories or type a custom one and start a session. The start time is saved to `session_state.json`.
3. Launch the app again to stop. It detects the active session and prompts you to log it.
4. Add optional notes and confirm. The session is written to `sessions.db` and the state file is deleted.
5. Open the dashboard to see your progress charts.

---

## Data storage

| File | Purpose |
|------|----------|
| `sessions.db` | Stores all completed sessions |
| `config.json` | Stores your category list |
| `session_state.json` | Tracks an active session; deleted after logging |

All files are stored in the project directory alongside `tracker.py`.

---

## Known limitations

- Hard power-offs cannot be intercepted. If the machine loses power mid-session, the active state remains in `session_state.json` and will prompt you on next launch.
- The dashboard opens in a separate matplotlib window, not embedded in the app UI.
- No multi-user support.

---

## Author

Tammy — Computer Science, College of Western Idaho
