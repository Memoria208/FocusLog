# SECTION 1: Imports and constants

import tkinter as tk
from tkinter import simpledialog, messagebox
import json
import os
import sqlite3  # Built-in Python database — no install needed
import matplotlib.pyplot as plt  # For rendering charts
import matplotlib.dates as mdates  # For formatting dates on chart axes
from datetime import datetime



# --- Config ---
# All data files live in the same folder as this script
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Local SQLite database file — stores all session data
DB_FILE = os.path.join(BASE_DIR, "sessions.db")

# Stores the user's custom category list
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")

# Temp file that tracks an active session between clicks
STATE_FILE = os.path.join(BASE_DIR, "session_state.json")

# SECTION 2: Database setup

def init_db():
    # Creates the sessions table if it doesn't exist yet
    # This runs every time the app starts — safe to call repeatedly
    # because CREATE TABLE IF NOT EXISTS won't overwrite existing data
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              date TEXT,
              start_time TEXT,
              end_time TEXT,
              duration_min REAL,
              topic TEXT,
              notes TEXT
        )
    """)
    conn.commit()  # Saves the changes
    conn.close()   # Always close the connection when done

def log_session(date, start_time, end_time, duration, topic, notes):
    # Inserts a completed session into the database
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        INSERT INTO sessions
              (date, start_time, end_time, duration_min, topic, notes)
              VALUES (?, ?, ?, ?, ?, ?)
""", (date, start_time, end_time, duration, topic, notes))
    conn.commit()
    conn.close()

