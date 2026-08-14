import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import Config

logger = logging.getLogger(__name__)

def is_authorized(update: Update) -> bool:
    user_id = str(update.effective_user.id)
    return user_id == Config.ADMIN_CHAT_ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    keyboard = [
        [InlineKeyboardButton("📸 Screenshot", callback_data="screenshot")],
        [InlineKeyboardButton("📱 Device Info", callback_data="device")],
        [InlineKeyboardButton("🔋 Battery", callback_data="battery")],
        [InlineKeyboardButton("📂 Files", callback_data="files")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome = "🤖 **Android Remote Control Bot**\n\nUse buttons below or commands:\n\n📸 `/screenshot` - Take a screenshot\n📱 `/device` - Device information\n🔋 `/battery` - Battery status\n📂 `/files` - List files\n🔊 `/volume up` - Control volume\n📤 `/upload /path` - Upload a file"
    
    await update.message.reply_text(welcome, reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    help_text = "🤖 **Android Remote Control Bot**\n\n**Commands:**\n\n📸 `/screenshot` - Take a screenshot\n📱 `/device` - Show device info\n🔋 `/battery` - Show battery status\n📂 `/files` - List files\n🔊 `/volume up/down/mute` - Control volume\n📤 `/upload /path` - Upload a file\n💬 `/echo [text]` - Echo your message\n/start - Show main menu\n/help - Show this help"
    
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    text = " ".join(context.args)
    if text:
        await update.message.reply_text(f"📢 {text}")
    else:
        await update.message.reply_text("Please type something after /echo")

async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    from handlers.screenshot import screenshot
    from handlers.device import device_info, battery, volume, files
    
    query = update.callback_query
    await query.answer()
    
    if not is_authorized(update):
        await query.edit_message_text("⛔ Unauthorized access!")
        return
    
    data = query.data
    
    if data == "screenshot":
        await screenshot(update, context)
    elif data == "device":
        await device_info(update, context)
    elif data == "battery":
        await battery(update, context)
    elif data == "files":
        await files(update, context)
    elif data == "help":
        await help_command(update, context)
    else:
        await query.edit_message_text("❌ Unknown command")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Update {update} caused error {context.error}")
    if update and update.effective_message:
        await update.effective_message.reply_text("❌ An error occurred. Please try again later.")
