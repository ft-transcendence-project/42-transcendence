import { changeLanguage } from "../../utils/i18n.js";
import { fetchWithHandling, fetchWithHandling } from "../../utils/fetchWithHandling.js";
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

      const response = await fetchWithHandling(
        `${window.env.ACCOUNT_HOST}/accounts/api/login/`,
        {
          method: "POST",
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
          const params = new URLSearchParams({ user: username });
          window.location.hash = `#/verify-otp?${params}`;
          return;
        }
        document.cookie = `isLoggedIn=true; path=/; max-age=86400`;
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
