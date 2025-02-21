class Game {
    constructor() {
        this.gameCanvas = document.getElementById("gameCanvas");
        this.ctx = this.gameCanvas.getContext("2d");
        this.gameCanvas.width = 1000;
        this.gameCanvas.height = 600;
        this.center_x = this.gameCanvas.width / 2;
        this.center_y = this.gameCanvas.height / 2;
        this.settingId = sessionStorage.getItem("settingId")?? 0;
    }
    displayPlayers(){
        const player1 = sessionStorage.getItem("player1");
        if (player1) {
            document.getElementById("player1").textContent = player1;
        }
        const player2 = sessionStorage.getItem("player2");
        if (player2) {
            document.getElementById("player2").textContent = player2;
        }
    }
    displayGameId(){
        document.getElementById("gameId").innerText = `game id = ${sessionStorage.getItem("settingId")}`;
    }
    drawGameCanvas(){
        this.ctx.clearRect(0, 0, this.gameCanvas.width, this.gameCanvas.height);
        this.ctx.fillStyle = "black";
        this.ctx.fillRect(0, 0, this.gameCanvas.width, this.gameCanvas.height);
    }
}

class Paddle
{
    constructor(Game) {
        this.paddle_h = 120;
        this.paddle_w = 15;
        this.left_x = 0;
        this.right_x = Game.gameCanvas.width;
        this.left_y = Game.center_y - this.paddle_h / 2;
        this.right_y = Game.center_y - this.paddle_h / 2;
    }
    drawPaddle(Game){
        Game.ctx.fillStyle = "white";
        Game.ctx.fillRect(this.left_x, this.left_y, this.paddle_w, this.paddle_h); //左側のパドル描画
        Game.ctx.fillRect(this.right_x - this.paddle_w, this.right_y, this.paddle_w, this.paddle_h); //右側のパドル描画
    }
    setPaddlePosition(left_y, right_y){
        this.left_y = left_y;
        this.right_y = right_y;
    }
}

class Ball
{
    constructor(Game,radius) {
        this.x = Game.center_x,
        this.y = Game.center_y,
        this.radius = radius
    }
    drawBall(Game){
        Game.ctx.fillStyle = "white";
        Game.ctx.fillRect(this.x - this.radius, this.y - this.radius, 2 * this.radius, 2 * this.radius);
    }
    setBallPosition(x, y){
        this.x = x;
        this.y = y;
    }
}

//Obstacleを使用してobstacle1, obstacle2, blindを作成する。
class Obstacle {
    constructor(x, y, width, height) {
        this.x = x;
        this.y = y;
        this.width = width;
        this.height = height;
    }

    drawObstacle(Game,color) {
        if (color === "red") { //blindの描画
            Game.ctx.fillStyle = "red";
            Game.ctx.fillRect(this.x, this.y, this.width, this.height);
        }
        else if (color === "yellow") {
            Game.ctx.fillStyle = "yellow";
            Game.ctx.fillRect(this.x, this.y, this.width, this.height);
        }
    }
}

class Score {
    constructor() {
        this.left = 0;
        this.right = 0;
    }
    drawScore(Game){
        Game.ctx.fillStyle = "white";
        Game.ctx.font = "50px Arial";
        Game.ctx.fillText(this.left, Game.center_x - 50, 50);
        Game.ctx.fillText(this.right, Game.center_x + 50, 50);
    }
    setScore(left, right){
        this.left = left;
        this.right = right;
    }
}

export { Game, Paddle, Ball, Obstacle, Score };