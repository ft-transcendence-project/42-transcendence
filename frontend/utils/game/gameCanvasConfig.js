export const setUpGameCanvas = () => {
    const gameCanvas = document.getElementById("gameCanvas");
    const ctx = gameCanvas.getContext("2d");
    gameCanvas.width = 1000;
    gameCanvas.height = 600;
    const center_x = gameCanvas.width / 2;
    const center_y = gameCanvas.height / 2;
    const settingId = sessionStorage.getItem("settingId");
    const player1 = sessionStorage.getItem("player1");
    if (player1) {
      document.getElementById("player1").textContent = player1;
    }
    const player2 = sessionStorage.getItem("player2");
    if (player2) {
      document.getElementById("player2").textContent = player2;
    }
    console.log("SettingId in Gameplay:", settingId);
    document.getElementById("gameId").innerText =
      `game id = ${sessionStorage.getItem("settingId")}`;
    return { gameCanvas, ctx, center_x, center_y , settingId, player1, player2};
}

export const getGameOptions = (center_x, center_y) => {
    return {
        obstacle1: {
            x: center_x,
            y: center_y,
            width: 0,
            height: 0,
          },
          obstacle2: {
            x: center_x,
            y: center_y,
            width: 0,
            height: 0,
          },
          blind: {
            x: 0,
            y: 0,
            width: 0,
            height: 0,
          }
    };
}

