const SetupOtp = {
  render: async () => {
    const template = await fetch("/views/templates/SetupOtp.html").then(
      (response) => response.text()
    );

    const response = await fetch(
      `${window.env.ACCOUNT_HOST}/accounts/api/setup-otp/`,
      {
        method: "GET",
        credentials: "include",
      }
    ).catch((error) => console.error(error));
    const data = await response.json();

    console.log(data);

    if (data.message === "OTP already set up") {
      return (await fetch("/views/templates/AlreadySetupOtp.html")).text();
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

        try {
          const response = await fetch(
            `${window.env.ACCOUNT_HOST}/accounts/api/setup-otp/`,
            {
              method: "POST",
              credentials: "include",
              headers: {
                "Content-Type": "application/json",
              },
            }
          );

          if (response.ok) {
            window.location.hash = "#/";
          } else {
            console.error(await response.json());
            alert(i18next.t("setupotp:errors.setup"));
          }
        } catch (error) {
          console.error("Error ", error);
          alert(i18next.t("setupotp:errors.unknown"));
        }
      });
  },
};

export default SetupOtp;
