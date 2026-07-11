"""
Scheduler module
-----------------
Sends reminders when their scheduled moment arrives, and reschedules
pending reminders when the bot starts up (based on tasks.json + the
system's real date/time).
"""

from datetime import datetime

from bot.storage import load_tasks, save_tasks


async def send_reminder(context):
    """Runs automatically when the scheduled moment arrives."""
    task_id = context.job.data
    tasks = load_tasks()
    task_obj = next((t for t in tasks if t["id"] == task_id), None)

    if task_obj is None or task_obj["sent"]:
        return  # it was deleted or already sent

    await context.bot.send_message(
        chat_id=task_obj["chat_id"],
        text=f"⏰ Reminder: {task_obj['task']}",
    )

    task_obj["sent"] = True
    save_tasks(tasks)


async def post_init(application):
    """
    When the bot starts, checks tasks.json and reschedules pending
    reminders by comparing their saved date/time against the system's
    current real date/time.
    """
    tasks = load_tasks()
    now = datetime.now()
    changed = False

    for t in tasks:
        if t["sent"]:
            continue

        target = datetime.fromisoformat(t["datetime"])
        delta = target - now

        if delta.total_seconds() <= 0:
            # The bot was offline when it should have fired: send it anyway, marked as late.
            await application.bot.send_message(
                chat_id=t["chat_id"],
                text=f"⏰ Reminder (late, the bot was offline): {t['task']}",
            )
            t["sent"] = True
            changed = True
        else:
            application.job_queue.run_once(
                send_reminder,
                when=delta,
                chat_id=t["chat_id"],
                data=t["id"],
                name=t["id"],
            )

    if changed:
        save_tasks(tasks)
