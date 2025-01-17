import { updateContent } from "../../../utils/i18n.js";
import { fetchWithHandling } from "../../utils/fetchWithHandling.js"
import { fetchHtml } from "../../utils/fetchHtml.js";

const GameSetting = {
  render: async () => {
    return (await fetchHtml("/views/templates/GameSetting.html"));
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

      // PUTリクエストを送信
      console.log(`${window.env.GAMEPLAY_HOST}/gamesetting/`);
      const response = await fetchWithHandling(
        `${window.env.GAMEPLAY_HOST}/gamesetting/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: settings,
      });

      if (response) {
        // 成功時の処理
        const responseData = await response.json();
        const settingId = responseData.id;
        console.log("Settings updated successfully:", settings);
        sessionStorage.setItem("settingId", settingId);
        console.log("Settings ID saved to sessionStorage:", sessionStorage.getItem("settingId"));
        if (sessionStorage.getItem("isTournament") === "true") {
            window.location.hash = `#/matches`; // Matches画面へ遷移
            return;
        }
        window.location.hash = `#/gameplay.${settingId}/`; // Gameplay画面へ遷移
        const tournamentButton = document.getElementById("navbar:tournament");
        if (tournamentButton) {
            tournamentButton.removeAttribute("href");
            tournamentButton.classList.replace("active", "disabled");
        } // トーナメントボタンを無効に
      }
    });
  },
};

export default GameSetting;