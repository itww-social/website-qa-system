const fs = require('fs');
const path = require('path');

const folder = process.env.RESULT_FOLDER;
const url = process.env.TARGET_URL;

const summary = {
  url: url,
  status: "Completed",
  date: new Date().toISOString(),
  note: "See Percy dashboard for visual results"
};

fs.writeFileSync(
  path.join(folder, 'qa-summary.json'),
  JSON.stringify(summary, null, 2)
);