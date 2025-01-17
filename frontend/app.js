"use strict";

import Navbar from "./views/components/Navbar.js";
import Login from "./views/pages/Login.js";
import Logout from "./views/pages/Logout.js";
import SignUp from "./views/pages/SignUp.js";
import SetupOtp from "./views/pages/SetupOtp.js";
import VerifyOtp from "./views/pages/VerifyOtp.js";
import Home from "./views/pages/Home.js";
import Gameplay from "./views/pages/Gameplay.js";
import GameSetting from "./views/pages/GameSetting.js";
import Tournament from "./views/pages/Tournament.js";
import Matches from "./views/pages/Matches.js";
import WinnerPage from "./views/pages/Winner.js";

import { updateContent } from "./utils/i18n.js";

const routes = {
  "/": Home,
  "/login": Login,
  "/logout": Logout,
  "/signup": SignUp,
  "/setup-otp": SetupOtp,
  "/verify-otp": VerifyOtp,
  "/gameplay": Gameplay,
  "/gamesetting": GameSetting,
  "/tournament": Tournament,
  "/matches": Matches,
  "/winner": WinnerPage,
};

const getCookie = (name) => {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) {
    const val = parts.pop().split(";").shift();
    return val && val.length > 0 ? val : null;
  }
  return null;
};

const router = async () => {
  const header = null || document.getElementById("header_container");
  const body = null || document.getElementById("body_container");
  const footer = null || document.getElementById("footer_container");

  let location = window.location.hash.slice(1).toLowerCase() || "/";
  console.log(location);

  const gameplayMatch = location.match(/^\/gameplay\.(\d+)/);  // 数字の部分をキャッチ
  if (gameplayMatch) {
    const settingId = gameplayMatch[1];  // settingId（例: '1'）を取得
    sessionStorage.setItem("settingId", settingId);  // sessionStorage に保存
    location = '/gameplay'; // locationを'/gameplay'に変更して遷移させる
  }

  if (window.currentPage && window.currentPage.cleanup) {
    window.currentPage.cleanup();
  }

  const page = routes[location];
  console.log(page);
  window.currentPage = page;

  if (getCookie("token")) {
    const loginButton = document.getElementById("navbar:login");
    if (loginButton) {
      loginButton.setAttribute("href", "#/logout");
      loginButton.setAttribute("data-i18n", "navbar:logout");
      loginButton.id = "navbar:logout";
      loginButton.textContent = "Logout";
    }
    if (getCookie("token") != "dummy") {
      const setupOtpButton = document.getElementById("navbar:setup-otp");
      if (setupOtpButton) {
        setupOtpButton.setAttribute("href", "#/setup-otp");
        setupOtpButton.classList.remove("disabled");
      }
    }
  }

  const gameplayButton = document.getElementById("navbar:gameplay");
  if (gameplayButton && sessionStorage.getItem("isTournament") === "true") {
    // トーナメントの場合ゲーム画面へ飛べないように
    gameplayButton.removeAttribute("href");
    gameplayButton.classList.replace("active", "disabled");
  } else if (gameplayButton) {
    gameplayButton.setAttribute("href", "#/gamesetting");
    gameplayButton.classList.replace("disabled", "active");
  }

  // footer

  body.innerHTML = DOMPurify.sanitize(await page.render());
  updateContent();
  await page.after_render();
};

window.addEventListener("hashchange", router);

window.addEventListener("load", router);

window.addEventListener("DOMContentLoaded", Navbar.setTranslateHook());
