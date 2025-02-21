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
                const settingIdResponse = await fetchWithHandling(
                  `${window.env.GAMEPLAY_HOST}/gamesetting/${settingId}/`,
                  {
                    method: "GET",
                  },
                );
                if (!settingIdResponse.ok) {
                  throw new Error("Game ID not found");
                }
                const settingIdResponseData = await settingIdResponse.json();
                console.log("settingdata GET successfully:", settingIdResponseData);
                const tournamentResponse = await fetchWithHandling(`${window.env.TOURNAMENT_HOST}/tournament/get-game-id/${settingId}/`, 
                {
                  method: "GET",
                });
                if (tournamentResponse.ok) {
                  if (tournamentResponse.status === 204) {
                    console.log("No tournament found for this game id");
                  }
                  else {
                    const tournamentData = await tournamentResponse.json();
                    console.log(`The game id is ${settingId} and the tournament id is ${tournamentData.id}`);
                    let unfinishedMatches = tournamentData.matches.filter(match => !match.is_finished).sort((a,b) => a.match_number - b.match_number);
                    let unfinishedMatch = unfinishedMatches.sort((a,b) => a.round - b.round)[0];
                    console.log("unfinishedMatch", unfinishedMatch);
                    const player1 = unfinishedMatch.player1.name;
                    const player2 = unfinishedMatch.player2.name;
                    sessionStorage.setItem("player1", player1);
                    sessionStorage.setItem("player2", player2);
                  }
                }
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
