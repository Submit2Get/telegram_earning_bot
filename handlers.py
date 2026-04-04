from telegram import *
from telegram.ext import *
from config import CHANNEL_USERNAME, ADMIN_ID
from database import *
import time

TASKS = {
    "1": {"name": "App Signup", "reward": 1, "link": "https://join.honeygain.com/SUBMI8997A"},
    "2": {"name": "YouTube Subscribe", "reward": 1, "link": "https://www.youtube.com/@Submit2Get"},
    "3": {"name": "Special Offer", "reward": 2, "link": "https://dm.1024terabox.com/referral/81365009834851"}
}

# START
async def start(update, context):
    user = update.effective_user.id
    ref = int(context.args[0]) if context.args else None
    add_user(user, ref)

    keyboard = [
        ["💰 Balance","👥 Refer"],
        ["🎁 Bonus","💸 Withdraw"],
        ["🎯 Task","📢 Channel"]
    ]

    await update.message.reply_text("Welcome 🚀", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# MESSAGE
async def message_handler(update, context):
    text = update.message.text
    user = update.effective_user.id

    if text == "💰 Balance":
        await update.message.reply_text(f"₹{get_balance(user):.2f}")

    elif text == "👥 Refer":
        link = f"https://t.me/{context.bot.username}?start={user}"
        await update.message.reply_text(f"🔗 {link}")

    elif text == "🎁 Bonus":
        last = get_last_bonus(user)
        now = int(time.time())

        if now - last >= 86400:
            add_balance(user, 0.15)
            update_bonus(user)
            await update.message.reply_text(f"✅ ₹0.15 Added\nBalance: ₹{get_balance(user):.2f}")
        else:
            await update.message.reply_text("❌ Already claimed today")

    elif text == "🎯 Task":
        buttons = []
        for tid, t in TASKS.items():
            buttons.append([
                InlineKeyboardButton(f"{t['name']} (₹{t['reward']})", url=t["link"]),
                InlineKeyboardButton("📤 Submit", callback_data=f"submit_{tid}")
            ])
        await update.message.reply_text("Complete task then submit screenshot", reply_markup=InlineKeyboardMarkup(buttons))

    elif text == "📢 Channel":
        await update.message.reply_text(f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")

    elif text == "💸 Withdraw":
        bal = get_balance(user)
        if bal < 200:
            await update.message.reply_text("❌ Minimum withdraw ₹200")
            return

        context.user_data["withdraw"] = True
        await update.message.reply_text("💳 Send UPI ID")

    elif "withdraw" in context.user_data:
        upi = text
        bal = get_balance(user)

        create_withdraw(user, bal, upi)

        await update.message.reply_text(f"✅ Request Sent\n₹{bal}\nUPI: {upi}")
        context.user_data.clear()

# BUTTON
async def button(update, context):
    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if q.data.startswith("submit_"):
        task_id = q.data.split("_")[1]
        context.user_data["task"] = task_id
        await q.message.reply_text("📸 Upload screenshot")

# PHOTO
async def photo_handler(update, context):
    user = update.effective_user.id

    if "task" not in context.user_data:
        return

    task_id = context.user_data["task"]
    file_id = update.message.photo[-1].file_id

    submit_task(user, task_id, file_id)
    await update.message.reply_text("✅ Submitted for review")

    context.user_data.clear()

# ADMIN TASK VIEW
async def admin_tasks(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    data = get_pending_tasks()

    for u, t, f, s in data:
        btn = [
            InlineKeyboardButton("Approve", callback_data=f"approve_{u}_{t}"),
            InlineKeyboardButton("Reject", callback_data=f"reject_{u}_{t}")
        ]

        await update.message.reply_photo(
            f,
            caption=f"User:{u} Task:{t}",
            reply_markup=InlineKeyboardMarkup([btn])
        )

# ADMIN ACTION
async def admin_button(update, context):
    q = update.callback_query
    await q.answer()

    action, user, task = q.data.split("_")
    reward = TASKS[task]["reward"]

    if action == "approve":
        approve_task(int(user), task, reward)
        await q.message.reply_text("✅ Approved")
    else:
        reject_task(int(user), task)
        await q.message.reply_text("❌ Rejected")

# STATS
async def stats(update, context):
    if update.effective_user.id != ADMIN_ID:
        return

    users = get_all_users()
    await update.message.reply_text(f"👥 Total Users: {len(users)}")