const SetupOtp = {
  render: async () => {
    const template = await fetch("/views/templates/SetupOtp.html").then(
      (response) => response.text()
    );

    const response = await fetch(
      `${window.env.BACKEND_HOST}/accounts/api/setup-otp/`,
      {
        method: "GET",
        headers: {
          Authorization: `JWT ${sessionStorage.getItem("token")}`,
        },
      }
    );
    const data = await response.json();

    console.log(data);

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
            `${window.env.BACKEND_HOST}/accounts/api/setup-otp/`,
            {
              method: "POST",
              headers: {
                Authorization: `JWT ${sessionStorage.getItem("token")}`,
                "Content-Type": "application/json",
              },
            }
          );

          if (response.ok) {
            window.location.hash = "#/";
          } else {
            console.error(await response.json());
            alert("Otp setup failed");
          }
        } catch (error) {
          console.error("Error ", error);
          alert("Error  occurred while setting up otp");
        }
      });
  },
};

export default SetupOtp;
