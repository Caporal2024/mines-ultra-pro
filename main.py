from flask import Flask, render_template, request, jsonify
import random
import time

app = Flask(__name__, static_folder="static")

# Stockage simple (remplace par base de données plus tard)
balances = {}
last_action = {}
mine_games = {}

@app.route("/")
def home():
    return "Casino Bot Running"

# =============================
# 🔐 UPDATE POINTS (ANTI TRICHE)
# =============================
@app.route("/update_points", methods=["POST"])
def update_points():
    data = request.json
    user_id = str(data.get("user_id"))
    amount = int(data.get("amount"))

    now = time.time()

    # Anti spam 3 secondes
    if user_id in last_action:
        if now - last_action[user_id] < 3:
            return jsonify({"error": "Too fast"}), 403

    last_action[user_id] = now

    # Limite gain max
    if amount > 200:
        return jsonify({"error": "Invalid amount"}), 403

    if user_id not in balances:
        balances[user_id] = 1000

    balances[user_id] += amount

    return jsonify({"success": True, "balance": balances[user_id]})

# =============================
# 💣 MINES LOGIQUE SERVEUR
# =============================
@app.route("/start_mines", methods=["POST"])
def start_mines():
    user_id = str(request.json.get("user_id"))

    mines = random.sample(range(25), 5)
    mine_games[user_id] = mines

    return jsonify({"started": True})

@app.route("/check_cell", methods=["POST"])
def check_cell():
    user_id = str(request.json.get("user_id"))
    index = int(request.json.get("index"))

    if user_id not in mine_games:
        return jsonify({"error": "Game not started"}), 400

    if index in mine_games[user_id]:
        return jsonify({"result": "mine"})
    else:
        return jsonify({"result": "safe"})

# =============================
# ROUTES HTML
# =============================
@app.route("/mines")
def mines():
    return render_template("mines.html")

@app.route("/jet")
def jet():
    return render_template("jet.html")

@app.route("/apple")
def apple():
    return render_template("apple.html")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000(body {
    margin: 0;
    font-family: 'Segoe UI', sans-serif;
    background: #0f1115;
    color: white;
}

/* Header */
.header {
    display: flex;
    justify-content: space-between;
    padding: 15px;
    background: #1a1d23;
    font-weight: bold;
}

.balance {
    background: #14161b;
    padding: 8px 15px;
    border-radius: 10px;
    color: #00ff88;
    box-shadow: 0 0 10px #00ff88;
}

/* Carte */
.card {
    margin: 20px;
    padding: 20px;
    background: #1a1d23;
    border-radius: 15px;
    box-shadow: 0 0 25px rgba(0,255,136,0.2);
}

/* Boutons */
button {
    width: 100%;
    padding: 14px;
    margin-top: 10px;
    border: none;
    border-radius: 12px;
    font-weight: bold;
    background: linear-gradient(90deg,#00ff88,#00ccff);
    color: black;
    cursor: pointer;
}

button:hover {
    transform: scale(1.05);
}

/* Grid Mines */
.grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 8px;
}

.cell {
    aspect-ratio: 1;
    background: #14161b;
    border-radius: 10px;
    cursor: pointer;
}

.safe {
    background: #00ff88;
}

.mine {
    background: red;
    animation: explode 0.3s ease-in-out;
}

@keyframes explode {
    0% { transform: scale(1); }
    50% { transform: scale(1.2); }
    100% { transform: scale(1); }
}<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static/casino.css">
</head>
<body>

<div class="header">
<div>💣 MINES</div>
<div class="balance" id="balance">1000 pts</div>
</div>

<div class="card">
<button onclick="startGame()">START GAME</button>
<div class="grid" id="grid"></div>
<button onclick="cashout()">💰 CASHOUT</button>
</div>

<script>
let user_id = 8094967191;
let grid = document.getElementById("grid");

for(let i=0;i<25;i++){
let cell=document.createElement("div");
cell.classList.add("cell");
cell.dataset.index=i;
cell.onclick=()=>clickCell(i, cell);
grid.appendChild(cell);
}

function startGame(){
fetch("/start_mines",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({user_id:user_id})
});
}

function clickCell(index, cell){
fetch("/check_cell",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({user_id:user_id,index:index})
})
.then(res=>res.json())
.then(data=>{
if(data.result=="mine"){
cell.classList.add("mine");
alert("💥 BOOM");
}else{
cell.classList.add("safe");
}
});
}

function cashout(){
fetch("/update_points",{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify({user_id:user_id,amount:100})
})
.then(res=>res.json())
.then(data=>{
document.getElementById("balance").innerText=data.balance+" pts";
});
}
</script>

</body>
</html><!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static/casino.css">
</head>
<body>

<div class="header">
<div>🚀 JET</div>
<div class="balance">Jet Game</div>
</div>

<div class="card">
<h2 id="multi">1.00x</h2>
<button onclick="start()">LANCER</button>
</div>

<script>
function start(){
let multi = 1;
let crash = (Math.random()*3+1).toFixed(2);

let interval=setInterval(()=>{
multi+=0.05;
document.getElementById("multi").innerText=multi.toFixed(2)+"x";

if(multi>=crash){
clearInterval(interval);
document.getElementById("multi").style.color="red";
alert("💥 Crash à "+crash+"x");
}
},80);
}
</script>

</body>
</html><!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static/casino.css">
</head>
<body>

<div class="header">
<div>🍏 APPLE</div>
<div class="balance">Apple Game</div>
</div>

<div class="card">
<button onclick="play()">CHOISIR</button>
</div>

<script>
function play(){
let win = Math.random()<0.7;
if(win){
alert("🍏 GAGNÉ !");
}else{
alert("❌ PERDU");
}
}
</script>

</body>
</html>