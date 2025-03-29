// style-dictionary.config.js
const path = require('path');

module.exports = {
  source: ['tokens/btokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'build/css/',
      files: [{
        destination: 'variables.css',
        format: 'css/variables',
        options: {
          outputReferences: true
        }
      }]
    }
  }
};
