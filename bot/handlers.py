"""
Handlers module
---------------
Telegram command handlers: /start, /remind, /pending, /edit, /delete

Messages use HTML formatting (<b>, <code>) for a cleaner look. The app's
Defaults(parse_mode=ParseMode.HTML) in main.py makes this render automatically.
User-provided text is escaped with html.escape() so tasks containing
symbols like < or & don't break the formatting.
"""

import html
import uuid
from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes

from bot.parser import parse_day, parse_time, DAY_NAMES
from bot.storage import load_tasks, save_tasks
from bot.scheduler import send_reminder


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 <b>Welcome to TaskPing!</b>\n"
        "Your personal reminder assistant.\n\n"
        "Tell me a task with a day and a time, and I'll ping you right when it matters.\n\n"
        "<b>📌 Main command</b>\n"
        "<code>/remind &lt;day&gt; &lt;time&gt; &lt;task&gt;</code>\n\n"
        "<b>✨ Examples</b>\n"
        "• <code>/remind today 20:00 study for the exam</code>\n"
        "• <code>/remind tomorrow 08:30 buy bread</code>\n"
        "• <code>/remind thursday 14:00 submit the project</code>\n"
        "• <code>/remind 5/7/26 09:00 doctor's appointment</code>\n\n"
        "<b>🛠️ Manage your reminders</b>\n"
        "• <code>/pending</code> — view your saved reminders\n"
        "• <code>/edit &lt;number&gt; &lt;day&gt; &lt;time&gt; &lt;task&gt;</code> — update one\n"
        "• <code>/delete &lt;number&gt;</code> — remove one"
    )


async def remind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes /remind <day> <time> <task>, saves it to tasks.json, and schedules it."""
    chat_id = update.effective_chat.id

    try:
        day_text = context.args[0]
        time_text = context.args[1]
        task = " ".join(context.args[2:])
        if not task:
            raise IndexError
    except IndexError:
        await update.message.reply_text(
            "⚠️ <b>Wrong format</b>\n"
            "Use: <code>/remind &lt;day&gt; &lt;time&gt; &lt;task&gt;</code>\n\n"
            "<b>Examples</b>\n"
            "• <code>/remind today 20:00 study for the exam</code>\n"
            "• <code>/remind tomorrow 08:30 buy bread</code>\n"
            "• <code>/remind thursday 14:00 submit the project</code>\n"
            "• <code>/remind 5/7/26 09:00 doctor's appointment</code>"
        )
        return

    day = parse_day(day_text)
    time_valid = parse_time(time_text)

    if day is None:
        await update.message.reply_text(
            "🤔 I didn't understand the <b>day</b>.\n"
            "Try <code>today</code>, <code>tomorrow</code>, a weekday like <code>thursday</code>, "
            "or a date like <code>5/7/26</code>."
        )
        return

    if time_valid is None:
        await update.message.reply_text(
            "🤔 I didn't understand the <b>time</b>.\n"
            "Use 24-hour <code>HH:MM</code> format, e.g. <code>14:30</code>."
        )
        return

    h, m = time_valid
    target = datetime.combine(day, datetime.min.time()).replace(hour=h, minute=m)
    now = datetime.now()  # <- system's real time
    delta = target - now

    if delta.total_seconds() <= 0:
        await update.message.reply_text(
            "⏳ That date and time have already passed.\nPick a moment in the future."
        )
        return

    # Save the task to tasks.json BEFORE scheduling it
    task_id = str(uuid.uuid4())
    tasks = load_tasks()
    tasks.append({
        "id": task_id,
        "chat_id": chat_id,
        "task": task,
        "datetime": target.isoformat(),
        "sent": False,
    })
    save_tasks(tasks)

    context.job_queue.run_once(
        send_reminder,
        when=delta,
        chat_id=chat_id,
        data=task_id,
        name=task_id,
    )

    weekday = DAY_NAMES[target.weekday()]
    await update.message.reply_text(
        "✅ <b>Reminder saved!</b>\n\n"
        f"📝 {html.escape(task)}\n"
        f"📅 {weekday}, {target.strftime('%d/%m/%Y')} at {target.strftime('%H:%M')}\n\n"
        "I'll ping you right on time. Use /pending anytime to check your list."
    )


async def pending(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Shows tasks saved in tasks.json that haven't been sent yet, for this chat.

    Reminders are numbered (1, 2, 3...) in date/time order. That number is
    what /edit and /delete expect — not the internal ID.
    """
    chat_id = update.effective_chat.id
    tasks = load_tasks()
    own = [t for t in tasks if t["chat_id"] == chat_id and not t["sent"]]

    if not own:
        await update.message.reply_text(
            "🎉 <b>All clear!</b>\nYou have no pending reminders."
        )
        return

    own.sort(key=lambda t: t["datetime"])
    lines = ["📋 <b>Your pending reminders</b>\n"]
    for i, t in enumerate(own, start=1):
        target = datetime.fromisoformat(t["datetime"])
        weekday = DAY_NAMES[target.weekday()]
        lines.append(
            f"<b>{i}.</b> {html.escape(t['task'])}\n"
            f"     📅 {weekday}, {target.strftime('%d/%m/%Y')} at {target.strftime('%H:%M')}"
        )

    lines.append(
        "\nUse <code>/edit &lt;number&gt; &lt;day&gt; &lt;time&gt; &lt;task&gt;</code> "
        "or <code>/delete &lt;number&gt;</code> to manage one."
    )

    await update.message.reply_text("\n".join(lines))


