from telegram import *
from telegram.ext import *
from database import *
import random, time

# =============================
# GLOBAL POINT SYSTEM
# =============================
# Base: 1000 pts = ₹80 (India)
POINT_RATE = 1000
INR_VALUE = 90

CURRENCY = {
    "IN": ("₹", 90),
    "US": ("$", 1),
    "BD": ("৳", 120),
    "PK": ("₨", 270)
}

# =============================
# CPA TASKS (LOW COST HIGH PROFIT)
# =============================
TASKS = {
    "1": {"name": "App Install", "points": 40, "link": "YOUR_CPA_LINK"},
    "2": {"name": "Signup Offer", "points": 60, "link": "YOUR_CPA_LINK"},
    "3": {"name": "Survey Task", "points": 80, "link": "YOUR_CPA_LINK"}
}

# Detect country (simple fallback)
def get_country(user_id):
    # Later upgrade with API
    return "IN"

# Convert points → local currency

def convert(points, country):
    symbol, rate = CURRENCY.get(country, ("₹", 80))
    value = (points / POINT_RATE) * rate
    return symbol, value

# ---------- START ----------
async def start(update, context):
    user = update.effective_user.id
    add_user(user)

    total = get_total_users()
    active = int(total * random.uniform(0.75, 0.92))

    text = f"""
🚀 Welcome to Global Earn Bot
🔥 {active}+ users active this month

Earn points & convert to real money 💰
"""

    keyboard = [
        ["💰 Balance","👥 Refer"],
        ["🎯 Tasks","🎁 Bonus"],
        ["📊 Stats","💸 Withdraw"]
    ]

    await update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

# ---------- MESSAGE ----------
async def message_handler(update, context):
    user = update.effective_user.id
    text = update.message.text
    country = get_country(user)

    if text == "💰 Balance":
        pts = get_points(user)
        symbol, money = convert(pts, country)
        await update.message.reply_text(f"💰 {pts} pts (~{symbol}{money:.2f})")

    elif text == "👥 Refer":
        link = f"https://t.me/{context.bot.username}?start={user}"
        await update.message.reply_text(f"🔗 {link}\nEarn 10% commission")

    elif text == "🎁 Bonus":
        if can_claim_bonus(user):
            pts = random.randint(5,15)
            add_points(user, pts)
            update_bonus(user)
            await update.message.reply_text(f"🎉 +{pts} pts added")
        else:
            await update.message.reply_text("❌ Already claimed today")

    elif text == "🎯 Tasks":
        buttons = []
        for tid,t in TASKS.items():
            buttons.append([
                InlineKeyboardButton(f"{t['name']} (+{t['points']} pts)", url=t['link']),
                InlineKeyboardButton("✅ Done", callback_data=f"done_{tid}")
            ])
        await update.message.reply_text("Complete task & click done", reply_markup=InlineKeyboardMarkup(buttons))

    elif text == "📊 Stats":
        total = get_total_users()
        paid = random.randint(500,2000)
        await update.message.reply_text(f"👥 Total Users: {total}\n💸 Paid Today: ₹{paid}")

    elif text == "💸 Withdraw":
        pts = get_points(user)
        if pts < 100:
            await update.message.reply_text("❌ Minimum 100 pts")
            return
        context.user_data['withdraw'] = True
        await update.message.reply_text("Send UPI / PayPal Email")

    elif "withdraw" in context.user_data:
        create_withdraw(user, get_points(user), text)
        reset_points(user)
        await update.message.reply_text("✅ Withdraw request sent")
        context.user_data.clear()

# ---------- BUTTON ----------
async def button(update, context):
    q = update.callback_query
    await q.answer()

    user = q.from_user.id

    if q.data.startswith("done_"):
        tid = q.data.split("_")[1]
        pts = TASKS[tid]['points']
        add_points(user, pts)

        # Live activity
        activity = f"User {user} earned {pts} pts"
        save_activity(activity)

        await q.message.reply_text(f"🎉 +{pts} pts added")

# ---------- STATS ----------
async def stats(update, context):
    total = get_total_users()
    await update.message.reply_text(f"Users: {total}")