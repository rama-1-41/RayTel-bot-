import os
import subprocess
import logging
from telegram import Update
from telegram.ext import ContextTypes
from handlers.basic import is_authorized

logger = logging.getLogger(__name__)

def get_device_info() -> dict:
    info = {}
    
    try:
        result = subprocess.run(["getprop", "ro.build.version.release"], capture_output=True, text=True, timeout=5)
        info["android_version"] = result.stdout.strip() or "Unknown"
    except:
        info["android_version"] = "Unknown"
    
    try:
        result = subprocess.run(["getprop", "ro.product.model"], capture_output=True, text=True, timeout=5)
        info["model"] = result.stdout.strip() or "Unknown"
    except:
        info["model"] = "Unknown"
    
    try:
        result = subprocess.run(["getprop", "ro.product.manufacturer"], capture_output=True, text=True, timeout=5)
        info["manufacturer"] = result.stdout.strip() or "Unknown"
    except:
        info["manufacturer"] = "Unknown"
    
    try:
        result = subprocess.run(["dumpsys", "battery"], capture_output=True, text=True, timeout=5)
        for line in result.stdout.split("\n"):
            if "level:" in line:
                info["battery"] = line.split(":")[1].strip()
                break
    except:
        info["battery"] = "Unknown"
    
    return info

async def device_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    await update.message.reply_text("📱 Getting device info...")
    info = get_device_info()
    
    text = "📱 **Device Information**\n\n"
    text += f"📌 **Model:** {info.get(model, Unknown)}\n"
    text += f"🏷️ **Manufacturer:** {info.get(manufacturer, Unknown)}\n"
    text += f"🤖 **Android:** {info.get(android_version, Unknown)}\n"
    text += f"🔋 **Battery:** {info.get(battery, Unknown)}%"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def battery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    try:
        result = subprocess.run(["dumpsys", "battery"], capture_output=True, text=True, timeout=5)
    except:
        await update.message.reply_text("❌ Failed to get battery info")
        return
    
    battery_info = {}
    for line in result.stdout.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            battery_info[key.strip()] = value.strip()
    
    status_map = {"1": "🔌 Charging (AC)", "2": "🔌 Charging (USB)", "3": "🔋 Discharging", "4": "⛔ Not charging", "5": "⚡ Full"}
    
    text = "🔋 **Battery Status**\n\n"
    text += f"**Level:** {battery_info.get(level, Unknown)}%\n"
    text += f"**Status:** {status_map.get(battery_info.get(status), Unknown)}\n"
    text += f"**Health:** {battery_info.get(health, Unknown)}\n"
    
    if "temperature" in battery_info:
        temp = int(battery_info["temperature"]) / 10
        text += f"**Temperature:** {temp:.1f}°C\n"
    
    if "voltage" in battery_info:
        voltage = int(battery_info["voltage"]) / 1000
        text += f"**Voltage:** {voltage:.2f}V"
    
    await update.message.reply_text(text, parse_mode="Markdown")

async def volume(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    args = context.args
    
    if not args:
        await update.message.reply_text("🔊 **Volume Control**\n\nUsage:\n/volume up - Increase\n/volume down - Decrease\n/volume mute - Mute\n/volume max - Maximum", parse_mode="Markdown")
        return
    
    command = args[0].lower()
    key_events = {"up": "24", "down": "25", "mute": "164", "max": "24"}
    
    if command in key_events:
        key = key_events[command]
        presses = 15 if command == "max" else 1
        
        for _ in range(presses):
            subprocess.run(["input", "keyevent", key], capture_output=True)
        
        messages = {"up": "🔊 Volume increased", "down": "🔉 Volume decreased", "mute": "🔇 Volume muted", "max": "🔊 Volume set to maximum"}
        await update.message.reply_text(messages.get(command, "✅ Done"))
    else:
        await update.message.reply_text(f"❌ Unknown command: {command}")

async def files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    path = "/sdcard"
    if context.args:
        new_path = " ".join(context.args)
        path = new_path if new_path.startswith("/") else f"/sdcard/{new_path}"
    
    try:
        result = subprocess.run(["ls", "-la", path], capture_output=True, text=True, timeout=10)
    except:
        await update.message.reply_text(f"❌ Failed to list directory: {path}")
        return
    
    if result.returncode != 0:
        await update.message.reply_text(f"❌ Failed to list directory: {path}")
        return
    
    lines = result.stdout.split("\n")
    if len(lines) > 30:
        lines = lines[:30]
        lines.append("... (truncated)")
    
    file_list = f"📂 **Files in {path}**\n\n```\n" + "\n".join(lines) + "\n```"
    
    try:
        await update.message.reply_text(file_list, parse_mode="Markdown")
    except Exception:
        temp_file = "/sdcard/files_list.txt"
        with open(temp_file, "w") as f:
            f.write("\n".join(lines))
        await update.message.reply_document(document=open(temp_file, "rb"), caption=f"📂 Files in {path}")
        os.remove(temp_file)

async def upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_authorized(update):
        await update.message.reply_text("⛔ Unauthorized access!")
        return
    
    if not context.args:
        await update.message.reply_text("📤 **Upload File**\n\nUsage: /upload /path/to/file\nExample: /upload /sdcard/example.jpg", parse_mode="Markdown")
        return
    
    file_path = " ".join(context.args)
    
    if not os.path.exists(file_path):
        await update.message.reply_text(f"❌ File not found: {file_path}")
        return
    
    try:
        await update.message.reply_text(f"📤 Uploading: {os.path.basename(file_path)}")
        with open(file_path, "rb") as f:
            await update.message.reply_document(document=f, caption=f"📎 {os.path.basename(file_path)}")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")
