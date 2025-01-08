const Home = {
  render: async () => {
    return (await fetch("/views/templates/Home.html")).text();
  },
  after_render: async () => {},
};

export default Home;