async def edit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes /edit <number> <day> <time> <new task>: updates an existing pending reminder.

    <number> refers to the position shown by /pending, not the internal ID.
    """
    chat_id = update.effective_chat.id

    try:
        number = int(context.args[0])
        day_text = context.args[1]
        time_text = context.args[2]
        new_task = " ".join(context.args[3:])
        if not new_task:
            raise IndexError
    except (IndexError, ValueError):
        await update.message.reply_text(
            "⚠️ <b>Wrong format</b>\n"
            "Use: <code>/edit &lt;number&gt; &lt;day&gt; &lt;time&gt; &lt;new task&gt;</code>\n\n"
            "<b>Example</b>\n"
            "<code>/edit 1 tomorrow 09:00 study for the exam</code>\n\n"
            "Use /pending to see the number of each reminder."
        )
        return

    tasks = load_tasks()
    own = sorted(
        [t for t in tasks if t["chat_id"] == chat_id and not t["sent"]],
        key=lambda t: t["datetime"],
    )

    if number < 1 or number > len(own):
        await update.message.reply_text(
            "❌ I couldn't find a pending reminder with that number.\nUse /pending to check."
        )
        return

    match = own[number - 1]

    day = parse_day(day_text)
    time_valid = parse_time(time_text)

    if day is None:
        await update.message.reply_text(
            "🤔 I didn't understand the <b>day</b>.\n"
            "Try <code>today</code>, <code>tomorrow</code>, a weekday like <code>thursday</code>, "
            "or a date like <code>5/7/26</code>."
        )
        return

    if time_valid is None:
        await update.message.reply_text(
            "🤔 I didn't understand the <b>time</b>.\n"
            "Use 24-hour <code>HH:MM</code> format, e.g. <code>14:30</code>."
        )
        return

    h, m = time_valid
    target = datetime.combine(day, datetime.min.time()).replace(hour=h, minute=m)
    now = datetime.now()
    delta = target - now

    if delta.total_seconds() <= 0:
        await update.message.reply_text(
            "⏳ That date and time have already passed.\nPick a moment in the future."
        )
        return

    # Cancel the previously scheduled job for this task
    for job in context.job_queue.get_jobs_by_name(match["id"]):
        job.schedule_removal()

    # Update the stored task and reschedule it
    match["task"] = new_task
    match["datetime"] = target.isoformat()
    save_tasks(tasks)

    context.job_queue.run_once(
        send_reminder,
        when=delta,
        chat_id=chat_id,
        data=match["id"],
        name=match["id"],
    )

    weekday = DAY_NAMES[target.weekday()]
    await update.message.reply_text(
        "✏️ <b>Reminder updated!</b>\n\n"
        f"📝 {html.escape(new_task)}\n"
        f"📅 {weekday}, {target.strftime('%d/%m/%Y')} at {target.strftime('%H:%M')}"
    )


async def delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Processes /delete <number>: removes a pending reminder and cancels its scheduled job.

    <number> refers to the position shown by /pending, not the internal ID.
    """
    chat_id = update.effective_chat.id

    try:
        number = int(context.args[0])
    except (IndexError, ValueError):
        await update.message.reply_text(
            "⚠️ Use: <code>/delete &lt;number&gt;</code>\nUse /pending to see the number of each reminder."
        )
        return

    tasks = load_tasks()
    own = sorted(
        [t for t in tasks if t["chat_id"] == chat_id and not t["sent"]],
        key=lambda t: t["datetime"],
    )

    if number < 1 or number > len(own):
        await update.message.reply_text(
            "❌ I couldn't find a pending reminder with that number.\nUse /pending to check."
        )
        return

    match = own[number - 1]

    # Cancel the scheduled job so it doesn't fire after deletion
    for job in context.job_queue.get_jobs_by_name(match["id"]):
        job.schedule_removal()

    tasks.remove(match)
    save_tasks(tasks)

    await update.message.reply_text(
        f"🗑️ <b>Reminder deleted</b>\n{html.escape(match['task'])} won't be sent anymore."
    )