import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration"""
    
    # Bot token from @BotFather
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    
    # Your Telegram user ID (only you can control)
    ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")
    
    # Debug mode
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Heroku app name
    HEROKU_APP_NAME = os.getenv("HEROKU_APP_NAME", "")
    
    # Validate configuration
    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is not set!")
        if not cls.ADMIN_CHAT_ID:
            raise ValueError("ADMIN_CHAT_ID is not set!")
        return True
