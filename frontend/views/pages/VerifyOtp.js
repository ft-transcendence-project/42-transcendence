import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const VerifyOtp = {
  render: async () => {
    return (await fetchHtml("/views/templates/VerifyOtp.html"));
  },

  after_render: async () => {
    const form = document.getElementById("verify-otp-form");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      function getCSRFToken() {
        return document.cookie
          .split("; ")
          .find((row) => row.startsWith("csrftoken="))
          ?.split("=")[1];
      }

      const user = sessionStorage.getItem("user");
      const otp_token = document.getElementById("id_otp_token").value;
      const response = await fetchWithHandling(
        `${window.env.ACCOUNT_HOST}/accounts/api/verify-otp/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: { user, otp_token },
        },
        "verifyotp:errors.verify"
      );
      const data = await response.json();
      if (response.ok) {
        console.log("Login successful:", data);
        document.cookie = `token=${data.token}; path=/; Secure; SameSite=Strict; max-age=86400`;
        window.location.hash = "#/";
      }
    });
  },
};

export default VerifyOtp;
