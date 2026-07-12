/* Orbit Deck smoke test - runs WITHOUT an Electron binary:
   1. scanTree (lib/scan.js) against the repo's planted fixture tree - counts must match.
   2. Renderer UI in a real Chromium (playwright-core) with window.deck mocked:
      tree renders, dashboard embeds, chat send -> bubbles + tool timeline.
   Usage: node tests/deck-smoke.js [chromium-path]
   Exit 0 on PASS, 1 on FAIL. ASCII-only output. */
const path = require("path");
const { scanTree } = require("../lib/scan");

const APP = path.resolve(__dirname, "..");
const REPO = path.resolve(APP, "..");
const FIXTURE = path.join(REPO, "tests", "fixture-find", "tree");

const failures = [];
const check = (cond, msg) => { if (!cond) failures.push(msg); };

// ---- part 1: scanner ----
const tree = scanTree(FIXTURE);
check(!tree.error, `scanTree error: ${tree.error}`);
check(tree.areas && tree.areas.length === 6, `expected 6 areas, got ${tree.areas && tree.areas.length}`);
const byName = Object.fromEntries((tree.areas || []).map((a) => [a.name, a]));
check(byName["00-inbox"] && byName["00-inbox"].fileCount === 2, "00-inbox should hold 2 files (scan + provenance)");
check(byName["40-projects"] && byName["40-projects"].fileCount === 2, "40-projects should hold 2 files");
const proj = byName["40-projects"] && byName["40-projects"].children.find((c) => c.name === "erp-upgrade");
check(proj && proj.dir && proj.children.length === 2, "erp-upgrade subfolder should nest 2 files");
console.log(`scan: ${tree.areas ? tree.areas.length : 0} areas, ` +
  `${(tree.areas || []).reduce((n, a) => n + a.fileCount, 0)} files - ${failures.length ? "issues" : "ok"}`);

// ---- part 2: renderer in chromium ----
(async () => {
  const { chromium } = require("playwright-core");
  const executablePath = process.argv[2] || "/opt/pw-browsers/chromium-1194/chrome-linux/chrome";
  const browser = await chromium.launch({ executablePath, args: ["--no-sandbox"] });
  const page = await browser.newPage();

  const treeData = JSON.stringify(tree);
  await page.addInitScript(`
    window.__agentCb = null;
    window.__treeCb = null;
    window.__tree = ${treeData};
    window.deck = {
      getConfig: async () => ({ root: "/fake/orbit", pythonCmd: "python3", claudeCmd: "claude", permissionMode: "acceptEdits" }),
      setConfig: async (p) => p,
      pickRoot: async () => null,
      scanTree: async () => window.__tree,
      regenDashboard: async () => ({ html: "<html><body><h1 id='dash-ok'>DASH</h1></body></html>" }),
      agentSend: async () => ({ ok: true }),
      agentCancel: async () => ({ ok: true }),
      openPath: async () => "",
      onTreeChanged: (cb) => { window.__treeCb = cb; },
      onAgentEvent: (cb) => { window.__agentCb = cb; },
    };
  `);
  page.on("pageerror", (err) => failures.push(`pageerror: ${err.message}`));
  await page.goto("file://" + path.join(APP, "renderer", "index.html"));
  await page.waitForTimeout(400);

  check((await page.locator(".row.area").count()) === 6, "UI: 6 area rows should render");
  check((await page.locator(".badge.hot").count()) === 1, "UI: inbox badge should be hot (files waiting)");
  const dashSrc = await page.locator("#dashFrame").getAttribute("srcdoc");
  check(dashSrc && dashSrc.includes("DASH"), "UI: dashboard iframe should carry the generated html");

  // expand an area, check files render
  await page.locator(".row.area").first().click();
  check((await page.locator(".row.file").count()) > 0, "UI: files should render after expanding an area");

  // chat: send + simulated stream events
  await page.fill("#chatInput", "sort the inbox");
  await page.locator("#chatForm button[type=submit]").click();
  await page.waitForTimeout(200);
  check((await page.locator(".bubble.user").count()) === 1, "UI: user bubble after send");
  await page.evaluate(() => {
    window.__agentCb({ type: "system", subtype: "init", session_id: "s-123" });
    window.__agentCb({ type: "assistant", message: { content: [{ type: "text", text: "Scanning the inbox." }] } });
    window.__agentCb({ type: "assistant", message: { content: [{ type: "tool_use", name: "Bash", input: { command: "ls 00-inbox" } }] } });
    window.__agentCb({ type: "result", subtype: "success", duration_ms: 1200, total_cost_usd: 0.01, session_id: "s-123" });
    window.__agentCb({ type: "deck:done", code: 0 });
  });
  await page.waitForTimeout(200);
  check((await page.locator(".bubble.claude").count()) === 1, "UI: claude bubble streams in");
  check((await page.locator(".tool").count()) === 1, "UI: tool-use timeline row renders");
  check((await page.locator(".turnFoot").count()) === 1, "UI: turn footer with duration/cost");
  check(await page.locator("#btnSend").isEnabled(), "UI: send re-enables after deck:done");

  // meteor micro-interactions: rows carry paths; a removal burns up, an arrival lands
  check((await page.locator('.node[data-path="30-operations/dr-recovery-runbook.md"]').count()) === 1,
    "UI: rows carry data-path for the diff");
  await page.evaluate(() => {
    const ops = window.__tree.areas.find((a) => a.name === "30-operations");
    ops.children = ops.children.filter((n) => n.name !== "dr-recovery-runbook.md");
    ops.fileCount -= 1;
    window.__treeCb(); // watcher fires
  });
  await page.waitForTimeout(250);
  check((await page.locator(".node.burnout").count()) === 1, "UI: removed row burns up like a meteor");
  await page.waitForTimeout(900);
  check((await page.locator('.node[data-path="30-operations/dr-recovery-runbook.md"]').count()) === 0,
    "UI: burned row is gone after the rebuild");
  await page.evaluate(() => {
    const inbox = window.__tree.areas.find((a) => a.name === "00-inbox");
    inbox.children.push({ name: "2026-07-08-new-drop.txt", dir: false, size: 10, mtime: Date.now() });
    inbox.fileCount += 1;
    window.__treeCb();
  });
  await page.waitForTimeout(300);
  check((await page.locator(".node.landing").count()) >= 1, "UI: arriving file gets the touchdown glow");
  check((await page.locator(".badge.ping").count()) === 1, "UI: inbox badge shockwave on new arrival");

  await browser.close();

  if (failures.length) {
    console.log(`FAIL (${failures.length}):`);
    for (const f of failures) console.log("  " + f);
    process.exit(1);
  }
  console.log("PASS: scanner counts + renderer UI (tree, dashboard embed, chat stream, "
    + "meteor burnout / touchdown / badge ping) all verified");
})().catch((err) => { console.log("FAIL: " + err.message); process.exit(1); });
