const { test, expect } = require('@playwright/test');
const AxeBuilder = require('@axe-core/playwright').default;
const percySnapshot = require('@percy/playwright');
const fs = require('fs');
const path = require('path');

test('Full QA Test', async ({ page }) => {

  const url = process.env.TARGET_URL;
  const folder = process.env.RESULT_FOLDER;

  await page.goto(url);

  await expect(page).toHaveTitle(/./);

  await percySnapshot(page, 'Homepage');

  const accessibilityResults = await new AxeBuilder({ page }).analyze();

  fs.writeFileSync(
    path.join(folder, 'accessibility.json'),
    JSON.stringify(accessibilityResults, null, 2)
  );

});