import { updateContent } from "../../utils/i18n.js";

const WinnerPage = {
  render: async () => {
    return (await fetch("/views/templates/Winner.html")).text();
  },

  after_render: async () => {
    updateContent();

    const winner = sessionStorage.getItem("winner");

    document.getElementById("winner").textContent = winner;

    sessionStorage.removeItem("winner");
  },
};

export default WinnerPage;
