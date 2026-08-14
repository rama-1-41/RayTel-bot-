#!/usr/bin/env python3
"""
Telegram Bot for Heroku (Webhook Version)
"""

import os
import logging
import sys
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler
from config import Config
from handlers.basic import start, help_command, echo, error_handler, callback_handler
from handlers.screenshot import screenshot
from handlers.device import device_info, battery, volume, files, upload

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Initialize bot application
bot_app = None

def init_bot():
    """Initialize the bot application"""
    global bot_app
    
    try:
        Config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        logger.info("Please set BOT_TOKEN in environment variables")
        return None
    
    logger.info("🤖 Initializing Android Remote Control Bot...")
    
    # Create application
    application = Application.builder().token(Config.BOT_TOKEN).build()
    
    # Add command handlers
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
    
    logger.info("✅ Bot initialized successfully!")
    return application

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return "🤖 Android Telegram Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    if not bot_app:
        return "Bot not initialized", 500
    
    try:
        # Parse the incoming request
        update = Update.de_json(request.get_json(force=True), bot_app.bot)
        bot_app.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return "Error", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return {"status": "healthy", "bot": "running"}, 200

if __name__ == "__main__":
    # For local development
    bot_app = init_bot()
    if bot_app:
        logger.info("🚀 Starting bot in polling mode...")
        bot_app.run_polling()
else:
    # For Heroku
    bot_app = init_bot()
    if bot_app:
        # Set webhook
        webhook_url = f"https://raytele-bot.herokuapp.com/webhook"
        bot_app.bot.set_webhook(url=webhook_url)
        logger.info(f"🔗 Webhook set to: {webhook_url}")
