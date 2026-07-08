// Orbit Deck - main process. Local desktop shell for an orbit root:
// tree explorer + live dashboard + Claude agent panel. No server, no telemetry;
// the only processes it spawns are python (dashboard) and the claude CLI (agent).
const { app, BrowserWindow, ipcMain, dialog, shell } = require("electron");
const { spawn } = require("child_process");
const fs = require("fs");
const path = require("path");

let win = null;
let watcher = null;
let watchTimer = null;
let agentChild = null;

// ---------- config (plain JSON in userData) ----------
const configPath = () => path.join(app.getPath("userData"), "orbit-deck.json");
const DEFAULTS = {
  root: "",
  pythonCmd: process.platform === "win32" ? "python" : "python3",
  claudeCmd: "claude",
  permissionMode: "acceptEdits", // "plan" | "acceptEdits" | "bypass"
};

function loadConfig() {
  let cfg;
  try {
    cfg = { ...DEFAULTS, ...JSON.parse(fs.readFileSync(configPath(), "utf-8")) };
  } catch {
    cfg = { ...DEFAULTS };
  }
  if (process.env.ORBIT_DECK_ROOT) cfg.root = process.env.ORBIT_DECK_ROOT; // smoke/dev override
  return cfg;
}
function saveConfig(cfg) {
  fs.mkdirSync(app.getPath("userData"), { recursive: true });
  fs.writeFileSync(configPath(), JSON.stringify(cfg, null, 2), "utf-8");
}

// ---------- tree scan (lib/scan.js: plain Node so tests run without Electron) ----------
const { scanTree } = require("./lib/scan");

// ---------- watcher ----------
function startWatcher(root) {
  stopWatcher();
  try {
    watcher = fs.watch(root, { recursive: true }, (_ev, file) => {
      if (file && (String(file).includes("dashboard.html") || String(file).startsWith(".git"))) return;
      clearTimeout(watchTimer);
      watchTimer = setTimeout(() => win && win.webContents.send("tree:changed"), 700);
    });
  } catch {
    watcher = null; // recursive watch unavailable - renderer offers manual refresh
  }
}
function stopWatcher() {
  if (watcher) { watcher.close(); watcher = null; }
  clearTimeout(watchTimer);
}

// ---------- dashboard ----------
function regenDashboard(cfg) {
  return new Promise((resolve) => {
    const script = path.join(cfg.root, "skills", "orbit-dashboard", "generate.py");
    if (!fs.existsSync(script)) {
      return resolve({ error: "skills/orbit-dashboard/generate.py not found under the orbit root" });
    }
    const child = spawn(cfg.pythonCmd, [script, cfg.root], {
      cwd: cfg.root,
      env: { ...process.env, PYTHONIOENCODING: "utf-8" },
      shell: process.platform === "win32",
    });
    let stderr = "";
    child.stderr.on("data", (d) => (stderr += d));
    child.on("error", (err) => resolve({ error: `Cannot run ${cfg.pythonCmd}: ${err.message}` }));
    child.on("close", (code) => {
      if (code !== 0) return resolve({ error: `generate.py exited ${code}: ${stderr.slice(0, 500)}` });
      try {
        resolve({ html: fs.readFileSync(path.join(cfg.root, "dashboard.html"), "utf-8") });
      } catch (err) {
        resolve({ error: `dashboard.html unreadable: ${err.message}` });
      }
    });
  });
}

