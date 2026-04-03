const mongoose = require('mongoose');

const withdrawalSchema = new mongoose.Schema({
  userId: Number,
  amount: Number,
  status: {
    type: String,
    default: "pending" // approved / rejected
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('Withdrawal', withdrawalSchema);