// Tree scanning for Orbit Deck - plain Node, no Electron imports, so it can be
// exercised by tests/deck-smoke.js without an Electron binary.
const fs = require("fs");
const path = require("path");

const MAX_ENTRIES = 8000;

const isAreaDir = (name) => /^\d{2}-/.test(name);

function scanDir(dir, state) {
  const out = [];
  let entries;
  try {
    entries = fs.readdirSync(dir, { withFileTypes: true });
  } catch {
    return out;
  }
  entries.sort((a, b) =>
    a.isDirectory() === b.isDirectory() ? a.name.localeCompare(b.name) : a.isDirectory() ? -1 : 1);
  for (const e of entries) {
    if (state.count >= MAX_ENTRIES) { state.truncated = true; break; }
    if (e.name === ".gitkeep" || e.name.startsWith(".git")) continue;
    const p = path.join(dir, e.name);
    state.count++;
    if (e.isDirectory()) {
      out.push({ name: e.name, dir: true, children: scanDir(p, state) });
    } else {
      let size = 0, mtime = 0;
      try { const st = fs.statSync(p); size = st.size; mtime = st.mtimeMs; } catch {}
      out.push({ name: e.name, dir: false, size, mtime });
    }
  }
  return out;
}

function countFiles(nodes) {
  let n = 0;
  for (const node of nodes) n += node.dir ? countFiles(node.children) : 1;
  return n;
}

function scanTree(root) {
  const state = { count: 0, truncated: false };
  const areas = [];
  let names;
  try {
    names = fs.readdirSync(root).filter(isAreaDir).sort();
  } catch (err) {
    return { error: `Cannot read root: ${err.message}` };
  }
  for (const name of names) {
    const children = scanDir(path.join(root, name), state);
    areas.push({ name, dir: true, children, fileCount: countFiles(children) });
  }
  return { areas, truncated: state.truncated, scannedAt: Date.now() };
}

module.exports = { scanTree, isAreaDir };
