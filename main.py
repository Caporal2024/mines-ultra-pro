<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="/static/casino.css">
</head>
<body>

<div class="header">
<div>🍏 APPLE</div>
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