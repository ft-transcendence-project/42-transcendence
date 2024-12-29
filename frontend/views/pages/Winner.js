import { updateContent } from "../../utils/i18n.js";

const WinnerPage = {
  render: async () => {
    return (await fetch("/views/templates/winner.html")).text();
  },

  after_render: async () => {
    updateContent();

    const winner = sessionStorage.getItem("gameWinner");

    document.getElementById("winner").textContent = winner;

    sessionStorage.removeItem("gameWinner");
  },
};

export default WinnerPage;
