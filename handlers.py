from telegram import *
from telegram.ext import *
from config import CHANNEL_USERNAME, ADMIN_ID
from database import *
import time

# ===== TASK CONFIG =====
TASKS = {
    "1": {"name": "App Signup", "reward": 2, "link": "https://join.honeygain.com/SUBMI8997A"},
    "2": {"name": "YouTube Subscribe", "reward": 2, "link": "https://www.youtube.com/@Submit2Get"},
    "3": {"name": "Special Offer", "reward": 3, "link": "https://dm.1024terabox.com/referral/81365009834851"}
}

# ===== USER AUTO CREATE =====
def ensure_user(user_id, ref=None):
    add_user(user_id, ref)

# ===== CHECK JOIN =====
async def check_join(update, context):
    try:
        member = await context.bot.get_chat_member(CHANNEL_USERNAME, update.effective_user.id)
        return member.status in ["member", "administrator", "creator"]
    except:
        return False

# ===== START =====
async def start(update, context):
    user = update.effective_user.id

    ref = None
    if context.args:
        try:
            ref = int(context.args[0])
        except:
            ref = None

    ensure_user(user, ref)

    # JOIN FORCE
    if not await check_join(update, context):
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")],
            [InlineKeyboardButton("✅ Joined", callback_data="check_join")]
        ]

        await update.message.reply_text(
            "🚫 আগে চ্যানেলে জয়েন করুন!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
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

# ===== MESSAGE HANDLER =====
async def message_handler(update, context):
    user = update.effective_user.id
    text = update.message.text

    ensure_user(user)

    # FORCE JOIN CHECK EVERY TIME
    if not await check_join(update, context):
        await update.message.reply_text("⚠️ আগে চ্যানেল জয়েন করুন!")
        return

    # ===== BALANCE =====
    if text == "💰 Balance":
        bal = get_balance(user)
        await update.message.reply_text(f"💰 Balance: ₹{bal:.1f}")

    # ===== REFER =====
    elif text == "👥 Refer":
        link = f"https://t.me/{context.bot.username}?start={user}"
        await update.message.reply_text(f"🔗 Referral Link:\n{link}")

    # ===== BONUS (FULL FIX) =====
    elif text == "🎁 Bonus":
        last = get_last_bonus(user) or 0
        now = int(time.time())

        if now - last >= 86400:
            add_balance(user, 0.15)
            update_bonus(user)

            new_bal = get_balance(user)

            await update.message.reply_text(
                f"✅ Bonus Added ₹0.15\n💰 Updated Balance: ₹{new_bal:.1f}"
            )
        else:
            remain = 86400 - (now - last)
            hours = remain // 3600
            minutes = (remain % 3600) // 60

            await update.message.reply_text(
                f"⏳ Try after {hours}h {minutes}m"
            )

    # ===== TASK SYSTEM (UPGRADED UI) =====
    elif text == "🎯 Task":

        keyboard = []
        for tid, t in TASKS.items():
            keyboard.append([
                InlineKeyboardButton(f"🔗 {t['name']}", url=t["link"]),
                InlineKeyboardButton(f"✅ Claim ₹{t['reward']}", callback_data=f"claim_{tid}")
            ])

        await update.message.reply_text(
            "🎯 Complete tasks then click CLAIM:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== CHANNEL =====
    elif text == "📢 Channel":
        await update.message.reply_text(f"https://t.me/{CHANNEL_USERNAME.replace('@','')}")

# ===== BUTTON HANDLER =====
async def button(update, context):
    query = update.callback_query
    await query.answer()

    user = query.from_user.id

    # JOIN VERIFY BUTTON
    if query.data == "check_join":
        if await check_join(update, context):
            await query.message.reply_text("✅ Verified! Now use bot menu")
        else:
            await query.message.reply_text("❌ এখনও জয়েন করেননি!")

    # TASK CLAIM
    elif query.data.startswith("claim_"):
        task_id = query.data.split("_")[1]

        if is_task_done(user, task_id):
            await query.message.reply_text("❌ Already claimed this task")
            return

        reward = TASKS[task_id]["reward"]

        add_balance(user, reward)
        complete_task(user, task_id)

        new_bal = get_balance(user)

        await query.message.reply_text(
            f"🎉 Task Completed!\n💸 Earned: ₹{reward}\n💰 Balance: ₹{new_bal:.2f}"
        )