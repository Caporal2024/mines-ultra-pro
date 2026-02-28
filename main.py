# ==============================
# 🎮 MINES 5x5
# ==============================

MINES_COUNT = 5
GRID_SIZE = 5

def generate_mines():
    positions = list(range(GRID_SIZE * GRID_SIZE))
    return random.sample(positions, MINES_COUNT)

def build_mines_keyboard(revealed):
    keyboard = []
    for i in range(GRID_SIZE):
        row = []
        for j in range(GRID_SIZE):
            index = i * GRID_SIZE + j
            if index in revealed:
                row.append(InlineKeyboardButton("💎", callback_data="ignore"))
            else:
                row.append(InlineKeyboardButton("⬜", callback_data=f"cell_{index}"))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton("💰 Cashout", callback_data="cashout")])
    return InlineKeyboardMarkup(keyboard)

async def start_mines(query, user):
    user["game"] = "mines"
    user["bet"] = 1000
    user["mines"] = generate_mines()
    user["revealed"] = []
    user["balance"] -= user["bet"]

    await query.edit_message_text(
        f"💣 Mines 5x5\nMise: {user['bet']} FCFA",
        reply_markup=build_mines_keyboard([])
    )

async def handle_mines(query, user, data):
    index = int(data.split("_")[1])

    if index in user["mines"]:
        user["losses"] += 1
        user["game"] = None
        await query.edit_message_text("💥 BOOM ! Tu as perdu.")
        return

    user["revealed"].append(index)

    multiplier = 1 + (len(user["revealed"]) * 0.2)

    await query.edit_message_text(
        f"💎 Safe!\nMultiplicateur: x{round(multiplier,2)}",
        reply_markup=build_mines_keyboard(user["revealed"])
    )

async def mines_cashout(query, user):
    multiplier = 1 + (len(user["revealed"]) * 0.2)
    gain = int(user["bet"] * multiplier)

    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(
        f"💰 Cashout réussi !\nGain: {gain} FCFA"
    )

# ==============================
# 🚀 LUCKY JET
# ==============================

async def start_lucky(query, user):
    user["game"] = "lucky"
    user["bet"] = 1000
    user["balance"] -= user["bet"]

    multiplier = 1.0
    crash = random.uniform(1.5, 5.0)

    message = await query.edit_message_text(
        f"🚀 Lucky Jet\nx{multiplier}",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("💰 Cashout", callback_data="lucky_cashout")]
        ])
    )

    while multiplier < crash:
        await asyncio.sleep(1)
        multiplier += 0.3
        try:
            await message.edit_text(
                f"🚀 Lucky Jet\nx{round(multiplier,2)}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("💰 Cashout", callback_data="lucky_cashout")]
                ])
            )
        except:
            return

    user["losses"] += 1
    user["game"] = None
    await message.edit_text("💥 Crash ! Perdu.")

async def lucky_cashout(query, user):
    text = query.message.text
    multiplier = float(text.split("x")[1])
    gain = int(user["bet"] * multiplier)

    user["balance"] += gain
    user["wins"] += 1
    user["game"] = None

    await query.edit_message_text(f"💰 Cashout à x{multiplier}\nGain: {gain} FCFA")

# ==============================
# ⚽ PENALTY
# ==============================

async def start_penalty(query, user):
    user["game"] = "penalty"
    user["bet"] = 1000
    user["balance"] -= user["bet"]

    keyboard = [
        [
            InlineKeyboardButton("⬅️", callback_data="left"),
            InlineKeyboardButton("⬆️", callback_data="center"),
            InlineKeyboardButton("➡️", callback_data="right")
        ]
    ]

    await query.edit_message_text(
        "⚽ Choisis une direction",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def handle_penalty(query, user, choice):
    keeper = random.choice(["left","center","right"])

    if choice == keeper:
        user["losses"] += 1
        result = "🧤 Arrêt du gardien ! Perdu."
    else:
        gain = user["bet"] * 2
        user["balance"] += gain
        user["wins"] += 1
        result = f"⚽ BUT ! Gain: {gain} FCFA"

    user["game"] = None
    await query.edit_message_text(result)