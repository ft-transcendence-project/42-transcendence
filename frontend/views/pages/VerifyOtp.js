const VerifyOtp = {
  render: async () => {
    return (await fetch("/views/templates/VerifyOtp.html")).text();
  },

  after_render: async () => {
    const form = document.getElementById("verify-otp-form");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      try {
        const user = sessionStorage.getItem("user");
        const otp_token = document.getElementById("id_otp_token").value;
        const response = await fetch(
          `${window.env.ACCOUNT_HOST}/accounts/api/verify-otp/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ user, otp_token }),
          }
        );

        const data = await response.json();

        if (response.ok) {
          console.log("Login successful:", data);
          window.location.hash = "#/";
        } else {
          const errors = Object.entries(data)
            .map(([k, v]) => `${k}: ${v}`)
            .join(", ");
          console.error("OTP verification failed: ", errors);
          alert(i18next.t("verifyotp:errors.verify"));
        }
      } catch (error) {
        console.error("Error during OTP verification:", error);
        alert(i18next.t("verifyotp:errors.unknown"));
      }
    });
  },
};

export default VerifyOtp;
