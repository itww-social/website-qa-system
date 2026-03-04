// playwright.config.js

const path = require('path');

module.exports = {
  reporter: [
    ['json', { outputFile: process.env.RESULT_FOLDER + '/playwright-report.json' }]
  ],
};