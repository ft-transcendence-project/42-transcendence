const Gameplay = {
	render: async () => {
		return (await fetch("/views/templates/Gameplay.html")).text();
	},

	keyStates: {
		left: false,
		right: false,
	},
	leftInterval: null,
	rightInterval: null,
	keydownListener: null,
	keyupListener: null,

	after_render: async () => {	
        const player1 = sessionStorage.getItem("player1");
        if (player1) {
            document.getElementById("player1").textContent = player1;
        }
        const player2 = sessionStorage.getItem("player2");
        if (player2) {
            document.getElementById("player2").textContent = player2;
        }

		console.log("SettingId in Gameplay:", sessionStorage.getItem('settingId'));

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
		const url = `${window.env.GAMEPLAY_WS_HOST}/ponglogic/${sessionStorage.getItem('settingId')}/`;
		window.ws = new WebSocket(url);
		console.log(url + " WebSocket created");

		window.ws.onopen = () => {
			console.log("WebSocket opened");
			if (animationFrameId) {
				cancelAnimationFrame(animationFrameId);
			}
			animationFrameId = requestAnimationFrame(update);
		};

		async function gameOver(data) {
			let winner = data.winner;
			if (winner === "left") {
				winner = sessionStorage.getItem("player1");
			} else if (winner === "right") {
				winner = sessionStorage.getItem("player2");
			}

            if (sessionStorage.getItem("isTournament") === "true") {
                try {
                    const response = await fetch(`${window.env.TOURNAMENT_HOST}/tournament/api/save-data/${localStorage.getItem("tournamentId")}/`);
    
                    if (!response.ok) {
                        const errorData = await response.json();
                        console.error("Error updating tournament data:", errorData);
                        throw new Error(`HTTP Error Status: ${response.status}`);
                    }
    
                    const tournamentData = await response.json();
                    console.log("Tournament data get successfully:", tournamentData);
    
                    const currentMatchId = parseInt(sessionStorage.getItem("currentMatch")) - 1;
    
                    if (tournamentData && tournamentData.matches) {
						let currentMatch = tournamentData.matches[currentMatchId];

                        currentMatch.player1_score = data.left_score;
                        currentMatch.player2_score = data.right_score;
                        currentMatch.winner = winner;
						console.log("currentMatch", currentMatch);

                        const postResponse = await fetch(`${window.env.TOURNAMENT_HOST}/tournament/api/save-data/${localStorage.getItem("tournamentId")}/`, {
                            method: "PUT",
                            headers: {
                                "Content-Type": "application/json",
                            },
                            body: JSON.stringify({ currentMatch }),
                        });
    
                        if (!postResponse.ok) {
                            const errorData = await postResponse.json();
                            console.error("Error updating tournament data:", errorData);
                            throw new Error(`HTTP Error Status: ${postResponse.status}`);
                        }
    
                        const responseData = await postResponse.json();
                        console.log("Tournament data updated successfully:", responseData);
                        }

					alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
                    document.getElementById('nextGameButton').style.display = 'block';
                } catch (error) {
                    console.error("Error updating tournament data:", error);
                }
            } else {
				alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
                document.getElementById('gameOverButton').style.display = 'block';
            }
		}

		window.ws.onmessage = (e) => {
			if (window.ws === null || window.ws.readyState !== WebSocket.OPEN)
				return;
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
		
			if (message && message.paddle === "left" && !Gameplay.keyStates.left) {
				Gameplay.keyStates.left = true;
				Gameplay.leftInterval = setInterval(function () {
					sendMessage(message);
				}, 1);
			}
			if (message && message.paddle === "right" && !Gameplay.keyStates.right) {
				Gameplay.keyStates.right = true;
				Gameplay.rightInterval = setInterval(function () {
					sendMessage(message);
				}, 1);
			}
		};
		Gameplay.keyupListener = (event) => {
			if ( event.key === "E" ||
				event.key === "e" ||
				event.key === "D" ||
				event.key === "d" )
			{
				clearInterval(Gameplay.leftInterval); // メッセージ送信の間隔を止める
				Gameplay.keyStates.left = false;
			}
			else if ( event.key === "I" ||
				event.key === "i" ||
				event.key === "K" ||
				event.key === "k" )
			{
				clearInterval(Gameplay.rightInterval); // メッセージ送信の間隔を止める
				Gameplay.keyStates.right = false;
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

			ctx.fillStyle = "white";
			ctx.font = "50px Arial";
			ctx.fillText(score.left, center_x - 50, 50);
			ctx.fillText(score.right, center_x + 50, 50);

			ctx.fillStyle = "red";
			ctx.fillRect(blind.x, blind.y, blind.width, blind.height);

			ctx.fillStyle = "yellow";
			ctx.fillRect(obstacle1.x, obstacle1.y, obstacle1.width, obstacle1.height);
			ctx.fillRect(obstacle2.x, obstacle2.y, obstacle2.width, obstacle2.height);
		}

		function update() {
			draw();
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
		  try {
			const response = await fetch(`${window.env.GAMEPLAY_HOST}/gamesetting/api/${window.sessionStorage.getItem('settingId')}/`, {
			  method: "DELETE",
			});
	
			if (!response.ok) {
			  throw new Error(`HTTP error! status: ${response.status}`);
			}
	
            sessionStorage.removeItem('settingId')
			console.log("Settings deleted successfully:", sessionStorage.getItem('settingId'));
		  } catch (error) {
			console.error("Failed to delete settings:", error);
		  }
		}

        const tournamentButton = document.getElementById("navbar:tournament");
        if (tournamentButton) {
            tournamentButton.setAttribute("href", "#/tournament");
            tournamentButton.classList.replace("disabled", "active");
        } // トーナメントボタンを有効に
	  },
};

export default Gameplay;