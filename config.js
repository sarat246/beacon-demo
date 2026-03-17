// style-dictionary.config.js
const path = require('path');

module.exports = {
  source: ['tokens/btokens.fixed.json'],
  platforms: {
    scss: {
      transformGroup: 'scss',
      buildPath: 'build/scss/',
      files: [{
        destination: 'variables.scss',
        format: 'scss/variables',
        options: {
          outputReferences: true
        }
      }]
    }
  }
};
