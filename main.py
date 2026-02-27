<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>PLAY ME PRO MAX</title>
<style>
body{
    background:#0f1116;
    font-family:Arial;
    color:white;
    text-align:center;
}
h1{
    color:#00aaff;
}
.grid{
    display:grid;
    grid-template-columns:repeat(5,60px);
    gap:10px;
    justify-content:center;
    margin:20px;
}
.cell{
    width:60px;
    height:60px;
    background:#2a2d36;
    border-radius:10px;
    cursor:pointer;
}
.win{
    background:#0080ff; /* BLEU gagnant */
}
.bomb{
    background:red;
}
.controls{
    margin-top:20px;
}
button{
    padding:10px 20px;
    margin:5px;
    border:none;
    border-radius:8px;
    cursor:pointer;
}
.blue{
    background:#007bff;
    color:white;
}
.dark{
    background:#1c1f26;
    color:white;
}
</style>
</head>
<body>

<h1>🎮 PLAY ME PRO MAX</h1>
<p>ID Joueur : 8094967191</p>

<h3>💰 Capital : <span id="balance">10000</span> FCFA</h3>

<div>
Nombre de bombes :
<button class="dark" onclick="setBombs(2)">2</button>
<button class="dark" onclick="setBombs(3)">3</button>
<button class="dark" onclick="setBombs(5)">5</button>
<button class="dark" onclick="setBombs(7)">7</button>
</div>

<div class="grid" id="grid"></div>

<div class="controls">
<input type="number" id="bet" value="500">
<button class="blue" onclick="startGame()">PARI</button>
</div>

<hr>

<h2>⚽ Jeu Penalty</h2>
<p>Choisis une direction :</p>
<button class="blue" onclick="penalty('left')">Gauche</button>
<button class="blue" onclick="penalty('center')">Centre</button>
<button class="blue" onclick="penalty('right')">Droite</button>

<script>
let bombs = 3;
let bombPositions = [];
let balance = 10000;
let gameActive = false;

function setBombs(n){
    bombs = n;
}

function startGame(){
    gameActive = true;
    bombPositions = [];
    document.getElementById("grid").innerHTML="";
    let bet = parseInt(document.getElementById("bet").value);

    if(bet > balance){
        alert("Solde insuffisant !");
        return;
    }

    balance -= bet;
    updateBalance();

    while(bombPositions.length < bombs){
        let r = Math.floor(Math.random()*25);
        if(!bombPositions.includes(r)){
            bombPositions.push(r);
        }
    }

    for(let i=0;i<25;i++){
        let cell = document.createElement("div");
        cell.classList.add("cell");
        cell.onclick = function(){
            if(!gameActive) return;

            if(bombPositions.includes(i)){
                cell.classList.add("bomb");
                alert("💣 Perdu !");
                gameActive=false;
            }else{
                cell.classList.add("win");
                balance += bet * 1.2;
                updateBalance();
            }
        };
        document.getElementById("grid").appendChild(cell);
    }
}

function updateBalance(){
    document.getElementById("balance").innerText = balance;
}

function penalty(choice){
    let directions = ["left","center","right"];
    let random = directions[Math.floor(Math.random()*3)];

    if(choice === random){
        balance += 1000;
        alert("⚽ BUT ! +1000 FCFA");
    }else{
        balance -= 500;
        alert("❌ Arrêt du gardien !");
    }
    updateBalance();
}
</script>

</body>
</html>
