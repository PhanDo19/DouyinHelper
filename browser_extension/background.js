const DEFAULTS = {
  enabled: true,
  port: 8765,
  token: ""
};

const ALLOWED_HEADERS = new Set([
  "accept",
  "accept-language",
  "cookie",
  "origin",
  "range",
  "referer",
  "user-agent"
]);

const pageByTab = new Map();
const recentKeys = new Map();
const activeJobsByTab = new Map();
let currentJob = null;

// MV3 service workers are suspended after ~30s idle, so in-memory state
// (currentJob / activeJobsByTab) can be wiped between events. Persist the
// active batch job to session storage and rehydrate it on every wake-up.
async function persistCurrentJob() {
  try {
    await chrome.storage.session.set({ currentJob });
  } catch (_) {}
}

async function rehydrateCurrentJob() {
  if (currentJob) return;
  try {
    const data = await chrome.storage.session.get({ currentJob: null });
    if (data.currentJob) {
      currentJob = data.currentJob;
      if (currentJob.tabId !== undefined) {
        activeJobsByTab.set(currentJob.tabId, currentJob);
      }
    }
  } catch (_) {}
}

async function clearCurrentJob() {
  currentJob = null;
  try {
    await chrome.storage.session.remove("currentJob");
  } catch (_) {}
}

function nowIso() {
  return new Date().toISOString();
}

function getSettings() {
  return chrome.storage.local.get(DEFAULTS);
}

function normalizeHeaderName(name) {
  return String(name || "")
    .split("-")
    .map((part) => part ? part[0].toUpperCase() + part.slice(1).toLowerCase() : part)
    .join("-");
}

