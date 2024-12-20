const Matches = {
  render: async () => {
    return (await fetch("/views/templates/Matches.html")).text();
  },

  after_render: async () => {
    try {
      let currentMatch;
      if (sessionStorage.getItem("currentMatch")) {
        currentMatch = parseInt(sessionStorage.getItem("currentMatch"));
        currentMatch = currentMatch >= 4 ? 1 : currentMatch + 1;
      } else {
        currentMatch = 1;
      }
      sessionStorage.setItem("currentMatch", currentMatch);
      console.log(currentMatch);

      const storedData = sessionStorage.getItem("tournamentData");
      if (storedData) {
        const tournamentData = JSON.parse(storedData);
        const currentMatchData = tournamentData.matches[currentMatch - 1];

        sessionStorage.setItem("player1", currentMatchData.player1.name);
        console.log(sessionStorage.getItem("player1"));
        sessionStorage.setItem("player2", currentMatchData.player2.name);
        console.log(sessionStorage.getItem("player2"));
        console.log(tournamentData);
        updateMatchDisplay(tournamentData);
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
    }
  });
}

export default Matches;
