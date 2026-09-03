import logging
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters as tg_filters,
)

from config import BOT_TOKEN
from handlers.start import bootstrap_handler, start
from handlers.menu import button_handler
from handlers.text import text_handler
from handlers.notifier import send_daily_summary
from datetime import time
import pytz


EGYPT_TZ = pytz.timezone("Africa/Cairo")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    # Schedule daily summary notification at 21:00 (9:00 PM) every day
    app.job_queue.run_daily(
        send_daily_summary,
        time=time(hour=21, minute=0 , tzinfo=EGYPT_TZ),
    ) 

   # Group -1 runs before everything else: auto-sends the welcome menu
    # the very first time a user contacts the bot, without needing /start.
    app.add_handler(MessageHandler(tg_filters.ALL & ~tg_filters.COMMAND, bootstrap_handler), group=-1)


    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(tg_filters.TEXT & ~tg_filters.COMMAND, text_handler))

    logger.info("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