// ---------- agent (claude CLI, stream-json) ----------
function agentSend(cfg, prompt, sessionId) {
  if (agentChild) return { error: "An agent turn is already running - cancel it first." };
  const args = ["-p", "--output-format", "stream-json", "--verbose"];
  if (sessionId) args.push("--resume", sessionId);
  if (cfg.permissionMode === "bypass") args.push("--dangerously-skip-permissions");
  else args.push("--permission-mode", cfg.permissionMode === "plan" ? "plan" : "acceptEdits");

  let child;
  try {
    child = spawn(cfg.claudeCmd, args, {
      cwd: cfg.root,
      env: { ...process.env },
      shell: process.platform === "win32",
    });
  } catch (err) {
    return { error: `Cannot run ${cfg.claudeCmd}: ${err.message}` };
  }
  agentChild = child;
  child.stdin.write(prompt);
  child.stdin.end();

  let buf = "";
  const emit = (ev) => win && win.webContents.send("agent:event", ev);
  child.stdout.on("data", (d) => {
    buf += d.toString("utf-8");
    let i;
    while ((i = buf.indexOf("\n")) >= 0) {
      const line = buf.slice(0, i).trim();
      buf = buf.slice(i + 1);
      if (!line) continue;
      try { emit(JSON.parse(line)); } catch { emit({ type: "raw", text: line }); }
    }
  });
  let stderr = "";
  child.stderr.on("data", (d) => (stderr += d.toString("utf-8")));
  child.on("error", (err) => { emit({ type: "deck:error", error: `claude spawn failed: ${err.message}` }); agentChild = null; });
  child.on("close", (code) => {
    if (code !== 0 && stderr) emit({ type: "deck:error", error: stderr.slice(0, 800) });
    emit({ type: "deck:done", code });
    agentChild = null;
  });
  return { ok: true };
}

// ---------- IPC ----------
ipcMain.handle("config:get", () => loadConfig());
ipcMain.handle("config:set", (_e, patch) => {
  const cfg = { ...loadConfig(), ...patch };
  saveConfig(cfg);
  if (patch.root) startWatcher(cfg.root);
  return cfg;
});
ipcMain.handle("root:pick", async () => {
  const r = await dialog.showOpenDialog(win, { properties: ["openDirectory"], title: "Pick your orbit root" });
  if (r.canceled || !r.filePaths[0]) return null;
  const cfg = { ...loadConfig(), root: r.filePaths[0] };
  saveConfig(cfg);
  startWatcher(cfg.root);
  return cfg;
});
ipcMain.handle("tree:scan", () => {
  const cfg = loadConfig();
  if (!cfg.root) return { error: "No orbit root configured" };
  return scanTree(cfg.root);
});
ipcMain.handle("dashboard:regen", () => regenDashboard(loadConfig()));
ipcMain.handle("agent:send", (_e, { prompt, sessionId }) => agentSend(loadConfig(), prompt, sessionId));
ipcMain.handle("agent:cancel", () => {
  if (agentChild) { agentChild.kill(); agentChild = null; return { ok: true }; }
  return { ok: false };
});
ipcMain.handle("path:open", (_e, rel) => {
  const cfg = loadConfig();
  return shell.openPath(path.join(cfg.root, rel));
});

// ---------- lifecycle ----------
function createWindow() {
  win = new BrowserWindow({
    width: 1480,
    height: 920,
    backgroundColor: "#08090c",
    title: "Orbit Deck",
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });
  win.setMenuBarVisibility(false);
  win.loadFile(path.join(__dirname, "renderer", "index.html"));
  const cfg = loadConfig();
  if (cfg.root) startWatcher(cfg.root);

  if (process.env.ORBIT_DECK_SMOKE) {
    win.webContents.on("did-finish-load", async () => {
      const cfgNow = loadConfig();
      const tree = cfgNow.root ? scanTree(cfgNow.root) : { error: "no root" };
      console.log("SMOKE: window loaded; tree areas =", tree.areas ? tree.areas.length : tree.error);
      const dash = cfgNow.root ? await regenDashboard(cfgNow) : { error: "no root" };
      console.log("SMOKE: dashboard =", dash.html ? `${dash.html.length} bytes` : dash.error);
      app.quit();
    });
  }
}

app.whenReady().then(createWindow);
app.on("window-all-closed", () => { stopWatcher(); app.quit(); });
