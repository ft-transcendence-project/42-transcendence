import { updateContent } from "../../../utils/i18n.js";

const GameSetting = {
  render: async () => {
    return (await fetch("/views/templates/GameSetting.html")).text();
  },
  after_render: async () => {
    updateContent();

    document.getElementById("play-button").addEventListener("click", async () => {
      // 各設定値を取得
      const velocity = document.querySelector('input[name="velocity"]:checked').id.replace("velocity-", "");
      const ballSize = document.querySelector('input[name="ball-size"]:checked').id.replace("size-", "");
      const map = document.querySelector('input[name="map"]:checked').id.replace("map-", "");

      // 送信データを構築
      const settings = {
        ball_velocity: velocity,
        ball_size: ballSize,
        map: map,
      };

      try {
        // PUTリクエストを送信
        console.log(`${window.env.GAMEPLAY_HOST}/gamesetting/api/`);
        const response = await fetch(
          `${window.env.GAMEPLAY_HOST}/gamesetting/api/`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(settings),
        });

        if (!response.ok) {
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        // 成功時の処理
        const responseData = await response.json();
        const settingId = responseData.id;
        console.log("Settings updated successfully:", settings);
        localStorage.setItem("settingId", settingId);
        console.log("Settings ID saved to localStorage:", window.localStorage.getItem("settingId"));
        window.location.hash = `#/gameplay`; // Gameplay画面へ遷移
      } catch (error) {
        console.error("Failed to update settings:", error);
      }
    });
  },
};

export default GameSetting;