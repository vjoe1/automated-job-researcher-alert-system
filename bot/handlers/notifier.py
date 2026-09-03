import logging
from telegram.ext import ContextTypes
from services import (
    get_new_jobs_since_last_check, 
    mark_jobs_checked, 
    get_all_user_ids
)
import asyncio

logger = logging.getLogger(__name__)



async def send_daily_summary(context: ContextTypes.DEFAULT_TYPE):
    sent_successfully = False
    try:
        new_jobs = await get_new_jobs_since_last_check()
        new_count = len(new_jobs)
        print(f"DEBUG: new jobs count = {new_count}")

        user_ids = await get_all_user_ids()
                
        if new_count == 0:
            messages = [
                (
                    "🔍 *Job Discovery Report*\n\n"
                    "❌ No new jobs found today."
                )
            ]

        else:
            messages = []

            for i in range(0, new_count, 20):
                batch = new_jobs[i:i + 20]

                lines = [
                    "📊 *Job Discovery Report*",
                    "",
                    f"🔥 *{new_count}* new jobs found!",
                    "",
                ]

                for job in batch:
                    title = job.get("title", "Unknown Title")
                    company = job.get("company", "Unknown Company")
                    location = job.get("location", "Not specified")
                    job_link = job.get("job_link")

                    lines.append(f"💼 *{title}*")
                    lines.append(f"🏢 {company}")
                    lines.append(f"📍 {location}")

                    if job_link:
                        lines.append(f"🔗 [View Job]({job_link})")

                    lines.append("")

                messages.append("\n".join(lines))

        for telegram_id in user_ids:
            try:
                for message_text in messages:
                    await context.bot.send_message(
                        chat_id=telegram_id,
                        text=message_text,
                        parse_mode="Markdown",
                        disable_web_page_preview=True,
                    )
                    await asyncio.sleep(0.05)

                sent_successfully = True

            except Exception as e:
                logger.warning(
                    f"Could not send update to {telegram_id}: {e}"
                )
        if sent_successfully:
            await mark_jobs_checked()
    except Exception as e:
        logger.exception(
            f"Failed to send job summary: {e}"
        )
