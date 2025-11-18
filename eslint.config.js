export default [
  {
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
      globals: {
        console: "readonly",
        process: "readonly",
        document: "readonly",
        window: "readonly"
      }
    },
    rules: {
      "no-unused-vars": "warn",
      "no-undef": "warn",
      "semi": ["error", "always"],
      "quotes": ["warn", "single", { "avoidEscape": true, "allowTemplateLiterals": true }]
    }
  }
];
