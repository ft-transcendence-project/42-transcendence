const WinnerPage = {
  render: async () => {
    return (await fetch("/views/templates/Winner.html")).text();
  },

  after_render: async () => {
    const winner = sessionStorage.getItem("winner");
    document.getElementById("winner").textContent = winner;
  },
};

export default WinnerPage;
