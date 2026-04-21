const fs = require("fs");
const path = require("path");

const CACHE_DIR = path.join(require("os").homedir(), ".openclaw", "cron");

function ensureDir() {
  if (!fs.existsSync(CACHE_DIR)) fs.mkdirSync(CACHE_DIR, { recursive: true });
}

function readCache(filename) {
  ensureDir();
  const fp = path.join(CACHE_DIR, filename);
  try {
    return JSON.parse(fs.readFileSync(fp, "utf8"));
  } catch {
    return {};
  }
}

function writeCache(filename, data) {
  ensureDir();
  const fp = path.join(CACHE_DIR, filename);
  fs.writeFileSync(fp, JSON.stringify(data, null, 2));
}

module.exports = { readCache, writeCache };
