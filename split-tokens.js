const fs = require('fs');
const path = require('path');

const inputPath = './tokens/btokens.json'; // adjust path if needed
const outputDir = './tokens/sets';

const raw = fs.readFileSync(inputPath);
const data = JSON.parse(raw);

// Ensure base output directories exist
const createDir = (dir) => {
  if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true });
};

createDir(outputDir);

Object.entries(data).forEach(([key, value]) => {
  let [folder, name] = key.split('/');
  folder = folder.toLowerCase();

  // fallback if structure doesn't match expected pattern
  if (!name) {
    name = folder;
    folder = 'misc';
  }

  const targetDir = path.join(outputDir, folder);
  createDir(targetDir);

  const fileName = name.replace(/\s+/g, '').toLowerCase() + '.json';
  const filePath = path.join(targetDir, fileName);

  fs.writeFileSync(filePath, JSON.stringify(value, null, 2));
  console.log(`✅ Wrote ${filePath}`);
});