const lighthouse = require('lighthouse');
const chromeLauncher = require('chrome-launcher');
const fs = require('fs');
const path = require('path');

(async () => {

  const url = process.env.TARGET_URL;
  const folder = process.env.RESULT_FOLDER;

  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });

  const options = {
    logLevel: 'info',
    output: 'json',
    port: chrome.port,
  };

  const runnerResult = await lighthouse(url, options);

  fs.writeFileSync(
    path.join(folder, 'lighthouse.json'),
    runnerResult.report
  );

  await chrome.kill();

})();