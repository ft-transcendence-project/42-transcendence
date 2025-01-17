import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const Logout = {
  render: async () => {
    try {
      const response = await fetch(
        `${window.env.ACCOUNT_HOST}/accounts/api/logout/`,
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Logout failed");
      }

      document.cookie =
        "isLoggedIn=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
      document.cookie = "default_language=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
    } catch (error) {
      console.error("Failed to logout:", error);
      alert(i18next.t("login:errors.logout"));
      return;
    }

    return (await fetchHtml("/views/templates/Logout.html"));
  },

  after_render: async () => {
    const logoutButton = document.getElementById("navbar:logout");
    if (logoutButton) {
      logoutButton.setAttribute("href", "#/login");
      logoutButton.setAttribute("data-i18n", "navbar:login");
      logoutButton.id = "navbar:login";
      logoutButton.textContent = "Login";
    }

    const setupOtpButton = document.getElementById("navbar:setup-otp");
    if (setupOtpButton) {
      setupOtpButton.removeAttribute("href");
      setupOtpButton.classList.add("disabled");
    }
  },
};

export default Logout;
