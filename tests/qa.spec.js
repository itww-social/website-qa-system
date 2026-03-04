const percySnapshot = require('@percy/playwright');
const { test } = require('@playwright/test');
const { injectAxe } = require('@axe-core/playwright');
const fs = require('fs');

test('Full QA Test', async ({ page }) => {

  const url = process.env.TARGET_URL;
  const resultFolder = process.env.RESULT_FOLDER;

  await page.goto(url);

  // Percy snapshot (IMPORTANT)
  await percySnapshot(page, 'Homepage');

  // Save screenshot
  await page.screenshot({ path: resultFolder + '/screenshot.png', fullPage: true });

  // Proper AXE run
  await injectAxe(page);

  const axeResults = await page.evaluate(async () => {
    return await axe.run();
  });

  fs.writeFileSync(
    resultFolder + '/accessibility.json',
    JSON.stringify(axeResults, null, 2)
  );
});