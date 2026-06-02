function sendPageInfo() {
  safeSend({
    type: "page-info",
    url: location.href,
    title: document.title || ""
  });
}

function shouldSendMediaUrl(url) {
  if (!url || /^(blob|data|filesystem):/i.test(url)) return false;
  return /\.(m3u8|mpd|mp4|webm|m4a|mp3|aac|opus)(\?|#|$)/i.test(url);
}

function scanMediaElements() {
  const nodes = document.querySelectorAll("video[src], audio[src], source[src]");
  for (const node of nodes) {
    const url = node.currentSrc || node.src;
    if (!shouldSendMediaUrl(url)) continue;
    safeSend({
      type: "media-element",
      media_url: url,
      page_url: location.href,
      page_title: document.title || ""
    });
  }
}

function safeSend(message) {
  try {
    chrome.runtime.sendMessage(message);
  } catch (_) {
    // The extension context can be invalidated during reload/update.
  }
}

function tryBatchPlay() {
  for (const video of document.querySelectorAll("video")) {
    try {
      video.muted = true;
      video.play().catch(() => {});
    } catch (_) {}
  }
  scanMediaElements();
}

chrome.runtime.onMessage.addListener((message) => {
  if (message && message.type === "batch-play") {
    setTimeout(tryBatchPlay, 500);
    setTimeout(tryBatchPlay, 2500);
  }
});

sendPageInfo();
document.addEventListener("DOMContentLoaded", () => {
  sendPageInfo();
  scanMediaElements();
});
window.addEventListener("load", () => {
  sendPageInfo();
  scanMediaElements();
});

let lastTitle = document.title;
let lastUrl = location.href;
setInterval(() => {
  if (document.title !== lastTitle || location.href !== lastUrl) {
    lastTitle = document.title;
    lastUrl = location.href;
    sendPageInfo();
  }
  scanMediaElements();
}, 3000);
