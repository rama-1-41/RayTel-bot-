#!/usr/bin/env python3
import logging
import sys
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import Config
from handlers.basic import start, help_command, echo, error_handler, callback_handler
from handlers.screenshot import screenshot
from handlers.device import device_info, battery, volume, files, upload

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("Please set BOT_TOKEN and ADMIN_CHAT_ID in .env file")
        sys.exit(1)
    
    logger.info("🤖 Starting Android Remote Control Bot...")
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("screenshot", screenshot))
    application.add_handler(CommandHandler("device", device_info))
    application.add_handler(CommandHandler("battery", battery))
    application.add_handler(CommandHandler("volume", volume))
    application.add_handler(CommandHandler("files", files))
    application.add_handler(CommandHandler("upload", upload))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CallbackQueryHandler(callback_handler))
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot is running! Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
