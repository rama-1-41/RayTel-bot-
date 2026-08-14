import os
import time
import subprocess
import logging
from datetime import datetime
from telegram import Update
from telegram.ext import ContextTypes
from handlers.basic import is_authorized

logger = logging.getLogger(__name__)

def take_screenshot() -> str:
    timestamp = int(time.time())
    filename = f"/sdcard/screen_{timestamp}.png"
    
    try:
        result = subprocess.run(["termux-screenshot", filename], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and os.path.exists(filename):
            return filename
    except:
        pass
    
    try:
        result = subprocess.run(["su", "-c", f"screencap -p {filename}"], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and os.path.exists(filename):
            return filename
    except:
        pass
    
    try:
        result = subprocess.run(["screencap", "-p", filename], capture_output=True, text=True, timeout=10)
        if result.returncode == 0 and os.path.exists(filename):
            return filename
    except:
        pass
    
    return None

async def screenshot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    if update.message:
        await update.message.reply_text("📸 Taking screenshot...")
    elif update.callback_query:
        await update.callback_query.answer("Taking screenshot...")
    
    filename = take_screenshot()
    
    if not filename:
        error_msg = "❌ Failed to take screenshot!\n\nTry:\n`pkg install termux-api`\n`termux-setup-storage`"
        if update.message:
            await update.message.reply_text(error_msg, parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.edit_message_text(error_msg, parse_mode="Markdown")
        return
    
    try:
        caption = f"📸 Screenshot at {datetime.now().strftime(%Y-%m-%d %H:%M:%S)}"
        
        if update.message:
            with open(filename, "rb") as photo:
                await update.message.reply_photo(photo, caption=caption)
        elif update.callback_query:
            await update.callback_query.edit_message_text("Sending screenshot...")
            with open(filename, "rb") as photo:
                await update.callback_query.message.reply_photo(photo, caption=caption)
        
        os.remove(filename)
    except Exception as e:
        error_msg = f"❌ Error: {str(e)}"
        if update.message:
            await update.message.reply_text(error_msg)
        elif update.callback_query:
            await update.callback_query.edit_message_text(error_msg)
