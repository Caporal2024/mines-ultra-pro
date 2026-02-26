require("dotenv").config();
const TelegramBot = require("node-telegram-bot-api");

const token = process.env.BOT_TOKEN;

const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
  bot.sendMessage(msg.chat.id, "🚀 Bot Mines 5x5 Pro activé !");
});

bot.onText(/\/mines/, (msg) => {
  let grid = "";
  for (let i = 0; i < 5; i++) {
    grid += "🟦 🟦 🟦 🟦 🟦\n";
  }
  bot.sendMessage(msg.chat.id, "🎮 Grille Mines 5x5 :\n\n" + grid);
});

console.log("✅ Bot lancé...");