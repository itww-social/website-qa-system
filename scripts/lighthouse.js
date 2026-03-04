// scripts/lighthouse.js
const fs = require('fs');

(async () => {
  try {
    // Dynamic import and robust extraction of exported items
    const lhModule = await import('lighthouse');
    const lighthouse = (lhModule && (lhModule.default || lhModule)) ;

    const chModule = await import('chrome-launcher');
    // `chrome-launcher` may export `launch` directly or as default.launch depending on build
    const launch = chModule.launch || (chModule.default && chModule.default.launch) || chModule.default;

    if (typeof launch !== 'function') {
      console.error('ERROR: chrome-launcher.launch is not a function. module shape:', Object.keys(chModule));
      throw new Error('chrome-launcher.launch is not available');
    }

    const url = process.env.TARGET_URL;
    const resultFolder = process.env.RESULT_FOLDER;

    if (!url || !resultFolder) {
      throw new Error('TARGET_URL or RESULT_FOLDER env var missing');
    }

    console.log('Lighthouse starting for', url, '-> results folder:', resultFolder);

    // Launch Chrome with recommended flags for CI
    const chrome = await launch({
      chromeFlags: ['--headless', '--no-sandbox', '--disable-setuid-sandbox', '--disable-gpu'],
    });

    console.log('Chrome launched on port', chrome.port);

    // Run lighthouse
    const runnerResult = await lighthouse(url, {
      port: chrome.port,
      output: 'json',
    });

    // runnerResult.report is a JSON string (Lighthouse returns string when output=json)
    const outPath = `${resultFolder}/lighthouse.json`;
    fs.writeFileSync(outPath, runnerResult.report);
    console.log('Lighthouse report written to', outPath);

    await chrome.kill();
    console.log('Chrome killed, lighthouse step complete.');
  } catch (err) {
    console.error('Lighthouse step failed:', err);
    // rethrow so GitHub Actions fails the job and shows this stack trace
    throw err;
  }
})();