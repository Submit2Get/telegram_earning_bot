const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  userId: Number,
  username: String,
  balance: {
    type: Number,
    default: 0
  },
  createdAt: {
    type: Date,
    default: Date.now
  }
});

module.exports = mongoose.model('User', userSchema);