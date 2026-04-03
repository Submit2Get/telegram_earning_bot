from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from config import CHANNEL_USERNAME, ADMIN_ID
from database import *
import time


async def check_join(update, context):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    referrer = None
    if context.args:
        try:
            referrer = int(context.args[0])
        except:
            pass

    add_user(user_id, referrer)

    if not await check_join(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("✅ Joined", callback_data="check_join")]
        ]
        await update.message.reply_text("🚫 Join channel first!", reply_markup=InlineKeyboardMarkup(keyboard))
        return

    keyboard = [
        ["💰 Balance", "👥 Refer"],
        ["🎁 Bonus", "💸 Withdraw"],
        ["🎯 Task", "📢 Channel"]
    ]
    await update.message.reply_text(
        "✅ Welcome to Earning Bot 🚀",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "check_join":
        if await check_join(update, context):
            keyboard = [
                ["💰 Balance", "👥 Refer"],
                ["🎁 Bonus", "💸 Withdraw"],
                ["🎯 Task", "📢 Channel"]
            ]
            await query.message.reply_text(
                "✅ Verified!",
                reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
            )
        else:
            await query.message.reply_text("❌ Join not completed!")


async def message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id

    if not await check_join(update, context):
        await update.message.reply_text("⚠️ First channel join now!")
        return

    if text == "💰 Balance":
        balance = get_balance(user_id)
        await update.message.reply_text(f"💰 Balance: ₹{balance:.2f}")

    elif text == "👥 Refer":
        link = f"https://t.me/{context.bot.username}?start={user_id}"
        await update.message.reply_text(f"🔗 Referral link:\n{link}")

    elif text == "🎁 Bonus":
        last = get_last_bonus(user_id)
        now = int(time.time())

        if now - last >= 86400:
            add_balance(user_id, 0.10)
            update_bonus(user_id)
            await update.message.reply_text("✅ Daily Bonus ₹0.10 added")
        else:
            await update.message.reply_text("❌ Already claimed today!")

    elif text == "💸 Withdraw":
        balance = get_balance(user_id)

        if balance < 100:
            await update.message.reply_text("❌ Minimum withdraw = ₹100")
        else:
            create_withdraw(user_id, balance)
            await update.message.reply_text("✅ Withdraw request sent!")

    elif text == "🎯 Task":
        await update.message.reply_text(
            "🎯 Tasks:\n\n"
            "1. Daily Bonus → ₹0.10\n"
            "2. Refer Friend → ₹1\n"
            "3. Join Channel → Reward\n\n"
            "Keep earning 💰"
        )

    elif text == "📢 Channel":
        await update.message.reply_text(f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    message = " ".join(context.args)
    users = get_all_users()

    for user in users:
        try:
            await context.bot.send_message(user[0], message)
        except:
            pass

    await update.message.reply_text("✅ Broadcast sent")


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    users = get_all_users()
    await update.message.reply_text(f"👥 Total users: {len(users)}")


async def check_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    cursor.execute("SELECT * FROM withdraws WHERE status='pending'")
    data = cursor.fetchall()

    if not data:
        await update.message.reply_text("No pending requests")
        return

    msg = ""
    for row in data:
        msg += f"User: {row[0]} | Amount: ₹{row[1]}\n"

    await update.message.reply_text(msg)


async def approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    cursor.execute("UPDATE withdraws SET status='approved' WHERE user_id=?", (user_id,))
    cursor.execute("UPDATE users SET balance=0 WHERE user_id=?", (user_id,))
    cursor.connection.commit()

    await update.message.reply_text(f"✅ Approved {user_id}")


async def reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    user_id = int(context.args[0])

    cursor.execute("UPDATE withdraws SET status='rejected' WHERE user_id=?", (user_id,))
    cursor.connection.commit()

    await update.message.reply_text(f"❌ Rejected {user_id}")
