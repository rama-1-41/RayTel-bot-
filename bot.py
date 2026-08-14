#!/usr/bin/env python3
"""
Telegram Bot for Heroku (Webhook Version)
"""

import os
import logging
import sys
from flask import Flask, request, jsonify
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
    logger.info(f"Bot Token: {Config.BOT_TOKEN[:10]}...")
    logger.info(f"Admin Chat ID: {Config.ADMIN_CHAT_ID}")
    
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
    return jsonify({
        "status": "running",
        "bot": "Android Remote Control Bot",
        "version": "1.0.0"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    if not bot_app:
        logger.error("Bot app not initialized")
        return "Bot not initialized", 500
    
    try:
        # Get the request body
        body = request.get_json(force=True)
        logger.info(f"Received webhook update: {body.get('message', {}).get('text', '')[:50]}")
        
        # Parse the incoming request
        update = Update.de_json(body, bot_app.bot)
        bot_app.process_update(update)
        return "OK", 200
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return f"Error: {str(e)}", 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "bot_initialized": bot_app is not None
    })

@app.route('/setwebhook', methods=['GET'])
def set_webhook():
    """Manually set the webhook"""
    if not bot_app:
        return "Bot not initialized", 500
    
    try:
        webhook_url = f"https://raytele-bot.herokuapp.com/webhook"
        bot_app.bot.set_webhook(url=webhook_url)
        logger.info(f"🔗 Webhook set to: {webhook_url}")
        return jsonify({
            "status": "success",
            "webhook_url": webhook_url
        })
    except Exception as e:
        logger.error(f"Failed to set webhook: {e}")
        return jsonify({"error": str(e)}), 500

# Initialize bot when the app starts
with app.app_context():
    bot_app = init_bot()
    if bot_app:
        try:
            webhook_url = f"https://raytele-bot.herokuapp.com/webhook"
            bot_app.bot.set_webhook(url=webhook_url)
            logger.info(f"🔗 Webhook set to: {webhook_url}")
        except Exception as e:
            logger.error(f"Failed to set webhook on startup: {e}")
    else:
        logger.error("Failed to initialize bot on startup")

if __name__ == "__main__":
    # For local development with polling
    bot_app = init_bot()
    if bot_app:
        logger.info("🚀 Starting bot in polling mode for local development...")
        bot_app.run_polling()
