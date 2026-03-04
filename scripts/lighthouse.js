const fs = require('fs');

(async () => {
  const lighthouse = (await import('lighthouse')).default;
  const chromeLauncher = (await import('chrome-launcher')).default;

  const url = process.env.TARGET_URL;
  const resultFolder = process.env.RESULT_FOLDER;

  const chrome = await chromeLauncher.launch({
    chromeFlags: ['--headless']
  });

  const runnerResult = await lighthouse(url, {
    port: chrome.port,
    output: 'json'
  });

  fs.writeFileSync(
    resultFolder + '/lighthouse.json',
    runnerResult.report
  );

  await chrome.kill();
})();