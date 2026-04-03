import os
import threading
from flask import Flask
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN
from handlers import *

# Telegram Bot
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("withdraws", check_withdraw))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))

app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

# Flask Web Server (Railway keep alive)
web = Flask(__name__)

@web.route('/')
def home():
    return "Bot is running!"

def run_web():
    port = int(os.environ.get("PORT", 8080))
    web.run(host="0.0.0.0", port=port)

# Run Flask in separate thread
threading.Thread(target=run_web).start()

print("🤖 Bot Started...")
app.run_polling()


print("Bot Started...")

async def start(update, context):
    print("Start command from:", update.effective_user.id)
    await update.message.reply_text("Bot working!")
