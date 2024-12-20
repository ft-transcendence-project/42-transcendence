import { updateContent } from "../../utils/i18n.js";

const Tournament = {
  render: async () => {
    return (await fetch("/views/templates/Tournament.html")).text();
  },

  after_render: async () => {
    updateContent();

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

        try {
          const response = await fetch(
            `${window.env.BACKEND_HOST}/tournament/api/register/`,
            {
              method: "POST",
              headers: {
                "Content-Type": "application/json",
              },
              body: JSON.stringify(users),
            }
          );

          const data = await response.json();

          if (response.ok) {
            console.log(data);
            sessionStorage.setItem("tournamentData", JSON.stringify(data));
            window.location.hash = "#/matches";
          } else {
            const errors = Object.entries(data)
              .map(([k, v]) => {
                return `${k}: ${v}`;
              })
              .join(", ");
            console.error("Tournament register failed: ", errors);
            alert("Tournament register failed: ", errors);
          }
        } catch (error) {
          console.error("Unknown error: ", error);
          alert("Unknown error: ", error);
        }
      });
  },
};

export default Tournament;
