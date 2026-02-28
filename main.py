const TelegramBot = require('node-telegram-bot-api');

const token = "TON_TOKEN_ICI";
const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "🚀 Lucky Jet est actif !");
});

console.log("Bot lancé...");