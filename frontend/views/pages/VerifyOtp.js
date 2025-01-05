import { updateContent } from "../../utils/i18n.js";

const VerifyOtp = {
  render: async () => {
    return (await fetch("/views/templates/VerifyOtp.html")).text();
  },

  after_render: async () => {
    updateContent();

    const form = document.getElementById("verify-otp-form");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      function getCSRFToken() {
        return document.cookie
          .split("; ")
          .find((row) => row.startsWith("csrftoken="))
          ?.split("=")[1];
      }

      try {
        const user = sessionStorage.getItem("user");
        const otp_token = document.getElementById("id_otp_token").value;
        const response = await fetch(
          `${window.env.BACKEND_HOST}/accounts/api/verify-otp/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ user, otp_token }),
          }
        );

        const data = await response.json();

        if (response.ok) {
          console.log("Login successful:", data);
          document.cookie = `token=${data.token}; path=/; Secure; SameSite=Strict; max-age=86400`;
          window.location.hash = "#/";
        } else {
          const errors = Object.entries(data)
            .map(([k, v]) => `${k}: ${v}`)
            .join(", ");
          console.error("OTP verification failed: ", errors);
          alert("OTP verification failed");
        }
      } catch (error) {
        console.error("Error during OTP verification:", error);
        alert("Error during OTP verification");
      }
    });
  },
};

export default VerifyOtp;
