import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const Tournament = {
  render: async () => {
    return (await fetchHtml("/views/templates/Tournament.html"));
  },

  after_render: async () => {
    sessionStorage.setItem("isTournament", "true");
    sessionStorage.removeItem("winner");

    // トーナメントデータがあり、終了していない場合は続きを行う
    const response = await fetchWithHandling(
      `${
        window.env.TOURNAMENT_HOST
      }/tournament/save-data/${localStorage.getItem("tournamentId")}/`
    );
    if (response) {
      const tournamentData = await response.json();
      if (!sessionStorage.getItem("settingId")) {
        window.location.hash = "#/gamesetting";
        return;
      } else if (tournamentData?.is_over === false) {
        window.location.hash = "#/matches";
        return;
      }
    }

    sessionStorage.setItem("currentMatch", 1);

    document
      .getElementById("tournament-form")
      .addEventListener("submit", async (event) => {
        event.preventDefault();
        const users = [];

        for (let index = 0; index < 8; index++) {
          if (document.getElementById(`player${index + 1}`).value) {
            users.push(document.getElementById(`player${index + 1}`).value);
          } else {
            users.push(`player${index + 1}`);
          }
        }

        const uniqueUsers = [...new Set(users)];

        const response = await fetchWithHandling(
          `${window.env.TOURNAMENT_HOST}/tournament/register/`,
          {
            method: "POST",
            body: uniqueUsers,
          },
          "tournament:errors.register"
        );
        const data = await response.json();
        if (response) {
          console.log(data);
          localStorage.setItem("tournamentId", data.id);
          window.location.hash = "#/gamesetting";
        }
      });
  },
};

export default Tournament;
