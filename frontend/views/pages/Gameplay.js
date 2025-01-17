import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const Gameplay = {
	render: async () => {
		return (await fetchHtml("/views/templates/Gameplay.html"));
	},

	isPaddleMoving: {
		left: false,
		right: false,
	},
	keydownListener: null,
	keyupListener: null,

	after_render: async () => {	
		const settingId = sessionStorage.getItem('settingId')
        const player1 = sessionStorage.getItem("player1");
        if (player1) {
            document.getElementById("player1").textContent = player1;
        }
        const player2 = sessionStorage.getItem("player2");
        if (player2) {
            document.getElementById("player2").textContent = player2;
        }

		console.log("SettingId in Gameplay:", settingId);
		document.getElementById('gameId').innerText = `game id = ${sessionStorage.getItem('settingId')}`;
		const gameCanvas = document.getElementById('gameCanvas');
		const ctx = gameCanvas.getContext('2d');

		gameCanvas.width = 1000;
		gameCanvas.height = 600;

		let first = true;
		const center_x = gameCanvas.width / 2;
		const center_y = gameCanvas.height / 2;
		let paddle_h = 120;
		let paddle_w = 15;
		let paddle = {
			left_x: 0,
			right_x: gameCanvas.width,
			left_y: center_y - paddle_h / 2,
			right_y: center_y - paddle_h / 2,
		};
		let ball = {
			x: center_x,
			y: center_y,
			radius: 10,
		};
		let obstacle1 = {
			x: center_x,
			y: center_y,
			width: 0,
			height: 0,
		};
		let obstacle2 = {
			x: center_x,
			y: center_y,
			width: 0,
			height: 0,
		};
		let blind = {
			x: 0,
			y: 0,
			width: 0,
			height: 0,
		};
		let score = {
			left: 0,
			right: 0,
		};

		let animationFrameId = null;

		// Websocket
		const url = `${window.env.GAMEPLAY_WS_HOST}/ponglogic/${settingId}/`;
		window.ws = new WebSocket(url);
		console.log(url + " WebSocket created");

		window.ws.onopen = () => {
			console.log("WebSocket opened");
			if (animationFrameId) {
				cancelAnimationFrame(animationFrameId);
			}
			animationFrameId = requestAnimationFrame(update);
		};

		const gameStartButton = document.querySelector(".btn.btn-success.mt-3");
		
		// ボタンにクリックイベントを追加
		gameStartButton.addEventListener("click", function () {
			console.log("Game Startボタンが押されました");
			gameStartButton.style.display = "none";
			window.ws.send(JSON.stringify({ "game_signal": "start" }));
		});

		async function gameOver(data) {
			let winner = data.winner;
			if (winner === "left") {
				winner = sessionStorage.getItem("player1")? sessionStorage.getItem("player1") : i18next.t("gameplay:popup.left");
			} else if (winner === "right") {
				winner = sessionStorage.getItem("player2")? sessionStorage.getItem("player2") : i18next.t("gameplay:popup.right");
			}

            if (sessionStorage.getItem("isTournament") === "true") {
                const tournamentResponse = await fetchWithHandling(`${window.env.TOURNAMENT_HOST}/tournament/save-data/${localStorage.getItem("tournamentId")}/`);
				if (tournamentResponse) {	
					const tournamentData = await tournamentResponse.json();
                	console.log("Tournament data get successfully:", tournamentData);
	
                	const currentMatchId = parseInt(sessionStorage.getItem("currentMatch")) - 1;

                	if (tournamentData && tournamentData.matches) {
						let currentMatch = tournamentData.matches[currentMatchId];

                		currentMatch.player1_score = data.left_score;
                		currentMatch.player2_score = data.right_score;
                		currentMatch.winner = winner;
						console.log("currentMatch", currentMatch);

                		const response = await fetchWithHandling(`${window.env.TOURNAMENT_HOST}/tournament/save-data/${localStorage.getItem("tournamentId")}/`, {
                		    method: "PUT",
                		    body: currentMatch,
                		});
						const responseData = await response.json();
                		console.log("Tournament data updated successfully:", responseData);
					}

				alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
                document.getElementById('nextGameButton').style.display = 'block';
				}
            } else {
				alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
                document.getElementById('gameOverButton').style.display = 'block';
            }
		}

		window.ws.onmessage = (e) => {
			if (window.ws === null || window.ws.readyState !== WebSocket.OPEN)
				return;
			if (!first) {
				gameStartButton.style.display = "none";
			}
			const data = JSON.parse(e.data);
            if (data.type === "game_over") {
                gameOver(data);
                return;
            }
			score.left = data.left_score;
			score.right = data.right_score;
			paddle.left_y = data.left_paddle_y;
			paddle.right_y = data.right_paddle_y;
			ball.x = data.ball_x;
			ball.y = data.ball_y;
			if (first) {
				ball.radius = data.ball_radius;
				obstacle1.x = data.obstacle1_x;
				obstacle1.y = data.obstacle1_y;
				obstacle1.width = data.obstacle1_width;
				obstacle1.height = data.obstacle1_height;
				obstacle2.x = data.obstacle2_x;
				obstacle2.y = data.obstacle2_y;
				obstacle2.width = data.obstacle2_width;
				obstacle2.height = data.obstacle2_height;
				blind.x = data.blind_x;
				blind.y = data.blind_y;
				blind.width = data.blind_width;
				blind.height = data.blind_height;
				first = false;
			}
		};

		function sendMessage(message) {
			if (window.ws === null || window.ws.readyState !== WebSocket.OPEN)
				return;
			window.ws.send(JSON.stringify(message));
		}

		Gameplay.keydownListener = (event) => {
			let paddle_instruction = null;
			if (event.key === "D" || event.key === "d") {
				paddle_instruction = { move_direction: "down", action: "start", side: "left" };
			} else if (event.key === "E" || event.key === "e") {
				paddle_instruction = { move_direction: "up", action: "start", side: "left" };
			} else if (event.key === "I" || event.key === "i") {
				paddle_instruction = { move_direction: "up", action: "start", side: "right" };
			} else if (event.key === "K" || event.key === "k") {
				paddle_instruction = { move_direction: "down", action: "start", side: "right" };
			}
		
			if (paddle_instruction && paddle_instruction.side === "left" && !Gameplay.isPaddleMoving.left) {
				Gameplay.isPaddleMoving.left = true;
				sendMessage(paddle_instruction);
			}
			if (paddle_instruction && paddle_instruction.side === "right" && !Gameplay.isPaddleMoving.right) {
				Gameplay.isPaddleMoving.right = true;
				sendMessage(paddle_instruction);
			}
		};

		Gameplay.keyupListener = (event) => {
			let paddle_instruction = null;
			if (event.key === "D" || event.key === "d") {
				paddle_instruction = { move_direction: "down", action: "stop", side: "left" };
			} else if (event.key === "E" || event.key === "e") {
				paddle_instruction = { move_direction: "up", action: "stop", side: "left" };
			} else if (event.key === "I" || event.key === "i") {
				paddle_instruction = { move_direction: "up", action: "stop", side: "right" };
			} else if (event.key === "K" || event.key === "k") {
				paddle_instruction = { move_direction: "down", action: "stop", side: "right" };
			}
		
			if (paddle_instruction && paddle_instruction.side === "left" && Gameplay.isPaddleMoving.left) {
				Gameplay.isPaddleMoving.left = false;
				sendMessage(paddle_instruction);
			}
			if (paddle_instruction && paddle_instruction.side === "right" && Gameplay.isPaddleMoving.right) {
				Gameplay.isPaddleMoving.right = false;
				sendMessage(paddle_instruction);
			}
		};

		if (!window.keydownListenerAdded) {
			document.addEventListener("keydown", Gameplay.keydownListener);
			document.addEventListener("keyup", Gameplay.keyupListener);
			window.keydownListenerAdded = true;
		}

		window.ws.onclose = () => console.log("Disconnected");
  
		// 描画関数
		function draw() {
			ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
			ctx.fillStyle = "black";
			ctx.fillRect(0, 0, gameCanvas.width, gameCanvas.height);

			ctx.fillStyle = "white";
			ctx.fillRect(paddle.left_x, paddle.left_y, paddle_w, paddle_h);
			ctx.fillRect(paddle.right_x - paddle_w, 0 + paddle.right_y, paddle_w, paddle_h);
			ctx.fillRect(ball.x - ball.radius, ball.y - ball.radius, 2 * ball.radius, 2 * ball.radius);

			ctx.fillStyle = "red";
			ctx.fillRect(blind.x, blind.y, blind.width, blind.height);

			ctx.fillStyle = "yellow";
			ctx.fillRect(obstacle1.x, obstacle1.y, obstacle1.width, obstacle1.height);
			ctx.fillRect(obstacle2.x, obstacle2.y, obstacle2.width, obstacle2.height);
	
			ctx.fillStyle = "white";
			ctx.font = "50px Arial";
			ctx.fillText(score.left, center_x - 50, 50);
			ctx.fillText(score.right, center_x + 50, 50);
		}

		let lastUpdateTime = 0;
		const FPS = 60;
		function update(timestamp) {
			if (timestamp - lastUpdateTime >= (1000 / FPS)) {
				lastUpdateTime += (1000 / FPS);
				draw();
			}
			animationFrameId = requestAnimationFrame(update);
		}

		update();
	},

	cleanup: async () => {
		if (window.ws) {
		  document.removeEventListener("keydown", Gameplay.keydownListener);
		  document.removeEventListener("keyup", Gameplay.keyupListener);
		  window.keydownListenerAdded = false;
		  window.ws.close();
		  window.ws = null;
		  console.log("WebSocket closed");
		}
	
		if (sessionStorage.getItem('settingId') && sessionStorage.getItem("isTournament") !== "true") {
			await fetchWithHandling(`${window.env.GAMEPLAY_HOST}/gamesetting/${window.sessionStorage.getItem('settingId')}/`, {
			  method: "DELETE",
			});
	
            sessionStorage.removeItem('settingId')
			console.log("Settings deleted successfully:", sessionStorage.getItem('settingId'));
		}

        const tournamentButton = document.getElementById("navbar:tournament");
        if (tournamentButton) {
            tournamentButton.setAttribute("href", "#/tournament");
            tournamentButton.classList.replace("disabled", "active");
        } // トーナメントボタンを有効に
	  },
};

export default Gameplay;