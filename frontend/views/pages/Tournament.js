import { updateContent } from "../../utils/i18n.js";

const Tournament = {
  render: async () => {
    return (await fetch("/views/templates/Tournament.html")).text();
  },

  after_render: async () => {
    updateContent();

    sessionStorage.setItem("currentMatch", 1);
    sessionStorage.setItem("isTournament", "true");

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

        try {
          const response = await fetch(
            `${window.env.BACKEND_HOST}/tournament/api/register/`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(uniqueUsers),
            }
          );

          const data = await response.json();

          if (response.ok) {
            console.log(data);
            window.location.hash = "#/gamesetting";
          } else {
            const errors = Object.entries(data)
              .map(([k, v]) => {
                return `${k}: ${v}`;
              })
              .join(", ");
            console.error("Tournament register failed", errors);
            alert("Tournament register failed");
          }
        } catch (error) {
          console.error("Unknown error: ", error);
          alert("Unknown error: ", error);
        }
      });
  },
};

export default Tournament;
