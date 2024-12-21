import { updateContent } from "../../utils/i18n.js";

const Home = {
  render: async () => {
		return (await fetch("/views/templates/Home.html")).text();
  },
  after_render: async () => {
    updateContent();
  },
};

export default Home;
