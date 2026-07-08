/* Orbit Deck renderer - tree explorer, dashboard embed, agent chat. */
const $ = (id) => document.getElementById(id);
const human = (n) => {
  for (const u of ["B", "KB", "MB", "GB", "TB"]) {
    if (n < 1024 || u === "TB") return `${n < 10 && u !== "B" ? n.toFixed(1) : Math.round(n)} ${u}`;
    n /= 1024;
  }
};

let cfg = null;
let sessionId = null;
let busy = false;

// ---------- tree ----------
function nodeRow(node, relPath, isArea) {
  const wrap = document.createElement("div");
  wrap.className = "node";
  const row = document.createElement("div");
  row.className = `row ${isArea ? "area" : node.dir ? "" : "file"}`;
  const twist = document.createElement("span");
  twist.className = "twist";
  twist.textContent = node.dir ? "▸" : "";
  const nm = document.createElement("span");
  nm.className = "nm";
  nm.textContent = node.name;
  row.append(twist, nm);

  if (isArea) {
    const badge = document.createElement("span");
    const hot = node.name.startsWith("00-") && node.fileCount > 0;
    badge.className = `badge${hot ? " hot" : ""}`;
    badge.textContent = node.fileCount;
    badge.title = `${node.fileCount} files`;
    row.append(badge);
  } else if (!node.dir) {
    const sz = document.createElement("span");
    sz.className = "sz";
    sz.textContent = human(node.size);
    row.append(sz);
  }
  wrap.append(row);

  if (node.dir) {
    const kids = document.createElement("div");
    kids.className = "kids hidden";
    for (const c of node.children) kids.append(nodeRow(c, `${relPath}/${c.name}`, false));
    if (!node.children.length) {
      const e = document.createElement("p");
      e.className = "dim pad";
      e.textContent = "(empty)";
      kids.append(e);
    }
    wrap.append(kids);
    row.addEventListener("click", () => {
      kids.classList.toggle("hidden");
      twist.textContent = kids.classList.contains("hidden") ? "▸" : "▾";
    });
  } else {
    row.addEventListener("dblclick", () => window.deck.openPath(relPath));
    row.title = "double-click to open";
  }
  return wrap;
}

async function refreshTree() {
  const res = await window.deck.scanTree();
  const tree = $("tree");
  tree.textContent = "";
  if (res.error) {
    tree.innerHTML = `<p class="dim pad"></p>`;
    tree.firstChild.textContent = res.error;
    return;
  }
  for (const area of res.areas) tree.append(nodeRow(area, area.name, true));
  const total = res.areas.reduce((n, a) => n + a.fileCount, 0);
  $("treeMeta").textContent = `${res.areas.length} areas · ${total} files${res.truncated ? " (view truncated)" : ""}`;
}

// ---------- dashboard ----------
async function refreshDashboard() {
  $("dashMeta").textContent = "generating…";
  const res = await window.deck.regenDashboard();
  if (res.error) {
    $("dashMeta").textContent = res.error;
    return;
  }
  $("dashFrame").srcdoc = res.html;
  $("dashEmpty").classList.add("hidden");
  $("dashMeta").textContent = `regenerated ${new Date().toLocaleTimeString()}`;
}

// ---------- agent chat ----------
const chat = $("chat");
let currentText = null; // streaming text bubble for this turn

function addBubble(cls, text) {
  const b = document.createElement("div");
  b.className = `bubble ${cls}`;
  b.textContent = text;
  chat.append(b);
  chat.scrollTop = chat.scrollHeight;
  return b;
}

function addTool(name, input) {
  const t = document.createElement("div");
  t.className = "tool";
  const head = document.createElement("div");
  const b = document.createElement("b");
  b.textContent = name;
  head.append("⚙ ", b);
  const summary = toolSummary(name, input);
  if (summary) head.append(` ${summary}`);
  const inp = document.createElement("div");
  inp.className = "in";
  inp.textContent = JSON.stringify(input, null, 1).slice(0, 2000);
  t.append(head, inp);
  t.addEventListener("click", () => t.classList.toggle("open"));
  chat.append(t);
  chat.scrollTop = chat.scrollHeight;
}

