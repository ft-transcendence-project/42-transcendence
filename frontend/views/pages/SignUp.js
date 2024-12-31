import { updateContent } from "../../utils/i18n.js";

const SignUp = {
  render: async () => {
    return (await fetch("/views/templates/signup.html")).text();
  },

  after_render: async () => {
    updateContent();

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
            body: JSON.stringify({ username, password, email }),
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
