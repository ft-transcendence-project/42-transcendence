import { changeLanguage } from "../../utils/i18n.js";

const Navbar = {
  setTranslateHook: async () => {
    document
      .getElementById("change_to_english")
      .addEventListener("click", (event) => {
        event.preventDefault(); // ページ遷移を防ぐ
        changeLanguage("en");
      });
    document
      .getElementById("change_to_japanese")
      .addEventListener("click", (event) => {
        event.preventDefault();
        changeLanguage("ja");
      });
    document
      .getElementById("change_to_chinese")
      .addEventListener("click", (event) => {
        event.preventDefault();
        changeLanguage("zh");
      });
  },
};

export default Navbar;
