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

      const response = await fetchWithHandling(
        `${window.env.ACCOUNT_HOST}/accounts/api/signup/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
          },
          body: { username, password, email, default_language },
        },
        "signup:errors.signup"
      );
      const data = await response.json();
      if (response) {
        console.log("Signup successful: ", data);
        window.location.hash = "#/";
      }
    });
  },
};

export default SignUp;
