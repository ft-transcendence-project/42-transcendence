import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const WinnerPage = {
  render: async () => {
    return (await fetchHtml("/views/templates/Winner.html"));
  },

  after_render: async () => {
    const winner = sessionStorage.getItem("winner");
    document.getElementById("winner").textContent = winner;
  },
};

export default WinnerPage;
