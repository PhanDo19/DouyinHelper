# Local Video Detector extension

This unpacked Chrome/Coc Coc extension detects clear media requests in the browser and sends candidates to the Python app running on `127.0.0.1`.

## Install

1. Open `chrome://extensions` or Coc Coc's extensions page.
2. Enable Developer mode.
3. Click "Load unpacked".
4. Select this `browser_extension` folder.
5. Open the Python app, go to the `Browser Detector` tab, copy the token.
6. Open the extension popup, paste the token, keep port `8765` (the app always uses this port; if it's busy the app shows an error instead of moving ports), then click Save/Test.

## Notes

- The token changes every app launch.
- The extension forwards selected request headers, including `Cookie` when the browser exposes it. Keep this local.
- **Security:** to download private/age-restricted videos the extension collects your Google/YouTube auth cookies (including login session tokens) and sends them to the local app over `127.0.0.1`, protected only by the shared token. Only enable the extension when you need it, and don't share the token.
- DRM/EME streams are not supported.
- For YouTube, selecting any detected `googlevideo` row lets the app retry the original YouTube page through `yt-dlp` at the quality selected in the app's `Browser Detector` tab. The detected request provides browser context/cookies; it is not limited to the visible 360p row unless the page retry fails.
- Batch mode: paste URLs into the app's `Browser Detector` tab and click `Start Batch`. The extension polls the local app, opens one URL at a time, sends the first usable video candidate, then closes the tab and moves to the next URL. Keep the extension enabled and the token current.
