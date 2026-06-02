const DEFAULTS = {
  enabled: true,
  port: 8765,
  token: "",
  lastStatus: "",
  lastError: "",
  lastSentAt: ""
};

const enabledEl = document.getElementById("enabled");
const portEl = document.getElementById("port");
const tokenEl = document.getElementById("token");
const statusEl = document.getElementById("status");

function setStatus(text) {
  statusEl.textContent = text || "";
}

async function load() {
  const data = await chrome.storage.local.get(DEFAULTS);
  enabledEl.checked = Boolean(data.enabled);
  portEl.value = data.port || 8765;
  tokenEl.value = data.token || "";
  const bits = [];
  if (data.lastStatus) bits.push(`Last: ${data.lastStatus}`);
  if (data.lastSentAt) bits.push(data.lastSentAt);
  if (data.lastError) bits.push(data.lastError);
  setStatus(bits.join(" | "));
}

async function save() {
  const port = Number(portEl.value || 8765);
  await chrome.storage.local.set({
    enabled: enabledEl.checked,
    port,
    token: tokenEl.value.trim()
  });
  setStatus("Saved");
}

async function test() {
  await save();
  const port = Number(portEl.value || 8765);
  try {
    const res = await fetch(`http://127.0.0.1:${port}/health`);
    const body = await res.json();
    setStatus(res.ok && body.ok ? `Connected to port ${body.port}` : "Health check failed");
  } catch (err) {
    setStatus(`Offline: ${err.message || err}`);
  }
}

document.getElementById("save").addEventListener("click", save);
document.getElementById("test").addEventListener("click", test);
load();
