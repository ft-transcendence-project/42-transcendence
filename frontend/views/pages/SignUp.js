import { fetchWithHandling } from "../../utils/fetchWithHandling.js";

const SignUp = {
  render: async () => {
    return (await fetchWithHandling("/views/templates/SignUp.html")).text();
  },

  after_render: async () => {
    const signupForm = document.getElementById("signup-form");

    signupForm.addEventListener("submit", async (event) => {
      event.preventDefault();
      if (!signupForm.checkValidity()) {
        event.stopPropagation();
        signupForm.classList.add("was-validated");
        return;
      }

      signupForm.classList.add("was-validated");

      let username = document.getElementById("username").value;
      let password = document.getElementById("password").value;
      let email = document.getElementById("email").value;
      let default_language = document.querySelector('input[name="language"]:checked').id.replace("language-", "");

      function getCSRFToken() {
        return document.cookie
          .split("; ")
          .find((row) => row.startsWith("csrftoken="))
          ?.split("=")[1];
      }

      try {
        const response = await fetch(
          `${window.env.ACCOUNT_HOST}/accounts/api/signup/`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              "X-CSRFToken": getCSRFToken(),
            },
            body: JSON.stringify({ username, password, email, default_language }),
          }
        );

        const data = await response.json();

        if (response.ok) {
          console.log("Signup successful: ", data);
          window.location.hash = "#/";
        } else {
          const errors = Object.entries(data)
            .map(([k, v]) => `${k}: ${v}`)
            .join(", ");
          console.error("Signup failed: ", errors);
          alert(i18next.t("signup:errors.signup"));
        }
      } catch (error) {
        console.error("Error during signup: ", error);
        alert(i18next.t("signup:errors.unknown"));
      }
    });
  },
};

export default SignUp;
