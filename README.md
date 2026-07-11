# 🔔 TaskPing Bot

**A personal reminder assistant for Telegram.** Tell it a task, a day, and a time — TaskPing pings you the moment it's due, using your device's real calendar and clock.

![Version](https://img.shields.io/badge/version-1.0.0-blue)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Status](https://img.shields.io/badge/status-stable-brightgreen)

---

## 📖 Table of Contents

- [About](#-about)
- [Features](#-features)
- [Project Structure](#-project-structure)
- [Requirements](#-requirements)
- [Installation](#-installation)
- [Usage](#-usage)
- [Commands Reference](#-commands-reference)
- [How It Works](#-how-it-works)
- [Data Storage](#-data-storage)
- [Roadmap](#-roadmap)
- [Contributing](#-contributing)
- [License](#-license)

---

## 📌 About

TaskPing Bot is a lightweight Telegram bot built with Python that works as a personal productivity assistant. Instead of relying on a separate to-do app, TaskPing lives inside a messaging app you probably already use every day.

You send it a task with a specific day and time — using natural expressions like `today`, `tomorrow`, a weekday name, or an exact date — and it automatically sends you a notification the moment that time arrives. Reminders are saved permanently, so nothing is lost even if the bot restarts.

---

## ✨ Features

- 📅 **Real calendar support** — schedule with `today`, `tomorrow`, weekday names (`thursday`), or exact dates (`5/7/26`)
- ⏰ **Exact time scheduling** — 24-hour `HH:MM` format
- 💾 **Persistent storage** — reminders are saved to `tasks.json` and survive bot restarts
- 🔄 **Automatic rescheduling** — on startup, TaskPing reloads pending reminders and reschedules them based on the current real time
- 📋 **View pending reminders** — numbered list of everything still scheduled
- ✏️ **Edit reminders** — update the day, time, or text of an existing reminder
- 🗑️ **Delete reminders** — cancel a reminder before it fires
- 🎨 **Clean, formatted messages** — HTML-based formatting for a polished user experience
- 🧩 **Modular architecture** — clear separation between parsing, storage, scheduling, and command handling

---

## 🗂 Project Structure

```
TaskPing_Bot/
├── main.py                # Entry point: builds and runs the bot
├── requirements.txt       # Python dependencies
├── README.md
├── LICENSE
├── .gitignore
└── bot/
    ├── __init__.py
    ├── handlers.py         # Telegram command handlers (/start, /remind, /pending, /edit, /delete)
    ├── parser.py           # Day/time parsing logic (real calendar-aware)
    ├── scheduler.py        # Sends reminders + reschedules pending tasks on startup
    └── storage.py          # Reads/writes tasks.json
```

---

## ⚙️ Requirements

- Python 3.10 or higher
- A Telegram account
- A bot token from [@BotFather](https://t.me/BotFather)

---

## 🚀 Installation

**1. Clone the repository**
```bash
git clone https://github.com/your-username/TaskPing_Bot.git
cd TaskPing_Bot
```

**2. Create and activate a virtual environment**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate
```

**3. Install dependencies**
```bash
pip install -r requirements.txt
```

**4. Create your bot with BotFather**
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` and follow the prompts
3. Copy the token BotFather gives you

**5. Add your token**

Open `main.py` and replace the placeholder:
```python
TOKEN = "YOUR_TOKEN_HERE"
```

> ⚠️ **Never commit your real token.** Keep `main.py`'s token as a placeholder in version control, or move it to a `.env` file and load it with `python-dotenv`.

**6. Run the bot**
```bash
python main.py
```

You should see:
```
TaskPing Bot running... press Ctrl+C to stop it.
```

---

## 💬 Usage

Open Telegram, search for your bot by its username, and send `/start` to begin.

```
/remind today 20:00 study for the exam
/remind tomorrow 08:30 buy bread
/remind thursday 14:00 submit the project
/remind 5/7/26 09:00 doctor's appointment
```

---

## 📋 Commands Reference

| Command | Description | Example |
|---|---|---|
| `/start` | Shows a welcome message and usage instructions | `/start` |
| `/remind <day> <time> <task>` | Schedules a new reminder | `/remind today 20:00 study for the exam` |
| `/pending` | Lists all pending (not-yet-sent) reminders, numbered | `/pending` |
| `/edit <number> <day> <time> <task>` | Updates an existing reminder | `/edit 1 tomorrow 09:00 study harder` |
| `/delete <number>` | Cancels a pending reminder | `/delete 1` |

**Accepted values for `<day>`:**
| Value | Meaning |
|---|---|
| `today` | The current date |
| `tomorrow` | The next day |
| `monday` … `sunday` | The next occurrence of that weekday (if it's the same day today, it schedules for next week) |
| `dd/mm/yy` or `dd/mm/yyyy` | An exact date, e.g. `5/7/26` |

**`<time>` format:** 24-hour `HH:MM`, e.g. `08:30`, `14:00`, `20:00`.

---

## 🧠 How It Works

```
Input → Processing → Storage → Waiting → Output
```

1. **Input** — The user sends `/remind <day> <time> <task>`
2. **Processing** — `bot/parser.py` interprets the day and time against the system's real calendar
3. **Storage** — The reminder is saved to `tasks.json` *before* being scheduled, so it isn't lost
4. **Waiting** — `bot/scheduler.py` uses Telegram's `JobQueue` to wait until the exact date/time
5. **Output** — When the moment arrives, the bot sends the reminder and marks it as sent

On startup, `post_init()` in `scheduler.py` reads `tasks.json` and reschedules everything still pending, comparing it against the current real date and time — so restarting the bot never causes a missed reminder.

---

## 💾 Data Storage

Reminders are stored locally in `tasks.json`, created automatically the first time a reminder is saved. Example entry:

```json
{
  "id": "3f9a2b7e-1234-4c56-9abc-9876543210ef",
  "chat_id": 123456789,
  "task": "study for the exam",
  "datetime": "2026-07-12T20:00:00",
  "sent": false
}
```

| Field | Description |
|---|---|
| `id` | Unique identifier used internally to schedule/cancel the reminder |
| `chat_id` | The Telegram chat that should receive the notification |
| `task` | The reminder text |
| `datetime` | ISO 8601 date and time the reminder is due |
| `sent` | Whether the notification has already been delivered |

> `tasks.json` is excluded from version control via `.gitignore`, since it contains user-specific data.

---

## 🗺 Roadmap

- [ ] Recurring reminders (daily, weekly)
- [ ] Timezone support for multi-region users
- [ ] Migrate storage from JSON to SQLite for larger scale
- [ ] Inline buttons for quick edit/delete from `/pending`
- [ ] Optional reminder categories/tags

---

## 🤝 Contributing

Contributions, issues, and feature requests are welcome.

1. Fork the project
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m "Add amazing feature"`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## ✍️ Author
 
**Wandrys Ferrand** — creator and developer of TaskPing Bot.
 
---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

<p align="center">Built with 🐍 Python and 💬 Telegram Bot API</p>
