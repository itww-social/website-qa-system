// playwright.config.js
module.exports = {
  reporter: [
    ['list'],
    ['json', { outputFile: process.env.RESULT_FOLDER + '/playwright-report.json' }]
  ],
};