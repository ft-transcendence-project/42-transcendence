import { fetchWithHandling } from "../../utils/fetchWithHandling.js";
import { fetchHtml } from "../../utils/fetchHtml.js";

const SetupOtp = {
  render: async () => {
    const template = await fetchHtml("/views/templates/SetupOtp.html");

    const response = await fetch(
      `${window.env.ACCOUNT_HOST}/accounts/setup-otp/`,
      {
        method: "GET",
        credentials: "include",
      }
    ).catch((error) => console.error(error));
    const data = await response.json();

    console.log(data);

    if (data.message === "OTP already set up") {
      return (await fetchHtml("/views/templates/AlreadySetupOtp.html"));
    }

    return template
      .replace("{{ otpauth_url }}", encodeURIComponent(data.otpauth_url))
      .replace("{{ secret_key }}", data.secret_key);
  },

  after_render: async () => {
    document
      .getElementById("setup-otp-form")
      .addEventListener("submit", async (e) => {
        e.preventDefault();

        const response = await fetchWithHandling(
          `${window.env.ACCOUNT_HOST}/accounts/setup-otp/`,
          {
            method: "POST",
            credentials: "include",
          },
          "setupotp:errors.setup"
        );
        if (response) {
          window.location.hash = "#/";
        }
      });
  },
};

export default SetupOtp;
