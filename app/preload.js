const { contextBridge, ipcRenderer } = require("electron");

contextBridge.exposeInMainWorld("deck", {
  getConfig: () => ipcRenderer.invoke("config:get"),
  setConfig: (patch) => ipcRenderer.invoke("config:set", patch),
  pickRoot: () => ipcRenderer.invoke("root:pick"),
  scanTree: () => ipcRenderer.invoke("tree:scan"),
  regenDashboard: () => ipcRenderer.invoke("dashboard:regen"),
  agentSend: (prompt, sessionId) => ipcRenderer.invoke("agent:send", { prompt, sessionId }),
  agentCancel: () => ipcRenderer.invoke("agent:cancel"),
  openPath: (rel) => ipcRenderer.invoke("path:open", rel),
  onTreeChanged: (cb) => ipcRenderer.on("tree:changed", cb),
  onAgentEvent: (cb) => ipcRenderer.on("agent:event", (_e, ev) => cb(ev)),
});
