import httpx
from telegram import Update
from telegram.ext import ContextTypes
from keyboards import main_menu_keyboard , notifications_keyboard
from services import register_user , get_job_count



async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    try : 
        await register_user(user.id, user.username)
    except httpx.HTTPError:
        pass

    context.user_data.setdefault("filters", {})
    context.user_data["awaiting"] = None
    context.user_data["offset"] = 0
    context.user_data["started"] = True

    try:
        count = await get_job_count()
    except httpx.HTTPError:
        count = None

    text = f"Welcome, {user.first_name or 'there'}! 👋\n"
    if count is not None:
        text += f"\nThere are currently *{count}* jobs available.\n"
    text += "\nUse the menu below to search or filter jobs:"

    await update.effective_message.reply_text(text, parse_mode="Markdown", reply_markup=main_menu_keyboard())
    await update.effective_message.reply_text("🔔 Would you like to receive notifications when new jobs are found?",reply_markup=notifications_keyboard())


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Explicit /start command."""
    await send_welcome(update, context)


async def bootstrap_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Runs on ANY incoming message before the normal handlers.
    If this is the user's first contact with the bot (they haven't
    used /start), it automatically sends the welcome menu so users
    never have to type /start manually.
    """
    if not context.user_data.get("started"):
        await send_welcome(update, context)