function shouldCaptureUrl(url) {
  if (!url || /^(blob|data|filesystem):/i.test(url)) return false;
  if (isUiAssetUrl(url)) return false;
  if (/googlevideo\.com\/videoplayback/i.test(url)) return true;
  if (/\.(m3u8|mpd|mp4|webm|m4a|mp3|aac|opus)(\?|#|$)/i.test(url)) return true;
  return false;
}

function isUiAssetUrl(url) {
  try {
    const parsed = new URL(url);
    const host = parsed.hostname.toLowerCase();
    const path = parsed.pathname.toLowerCase();
    if (host.endsWith("youtube.com") && path.startsWith("/s/")) return true;
    if (/\/(failure|input|open|success)\.mp3$/i.test(path)) return true;
  } catch (_) {
    return false;
  }
  return false;
}

function isLikelySegmentOnly(url) {
  if (/googlevideo\.com\/videoplayback/i.test(url)) return false;
  return /\.(ts|m4s|cmfv|cmfa)(\?|#|$)/i.test(url);
}

function dedupeKey(payload) {
  try {
    const url = new URL(payload.media_url);
    if (/googlevideo\.com$/i.test(url.hostname) || /googlevideo\.com/i.test(url.hostname)) {
      const itag = url.searchParams.get("itag") || "";
      const mime = url.searchParams.get("mime") || "";
      if (itag) return `${payload.page_url}|${url.hostname}|${itag}|${mime}`;
    }
  } catch (_) {
    return payload.media_url;
  }
  return payload.media_url;
}

function remember(key) {
  const now = Date.now();
  for (const [k, value] of recentKeys) {
    if (now - value > 5 * 60 * 1000) recentKeys.delete(k);
  }
  if (recentKeys.has(key)) return false;
  recentKeys.set(key, now);
  return true;
}

function pageInfoFor(details) {
  const page = pageByTab.get(details.tabId) || {};
  const documentUrl = details.documentUrl || "";
  return {
    page_url: documentUrl || page.url || details.initiator || "",
    page_title: page.title || "",
    tab_id: details.tabId
  };
}

function getCookiesForUrl(url) {
  return new Promise((resolve) => {
    if (!url || !chrome.cookies || !chrome.cookies.getAll) {
      resolve([]);
      return;
    }
    try {
      chrome.cookies.getAll({ url }, (cookies) => {
        if (chrome.runtime.lastError) {
          resolve([]);
          return;
        }
        resolve(cookies || []);
      });
    } catch (_) {
      resolve([]);
    }
  });
}

// SECURITY: this gathers Google/YouTube auth cookies (including login session
// tokens) and sends them to the local downloader app over plain HTTP on
// 127.0.0.1, gated only by the shared token. Required to download private /
// age-restricted videos. Only enable the extension while you actually need it,
// and keep the token private.
async function collectAuthCookies(payload) {
  const urls = new Set();
  const pageUrl = payload.page_url || "";
  if (/youtube\.com|youtu\.be/i.test(pageUrl)) {
    urls.add("https://www.youtube.com/");
    urls.add("https://youtube.com/");
    urls.add("https://m.youtube.com/");
  }
  urls.add("https://accounts.google.com/");
  urls.add("https://www.google.com/");
  urls.add("https://google.com/");
  if (/googlevideo\.com/i.test(payload.media_url || "")) {
    try {
      const media = new URL(payload.media_url);
      urls.add(`${media.protocol}//${media.hostname}/`);
    } catch (_) {}
  }

  const byKey = new Map();
  for (const url of urls) {
    const cookies = await getCookiesForUrl(url);
    for (const cookie of cookies) {
      const key = `${cookie.domain}|${cookie.path}|${cookie.name}`;
      byKey.set(key, {
        domain: cookie.domain,
        hostOnly: Boolean(cookie.hostOnly),
        path: cookie.path || "/",
        secure: Boolean(cookie.secure),
        expirationDate: cookie.expirationDate || 0,
        name: cookie.name,
        value: cookie.value
      });
    }
  }
  return Array.from(byKey.values());
}

async function sendCandidate(payload) {
  const settings = await getSettings();
  if (!settings.enabled || !settings.token) return;

  const key = dedupeKey(payload);
  if (!remember(key)) return;

  payload.cookies = await collectAuthCookies(payload);

  const endpoint = `http://127.0.0.1:${settings.port}/candidate`;
  try {
    const res = await fetch(endpoint, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-Downloader-Token": settings.token
      },
      body: JSON.stringify(payload)
    });
    const body = await res.json().catch(() => ({}));
    await chrome.storage.local.set({
      lastStatus: res.ok ? "sent" : `failed ${res.status}`,
      lastError: res.ok ? "" : (body.error || ""),
      lastSentAt: nowIso()
    });
    if (res.ok && body.close_tab && payload.batch_id && payload.tab_id !== undefined) {
      closeBatchTab(payload.tab_id, payload.batch_id);
    }
  } catch (err) {
    await chrome.storage.local.set({
      lastStatus: "offline",
      lastError: String(err && err.message ? err.message : err),
      lastSentAt: nowIso()
    });
  }
}

function handleRequestHeaders(details) {
  if (!shouldCaptureUrl(details.url) || isLikelySegmentOnly(details.url)) return;

  const headers = {};
  for (const item of details.requestHeaders || []) {
    const lower = String(item.name || "").toLowerCase();
    if (ALLOWED_HEADERS.has(lower)) {
      headers[normalizeHeaderName(item.name)] = item.value || "";
    }
  }

  const job = activeJobsByTab.get(details.tabId);
  sendCandidate({
    source: "extension-webrequest",
    media_url: details.url,
    method: details.method || "GET",
    headers,
    initiator: details.initiator || "",
    timestamp: nowIso(),
    batch_id: job ? job.id : "",
    batch_url: job ? job.url : "",
    ...pageInfoFor(details)
  });
}

chrome.webRequest.onBeforeSendHeaders.addListener(
  handleRequestHeaders,
  { urls: ["<all_urls>"] },
  ["requestHeaders", "extraHeaders"]
);

chrome.runtime.onMessage.addListener((message, sender) => {
  if (!message || typeof message !== "object") return;
  const tabId = sender.tab && sender.tab.id;

  if (message.type === "page-info" && tabId !== undefined) {
    pageByTab.set(tabId, {
      url: message.url || "",
      title: message.title || ""
    });
    return;
  }

  if (message.type === "media-element" && shouldCaptureUrl(message.media_url)) {
    const job = activeJobsByTab.get(tabId);
    sendCandidate({
      source: "extension-media-element",
      media_url: message.media_url,
      method: "GET",
      headers: {},
      timestamp: nowIso(),
      page_url: message.page_url || "",
      page_title: message.page_title || "",
      tab_id: tabId,
      batch_id: job ? job.id : "",
      batch_url: job ? job.url : ""
    });
  }
});

chrome.tabs.onRemoved.addListener((tabId) => {
  pageByTab.delete(tabId);
  activeJobsByTab.delete(tabId);
  if (currentJob && currentJob.tabId === tabId) {
    clearCurrentJob();
  }
});

chrome.tabs.onUpdated.addListener((tabId, changeInfo) => {
  if (changeInfo.status === "complete" && activeJobsByTab.has(tabId)) {
    chrome.tabs.sendMessage(tabId, { type: "batch-play" }).catch(() => {});
  }
});

async function postLocal(path, payload = null) {
  const settings = await getSettings();
  if (!settings.enabled || !settings.token) return null;
  const res = await fetch(`http://127.0.0.1:${settings.port}${path}`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-Downloader-Token": settings.token
    },
    body: payload ? JSON.stringify(payload) : ""
  });
  return res.json().catch(() => null);
}

