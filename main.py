import logging
import os
from dotenv import load_dotenv

from telegram.ext import ApplicationBuilder, CommandHandler, Defaults
from telegram.constants import ParseMode

from bot.handlers import start, remind, pending, edit, delete
from bot.scheduler import post_init

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

load_dotenv()

# Load token from .env file
TOKEN = os.getenv("TELEGRAM_TOKEN")

def main():
    defaults = Defaults(parse_mode=ParseMode.HTML)
    app = (
        ApplicationBuilder()
        .token(TOKEN)
        .defaults(defaults)
        .post_init(post_init)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("remind", remind))
    app.add_handler(CommandHandler("pending", pending))
    app.add_handler(CommandHandler("edit", edit))
    app.add_handler(CommandHandler("delete", delete))

    print("TaskPing Bot running... press Ctrl+C to stop it.")
    app.run_polling()


if __name__ == "__main__":
    main()

