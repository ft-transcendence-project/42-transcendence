import globals from "globals";
import pluginJs from "@eslint/js";

/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node,
        i18next: "readonly",
        i18nextHttpBackend: "readonly", 
        i18nextBrowserLanguageDetector: "readonly",
      },
    },
  },
  pluginJs.configs.recommended,
];
