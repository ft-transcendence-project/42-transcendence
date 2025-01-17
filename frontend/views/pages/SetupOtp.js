import { fetchWithHandling } from "../../utils/fetchWithHandling.js";

const SetupOtp = {
  render: async () => {
    const template = await fetchWithHandling("/views/templates/SetupOtp.html").then(
      (response) => response.text()
    );

    const token = document.cookie.replace(
      /(?:(?:^|.*;\s*)token\s*\=\s*([^;]*).*$)|^.*$/,
      "$1"
    );

    const response = await fetch(
      `${window.env.ACCOUNT_HOST}/accounts/api/setup-otp/`,
      {
        method: "GET",
        headers: {
          Authorization: `JWT ${token}`,
        },
      }
    ).catch((error) => console.error(error));
    const data = await response.json();

    console.log(data);

    if (data.message === "OTP already set up") {
      return (await fetchWithHandling("/views/templates/AlreadySetupOtp.html")).text();
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

        function getCSRFToken() {
          return document.cookie
            .split("; ")
            .find((row) => row.startsWith("csrftoken="))
            ?.split("=")[1];
        }

        const token = document.cookie.replace(
          /(?:(?:^|.*;\s*)token\s*\=\s*([^;]*).*$)|^.*$/,
          "$1"
        );
        const response = await fetchWithHandling(
          `${window.env.ACCOUNT_HOST}/accounts/api/setup-otp/`,
          {
            method: "POST",
            headers: {
              Authorization: `JWT ${token}`,
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
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
