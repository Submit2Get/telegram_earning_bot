from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from config import TOKEN
from handlers import *

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("broadcast", broadcast))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("withdraws", check_withdraw))
app.add_handler(CommandHandler("approve", approve))
app.add_handler(CommandHandler("reject", reject))

app.add_handler(CallbackQueryHandler(button_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

print("🤖 Bot running...")
app.run_polling()
