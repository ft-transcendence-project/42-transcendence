import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";
import { setUpGameCanvas } from "../../utils/game/gameCanvasConfig.js";
import { getGameOptions } from "../../utils/game/gameCanvasConfig.js";

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
    isRemote : false,
    ready: false,
  },

  after_render: async () => {
    const { gameCanvas, ctx, center_x, center_y , settingId} = setUpGameCanvas();
    const { obstacle1, obstacle2, blind } = getGameOptions(center_x, center_y);
    let first = true;
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

    window.ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    const gameStartButton = document.getElementById("game-start");
    const remote = document.getElementById("remote");
    const selectRemoteButton = document.getElementById("select-remote");
    const remoteOptions = document.getElementById("remote-options");
    const rightButton = document.getElementById("remote-right");
    const leftButton = document.getElementById("remote-left");
    const setRemoteButton = document.getElementById("set-remote");

    // ボタンにクリックイベントを追加
    gameStartButton.addEventListener("click", function (){
      console.log("Game Startボタンが押されました");
      if (!Gameplay.remote.isRemote || (Gameplay.remote.isRemote && Gameplay.remote.ready)) {
        window.ws.send(JSON.stringify({ game_signal: "start" }));
      }
      else
        alert(i18next.t("gameplay:error.start"));
    });

    selectRemoteButton.addEventListener("click", function () {
      if (selectRemoteButton.textContent === i18next.t("gameplay:Remote_OFF"))
        enableRemoteMode();
      else if (selectRemoteButton.textContent === i18next.t("gameplay:Remote_ON"))
        disableRemoteMode();

      function enableRemoteMode() {
        selectRemoteButton.textContent = i18next.t("gameplay:Remote_ON");
        remoteOptions.style.display = "block";
        Gameplay.remote.isRemote= true;
      }

      function  disableRemoteMode() {
        selectRemoteButton.textContent = i18next.t("gameplay:Remote_OFF");
        remoteOptions.style.display = "none";
        leftButton.style.backgroundColor = "white";
        rightButton.style.backgroundColor = "white";
        Gameplay.remote.isRemote= false;
        if (Gameplay.remote.left) {
          Gameplay.remote.left = false;
          sendMessage({ type: "remote_OFF", remote_player_pos: "left" });
        }
        else if (Gameplay.remote.right) {
          Gameplay.remote.right = false;
          sendMessage({ type: "remote_OFF", remote_player_pos: "right" });
        }
      }
    });

    rightButton.addEventListener("click", function () {
      Gameplay.remote.right = true;
      Gameplay.remote.left = false; 
      rightButton.style.backgroundColor = "orange";
      leftButton.style.backgroundColor = "white";
    });
    
    leftButton.addEventListener("click", function () {
      Gameplay.remote.left = true;
      Gameplay.remote.right = false;
      leftButton.style.backgroundColor = "orange";
      rightButton.style.backgroundColor = "white";
    });

    setRemoteButton.addEventListener("click", function () {
      let message = {};
      if (Gameplay.remote.right) {
          message = { type: "remote_ON", remote_player_pos: "right" };
        }
      else if (Gameplay.remote.left) {
          message = { type: "remote_ON", remote_player_pos: "left" };
        }
      else {
        alert(i18next.t("gameplay:error.remote_player"));
        return;
      }
      sendMessage(message);
    });

    async function getWinner(data)
    {
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
      console.log("Winner:", winner);
      return winner; 
    }

    async function gameOver(data) {
      const winner = await getWinner(data);
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

    window.ws.onmessage = async (e) => {
      try {
        if (window.ws === null || window.ws.readyState !== WebSocket.OPEN) return;
        const data = JSON.parse(e.data);
        switch (data.type) {
          case "start_OK":
            gameStartButton.style.display = "none";
            remote.classList.add("d-none");
            break;
          case "remote_OK":
            console.log("Remote OK");
            Gameplay.remote.isRemote = true;
            Gameplay.remote.ready = true;
            remote.classList.add("d-none");
            let remotePos = document.getElementById("remote-pos");
            if (data.player === "right")
              remotePos.textContent = i18next.t("gameplay:player_pos.right");
            else if (data.player === "left")
              remotePos.textContent = i18next.t("gameplay:player_pos.left");
            break;
          case "game_over":
            await gameOver(data);
            break;
        case "interrupted":
          alert(i18next.t("gameplay:error.interrupted"));
          await gameOver(data);
          break;
        case "interrupted before start":
          gameStartButton.style.display = "none";
          remote.classList.add("d-none");
          alert(i18next.t("gameplay:error.interrupted"));
          document.getElementById("gameOverButton").style.display = "block";
          break;
        case "reload":
          alert(i18next.t("gameplay:error.reload"));
          const winner = await getWinner(data);
          alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
          gameStartButton.style.display = "none";
          remote.classList.add("d-none");
          document.getElementById("gameOverButton").style.display = "block";
          break;
        default:
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
          break;
        }
      } catch (error) {
        console.error("WebSocket message error:", error);
      }
    };

    function sendMessage(message) {
      if (window.ws === null || window.ws.readyState !== WebSocket.OPEN) return;
      window.ws.send(JSON.stringify(message));
    }

    Gameplay.keydownListener = (event) => {
      let paddle_instruction = null;
      if ((!Gameplay.remote.isRemote|| (Gameplay.remote.isRemote&& Gameplay.remote.left)) && (event.key === "D" || event.key === "d")) {
        paddle_instruction = {
          move_direction: "down",
          action: "start",
          side: "left",
        };
      } else if ((!Gameplay.remote.isRemote|| (Gameplay.remote.isRemote&& Gameplay.remote.left)) && (event.key === "E" || event.key === "e")) {
        paddle_instruction = {
          move_direction: "up",
          action: "start",
          side: "left",
        };
      } else if ((!Gameplay.remote.isRemote|| (Gameplay.remote.isRemote&& Gameplay.remote.right)) && (event.key === "I" || event.key === "i")) {
        paddle_instruction = {
          move_direction: "up",
          action: "start",
          side: "right",
        };
      } else if ((!Gameplay.remote.isRemote|| (Gameplay.remote.isRemote&& Gameplay.remote.right)) && (event.key === "K" || event.key === "k")) {
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
