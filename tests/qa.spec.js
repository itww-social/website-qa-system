const { test } = require('@playwright/test');
const percySnapshot = require('@percy/playwright');
const AxeBuilder = require('@axe-core/playwright').default;
const fs = require('fs');
const path = require('path');

test('Full QA Test', async ({ page }) => {

  const url = process.env.TARGET_URL;
  const resultFolder = process.env.RESULT_FOLDER;

  await page.goto(url, { waitUntil: 'networkidle' });

  await page.screenshot({
    path: path.join(resultFolder, 'screenshot.png'),
    fullPage: true
  });

  const axeResults = await new AxeBuilder({ page }).analyze();

  fs.writeFileSync(
    path.join(resultFolder, 'accessibility.json'),
    JSON.stringify(axeResults, null, 2)
  );
});


// VISUAL TEST ONLY
test('@visual Percy Snapshot', async ({ page }) => {

  const url = process.env.TARGET_URL;

  await page.goto(url, { waitUntil: 'networkidle' });

  await percySnapshot(page, 'Homepage');
});