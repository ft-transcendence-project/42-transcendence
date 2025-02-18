export const setUpGameCanvas = () => {
    const gameCanvas = document.getElementById("gameCanvas");
    const ctx = gameCanvas.getContext("2d");
    gameCanvas.width = 1000;
    gameCanvas.height = 600;
    const center_x = gameCanvas.width / 2;
    const center_y = gameCanvas.height / 2;
    return { gameCanvas, ctx, center_x, center_y };
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

