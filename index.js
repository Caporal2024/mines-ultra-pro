const TelegramBot = require('node-telegram-bot-api');

const token = 'TON_NOUVEAU_TOKEN_ICI';

const bot = new TelegramBot(token, { polling: true });

bot.onText(/\/start/, (msg) => {
    bot.sendMessage(msg.chat.id, "💣 Bienvenue sur Mines 5x5 Pro !");
});

bot.onText(/\/mines/, (msg) => {
    let grid = "";
    for (let i = 0; i < 5; i++) {
        grid += "🟦 🟦 🟦 🟦 🟦\n";
    }
    bot.sendMessage(msg.chat.id, "🎮 Grille Mines 5x5 :\n\n" + grid);
});

console.log("✅ Bot lancé..."); Your token was replaced with a new one. You can use this token to access HTTP API:
8765706088:AAEbJZpFSvPfOqzqdVOVmXlzcnpUoLBtMLI