function toolSummary(name, input) {
  if (!input) return "";
  if (input.command) return String(input.command).slice(0, 90);
  if (input.file_path) return String(input.file_path).slice(-70);
  if (input.pattern) return String(input.pattern).slice(0, 60);
  if (input.prompt) return String(input.prompt).slice(0, 70);
  return "";
}

function setBusy(v) {
  busy = v;
  $("btnSend").disabled = v;
  $("btnCancel").disabled = !v;
  $("agentMeta").textContent = v ? "working…" : sessionId ? "session active" : "idle";
}

window.deck.onAgentEvent((ev) => {
  if (ev.type === "system" && ev.subtype === "init") {
    sessionId = ev.session_id || sessionId;
  } else if (ev.type === "assistant" && ev.message && Array.isArray(ev.message.content)) {
    for (const block of ev.message.content) {
      if (block.type === "text" && block.text) {
        if (!currentText) currentText = addBubble("claude", "");
        currentText.textContent += block.text;
        chat.scrollTop = chat.scrollHeight;
      } else if (block.type === "tool_use") {
        currentText = null; // next text opens a fresh bubble after the tool row
        addTool(block.name, block.input);
      }
    }
  } else if (ev.type === "result") {
    sessionId = ev.session_id || sessionId;
    const f = document.createElement("div");
    f.className = "turnFoot";
    const secs = ev.duration_ms ? `${(ev.duration_ms / 1000).toFixed(1)}s` : "";
    const cost = ev.total_cost_usd ? ` · $${ev.total_cost_usd.toFixed(3)}` : "";
    f.textContent = `${ev.subtype === "success" ? "done" : ev.subtype} · ${secs}${cost}`;
    chat.append(f);
    chat.scrollTop = chat.scrollHeight;
  } else if (ev.type === "deck:error") {
    addBubble("err", ev.error);
  } else if (ev.type === "deck:done") {
    currentText = null;
    setBusy(false);
    refreshTree(); // the agent may have moved files
  }
});

$("chatForm").addEventListener("submit", async (e) => {
  e.preventDefault();
  const prompt = $("chatInput").value.trim();
  if (!prompt || busy) return;
  addBubble("user", prompt);
  $("chatInput").value = "";
  setBusy(true);
  currentText = null;
  const res = await window.deck.agentSend(prompt, sessionId);
  if (res.error) {
    addBubble("err", res.error);
    setBusy(false);
  }
});
$("chatInput").addEventListener("keydown", (e) => {
  if (e.key === "Enter" && !e.shiftKey) {
    e.preventDefault();
    $("chatForm").requestSubmit();
  }
});
$("btnCancel").addEventListener("click", async () => {
  await window.deck.agentCancel();
  addBubble("sys", "turn cancelled");
  setBusy(false);
});
$("btnNewChat").addEventListener("click", () => {
  sessionId = null;
  chat.textContent = "";
  addBubble("sys", "fresh session");
  setBusy(false);
});

// ---------- shell ----------
async function applyConfig(c) {
  cfg = c;
  $("rootLabel").textContent = c.root || "no root selected";
  if (c.root) {
    await refreshTree();
    await refreshDashboard();
  }
}

$("btnPickRoot").addEventListener("click", async () => {
  const c = await window.deck.pickRoot();
  if (c) applyConfig(c);
});
$("btnRefresh").addEventListener("click", () => { refreshTree(); refreshDashboard(); });
$("btnDash").addEventListener("click", refreshDashboard);
window.deck.onTreeChanged(() => refreshTree());

// settings
$("btnSettings").addEventListener("click", () => {
  $("setPython").value = cfg.pythonCmd;
  $("setClaude").value = cfg.claudeCmd;
  $("setPerm").value = cfg.permissionMode;
  $("settingsDlg").showModal();
});
$("settingsDlg").addEventListener("close", async () => {
  if ($("settingsDlg").returnValue !== "save") return;
  cfg = await window.deck.setConfig({
    pythonCmd: $("setPython").value.trim() || "python",
    claudeCmd: $("setClaude").value.trim() || "claude",
    permissionMode: $("setPerm").value,
  });
});

window.deck.getConfig().then(applyConfig);
