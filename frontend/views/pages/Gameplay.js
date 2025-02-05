import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const Gameplay = {

  render: async () => {
    return await fetchHtml("/views/templates/Gameplay.html");
  },

  isPaddleMoving: {
    left: false,
    right: false,
  },
  keydownListener: null,
  keyupListener: null,
  remote: {
    right: false,
    left: false,
    remoteMode: false,
    ready: false,
  },
  after_render: async () => {
    let settingId = sessionStorage.getItem("settingId");
    console.log("SettingId in Gameplay:", settingId);
    document.getElementById("gameId").innerText =
      `game id = ${sessionStorage.getItem("settingId")}`;
    let player1 = sessionStorage.getItem("player1");
    if (player1) {
      document.getElementById("player1").textContent = player1;
    }
    let player2 = sessionStorage.getItem("player2");
    if (player2) {
      document.getElementById("player2").textContent = player2;
    }
    let isRemote = sessionStorage.getItem("isRemote");
    if (isRemote === "true") {
      Gameplay.remote.remoteMode = true;
    }
    else
      Gameplay.remote.remoteMode = false;
    let isRight = sessionStorage.getItem("isRight");
    if (isRight === "true") {
      Gameplay.remote.right = true;
    }
    else
      Gameplay.remote.right = false;
    let isLeft = sessionStorage.getItem("isLeft");
    if (isLeft === "true") {
      Gameplay.remote.left = true;
    }
    else
      Gameplay.remote.left = false;

    const gameCanvas = document.getElementById("gameCanvas");
    const ctx = gameCanvas.getContext("2d");
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
    let url = `${window.env.GAMEPLAY_WS_HOST}/ponglogic/${settingId}/`;
    // Websocket

    async function setupNewWebSocket(url) {
      Gameplay.remote.remoteMode= false;
      sessionStorage.setItem("isRemote", "false");
      if (window.ws && window.ws.readyState === WebSocket.OPEN && url !== window.ws.url) {
        console.log("Closing existing WebSocket before opening new one", settingId);
        // 確実に閉じた後にinitializeNewWebSocketを実行
        await new Promise((resolve) => {
          window.ws.onclose = () => {
            console.log("WebSocket closed", settingId);
            window.ws = null;
            resolve();
          };
          window.ws.close();
        });
      }
      await initializeNewWebSocket(url);
    }
    
    async function initializeNewWebSocket(url) {
      if (!window.ws) {
        window.ws = new WebSocket(url);
        console.log(url + " WebSocket created");
      }
      window.ws.onopen = () => {
        console.log("WebSocket opened", settingId);
        if (!window.location.hash.includes(`#/gameplay.${settingId}/`)) {
          window.location.hash = `#/gameplay.${settingId}/`;
        }
        if (animationFrameId) {
          cancelAnimationFrame(animationFrameId);
        }
        animationFrameId = requestAnimationFrame(update);
      };
    }

    setupNewWebSocket(url);

    window.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    const gameStartButton = document.getElementById("game-start");
    const remoteButton = document.getElementById("remote-mode");
    const remoteOptions = document.getElementById("remote-options");
    const gameIdInput = document.getElementById("game-id-text");
    const gameIdSetButton = document.getElementById("game-id-set-button");
    const rightButton = document.getElementById("remote-right");
    const leftButton = document.getElementById("remote-left");
    const remoteSetButton = document.getElementById("remote-set-button");

    // ボタンにクリックイベントを追加
    gameStartButton.addEventListener("click", function (){
      console.log("Game Startボタンが押されました");
      if (!Gameplay.remote.remoteMode || (Gameplay.remote.remoteMode && Gameplay.remote.ready)) {
        console.log("left2", Gameplay.remote.left, " right2", Gameplay.remote.right, " remoteMode2", Gameplay.remote.remoteMode);
        gameStartButton.style.display = "none";
        remoteButton.style.display = "none";
        remoteOptions.style.display = "none";
        window.ws.send(JSON.stringify({ game_signal: "start" }));
      }
      else
        alert("ゲームが開始できません");
    });

    remoteButton.addEventListener("click", function () {
      if (remoteButton.textContent === "Remote OFF") {
        remoteButton.textContent = "Remote ON";
        remoteOptions.style.display = "block";
        Gameplay.remote.remoteMode= true;
        sessionStorage.setItem("isRemote", "true");
      }
      else if (remoteButton.textContent === "Remote ON"){
        remoteButton.textContent = "Remote OFF";
        remoteOptions.style.display = "none";
        Gameplay.remote.remoteMode= false;
        sessionStorage.setItem("isRemote", "false");
      }
    });

    gameIdSetButton.addEventListener("click", async function () {
      try {
        if (gameIdInput.value) {
          sessionStorage.setItem("settingId", gameIdInput.value);
          settingId = sessionStorage.getItem("settingId");
          const response = await fetchWithHandling(
            `${window.env.GAMEPLAY_HOST}/gamesetting/${window.sessionStorage.getItem("settingId")}/`,
            {
              method: "GET",
            },
          );
          if (!response.ok) {
            throw new Error("Game ID not found");
          }
          const responseData = await response.json();
          console.log("settingdata GET successfully:", responseData);
          url = `${window.env.GAMEPLAY_WS_HOST}/ponglogic/${settingId}/`;
          setupNewWebSocket(url);
        }
      } catch (error) {
        console.error("Error:", error);
        alert("Invalid Game ID. Please try again.");
      }
    });

    rightButton.addEventListener("click", function () {
      Gameplay.remote.right = true;
      Gameplay.remote.left = false; 
      rightButton.style.backgroundColor = "orange";
      leftButton.style.backgroundColor = "white";
      sessionStorage.setItem("isRight", "true");
      sessionStorage.setItem("isLeft", "false");
    });
    
    leftButton.addEventListener("click", function () {
      Gameplay.remote.left = true;
      Gameplay.remote.right = false;
      leftButton.style.backgroundColor = "orange";
      rightButton.style.backgroundColor = "white";
      sessionStorage.setItem("isLeft", "true");
      sessionStorage.setItem("isRight", "false");
    });

    remoteSetButton.addEventListener("click", function () {
      let message = {};
      if (Gameplay.remote.right) {
          message = { type: "remote_ON", remote_player_pos: "right" };
        }
      else if (Gameplay.remote.left) {
          message = { type: "remote_ON", remote_player_pos: "left" };
        }
      else {
        alert("Please select the side of the remote player.");
        return;
      }
      console.log("right", Gameplay.remote.right, " left", Gameplay.remote.left," remoteMode", Gameplay.remote.remoteMode);
      sendMessage(message);
    });

    async function gameOver(data) {
      let winner = data.winner;
      if (winner === "left") {
        winner = sessionStorage.getItem("player1")
          ? sessionStorage.getItem("player1")
          : i18next.t("gameplay:popup.left");
      } else if (winner === "right") {
        winner = sessionStorage.getItem("player2")
          ? sessionStorage.getItem("player2")
          : i18next.t("gameplay:popup.right");
      }

      if (sessionStorage.getItem("isTournament") === "true") {
        const tournamentResponse = await fetchWithHandling(
          `${window.env.TOURNAMENT_HOST}/tournament/save-data/${localStorage.getItem("tournamentId")}/`,
        );
        if (tournamentResponse) {
          const tournamentData = await tournamentResponse.json();
          console.log("Tournament data get successfully:", tournamentData);

          const currentMatchId =
            parseInt(sessionStorage.getItem("currentMatch")) - 1;

          if (tournamentData && tournamentData.matches) {
            let currentMatch = tournamentData.matches[currentMatchId];

            currentMatch.player1_score = data.left_score;
            currentMatch.player2_score = data.right_score;
            currentMatch.winner = winner;
            console.log("currentMatch", currentMatch);

            const response = await fetchWithHandling(
              `${window.env.TOURNAMENT_HOST}/tournament/save-data/${localStorage.getItem("tournamentId")}/`,
              {
                method: "PUT",
                body: { currentMatch },
              },
            );
            const responseData = await response.json();
            console.log("Tournament data updated successfully:", responseData);
          }

          alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
          document.getElementById("nextGameButton").style.display = "block";
        }
      } else {
        alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
        document.getElementById("gameOverButton").style.display = "block";
      }
    }

    window.ws.onmessage = (e) => {
      if (window.ws === null || window.ws.readyState !== WebSocket.OPEN) return;
      if (!first) {
        gameStartButton.style.display = "none";
        remoteButton.style.display = "none";
        remoteOptions.style.display = "none";
      }
      const data = JSON.parse(e.data);
      if (data.type === "game_over") {
        gameOver(data);
        return;
      }
      if (data.type === "remote_OK"){
        Gameplay.remote.remoteMode= true;
        Gameplay.remote.ready = true;
        console.log("Remote OK");
        console.log("right", Gameplay.remote.right, " left", Gameplay.remote.left, " remoteMode", Gameplay.remote.remoteMode);
        return;
      }
      score.left = data.left_score;
      score.right = data.right_score;
      paddle.left_y = data.left_paddle_y;
      paddle.right_y = data.right_paddle_y;
      ball.x = data.ball_x;
      ball.y = data.ball_y;
      if (first) {
        console.log("firstだよ");
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
      if (window.ws === null || window.ws.readyState !== WebSocket.OPEN) return;
      window.ws.send(JSON.stringify(message));
    }

    Gameplay.keydownListener = (event) => {
      let paddle_instruction = null;
      console.log("keydownListener", event.key);
      console.log("remoteMode", Gameplay.remote.remoteMode, "RemoteLeft", Gameplay.remote.left, "RemoteRight", Gameplay.remote.right);
      if ((!Gameplay.remote.remoteMode|| (Gameplay.remote.remoteMode&& Gameplay.remote.left)) && (event.key === "D" || event.key === "d")) {
        paddle_instruction = {
          move_direction: "down",
          action: "start",
          side: "left",
        };
      } else if ((!Gameplay.remote.remoteMode|| (Gameplay.remote.remoteMode&& Gameplay.remote.left)) && (event.key === "E" || event.key === "e")) {
        paddle_instruction = {
          move_direction: "up",
          action: "start",
          side: "left",
        };
      } else if ((!Gameplay.remote.remoteMode|| (Gameplay.remote.remoteMode&& Gameplay.remote.right)) && (event.key === "I" || event.key === "i")) {
        paddle_instruction = {
          move_direction: "up",
          action: "start",
          side: "right",
        };
      } else if ((!Gameplay.remote.remoteMode|| (Gameplay.remote.remoteMode&& Gameplay.remote.right)) && (event.key === "K" || event.key === "k")) {
        paddle_instruction = {
          move_direction: "down",
          action: "start",
          side: "right",
        };
      }

      if (
        paddle_instruction &&
        paddle_instruction.side === "left" &&
        !Gameplay.isPaddleMoving.left
      ) {
        Gameplay.isPaddleMoving.left = true;
        sendMessage(paddle_instruction);
      }
      if (
        paddle_instruction &&
        paddle_instruction.side === "right" &&
        !Gameplay.isPaddleMoving.right
      ) {
        Gameplay.isPaddleMoving.right = true;
        sendMessage(paddle_instruction);
      }
    };

    Gameplay.keyupListener = (event) => {
      let paddle_instruction = null;
      if (event.key === "D" || event.key === "d") {
        paddle_instruction = {
          move_direction: "down",
          action: "stop",
          side: "left",
        };
      } else if (event.key === "E" || event.key === "e") {
        paddle_instruction = {
          move_direction: "up",
          action: "stop",
          side: "left",
        };
      } else if (event.key === "I" || event.key === "i") {
        paddle_instruction = {
          move_direction: "up",
          action: "stop",
          side: "right",
        };
      } else if (event.key === "K" || event.key === "k") {
        paddle_instruction = {
          move_direction: "down",
          action: "stop",
          side: "right",
        };
      }

      if (
        paddle_instruction &&
        paddle_instruction.side === "left" &&
        Gameplay.isPaddleMoving.left
      ) {
        Gameplay.isPaddleMoving.left = false;
        sendMessage(paddle_instruction);
      }
      if (
        paddle_instruction &&
        paddle_instruction.side === "right" &&
        Gameplay.isPaddleMoving.right
      ) {
        Gameplay.isPaddleMoving.right = false;
        sendMessage(paddle_instruction);
      }
    };

    if (!window.keydownListenerAdded) {
      document.addEventListener("keydown", Gameplay.keydownListener);
      document.addEventListener("keyup", Gameplay.keyupListener);
      window.keydownListenerAdded = true;
    }

    
    // 描画関数
    function draw() {
      ctx.clearRect(0, 0, gameCanvas.width, gameCanvas.height);
      ctx.fillStyle = "black";
      ctx.fillRect(0, 0, gameCanvas.width, gameCanvas.height);

      ctx.fillStyle = "white";
      ctx.fillRect(paddle.left_x, paddle.left_y, paddle_w, paddle_h);
      ctx.fillRect(
        paddle.right_x - paddle_w,
        0 + paddle.right_y,
        paddle_w,
        paddle_h,
      );
      ctx.fillRect(
        ball.x - ball.radius,
        ball.y - ball.radius,
        2 * ball.radius,
        2 * ball.radius,
      );

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
      if (timestamp - lastUpdateTime >= 1000 / FPS) {
        lastUpdateTime += 1000 / FPS;
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
      console.log("WebSocket closed",sessionStorage.getItem("settingId"));
    }

    if (
      sessionStorage.getItem("settingId") &&
      sessionStorage.getItem("isTournament") !== "true"
    ) {
      await fetchWithHandling(
        `${window.env.GAMEPLAY_HOST}/gamesetting/${window.sessionStorage.getItem("settingId")}/`,
        {
          method: "DELETE",
        },
      );

      sessionStorage.removeItem("settingId");
      console.log(
        "Settings deleted successfully:",
        sessionStorage.getItem("settingId"),
      );
    }

    const tournamentButton = document.getElementById("navbar:tournament");
    if (tournamentButton) {
      tournamentButton.setAttribute("href", "#/tournament");
      tournamentButton.classList.replace("disabled", "active");
    } // トーナメントボタンを有効に
  },
};

export default Gameplay;
