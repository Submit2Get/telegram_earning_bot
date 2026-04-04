import os
from telegram import *
from telegram.ext import *
from database import *
from dotenv import load_dotenv
import random, time

load_dotenv()
ADMIN_ID = int(os.getenv("ADMIN_ID"))

TASKS = {
    "1": {"name": "App Install", "points": 40, "link": "https://join.honeygain.com/SUBMI8997A"},
    "2": {"name": "Signup Offer", "points": 60, "link": "https://dm.1024terabox.com/referral/81365009834851"},
    "3": {"name": "Survey Task", "points": 80, "link": "https://www.youtube.com/@Submit2Get"}
}

# START
async def start(update, context):
    user = update.effective_user.id
    add_user(user)

    total = get_total_users()
    active = int(total * random.uniform(0.75, 0.9))

    text = f"🚀 Welcome\n🔥 {active}+ active users"

    keyboard = [
        ["💰 Balance","👥 Refer"],
        ["🎯 Tasks","🎁 Bonus"],
        ["📊 Stats","💸 Withdraw"]
    ]

    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# MESSAGE
async def message_handler(update, context):
    user = update.effective_user.id
    text = update.message.text

    if text == "💰 Balance":
        await update.message.reply_text(f"💰 {get_points(user)} pts")

    elif text == "🎯 Tasks":
        buttons = []
        for tid,t in TASKS.items():
            buttons.append([
                InlineKeyboardButton(f"{t['name']} (+{t['points']} pts)", url=t['link']),
                InlineKeyboardButton("Done", callback_data=f"done_{tid}")
            ])
        await update.message.reply_text("Complete task", reply_markup=InlineKeyboardMarkup(buttons))

    elif text == "🎁 Bonus":
        if can_claim_bonus(user):
            add_points(user, 10)
            update_bonus(user)
            await update.message.reply_text("+10 pts")
        else:
            await update.message.reply_text("Already claimed")

    elif text == "📊 Stats":
        total = get_total_users()
        paid = random.randint(500,1500)
        await update.message.reply_text(f"Users: {total}\nPaid: ₹{paid}")

    elif text == "💸 Withdraw":
        if get_points(user) < 100:
            await update.message.reply_text("Minimum 100 pts")
            return
        context.user_data['withdraw'] = True
        await update.message.reply_text("Send UPI / PayPal")

    elif "withdraw" in context.user_data:
    create_withdraw(user, get_points(user), text)
    reset_points(user)
    await update.message.reply_text("Request sent")
    context.user_data.clear()