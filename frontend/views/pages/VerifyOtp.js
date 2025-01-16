const VerifyOtp = {
  render: async () => {
    return (await fetch("/views/templates/VerifyOtp.html")).text();
  },

  after_render: async () => {
    const form = document.getElementById("verify-otp-form");

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      try {
        const urlParams = new URLSearchParams(
          window.location.hash.split("?")[1]
        );
        const user = urlParams.get("user");
        const otp_token = document.getElementById("id_otp_token").value;

        const response = await fetch(
          `${
            window.env.ACCOUNT_HOST
          }/accounts/api/verify-otp/?user=${encodeURIComponent(user)}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ otp_token }),
          }
        );

        const data = await response.json();

        if (response.ok) {
          console.log("Login successful:", data);
          document.cookie = `isLoggedIn=true; path=/; max-age=86400`;
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
