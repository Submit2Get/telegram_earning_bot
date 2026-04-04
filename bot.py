from telegram.ext import *
from handlers import *
from config import TOKEN

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admintasks", admin_tasks))

app.add_handler(CallbackQueryHandler(admin_button, pattern="approve|reject"))
app.add_handler(CallbackQueryHandler(button))

app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message_handler))

print("Bot Running...")
app.run_polling()