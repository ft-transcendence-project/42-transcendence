import { fetchWithHandling } from "../../utils/fetchWithHandling.js";

const Home = {
  render: async () => {
    return (await fetchWithHandling("/views/templates/Home.html")).text();
  },
  after_render: async () => {},
};

export default Home;