def get_all_sessions():
    # Retrieves all sessions from the database ordered by date
    # Returns a list of tuples — one tuple per session row
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        SELECT date, start_time, end_time, duration_min, topic, notes
        FROM sessions
        ORDER BY date ASC
    """)
    rows = c.fetchall()
    conn.close()
    return rows
    
# SECTION 3: State and category functions

def load_state():
    # Checks if a session is already in progress
    # Returns the session data as a dictionary, or None if no active session
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, "r") as f:
            return json.load(f)
    return None

def save_state(state):
    # Savves the current session info to a local file
    # This is how the script remembers a session between clicks
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        import tkinter.messagebox as mb
        mb.showerror("Save Error", f"Could not save state:\n{STATE_FILE}\n\n{e}")

def clear_state():
    # Deletes the session file once a session has been logged
    # Resets things so the next click starts a new session
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)

def load_categories():
    # Reads saved categories from config.json
    # Returns a list of category strings, or empty list if none exist
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r") as f:
            data = json.load(f)
            return data.get("categories", [])
    return []

def save_categories(categories):
    # Writes the updates category list to config.json
    with open(CONFIG_FILE, "w") as f:
        json.dump({"categories": categories}, f)




# SECTION 4: Settings menu and topic picker

def settings_menu(root):
    # Opens the settings window where the user can manage categories
    categories = load_categories()

    win = tk.Toplevel(root)
    win.title("Settings - Manage Categories")
    win.geometry("400x500")
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
    y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
    win.geometry(f"+{x}+{y}")
    win.resizable(False, False)

    tk.Label(
        win,
        text="Your Categories",
        font=("Arial", 13, "bold")
    ).pack(pady=10)

    # Scrollable list of current categories
    listbox = tk.Listbox(win, selectmode=tk.SINGLE, font=("Arial", 11), height=10)
    for cat in categories:
        listbox.insert(tk.END, cat)
    listbox.pack(padx=20, fill=tk.X)

    def add_category():
        # Opens a text input and addds the new category to the list
        new_cat = simpledialog.askstring(
            "Add Category",
            "Enter a new category name:",
            parent=win
        )
        if new_cat and new_cat.strip():
            categories.append(new_cat.strip())
            listbox.insert(tk.END, new_cat.strip())
            save_categories(categories)

    def remove_category():
        # Removes whichever category is selected in the listbox
        selected = listbox.curselection()
        if not selected:
            messagebox.showwarning(
                "No selection",
                "Please select a category to remove.",
                parent=win
            )
            return
        index = selected[0]
        removed = categories.pop(index)
        save_categories(categories)
        messagebox.showinfo("Removed", f"'{removed}' has been removed.", parent=win)

    def reset_categories():
        # Clears all categories after confirmation
        confirm = messagebox.askyesno(
            "Start Over",
            "This will delete all your current categories. Are you sure?",
            parent=win
        )
        if confirm:
            categories.clear()
            listbox.delete(0, tk.END)
            save_categories(categories)
            messagebox.showinfo(
                "Reset",
                "Categories cleared. Add new ones to get started.",
                parent=win
            )
    tk.Button(win, text="Add Category", width=20, command=add_category).pack(pady=5)
    tk.Button(win, text="Remove Selected", width=20, command=remove_category).pack(pady=5)
    tk.Button(win, text="Start Over", width=20, command=reset_categories).pack(pady=5)
    tk.Button(win, text="Done", width=20, command=win.destroy).pack(pady=10)

    win.grab_set()
    root.wait_window(win)

def pick_topic(root):
    # Opens a window showing saved categories as buttons
    # User picks one or selects Other: to type a custom topicc
    categories = load_categories()

    # If no categories exist yet, send them to settings first
    if not categories:
        messagebox.showinfo(
            "No Categories Yet",
            "You haven't set up any categories yet.\nLet's do that first!",
            parent=root
        )
        settings_menu(root)
        categories = load_categories()
        if not categories:
            return None  # Still empty — user cancelled setup
        
    selected_topic = tk.StringVar(value="")

    win = tk.Toplevel(root)
    win.title("What are you working on?")
    win.geometry("400x500")
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
    y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
    win.geometry(f"+{x}+{y}")
    win.resizable(False, False)

    tk.Label(
        win,
        text="What are you working on?",
        font=("Arial", 13, "bold")
    ).pack(pady=10)

    # One button per saved category
    for cat in categories:
        tk.Button(
            win,
            text=cat,
            width=30,
            font=("Arial", 11),
            command=lambda c=cat: [selected_topic.set(c), win.destroy()]
        ).pack(pady=3)

    def choose_other():
        # Opens a text input for a custom topic not in the category list
        other = simpledialog.askstring(
            "Other",
            "Describe what you're working on:",
            parent=win
        )
        if other and other.strip():
            selected_topic.set(f"Other: {other.strip()}")
            win.destroy()

    tk.Button(
        win,
        text="Other:",
        width=30,
        command=choose_other
    ).pack(pady=10)

    win.grab_set()
    root.wait_window(win)

    # Returns the selected topic, or None if cancelled
    return selected_topic.get() or None


# SECTION 5: Start session, stop session, and dashboard


def start_session(root):
    # Opens the topic picker and saves the session start time
    topic = pick_topic(root)

    if not topic:
        return  # User cancelled — do nothing

    now = datetime.now()
    state = {
        "date": now.strftime("%Y-%m-%d"),
        "start_time": now.strftime("%I:%M:%S %p"),
        "topic": topic
    }
    save_state(state)
    messagebox.showinfo(
        "Session Started",
        f"Timer started at {state['start_time']}\nTopic: {topic}\n\nClick the button again to stop."
    )

def stop_session(root, state):
    # Calculates session duration and logs it to the database
    now = datetime.now()

    # Reconstruct start time as a datetime object so we can do math on it
    start_dt = datetime.strptime(
        f"{state['date']} {state['start_time']}",
        "%Y-%m-%d %I:%M:%S %p"
    )
    # Calculate how many minutes the session lasted
    duration = round((now - start_dt).total_seconds() / 60, 1)

    # Ask for optional notes
    notes = simpledialog.askstring(
        "Stop Session",
        f"Session duration: {duration} minutes\n\nAny notes? (optional — hit OK to skip)",
        parent=root
    )

    try:
        # Write the completed session to the local database
        log_session(
            state["date"],
            state["start_time"],
            now.strftime("%I:%M:%S %p"),
            duration,
            state["topic"],
            notes or ""
        )
        clear_state()
        messagebox.showinfo(
            "Session Logged!",
            f"{duration} minutes logged\nTopic: {state['topic']}"
        )
    except Exception as e:
        messagebox.showerror("Error", f"Couldn't save session:\n{e}")

def show_dashboard(root):
    # Retrieves all sessions and displays two charts:
    # 1. A line chart of cumulative minutes logged over time
    # 2. A pie chart of total time broken down by topic
    rows = get_all_sessions()

    if not rows:
        messagebox.showinfo(
            "No Data Yet",
            "You haven't logged any sessions yet.\nStart one to see your dashboard!",
            parent=root
        )
        return

    # --- Prepare data for line chart ---
    # Group total minutes by date
    date_totals = {}
    for row in rows:
        date = row[0]
        duration = row[3]
        date_totals[date] = date_totals.get(date, 0) + duration

    # Sort dates chronologically
    sorted_dates = sorted(date_totals.keys())
    # Convert date strings to datetime objects for matplotlib
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in sorted_dates]
    minutes = [date_totals[d] for d in sorted_dates]

    # --- Prepare data for pie chart ---
    # Group total minutes by topic
    topic_totals = {}
    for row in rows:
        topic = row[4]
        duration = row[3]
        topic_totals[topic] = topic_totals.get(topic, 0) + duration

    # --- Build the charts ---
    # Create a figure with two side by side charts
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Learning Tracker Dashboard", fontsize=16, fontweight="bold")

    # Line chart — minutes logged over time
    ax1.plot(dates, minutes, marker="o", color="steelblue", linewidth=2)
    ax1.set_title("Minutes Logged Over Time")
    ax1.set_xlabel("Date")
    ax1.set_ylabel("Minutes")
    # Format x-axis dates so they don't overlap
    ax1.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
    fig.autofmt_xdate()
    ax1.grid(True, linestyle="--", alpha=0.5)

    # Pie chart — time by topic
    ax2.pie(
        topic_totals.values(),
        labels=topic_totals.keys(),
        autopct="%1.1f%%",  # Shows percentage on each slice
        startangle=140
    )
    ax2.set_title("Time by Topic")

    plt.tight_layout()
    plt.show()  # Opens the chart window

def main_menu(root):
    # Opens a clean main menu with clearly labeled buttons
    win = tk.Toplevel(root)
    win.title("Learning Tracker")
    win.geometry("300x250")
    win.update_idletasks()
    x = (win.winfo_screenwidth() // 2) - (win.winfo_width() // 2)
    y = (win.winfo_screenheight() // 2) - (win.winfo_height() // 2)
    win.geometry(f"+{x}+{y}")
    win.resizable(False, False)

    tk.Label(
        win,
        text="What would you like to do?",
        font=("Arial", 13, "bold")
    ).pack(pady=20)

    # Start Session button
    tk.Button(
        win,
        text="Start Session",
        width=20,
        font=("Arial", 11),
        command=lambda: [win.destroy(), start_session(root)]
    ).pack(pady=5)

    # Dashboard button — opens the charts window
    tk.Button(
        win,
        text="View Dashboard",
        width=20,
        font=("Arial", 11),
        command=lambda: [win.destroy(), show_dashboard(root)]
    ).pack(pady=5)

    # Settings button — manage categories
    tk.Button(
        win,
        text="Settings",
        width=20,
        font=("Arial", 11),
        command=lambda: [win.destroy(), settings_menu(root)]
    ).pack(pady=5)

    win.grab_set()
    root.wait_window(win)

def main():
    # Initialize the database on every launch
    # Safe to call repeatedly — won't overwrite existing data
    init_db()
    

    root = tk.Tk()
    root.withdraw()  # Hide the main window — we only want popups

    state = load_state()

    if state:
        # Active session found — ask if user wants to stop and log it
        confirm = messagebox.askyesno(
            "Active Session Found",
            f"Session in progress since {state['start_time']}\n"
            f"Topic: {state['topic']}\n\nStop and log it now?"
        )
        if confirm:
            stop_session(root, state)
    else:
        # No active session — show the main menu
        main_menu(root)

    root.destroy()  # Clean up tkinter when done

# This makes sure main() only runs when you execute this file directly
# (not if another script imports it)
if __name__ == "__main__":
    main()
        