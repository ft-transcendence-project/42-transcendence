import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const Remote = {
    render: async () => {
        return await fetchHtml("/views/templates/Remote.html");
    },

    after_render: async () => {
        document.getElementById("game-id-form").addEventListener("submit", async (event) => {
            event.preventDefault();
            try {
              const gameId = document.getElementById("game-id");
              if (gameId.value) {
                sessionStorage.setItem("settingId", gameId.value);
                const settingId = sessionStorage.getItem("settingId");
                const response = await fetchWithHandling(
                  `${window.env.GAMEPLAY_HOST}/gamesetting/${settingId}/`,
                  {
                    method: "GET",
                  },
                );
                if (!response.ok) {
                  throw new Error("Game ID not found");
                }
                const responseData = await response.json();
                console.log("settingdata GET successfully:", responseData);
                window.location.hash = `#/gameplay.${settingId}/`;
              }
            } catch (error) {
              console.error("Error:", error);
              alert(i18next.t("gameplay:error.game_id"));
            }
        });
    },
};
export default Remote;
