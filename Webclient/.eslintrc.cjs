/* eslint-env node */
require("@rushstack/eslint-patch/modern-module-resolution");

module.exports = {
  "root": true,
  "extends": [
     'plugin:vue/base',
     'eslint:recommended',
     'plugin:vue/vue3-recommended',
     'plugin:vue/essential',
     'plugin:@typescript-eslint/recommended',
  ],
  "parser": 'vue-eslint-parser',
}
