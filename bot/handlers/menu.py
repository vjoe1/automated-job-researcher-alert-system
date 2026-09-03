
import httpx
from telegram import Update
from telegram.ext import ContextTypes
from config import PAGE_SIZE
from services import fetch_jobs, save_job_for_user, api_get ,update_notifications
from keyboards import (
    main_menu_keyboard,
    filters_menu_keyboard,
    sort_menu_keyboard,
    jobtype_menu_keyboard,
    posted_menu_keyboard,
    experience_menu_keyboard,
    remote_menu_keyboard,
    hiring_menu_keyboard,
    load_more_keyboard,
    job_save_keyboard,
    format_job,
    job_saved_keyboard 
)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
        # ---------- Notifications ----------
    if data == "notifications:on":
        try:
            await update_notifications(query.from_user.id, True)
            await query.edit_message_text(
                "🔔 Notifications enabled! You'll be notified when new jobs are found.",
                reply_markup=main_menu_keyboard()
            )
        except httpx.HTTPError:
            await query.edit_message_text(
                "There was a problem connecting to the server."
            )
        return

    if data == "notifications:off":
        try:
            await update_notifications(query.from_user.id, False)
            await query.edit_message_text(
                "🔕 Notifications disabled. You can enable them anytime.",
                reply_markup=main_menu_keyboard()
            )
        except httpx.HTTPError:
            await query.edit_message_text(
                "There was a problem connecting to the server."
            )
        return
    context.user_data.setdefault("filters", {})
    filters_dict = context.user_data["filters"]

    # ---------- Menu navigation ----------
    if data == "menu:main":
        await query.edit_message_text("Main Menu:", reply_markup=main_menu_keyboard())
        return

    if data == "menu:filters":
        await query.edit_message_text("Choose what to filter by:", reply_markup=filters_menu_keyboard())
        return

    if data == "menu:sort":
        await query.edit_message_text("Sort results by:", reply_markup=sort_menu_keyboard())
        return

    if data == "menu:jobtype":
        await query.edit_message_text("Choose job type:", reply_markup=jobtype_menu_keyboard())
        return

    if data == "menu:posted":
        await query.edit_message_text("Choose date posted:", reply_markup=posted_menu_keyboard())
        return

    if data == "menu:experience":
        await query.edit_message_text("Choose experience level:", reply_markup=experience_menu_keyboard())
        return

    if data == "menu:remote":
        await query.edit_message_text("Choose work type:", reply_markup=remote_menu_keyboard())
        return

    if data == "menu:hiring":
        await query.edit_message_text("Only show companies actively hiring?", reply_markup=hiring_menu_keyboard())
        return

    if data == "menu:clear":
        context.user_data["filters"] = {}
        context.user_data["offset"] = 0
        await query.edit_message_text("All filters cleared. ✅", reply_markup=main_menu_keyboard())
        return

    # ---------- Free-text input requests (search / location / salary) ----------
    if data == "menu:search":
        context.user_data["awaiting"] = "q"
        await query.edit_message_text(
            "Type a keyword to search for (matches title, company, or description):"
        )
        return

    if data == "menu:similar":
        context.user_data["awaiting"] = "similar_query"
        await query.edit_message_text(
            "Describe your experience or the skills you're looking for "
            "(e.g. \"backend developer with Python experience in FastAPI and databases\"):"
        )
        return

    if data.startswith("filter:ask:"):
        field = data.split(":")[2]
        context.user_data["awaiting"] = field
        prompts = {
            "location": "Type a city or country:",
            "min_salary": "Type the minimum salary (numbers only):",
            "max_salary": "Type the maximum salary (numbers only):",
        }
        await query.edit_message_text(prompts[field])
        return

    # ---------- Selecting a preset filter value ----------
    if data.startswith("filter:"):
        _, field, value = data.split(":", 2)
        if field == "actively_hiring":
            filters_dict[field] = True if value == "true" else None
        else:
            filters_dict[field] = value or None
        context.user_data["offset"] = 0
        await query.edit_message_text("Done ✅ Want to add another filter?", reply_markup=filters_menu_keyboard())
        return

    # ---------- Sorting ----------
    if data.startswith("sort:"):
        filters_dict["sort_by"] = data.split(":")[1]
        context.user_data["offset"] = 0
        await query.edit_message_text("Results sorted ✅", reply_markup=main_menu_keyboard())
        return

    # ---------- Show results ----------
    if data == "menu:results":
        context.user_data["offset"] = 0
        await show_results(query, context, reset=True)
        return

    if data == "results:more":
        await show_results(query, context, reset=False)
        return

    
    # ---------- Saved jobs ----------
    if data == "menu:saved":
        telegram_id = query.from_user.id

        try:
            saved = await api_get(f"/users/{telegram_id}/saved-jobs")
        except httpx.HTTPError:
            await query.message.reply_text(
                "There was a problem connecting to the server."
            )
            return

        if not saved:
            await query.edit_message_text(
                "You don't have any saved jobs yet.",
                reply_markup=main_menu_keyboard()
            )
            return

        await query.message.reply_text(f"You have {len(saved)} saved job(s):")

        for job in saved:
            await query.message.reply_text(
                format_job(job),
                parse_mode="Markdown"
            )
        return


    # ---------- Saving a job ----------
    if data.startswith("save:"):
        rowid = int(data.split(":")[1])

        try:
            await save_job_for_user(query.from_user.id, rowid)

            # Change the button from "Save" to "Saved"
            await query.edit_message_reply_markup(
                reply_markup=job_saved_keyboard(rowid)
            )

            await query.answer("Saved! ⭐", show_alert=False)

        except httpx.HTTPError:
            await query.answer(
                "Something went wrong, please try again.",
                show_alert=True
            )

        return

async def show_results(query, context: ContextTypes.DEFAULT_TYPE, reset: bool):
    filters_dict = context.user_data.get("filters", {})
    offset = 0 if reset else context.user_data.get("offset", 0)

    try:
        jobs = await fetch_jobs(filters_dict, offset=offset, limit=PAGE_SIZE)
    except httpx.HTTPError:
        await query.message.reply_text("There was a problem connecting to the server.")
        return

    if not jobs:
        if offset == 0:
            await query.message.reply_text("No jobs match these filters.", reply_markup=main_menu_keyboard())
        else:
            await query.message.reply_text("No more jobs to show.", reply_markup=main_menu_keyboard())
        return

    if offset == 0:
        await query.message.reply_text(f"Showing {len(jobs)} job(s):")
    for job in jobs:
        await query.message.reply_text(
            format_job(job), parse_mode="Markdown", reply_markup=job_save_keyboard(job["rowid"], job["job_link"])
        )

    new_offset = offset + len(jobs)
    context.user_data["offset"] = new_offset

    if len(jobs) == PAGE_SIZE:
        await query.message.reply_text(
            "Want to see more jobs matching your filters?", reply_markup=load_more_keyboard()
        )
    else:
        await query.message.reply_text("That's all the jobs matching your filters.", reply_markup=main_menu_keyboard())