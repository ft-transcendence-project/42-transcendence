import { fetchHtml } from "../../utils/fetchHtml.js";

const Home = {
  render: async () => {
    return await fetchHtml("/views/templates/Home.html");
  },
  after_render: async () => {},
};

export default Home;
