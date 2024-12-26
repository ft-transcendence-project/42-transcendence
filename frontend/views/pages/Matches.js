const Matches = {
  render: async () => {
    return (await fetch("/views/templates/Matches.html")).text();
  },

  after_render: async function () {
    try {
      const currentMatch = Number(sessionStorage.getItem("currentMatch"));
      const response = await this.fetchTournamentData();
      const storedData = await response.json();

      await this.handleMatchData(currentMatch, storedData);
    } catch (error) {
      console.error("Error handling tournament data:", error);
      alert("Failed to load tournament data");
      return (window.location.hash = "#/tournament");
    }
  },

  async fetchTournamentData() {
    const response = await fetch(
      `${window.env.BACKEND_HOST}/tournament/api/save-data/`
    );
    if (!response.ok) throw new Error(`HTTP Error Status: ${response.status}`);
    return response;
  },

  async handleMatchData(currentMatch, storedData) {
    if (!storedData) {
      alert("No tournament data found in database.");
      return (window.location.hash = "#/tournament");
    }

    if (!currentMatch) {
      currentMatch = this.initializeCurrentMatch(storedData);
    }

    const matchData = storedData.matches[currentMatch - 1];

    if (matchData.player1 && matchData.player2) {
      sessionStorage.setItem("player1", matchData.player1.name);
      sessionStorage.setItem("player2", matchData.player2.name);
    } else {
      alert("Player information not found");
      return (window.location.hash = "#/tournament");
    }

    sessionStorage.setItem("matchData", JSON.stringify(matchData));
    updateMatchDisplay(storedData);
  },

  initializeCurrentMatch(storedData) {
    const firstUnplayedMatch = storedData.matches.findIndex(
      (match) => match.player1_score === 0 && match.player2_score === 0
    );

    const nextMatch = firstUnplayedMatch === -1 ? 1 : firstUnplayedMatch + 1;
    sessionStorage.setItem("currentMatch", nextMatch);
    return nextMatch;
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

      player1Div.classList.remove("winner");
      player2Div.classList.remove("winner");

      const winner = match.winner?.name;
      if (winner === player1) {
        player1Div.classList.add("winner");
      } else if (winner === player2) {
        player2Div.classList.add("winner");
      }
    }
  });
}

export default Matches;
