const Gameplay = {
	render: async () => {
		return (await fetch("/views/templates/Gameplay.html")).text();
	},

	after_render: async () => {
        const player1 = sessionStorage.getItem("player1");
        if (player1) {
            document.getElementById("player1").textContent = player1;
        }
        const player2 = sessionStorage.getItem("player2");
        if (player2) {
            document.getElementById("player2").textContent = player2;
        }

		console.log("SettingId in Gameplay:", window.localStorage.getItem('settingId'));

		const gameCanvas = document.getElementById('gameCanvas');
		const ctx = gameCanvas.getContext('2d');

		gameCanvas.width = 1000;
		gameCanvas.height = 600;

		const center_x = gameCanvas.width / 2;
		const center_y = gameCanvas.height / 2;
		const paddle_h = 120;
		const paddle_w = 15;
		const paddle = {
			left_x: 0,
			right_x: gameCanvas.width,
			left_y: center_y - paddle_h / 2,
			right_y: center_y - paddle_h / 2,
		};
		const ball = {
			x: center_x,
			y: center_y,
			radius: 10,
		};
		const obstacle1 = {
			x: center_x,
			y: center_y,
			width: 0,
			height: 0,
		};
		const obstacle2 = {
			x: center_x,
			y: center_y,
			width: 0,
			height: 0,
		};
		const blind = {
			x: 350,
			y: 0,
			width: 0,
			height: 0,
		};
		const score = {
			left: 0,
			right: 0,
		};

		let animationFrameId = null;
		const keyStates = {
			left: false,
			right: false,
		};

		// Websocket
		const url = `${window.env.BACKEND_WS_HOST}/gameplay/${window.localStorage.getItem('settingId')}/`;
		window.ws = new WebSocket(url);
		console.log(url + " WebSocket created");

		window.ws.onopen = () => {
			console.log("WebSocket opened");
			if (animationFrameId) {
				cancelAnimationFrame(animationFrameId);
			}
			animationFrameId = requestAnimationFrame(update);
		};

        function gameOver(data) {
            let winner = data.winner;
            if (winner === "left") {
                winner = sessionStorage.getItem("player1");
            } else if (winner === "right") {
                winner = sessionStorage.getItem("player2");
            }

            try {
                let tournamentData = JSON.parse(sessionStorage.getItem("tournamentData"));
                const currentMatch = parseInt(sessionStorage.getItem("currentMatch")) - 1;
                sessionStorage.setItem("currentMatch", currentMatch + 2);

                if (tournamentData && tournamentData.matches) {
                    tournamentData.matches[currentMatch].player1_score = data.left_score;
                    tournamentData.matches[currentMatch].player2_score = data.right_score;
                    tournamentData.matches[currentMatch].winner = winner;
                    sessionStorage.setItem("tournamentData", JSON.stringify(tournamentData));

                    if (currentMatch < 4) {
                        const nextMatch = currentMatch + 1;
                        if (nextMatch < tournamentData.matches.length) {
                            sessionStorage.setItem("player1", tournamentData.matches[nextMatch].player1.name);
                            sessionStorage.setItem("player2", tournamentData.matches[nextMatch].player2.name);
                        }
                    }
                }

                alert(`Game Over! ${winner} wins!`);
                document.getElementById('gameOverButtons').style.display = 'block';
            } catch (error) {
                console.error("Error updating tournament data:", error);
            }
        }

		window.ws.onmessage = (e) => {
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
			ball.radius = data.ball_radius;
			obstacle1.x = data.obstacle1_x;
			obstacle1.y = data.obstacle1_y;
			obstacle1.width = data.obstacle1_width;
			obstacle1.height = data.obstacle1_height;
			obstacle2.x = data.obstacle2_x;
			obstacle2.y = data.obstacle2_y;
			obstacle2.width = data.obstacle2_width;
			obstacle2.height = data.obstacle2_height;
			blind.width = data.blind_width;
			blind.height = data.blind_height;
		};

		function sendMessage(message) {
			window.ws.send(JSON.stringify(message));
		}

		if (!window.keydownListenerAdded) {
			let leftInterval = null;
			let rightInterval = null;
			document.addEventListener('keydown', function (event) {
				let message = null;
				if (event.key === "D" || event.key === "d") {
					message = { key: "D", action: "pressed", paddle: "left" };
				} else if (event.key === "E" || event.key === "e") {
					message = { key: "E", action: "pressed", paddle: "left" };
				} else if (event.key === "I" || event.key === "i") {
					message = { key: "I", action: "pressed", paddle: "right" };
				} else if (event.key === "K" || event.key === "k") {
					message = { key: "K", action: "pressed", paddle: "right" };
				}
			
				if (message && message.paddle === "left" && !keyStates.left) {
					keyStates.left = true;
					leftInterval = setInterval(function () {
						sendMessage(message);
					}, 1);
				}
				if (message && message.paddle === "right" && !keyStates.right) {
					keyStates.right = true;
					rightInterval = setInterval(function () {
						sendMessage(message);
					}, 1);
				}
			});
			document.addEventListener('keyup', function (event) {
				if ( event.key === "E" ||
					event.key === "e" ||
					event.key === "D" ||
					event.key === "d" )
				{
					clearInterval(leftInterval); // メッセージ送信の間隔を止める
					keyStates.left = false;
				}
				else if ( event.key === "I" ||
					event.key === "i" ||
					event.key === "K" ||
					event.key === "k" )
				{
					clearInterval(rightInterval); // メッセージ送信の間隔を止める
					keyStates.right = false;
				}
			});
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

		function update() {
			draw();
			animationFrameId = requestAnimationFrame(update);
		}

		update();
	},

	cleanup: async () => {
		if (window.ws) {
		  window.ws.close();
		  window.ws = null;
		  console.log("WebSocket closed");
		}
	
		if (window.localStorage.getItem('settingId')) {
		  try {
			const response = await fetch(`${window.env.BACKEND_HOST}/gameplay/api/gamesetting/${window.localStorage.getItem('settingId')}/`, {
			  method: "DELETE",
			});
	
			if (!response.ok) {
			  throw new Error(`HTTP error! status: ${response.status}`);
			}
	
			console.log("Settings deleted successfully:", window.localStorage.getItem('settingId'));
		  } catch (error) {
			console.error("Failed to delete settings:", error);
		  }
		}
	  },
};

export default Gameplay;