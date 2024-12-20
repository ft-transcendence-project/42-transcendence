const Gameplay = {
	render: async () => {
		return `
			<canvas id="gameCanvas" class="mx-auto p-5" style="width: 1000px;"></canvas>
		`;
	},

	after_render: async () => {
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
		const url = `${window.env.BACKEND_WS_HOST}/gameplay/`;
		window.ws = new WebSocket(url);
		console.log(url + " WebSocket created");

		window.ws.onopen = () => {
			console.log("WebSocket opened");
			if (animationFrameId) {
				cancelAnimationFrame(animationFrameId);
			}
			animationFrameId = requestAnimationFrame(update);
		};

		// 12/20 ここを修正しました。raza
		
		// window.ws.onmessage = (e) => {
		// 	const coordinates = JSON.parse(e.data);
		// 	score.left = coordinates.left_score;
		// 	score.right = coordinates.right_score;
		// 	paddle.left_y = coordinates.left_paddle_y;
		// 	paddle.right_y = coordinates.right_paddle_y;
		// 	ball.x = coordinates.ball_x;
		// 	ball.y = coordinates.ball_y;
		// };
		window.ws.onmessage = (e) => {
			const data = JSON.parse(e.data);
			score.left = data.left_score;
			score.right = data.right_score;
			paddle.left_y = data.left_paddle_y;
			paddle.right_y = data.right_paddle_y;
			ball.x = data.ball_x;
			ball.y = data.ball_y;
			
		
			// winnerが決まっていればここでゲームを終了することをしています。ソケット,animationは閉じました。他にあれば教えて
			if (data.winner) {
				if (animationFrameId) {
					cancelAnimationFrame(animationFrameId);
					animationFrameId = null;
				}
				if (window.ws) {
					window.ws.close();
					window.ws = null;
				}
				// アイテムの指定,遷移
				localStorage.setItem('gameWinner', data.winner);
				window.location.hash = "#/winnerpage";
			}
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
			ctx.fillRect(ball.x - 10, ball.y - 10, 20, 20);

			ctx.font = "20px Arial";
			ctx.fillText(score.left, center_x - 50, 50);
			ctx.fillText(score.right, center_x + 50, 50);
		}

		function update() {
			draw();
			animationFrameId = requestAnimationFrame(update);
		}

		update();
	},

	cleanup: () => {
		if (window.ws) {
			window.ws.close();
			window.ws = null;
			console.log("WebSocket closed");
		}
	},
};

export default Gameplay;
