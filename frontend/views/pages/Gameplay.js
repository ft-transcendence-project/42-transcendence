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

		console.log("SettingId in Gameplay:", sessionStorage.getItem('settingId'));

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
		const obstacle = {
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
		const url = `${window.env.BACKEND_WS_HOST}/gameplay/${sessionStorage.getItem('settingId')}/`;
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
                    const response = await fetch(`${window.env.BACKEND_HOST}/tournament/api/save-data/${localStorage.getItem("tournamentId")}/`);
    
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

                        const postResponse = await fetch(`${window.env.BACKEND_HOST}/tournament/api/save-data/${localStorage.getItem("tournamentId")}/`, {
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

                    alert(`Game Over! ${winner} wins!`);
                    document.getElementById('nextGameButton').style.display = 'block';
                } catch (error) {
                    console.error("Error updating tournament data:", error);
                }
            } else {
                alert(`Game Over! ${winner} wins!`);
                document.getElementById('gameOverButton').style.display = 'block';
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
			obstacle.x = data.obstacle_x;
			obstacle.y = data.obstacle_y;
			obstacle.width = data.obstacle_width;
			obstacle.height = data.obstacle_height;
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
			ctx.fillRect(obstacle.x, obstacle.y, obstacle.width, obstacle.height);

			ctx.fillStyle = "red";
			ctx.fillRect(blind.x, blind.y, blind.width, blind.height);

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
	
		if (sessionStorage.getItem('settingId') && sessionStorage.getItem("isTournament") !== "true") {
		  try {
			const response = await fetch(`${window.env.BACKEND_HOST}/gameplay/api/gamesetting/${sessionStorage.getItem('settingId')}/`, {
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