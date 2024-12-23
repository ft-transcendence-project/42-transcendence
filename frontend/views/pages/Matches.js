const Matches = {
  render: async () => {
    return (await fetch("/views/templates/Matches.html")).text();
  },

  after_render: async () => {
    try {
      let currentMatch = parseInt(sessionStorage.getItem("currentMatch"));
      console.log(currentMatch);

      const response = await fetch(`${window.env.BACKEND_HOST}/tournament/api/save-data/`);
      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error updating tournament data:", errorData);
        throw new Error(`HTTP Error Status: ${response.status}`);
      }

      const storedData = await response.json();
      console.log("Tournament data updated successfully:", storedData);

      if (storedData) {
        const currentMatchData = storedData.matches[currentMatch - 1];

        sessionStorage.setItem("player1", currentMatchData.player1.name);
        console.log(sessionStorage.getItem("player1"));
        sessionStorage.setItem("player2", currentMatchData.player2.name);
        console.log(sessionStorage.getItem("player2"));
        console.log(storedData);
        updateMatchDisplay(storedData);
      } else {
        alert("No tournament data found in session storage.");
        window.location.hash = "#/tournament";
      }
    } catch (error) {
      console.error("Error handling tournament data:", error);
    }
  },
};

function updateMatchDisplay(tournament) {
  // Round 1 matches
  tournament.matches.forEach((match) => {
    const player1 = match.player1.name;
    const player2 = match.player2.name;
    const score1 = match.player1_score;
    const score2 = match.player2_score;
    const winner = match.winner;

    const matchNumber = match.match_number;
    if (matchNumber <= 4) {
      const player1Div = document.querySelector(`#match${matchNumber}-player1`);
      if (player1Div.firstChild?.nodeType === Node.TEXT_NODE) {
        player1Div.firstChild.textContent = player1;
      } else {
        player1Div.insertBefore(
          document.createTextNode(player1),
          player1Div.firstChild
        );
      }

      const player2Div = document.querySelector(`#match${matchNumber}-player2`);
      if (player2Div.firstChild?.nodeType === Node.TEXT_NODE) {
        player2Div.firstChild.textContent = player2;
      } else {
        player2Div.insertBefore(
          document.createTextNode(player2),
          player2Div.firstChild
        );
      }

      if (score1 > 0 || score2 > 0) {
        document.querySelector(`#match${matchNumber}-score1`).textContent =
          score1;
        document.querySelector(`#match${matchNumber}-score2`).textContent =
          score2;
      }

      player1Div.classList.remove("winner");
      player2Div.classList.remove("winner");

      if (winner === player1) {
        player1Div.classList.add("winner");
      } else if (winner === player2) {
        player2Div.classList.add("winner");
      }
    }
  });
}

export default Matches;
