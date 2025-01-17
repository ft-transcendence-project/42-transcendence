import { changeLanguage } from "../../utils/i18n.js";
import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const Login = {
  render: async () => {
    return (await fetchHtml("/views/templates/Login.html"));
  },

  after_render: async () => {
    const loginForm = document.getElementById("login-form");

    loginForm.addEventListener("submit", async (event) => {
      event.preventDefault();

      if (!loginForm.checkValidity()) {
        event.stopPropagation();
        loginForm.classList.add("was-validated");
        return;
      }

      loginForm.classList.add("was-validated");

      let username = document.getElementById("id_username").value;
      let password = document.getElementById("id_password").value;

      function getCSRFToken() {
        return document.cookie
          .split("; ")
          .find((row) => row.startsWith("csrftoken="))
          ?.split("=")[1];
      }

      const response = await fetchWithHandling(
        `${window.env.ACCOUNT_HOST}/accounts/api/login/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: { username, password },
        },
        "login:errors.login"
      );
      const data = await response.json();
      if (response) {
        console.log("Login success: ", data);
        event.preventDefault();
        changeLanguage(data.default_language);
        if (data.redirect === "accounts:verify_otp") {
          sessionStorage.setItem("user", username);
          window.location.hash = "#/verify-otp";
          return;
        }
        window.location.hash = "#/";
      }
    });

    document
      .getElementById("oauth-login")
      .addEventListener("click", async (event) => {
        event.preventDefault();
        window.location.href = `${window.env.ACCOUNT_HOST}/oauth/`;
      });

    document
      .getElementById("sign-up")
      .addEventListener("click", async (event) => {
        event.preventDefault();
        window.location.hash = "#/signup";
      });
  },
};

export default Login;
