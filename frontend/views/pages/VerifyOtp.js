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

      const urlParams = new URLSearchParams(
        window.location.hash.split("?")[1]
      );
      const user = urlParams.get("user");
      const otp_token = document.getElementById("id_otp_token").value;
      const response = await fetchWithHandling(
        `${
          window.env.ACCOUNT_HOST
        }/accounts/verify-otp/?user=${encodeURIComponent(user)}`,
        {
          method: "POST",
          body: { otp_token },
        },
        "verifyotp:errors.verify"
      );
      const data = await response.json();
      if (response.ok) {
        console.log("Login successful:", data);
        document.cookie = `isLoggedIn=true; path=/; max-age=86400`;
        window.location.hash = "#/";
      }
    });
  },
};

export default VerifyOtp;