function createTab(url) {
  return new Promise((resolve, reject) => {
    chrome.tabs.create({ url, active: true }, (tab) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      resolve(tab);
    });
  });
}

async function pollBatchQueue() {
  await rehydrateCurrentJob();
  if (currentJob) return;
  let body;
  try {
    body = await postLocal("/batch/next");
  } catch (_) {
    return;
  }
  if (!body || !body.ok || !body.job) return;
  try {
    const tab = await createTab(body.job.url);
    currentJob = {
      ...body.job,
      tabId: tab.id,
      openedAt: Date.now(),
      closing: false
    };
    activeJobsByTab.set(tab.id, currentJob);
    await persistCurrentJob();
  } catch (err) {
    await postLocal("/batch/fail", {
      id: body.job.id,
      reason: err.message || String(err)
    });
    await clearCurrentJob();
  }
}

function closeBatchTab(tabId, jobId) {
  const job = activeJobsByTab.get(tabId);
  if (!job || job.id !== jobId || job.closing) return;
  job.closing = true;
  setTimeout(() => {
    chrome.tabs.remove(tabId, () => {
      activeJobsByTab.delete(tabId);
      if (currentJob && currentJob.id === jobId) {
        clearCurrentJob().then(pollBatchQueue);
      } else {
        pollBatchQueue();
      }
    });
  }, 3500);
}

async function checkBatchTimeout() {
  await rehydrateCurrentJob();
  if (!currentJob) return;
  if (Date.now() - currentJob.openedAt < 70000) return;
  const job = currentJob;
  await clearCurrentJob();
  activeJobsByTab.delete(job.tabId);
  chrome.tabs.remove(job.tabId, () => {});
  await postLocal("/batch/fail", {
    id: job.id,
    reason: "No media candidate detected before timeout"
  });
}

function tick() {
  pollBatchQueue();
  checkBatchTimeout();
}

// Fast cadence while the service worker is alive...
setInterval(tick, 2000);
// ...plus an alarm to wake a suspended MV3 worker. Chrome clamps alarm
// periods to ~30s minimum, so this is the recovery/heartbeat path, not the
// primary one — batches still progress (slower) even after the worker sleeps.
chrome.alarms.create("batchHeartbeat", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === "batchHeartbeat") tick();
});
