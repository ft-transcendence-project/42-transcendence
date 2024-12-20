"use strict";

import Navbar from "./views/components/Navbar.js";
import Login from "./views/pages/Login.js";
import SignUp from "./views/pages/SignUp.js";
import SetupOtp from "./views/pages/SetUpOtp.js";
import Home from "./views/pages/Home.js";
import Gameplay from "./views/pages/Gameplay.js";
import Tournament from "./views/pages/Tournament.js";
import Matches from "./views/pages/Matches.js";

const routes = {
  "/": Home,
  "/login": Login,
  "/signup": SignUp,
  "/setup-otp": SetupOtp,
  "/gameplay": Gameplay,
  "/tournament": Tournament,
  "/matches": Matches,
};

const router = async () => {
  const header = null || document.getElementById("header_container");
  const body = null || document.getElementById("body_container");
  const footer = null || document.getElementById("footer_container");

  // footer

  const location = window.location.hash.slice(1).toLowerCase() || "/";
  console.log(location);

  if (window.currentPage && window.currentPage.cleanup) {
    window.currentPage.cleanup();
  }

  const page = routes[location];
  window.currentPage = page;

  body.innerHTML = await page.render();
  await page.after_render();
};

window.addEventListener("hashchange", router);

window.addEventListener("load", router);

window.addEventListener("DOMContentLoaded", Navbar.setTranslateHook());
