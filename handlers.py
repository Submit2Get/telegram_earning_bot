from telegram import *
from telegram.ext import *
from config import CHANNEL_USERNAME, ADMIN_ID
from database import *
import time

# ===== TASK CONFIG =====
TASKS = {
    "1": {"name": "App Signup", "reward": 2, "link": "https://join.honeygain.com/SUBMI8997A"},
    "2": {"name": "YouTube Subscribe", "reward": 2, "link": "https://www.youtube.com/@Submit2Get"},
    "3": {"name": "Special Task", "reward": 3, "link": "https://dm.1024terabox.com/referral/81365009834851"}
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
    user = update.effective_user.id

    ref = None
    if context.args:
        ref = int(context.args[0])

    add_user(user, ref)

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

    # ===== BALANCE =====
    if text == "💰 Balance":
        bal = get_balance(user)
        await update.message.reply_text(f"💰 Your Balance: ₹{bal:.2f}")

    # ===== REFER =====
    elif text == "👥 Refer":
        link = f"https://t.me/{context.bot.username}?start={user}"
        await update.message.reply_text(f"🔗 {link}")

    # ===== BONUS FIX =====
    elif text == "🎁 Bonus":
        last = get_last_bonus(user)
        now = int(time.time())

        if now - last >= 86400:
            add_balance(user, 0.20)   # ₹0.20 bonus
            update_bonus(user)

            new_bal = get_balance(user)

            await update.message.reply_text(
                f"✅ Bonus Added ₹0.20\n💰 New Balance: ₹{new_bal:.2f}"
            )
        else:
            remain = 86400 - (now - last)
            hours = remain // 3600
            await update.message.reply_text(f"❌ Try after {hours} hours")

    # ===== TASK =====
    elif text == "🎯 Task":

        buttons = []
        for tid, t in TASKS.items():
            buttons.append([
                InlineKeyboardButton(f"{t['name']} (₹{t['reward']})", url=t["link"]),
                InlineKeyboardButton("✅ Claim", callback_data=f"claim_{tid}")
            ])

        await update.message.reply_text(
            "🎯 Complete task & claim:",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    # ===== CHANNEL =====
    elif text == "📢 Channel":
        await update.message.reply_text(f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")

# ===== BUTTON =====
async def button(update, context):
    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if q.data.startswith("claim_"):
        task_id = q.data.split("_")[1]

        if is_task_done(user, task_id):
            await q.message.reply_text("❌ Already claimed")
            return

        reward = TASKS[task_id]["reward"]

        add_balance(user, reward)
        complete_task(user, task_id)

        new_bal = get_balance(user)

        await q.message.reply_text(
            f"✅ Task Completed!\n₹{reward} Added\n💰 Balance: ₹{new_bal:.2f}"
        )