import random
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# ================= MENU =================

async def start(update, context):
    keyboard = [
        [InlineKeyboardButton("💣 Mines", callback_data="mines")],
        [InlineKeyboardButton("⚽ Penalty", callback_data="penalty")],
        [InlineKeyboardButton("🔥 Cross Fire Chicken", callback_data="crossfire")],
        [InlineKeyboardButton("🎲 Play Me", callback_data="playme")],
    ]

    await update.message.reply_text(
        "🎮 MULTI GAME SIMULATION\n\nChoisis ton jeu :",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= MINES =================

async def mines_game(query):
    mine_position = random.randint(1, 5)
    choice = random.randint(1, 5)

    if choice == mine_position:
        return "💥 Mine touchée !"
    else:
        return "✅ Safe !"

# ================= PENALTY =================

async def penalty_game(query):
    goalkeeper = random.choice(["gauche", "centre", "droite"])
    player = random.choice(["gauche", "centre", "droite"])

    if player == goalkeeper:
        return "🧤 Arrêt du gardien !"
    else:
        return "⚽ BUT !!!"

# ================= CROSS FIRE =================

async def crossfire_game(query):
    hit = random.random()

    if hit > 0.7:
        return "🔥 X5 gagné !"
    elif hit > 0.4:
        return "🎯 Petit gain"
    else:
        return "💣 Perdu"

# ================= PLAY ME =================

async def playme_game(query):
    result = random.randint(1, 10)

    if result == 10:
        return "💎 JACKPOT X5000"
    elif result > 7:
        return "✨ Gagné"
    else:
        return "❌ Perdu"cursor.execute("""
ALTER TABLE users ADD COLUMN coins INTEGER DEFAULT 1000
""")

cursor.execute("""
ALTER TABLE users ADD COLUMN tournament_points INTEGER DEFAULT 0
""")
conn.commit()elif query.data == "tournament":

    cursor.execute("SELECT coins FROM users WHERE user_id=?", (user_id,))
    coins = cursor.fetchone()[0]

    if coins < 100:
        await query.edit_message_text("❌ Pas assez de pièces.")
        return

    cursor.execute("""
        UPDATE users
        SET coins = coins - 100,
            tournament_points = tournament_points + 50
        WHERE user_id=?
    """, (user_id,))
    conn.commit()

    await query.edit_message_text(
        "🏆 Tu as rejoint le tournoi !\n"
        "🔥 +50 points tournoi"
    )elif query.data == "tournament_live":

    cursor.execute("""
        SELECT user_id, tournament_points, vip
        FROM users
        ORDER BY tournament_points DESC
        LIMIT 10
    """)

    players = cursor.fetchall()

    if not players:
        await query.edit_message_text("📊 Aucun joueur pour le moment.")
        return

    medals = ["🥇", "🥈", "🥉"]

    message = "🏆 CLASSEMENT TOURNOI LIVE 🏆\n\n"

    for i, (uid, points, vip) in enumerate(players):
        medal = medals[i] if i < 3 else "⭐"
        badge = " 👑" if vip == 1 else ""
        message += f"{medal} {uid} — {points} pts{badge}\n"

    await query.edit_message_text(message)🏆 CLASSEMENT TOURNOI LIVE 🏆

🥇 8094967191 — 350 pts 👑
🥈 123456789 — 280 pts
🥉 567891234 — 240 pts
⭐ 987654321 — 150 pts async def refresh_tournament_live(context):

job_data = context.job.data
    chat_id = job_data["chat_id"]
    message_id = job_data["message_id"]

    cursor.execute("""
        SELECT user_id, tournament_points, vip
        FROM users
        ORDER BY tournament_points DESC
        LIMIT 10
    """)

    players = cursor.fetchall()

    medals = ["🥇", "🥈", "🥉"]
    message = "🏆 CLASSEMENT TOURNOI LIVE 🏆\n\n"

    for i, (uid, points, vip) in enumerate(players):
        medal = medals[i] if i < 3 else "⭐"
        badge = " 👑" if vip == 1 else ""
        message += f"{medal} {uid} — {points} pts{badge}\n"

    try:
        await context.bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=message
        )
    except:
        pass