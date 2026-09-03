import httpx
from telegram import Update
from telegram.ext import ContextTypes
from services import fetch_similar_jobs
from keyboards import format_similar_job, job_save_keyboard, main_menu_keyboard


async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    awaiting = context.user_data.get("awaiting")
    if not awaiting:
        return

    value = update.message.text.strip()

    # Special case: semantic/similar search - replies immediately with results,
    # not stored as a regular accumulating filter.
    if awaiting == "similar_query":
        context.user_data["awaiting"] = None
        await update.message.reply_text("Looking for the best matching jobs for you...")

        try:
            print("DEBUG: calling fetch_similar_jobs")
            jobs = await fetch_similar_jobs(value)
            print("DEBUG: fetch_similar_jobs returned")
        except Exception as e:
            print(f"DEBUG ERROR: {type(e).__name__}: {e}")
            await update.message.reply_text("There was a problem connecting to the server.")
            return
        if not jobs:
            await update.message.reply_text("Couldn't find any jobs close to what you described.")
            return

        for job in jobs:
            await update.message.reply_text(
                format_similar_job(job),
                parse_mode="Markdown",
                reply_markup=job_save_keyboard(job["rowid"] ,  job["job_link"]),
            )
        await update.message.reply_text("Pick a job you like and save it ⭐", reply_markup=main_menu_keyboard())
        return

    # All other cases (plain text search, location, salary) - stored as accumulating filters
    filters_dict = context.user_data.setdefault("filters", {})

    if awaiting in ("min_salary", "max_salary"):
        try:
            filters_dict[awaiting] = float(value)
        except ValueError:
            await update.message.reply_text("That needs to be a number, please try again:")
            return
    else:
        filters_dict[awaiting] = value

    context.user_data["awaiting"] = None
    context.user_data["offset"] = 0
    await update.message.reply_text("Done ✅", reply_markup=main_menu_keyboard())

