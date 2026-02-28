import logging
import threading
import random
import asyncio
from flask import Flask, Response
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# ==============================
# CONFIG
# ==============================

TOKEN = "8765706088:AAGJlo8ONNbJUNF8zPg4KKeiuWgZL5w0sCw
PORT = 8080

# ==============================
# FLASK WEB SERVER
# ==============================

app_web = Flask(__name__)

@app_web.route("/")
def index():
    return Response("""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Empire Ultra</title>
<style>
body {
    background: #0f0c29;
    font-family: Arial;
    text-align: center;
    color: white;
}
button {
    background: #7b2ff7;
    border: none;
    padding: 15px;
    margin: 10px;
    color: white;
    font-size: 18px;
    border-radius: 10px;
    box-shadow: 0 0 15px #7b2ff7;
}
button:hover {
    background: #9d4edd;
}
.grid {
    display:grid;
    grid-template-columns:repeat(5,60px);
    gap:5px;
    justify-content:center;
    margin-top:20px;
}
.cell {
    width:60px;
    height:60px;
    background:#222;
    border-radius:5px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:20px;
}
</style>
</head>
<body>

<h1>👑 EMPIRE ULTRA</h1>

<button onclick="startMines()">💣 Mines 5x5</button>
<button onclick="startLucky()">🚀 Lucky Jet</button>

<div id="game-area"></div>

<script>
function startMines() {
    let grid = "<div class='grid'>";
    for (let i = 0; i < 25; i++) {
        grid += `<div class="cell" onclick="clickCell(this)"></div>`;
    }
    grid += "</div>";
    document.getElementById("game-area").innerHTML = grid;
}

function clickCell(cell) {
    let chance = Math.random();
    if (chance < 0.2) {
        cell.style.background = "red";
        cell.innerHTML = "💥";
        alert("BOOM !");
    } else {
        cell.style.background = "green";
        cell.innerHTML = "💎";
    }
}

function startLucky() {
    let multiplier = 1.00;
    let area = document.getElementById("game-area");

    let interval = setInterval(() => {
        multiplier += 0.1;
        area.innerHTML = "<h2>🚀 x" + multiplier.toFixed(2) + "</h2>";

        if (Math.random() < 0.05) {
            clearInterval(interval);
            area.innerHTML += "<h3>💥 Crash !</h3>";
        }
    }, 200);
}
</script>

</body>
</html>
""", mimetype='text/html')

def run_web():
    app_web.run(host="0.0.0.0", port=PORT)

# ==============================
# TELEGRAM BOT
# ==============================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    webapp_url = f"https://{update.effective_message.chat.username}.up.railway.app"

    keyboard = [
        [InlineKeyboardButton(
            "🎮 Ouvrir Empire WebApp",
            web_app=WebAppInfo(url=webapp_url)
        )]
    ]

    await update.message.reply_text(
        "👑 EMPIRE ULTRA PRO MAX\nClique pour ouvrir l’interface WebApp",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    threading.Thread(target=run_web).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()