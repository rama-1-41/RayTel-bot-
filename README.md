# 🤖 Android Telegram Bot

A fully-featured Telegram bot for controlling your Android device remotely.

## ✨ Features

- 📸 Screenshot Capture
- 📱 Device Info
- 🔋 Battery Status
- 🔊 Volume Control
- 📂 File Management
- 🔒 Secure Access

## 🚀 Quick Deploy

### Deploy to Railway
[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/telegram-bot-python)

## 📦 Requirements

- Python 3.8+
- Telegram Bot Token from @BotFather
- Termux (for Android features)

## 🔧 Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Create `.env` file with your bot token
4. Run: `python bot.py`

## 📚 Commands

| Command | Description |
|---------|-------------|
| `/start` | Show main menu |
| `/screenshot` | Take screenshot |
| `/device` | Show device info |
| `/battery` | Show battery status |
| `/volume up` | Increase volume |
| `/volume down` | Decrease volume |
| `/files` | List files |
| `/upload` | Upload file |

## 🛡️ Security

- Only authorized users can control the bot
- All commands are logged

## 📝 License

MIT License
