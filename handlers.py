from telegram import *
from telegram.ext import *
from config import CHANNEL_USERNAME, ADMIN_ID
from database import *
import time

TASKS = {
    "1": {"name": "Join Channel", "reward": 1},
    "2": {"name": "Watch Video", "reward": 2},
    "3": {"name": "Signup Website", "reward": 3},
}

# ===== CHECK JOIN =====
async def check_join(update, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, update.effective_user.id)
        return member.status in ["member","administrator","creator"]
    except:
        return False

# ===== START =====
async def start(update, context):
    user_id = update.effective_user.id

    ref = None
    if context.args:
        ref = int(context.args[0])

    add_user(user_id, ref)

    if not await check_join(update, context):
        btn = [
            [InlineKeyboardButton("Join", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("Check", callback_data="check")]
        ]
        await update.message.reply_text("Join first!", reply_markup=InlineKeyboardMarkup(btn))
        return

    keyboard = [
        ["💰 Balance","👥 Refer"],
        ["🎁 Bonus","💸 Withdraw"],
        ["🎯 Task","📢 Channel"]
    ]

    await update.message.reply_text("Welcome 🚀", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ===== MESSAGE =====
async def message_handler(update, context):
    text = update.message.text
    user = update.effective_user.id

    if text == "💰 Balance":
        await update.message.reply_text(f"₹{get_balance(user)}")

    elif text == "👥 Refer":
        link = f"https://t.me/{context.bot.username}?start={user}"
        await update.message.reply_text(link)

    elif text == "🎁 Bonus":
        last = get_last_bonus(user)
        now = int(time.time())

        if now - last >= 86400:
            add_balance(user, 0.10)
            update_bonus(user)
            await update.message.reply_text("Bonus added ₹0.10")
        else:
            await update.message.reply_text("Already claimed!")

    elif text == "🎯 Task":
        btn = [
            [InlineKeyboardButton("Task 1", callback_data="task_1")],
            [InlineKeyboardButton("Task 2", callback_data="task_2")],
            [InlineKeyboardButton("Task 3", callback_data="task_3")]
        ]
        await update.message.reply_text("Choose task", reply_markup=InlineKeyboardMarkup(btn))

    elif text == "💸 Withdraw":
        context.user_data["withdraw"] = True
        await update.message.reply_text("Send UPI ID")

    elif "withdraw" in context.user_data:
        upi = text
        bal = get_balance(user)

        if bal < 100:
            await update.message.reply_text("Minimum ₹100")
        else:
            create_withdraw(user, bal, upi)
            await update.message.reply_text("Request sent")

        context.user_data.clear()

# ===== BUTTON =====
async def button(update, context):
    q = update.callback_query
    await q.answer()

    if q.data.startswith("task_"):
        task_id = q.data.split("_")[1]
        context.user_data["task"] = task_id
        await q.message.reply_text("Send screenshot")

# ===== SCREENSHOT =====
async def photo_handler(update, context):
    user = update.effective_user.id

    if "task" not in context.user_data:
        return

    task_id = context.user_data["task"]
    file_id = update.message.photo[-1].file_id

    submit_task(user, task_id, file_id)
    await update.message.reply_text("Submitted for review")

    context.user_data.clear()

# ===== ADMIN =====
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

async def admin_button(update, context):
    q = update.callback_query
    await q.answer()

    data = q.data.split("_")
    action, user, task = data

    reward = TASKS[task]["reward"]

    if action == "approve":
        approve_task(int(user), task, reward)
        await q.message.reply_text("Approved")

    else:
        reject_task(int(user), task)
        await q.message.reply_text("Rejected")