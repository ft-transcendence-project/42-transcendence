const Gameplay = {
	render: async () => {
		return (await fetch("/views/templates/Gameplay.html")).text();
	},

	after_render: async () => {
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

		window.ws.onmessage = (e) => {
			const coordinates = JSON.parse(e.data);
			score.left = coordinates.left_score;
			score.right = coordinates.right_score;
			paddle.left_y = coordinates.left_paddle_y;
			paddle.right_y = coordinates.right_paddle_y;
			ball.x = coordinates.ball_x;
			ball.y = coordinates.ball_y;
			ball.radius = coordinates.ball_radius;
			obstacle.x = coordinates.obstacle_x;
			obstacle.y = coordinates.obstacle_y;
			obstacle.width = coordinates.obstacle_width;
			obstacle.height = coordinates.obstacle_height;
			blind.width = coordinates.blind_width;
			blind.height = coordinates.blind_height;
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