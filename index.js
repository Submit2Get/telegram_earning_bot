require('dotenv').config();
const TelegramBot = require('node-telegram-bot-api');
const connectDB = require('./db');
const User = require('./models/User');
const Withdrawal = require('./models/Withdrawal');

connectDB();

const bot = new TelegramBot(process.env.BOT_TOKEN, { polling: true });
const ADMIN_ID = Number(process.env.ADMIN_ID);

// User start
bot.onText(/\/start/, async (msg) => {
  const userId = msg.from.id;

  let user = await User.findOne({ userId });

  if (!user) {
    user = new User({
      userId,
      username: msg.from.username
    });
    await user.save();
  }

  bot.sendMessage(msg.chat.id, "Welcome! Your account is ready.");
});

// Balance check
bot.onText(/\/balance/, async (msg) => {
  const user = await User.findOne({ userId: msg.from.id });

  bot.sendMessage(msg.chat.id, `💰 Balance: ₹${user.balance}`);
});

// Withdraw request
bot.onText(/\/withdraw (.+)/, async (msg, match) => {
  const amount = Number(match[1]);

  if (!amount || amount <= 0) {
    return bot.sendMessage(msg.chat.id, "Invalid amount");
  }

  const withdrawal = new Withdrawal({
    userId: msg.from.id,
    amount
  });

  await withdrawal.save();

  bot.sendMessage(msg.chat.id, "Withdraw request sent!");

  // Notify admin
  bot.sendMessage(
    ADMIN_ID,
    `💸 Withdraw Request\nUser: ${msg.from.id}\nAmount: ₹${amount}`
  );
});

// Admin panel
bot.onText(/\/admin/, async (msg) => {
  if (msg.from.id !== ADMIN_ID) return;

  const users = await User.find();
  const withdrawals = await Withdrawal.find({ status: "pending" });

  bot.sendMessage(
    msg.chat.id,
    `👤 Total Users: ${users.length}\n💸 Pending Withdraws: ${withdrawals.length}`
  );
});

// Approve withdraw
bot.onText(/\/approve (.+)/, async (msg, match) => {
  if (msg.from.id !== ADMIN_ID) return;

  const id = match[1];
  const withdraw = await Withdrawal.findById(id);

  if (!withdraw) return;

  withdraw.status = "approved";
  await withdraw.save();

  bot.sendMessage(msg.chat.id, "Withdraw Approved");
});

// Reject withdraw
bot.onText(/\/reject (.+)/, async (msg, match) => {
  if (msg.from.id !== ADMIN_ID) return;

  const id = match[1];
  const withdraw = await Withdrawal.findById(id);

  if (!withdraw) return;

  withdraw.status = "rejected";
  await withdraw.save();

  bot.sendMessage(msg.chat.id, "Withdraw Rejected");
});

// Error handling
bot.on("polling_error", console.log);