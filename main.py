<!DOCTYPE html>
<html lang="fr">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Lucky Jet Premium</title>

<style>
body{
    margin:0;
    font-family:'Segoe UI',sans-serif;
    background:linear-gradient(135deg,#0f2027,#203a43,#2c5364);
    color:white;
}

/* CARD */
.card{
    background:rgba(0,0,0,0.6);
    backdrop-filter:blur(10px);
    margin:20px;
    padding:20px;
    border-radius:20px;
    box-shadow:0 0 25px rgba(0,255,120,0.3);
}

/* STAKE BUTTON */
.btn{
    background:linear-gradient(90deg,#00c853,#00e676);
    border:none;
    padding:15px;
    margin-top:10px;
    width:100%;
    border-radius:14px;
    color:white;
    font-weight:bold;
    font-size:16px;
    cursor:pointer;
    transition:0.2s;
}

.btn:hover{
    transform:scale(1.05);
    box-shadow:0 0 15px #00e676;
}

/* GRID */
.grid{
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:10px;
    margin-top:15px;
}

.tile{
    background:#1e3c50;
    height:65px;
    border-radius:12px;
    display:flex;
    align-items:center;
    justify-content:center;
    font-size:22px;
    cursor:pointer;
    transition:0.2s;
}

.tile:hover{
    background:#285c78;
}

.safe{
    background:#00c853 !important;
}

.bomb{
    background:#ff1744 !important;
}

/* TOP BAR */
.topbar{
    display:flex;
    justify-content:space-between;
    font-size:14px;
}

.big{
    font-size:20px;
    font-weight:bold;
    margin-top:10px;
}
</style>
</head>
<body>

<div class="card">
    <h2>🚀 LUCKY JET / MINES</h2>

    <div class="topbar">
        <div>💰 Solde: <span id="balance">10000</span> FCFA</div>
        <div>🏆 <span id="wins">0</span> | ❌ <span id="losses">0</span></div>
    </div>

    <div class="big">Multiplicateur: x<span id="multiplier">1.00</span></div>
    <div>Gain potentiel: <span id="potential">0</span> FCFA</div>

    <div class="grid" id="grid"></div>

    <button class="btn" onclick="cashout()">💰 CASHOUT</button>
    <button class="btn" onclick="startGame()">🔄 Nouvelle Partie</button>
</div>

<script>
let balance = 10000;
let bet = 200;
let multiplier = 1;
let wins = 0;
let losses = 0;
let mines = [];
let opened = 0;
let gameActive = true;

function startGame(){
    multiplier = 1;
    opened = 0;
    gameActive = true;
    mines = [];
    while(mines.length < 4){
        let r = Math.floor(Math.random()*25);
        if(!mines.includes(r)) mines.push(r);
    }
    document.getElementById("multiplier").innerText="1.00";
    document.getElementById("potential").innerText="0";
    createGrid();
}

function createGrid(){
    const grid = document.getElementById("grid");
    grid.innerHTML="";
    for(let i=0;i<25;i++){
        let tile=document.createElement("div");
        tile.className="tile";
        tile.onclick=()=>openTile(i,tile);
        grid.appendChild(tile);
    }
}

function openTile(index,tile){
    if(!gameActive || tile.classList.contains("safe")) return;

    if(mines.includes(index)){
        tile.classList.add("bomb");
        tile.innerHTML="💣";
        losses++;
        balance -= bet;
        update();
        gameActive=false;
        alert("💥 Perdu !");
    }else{
        tile.classList.add("safe");
        tile.innerHTML="💎";
        opened++;
        multiplier += 0.40;
        document.getElementById("multiplier").innerText=multiplier.toFixed(2);
        document.getElementById("potential").innerText=(bet*multiplier).toFixed(0);
    }
}

function cashout(){
    if(!gameActive) return;
    let gain = bet*multiplier;
    balance += gain;
    wins++;
    update();
    gameActive=false;
    alert("🚀 Cashout réussi !");
}

function update(){
    document.getElementById("balance").innerText=balance;
    document.getElementById("wins").innerText=wins;
    document.getElementById("losses").innerText=losses;
}

startGame();
</script>

</body>
</html>