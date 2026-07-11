"""
Storage module
--------------
Handles reading and writing tasks to the JSON file (tasks.json).
"""

import json
import os

TASKS_FILE = "tasks.json"


def load_tasks():
    """Reads tasks.json and returns the list of saved tasks (or [] if it doesn't exist)."""
    if not os.path.exists(TASKS_FILE):
        return []
    with open(TASKS_FILE, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []


def save_tasks(tasks):
    """Writes the full list of tasks to tasks.json."""
    with open(TASKS_FILE, "w", encoding="utf-8") as f:
        json.dump(tasks, f, ensure_ascii=False, indent=2)
