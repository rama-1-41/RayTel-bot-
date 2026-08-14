#!/bin/bash
echo "🚀 Deploying Android Telegram Bot..."
if [ ! -f .env ]; then
    echo "❌ .env file not found!"
    echo "Please create .env file with BOT_TOKEN and ADMIN_CHAT_ID"
    exit 1
fi
echo "📦 Installing dependencies..."
pip install -r requirements.txt
echo "🤖 Starting bot..."
python bot.py
