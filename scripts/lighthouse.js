import lighthouse from 'lighthouse';
import chromeLauncher from 'chrome-launcher';
import fs from 'fs';

(async () => {

  const url = process.env.TARGET_URL;
  const resultFolder = process.env.RESULT_FOLDER;

  const chrome = await chromeLauncher.launch({ chromeFlags: ['--headless'] });

  const runnerResult = await lighthouse(url, {
    port: chrome.port,
    output: 'json',
  });

  fs.writeFileSync(
    resultFolder + '/lighthouse.json',
    runnerResult.report
  );

  await chrome.kill();

})();