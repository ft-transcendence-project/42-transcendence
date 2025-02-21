import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";
import {Game, Paddle, Ball, Obstacle, Score} from "../../utils/game/Game.js";

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
    let first = true;
    const game = new Game();
    let paddle = new Paddle(game);
    let score = new Score();
    let obstacle1 = null;
    let obstacle2 = null;
    let blind = null;
    let ball = null;
    let animationFrameId = null;
    game.displayGameId();
    game.displayPlayers();
    // Websocket
    const url = `${window.env.GAMEPLAY_WS_HOST}/ponglogic/${game.settingId}/`;
    window.ws = new WebSocket(url);
    console.log(url + " WebSocket created");

    window.ws.onopen = () => {
      console.log("WebSocket opened");
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
        }
      }
      alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
      document.getElementById("gameOverButton").style.display = "block";
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
            handleRemoteOK();
            break;
          case "game_over":
            await gameOver(data);
            break;
        case "interrupted":
          alert(i18next.t("gameplay:error.interrupted"));
          await gameOver(data);
          break;
        case "interrupted before start":
          await handleInterruptedBeforeStart();
          break;
        case "reload":
          handleReload();
          break;
        default:
          updateGameState(data);
          break;
        }

      function handleRemoteOK(){
        console.log("Remote OK");
          Gameplay.remote.isRemote = true;
          Gameplay.remote.ready = true;
          remote.classList.add("d-none");
          let remotePos = document.getElementById("remote-pos");
          if (data.player === "right")
            remotePos.textContent = i18next.t("gameplay:player_pos.right");
          else if (data.player === "left")
            remotePos.textContent = i18next.t("gameplay:player_pos.left");
        }
      
      function handleInterruptedBeforeStart(){
        gameStartButton.style.display = "none";
          remote.classList.add("d-none");
          alert(i18next.t("gameplay:error.interrupted"));
          document.getElementById("gameOverButton").style.display = "block";
      }
      
      async function handleReload(){
        alert(i18next.t("gameplay:error.reload"));
          const winner = await getWinner(data);
          alert(`${i18next.t("gameplay:popup.game_over")} ${winner}`);
          gameStartButton.style.display = "none";
          remote.classList.add("d-none");
          document.getElementById("gameOverButton").style.display = "block";
      }

      function updateGameState(data) {
        if (first) {
          obstacle1 = new Obstacle(data.obstacle1_x, data.obstacle1_y, data.obstacle1_width, data.obstacle1_height);
          obstacle2 = new Obstacle(data.obstacle2_x, data.obstacle2_y, data.obstacle2_width, data.obstacle2_height);
          blind = new Obstacle(data.blind_x, data.blind_y, data.blind_width, data.blind_height);
          ball = new Ball(game, data.ball_radius);
          first = false;
          if (!animationFrameId)
            animationFrameId = requestAnimationFrame(update);
        }
        score.setScore(data.left_score, data.right_score);
        paddle.setPaddlePosition(data.left_paddle_y, data.right_paddle_y);
        ball.setBallPosition(data.ball_x, data.ball_y);
      } 
    }catch (error) {
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
      game.drawGameCanvas();
      paddle.drawPaddle(game);
      ball.drawBall(game);
      score.drawScore(game);
      if (obstacle1)
        obstacle1.drawObstacle(game,"yellow");
      if (obstacle2)
        obstacle2.drawObstacle(game,"yellow");
      if (blind)
        blind.drawObstacle(game,"red");
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
