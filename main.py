from datetime import datetime, timedelta

cooldowns = {}async def lucky(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Anti-spam 3 secondes
    now = datetime.now()
    if user_id in cooldowns:
        if now - cooldowns[user_id] < timedelta(seconds=3):
            await update.message.reply_text("⏳ Attends 3 secondes avant de rejouer.")
            return

    cooldowns[user_id] = now

    user = get_user(user_id)

    if len(context.args) == 0:
        await update.message.reply_text("Utilisation: /lucky 1000")
        return

    try:
        bet = int(context.args[0])
    except:
        await update.message.reply_text("Mise invalide.")
        return

    if bet <= 0:
        await update.message.reply_text("Mise invalide.")
        return

    balance = user[1]

    if bet > balance:
        await update.message.reply_text("❌ Solde insuffisant.")
        return

    crash_point = round(random.uniform(1.1, 5.0), 2)
    player_multiplier = round(random.uniform(1.1, 5.0), 2)

    cursor.execute("UPDATE users SET games_played = games_played + 1 WHERE user_id=?", (user_id,))

    if player_multiplier < crash_point:
        win_amount = int(bet * player_multiplier)
        profit = win_amount - bet

        cursor.execute("""
            UPDATE users
            SET balance = balance + ?,
                total_won = total_won + ?
            WHERE user_id=?
        """, (profit, profit, user_id))

        result = (
            f"🚀 Lucky Jet\n"
            f"💥 Crash à x{crash_point}\n"
            f"🛫 Cashout à x{player_multiplier}\n\n"
            f"✅ Gain: {profit} FCFA"
        )
    else:
        cursor.execute("""
            UPDATE users
            SET balance = balance - ?,
                total_lost = total_lost + ?
            WHERE user_id=?
        """, (bet, bet, user_id))

        result = (
            f"🚀 Lucky Jet\n"
            f"💥 Crash à x{crash_point}\n"
            f"❌ Tu as perdu {bet} FCFA"
        )

    conn.commit()
    await update.message.reply_text(result)