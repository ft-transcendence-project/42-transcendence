import globals from "globals";
import pluginJs from "@eslint/js";

/** @type {import('eslint').Linter.Config[]} */
export default [
  {
    languageOptions: {
      globals: {
        ...globals.browser,
        ...globals.node, // Node.js環境のグローバル変数を追加
      },
    },
  },
  pluginJs.configs.recommended,
];
