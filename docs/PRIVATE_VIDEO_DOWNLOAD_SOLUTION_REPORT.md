# Bao cao giai phap tai video private kieu Coc Coc

Ngay lap bao cao: 2026-06-02  
Pham vi review: app Python/Tkinter hien tai trong repo `new2`, trong tam la tab YouTube/TikTok/Douyin downloader va yeu cau tai video private khi nguoi dung co quyen xem.

## 1. Ket luan ngan gon

Khong the cam ket "chac chan tai duoc 100%" cho moi video private.

Co the xay dung mot solution kha tin cay neu video thoa tat ca dieu kien sau:

- Tai khoan nguoi dung dang nhap co quyen xem video.
- Stream la clear media, vi du direct MP4, HLS `.m3u8`, DASH `.mpd`/segment khong DRM.
- Cookie/session/header con hieu luc tai thoi diem tai.
- Request download chay cung dieu kien voi browser: dung IP/VPN/proxy, user-agent, referer, cookie, token tam thoi.
- Nen tang chua thay doi anti-bot, PO token, SABR, signature, hoac co fallback cap nhat kip.

Khong nen va khong the ho tro cac truong hop:

- Tai khoan khong co quyen xem video private.
- Noi dung DRM/EME/Widevine/PlayReady, phim thue/mua, paid VOD co license.
- Bypass paywall, membership, geo-block, age/identity check khi tai khoan khong du dieu kien.
- Video ma Dieu khoan dich vu cam tai xuong neu khong duoc phep.

Noi cach khac: "giong Coc Coc" ve mat ky thuat nen hieu la app nam trong/canh browser session de nhin thay request media, khong phai co kha nang vuot qua quyen truy cap hoac DRM.

## 2. Hien trang app trong repo

### 2.1 Thanh phan san co

- File chinh: `douyin_youtube_tool.py`.
- Dependency: `yt-dlp>=2025.1.1` trong `requirements.txt`.
- Moi truong hien tai co `yt-dlp 2026.03.17`.
- Repo co `ffmpeg/bin/ffmpeg.exe`, app auto-detect qua `FFMPEG_DIR`.
- Co nhieu file cookie trong root repo: `cookies.txt`, `cookies1.txt`, `cookies_Oanh96.txt`, `cookies_Oanh_all.txt`, `yt_cookies_auto.txt`.

### 2.2 Logic tai video hien tai

Trong `douyin_youtube_tool.py`:

- `_yt_build_opts(...)`: build option cho `yt-dlp`, co `format`, `outtmpl`, `ffmpeg_location`, `cookiefile`, `extractor_args`.
- `_yt_download_single(...)`: thu nhieu fallback cho YouTube:
  - no-cookie client: `android_vr`, `web_safari`, `tv_downgraded`;
  - cookie file neu nguoi dung chon;
  - `cookiesfrombrowser` cho Chrome/Edge/Firefox/Chromium;
  - fallback cuoi: `_yt_download_via_coccoc(...)`.
- `_yt_auto_cookie_from_browser(...)`: hien tai chu yeu la popup huong dan export `cookies.txt`; khong phai auto import that su.
- `_coccoc_cdp_get_player_response(...)`: co proof-of-concept mo Coc Coc bang remote debugging, doc `ytInitialPlayerResponse`, bat URL `videoplayback`.
- `_yt_download_via_coccoc(...)`: neu lay duoc URL truc tiep thi tai bang `ffmpeg` hoac `urlretrieve`.

### 2.3 Diem manh

- Da dung `yt-dlp`, dung huong cho YouTube/TikTok/Douyin.
- Da bundle `ffmpeg`, can thiet cho YouTube DASH high-quality video/audio merge.
- Da co UI chon `cookies.txt`, chon quality, batch download, history.
- Da co y tuong fallback Coccoc/CDP, cho thay huong "browser context" da duoc nghien cuu.

### 2.4 Diem yeu/bug can sua truoc khi tin cay

1. Xu ly loi "private" dang qua som.

   Trong `_yt_download_single(...)`, neu error string co `"private"`, code raise ngay:

   ```python
   if "private" in err_lower or "members only" in err_lower or "join this channel" in err_lower:
       raise RuntimeError(...)
   ```

   Van de: voi video private, khi chua co cookie hoac cookie chua dung, YouTube co the bao private/sign-in. Neu raise ngay thi code khong con co co hoi thu browser cookie fallback. Nen tach:

   - co cookie hop le ma van private -> kha nang cao khong co quyen xem/invalid cookie;
   - chua co cookie -> nen tiep tuc thu cookie/browser fallback;
   - members-only -> chi fail sau khi da thu authenticated path.

2. Message "Khong the tai du co cookie" co the sai.

   Neu tai khoan co quyen xem, cookie chinh xac co the giup tai private video. Cau dung hon la: "Khong the tai neu tai khoan trong cookie khong co quyen xem hoac cookie het han."

3. Nut "Auto tu Browser" khong auto.

   Ham hien tai mo guide export cookie. Label nen doi thanh "Huong dan cookie" hoac implement auto theo huong extension/native messaging. Tranh tao ky vong sai.

4. Helper doc cookie Chrome truc tiep khong con ben vung.

   Chrome 127+ tren Windows co App-Bound Encryption cho cookie. Doc/decrypt cookie offline tu file SQLite khong nen la duong chinh. Nen xem cookie la credential nhay cam va uu tien lay tu browser extension/session hien hanh.

5. Coccoc fallback dang co hanh vi nguy hiem.

   `_coccoc_cdp_get_player_response(...)` dang `taskkill /F /IM browser.exe` de dong Coc Coc truoc khi mo CDP. Viec nay co the lam mat session/tab dang mo cua user. Nen chuyen sang profile rieng cua app, port rieng, va khong kill browser that cua user.

6. Coccoc/CDP fallback chua du cho YouTube hien dai.

   Cach doc `ytInitialPlayerResponse` va bat URL `videoplayback` co the that bai khi:

   - format chi co `signatureCipher`, `n` signature, PO token;
   - YouTube dung SABR/MSE khong lo URL cao cap ro rang;
   - URL het han nhanh;
   - request can header/cookie/token ma code khong truyen lai cho `ffmpeg`;
   - video co DRM/EME.

7. Cookie files trong repo root la rui ro bao mat.

   Cookie YouTube/Google co the tuong duong session dang nhap. Khong nen luu trong repo root, khong nen log, khong nen commit. Nen dua vao thu muc ignored local-only, mask ten file trong log, va co nut clear.

## 3. Vi sao Coc Coc co ve tai duoc nhieu hon app ngoai browser

Coc Coc/extension nam trong browser context:

- Browser da dang nhap, da co cookie va token hop le.
- Video player tao request media voi dung `Referer`, `Origin`, `User-Agent`, client hints, cookie, token, IP.
- Browser co DevTools/network layer nhin thay URL request media.
- Neu stream la clear HLS/DASH/MP4, browser hoac extension co the phat hien URL segment/manifest.

App ngoai browser thieu cac dieu kien do. Neu chi dua vao URL video, app phai tu tai metadata, giai signature, chong bot, gui cookie dung format, merge DASH. `yt-dlp` lam tot viec nay, nhung phu thuoc vao thay doi lien tuc tu platform.

## 4. Ma tran "tai duoc / khong tai duoc"

| Case | Kha nang ho tro | Dieu kien | Ghi chu |
| --- | --- | --- | --- |
| YouTube public | Cao | `yt-dlp` moi, ffmpeg co san | Van co the bi anti-bot/PO token trong tung thoi diem |
| YouTube unlisted | Cao | Co URL | Gan nhu public neu khong co auth gate |
| YouTube age/login required | Trung binh-cao | Cookie tai khoan du dieu kien | Can cookie dung va con song |
| YouTube private duoc share cho tai khoan | Trung binh | Cookie cua tai khoan duoc share, khong DRM, khong bi token issue | Khong dam bao 100%; code hien tai can sua early private fail |
| YouTube private khong duoc share | Khong ho tro | Khong co quyen xem | Phai fail ro rang |
| YouTube members-only | Thap-trung binh | Cookie tai khoan dang la member, khong DRM, yt-dlp/client con ho tro | Rui ro ToS cao, de bi thay doi |
| YouTube movie/premium DRM | Khong ho tro | EME/Widevine/license | Khong nen implement bypass |
| TikTok/Douyin public | Trung binh-cao | `yt-dlp` hoac API hien tai con dung | Platform hay thay doi anti-scraping |
| Douyin/TikTok private/account-only | Trung binh-thap | Dang nhap co quyen, bat request tu browser | Nen dung extension/CDP thay vi API thu cong |
| HLS `.m3u8` clear | Cao | Manifest + key clear neu co + header dung | Dung `ffmpeg` |
| DASH `.mpd` clear | Trung binh-cao | Manifest + segment accessible | Dung `yt-dlp`/`ffmpeg` |
| DRM/EME stream | Khong ho tro | Can CDM/license | Chi nen detect va thong bao |

## 5. Kien truc de gan voi Coc Coc nhat

### 5.1 Khuyen nghi

Nen lam theo mo hinh Browser Companion:

```text
Chrome/Edge/Coc Coc extension
        |
        | gui video candidates + headers toi local app
        v
Python local receiver 127.0.0.1 hoac Native Messaging
        |
        v
Tkinter "Browser Detector" tab
        |
        v
yt-dlp / ffmpeg download engine
```

### 5.2 Thanh phan extension

Extension Manifest V3:

- `background service_worker`: nghe `chrome.webRequest` cho request media.
- `content_script` chay som tren page: inject script vao MAIN world de hook `fetch`/`XMLHttpRequest` khi can.
- `host_permissions`: gioi han theo domain user bat/tat, tranh `*://*/*` neu khong can.
- Phat hien:
  - `.m3u8`, `.mpd`, `.mp4`, `.webm`;
  - `videoplayback`, `m4s`, `ts`, `range` video;
  - `content-type` video/audio/application dash/hls.
- Metadata gui ve app:
  - `page_url`, `page_title`, `frame_url`;
  - `media_url`;
  - `method`, `request_headers` can thiet;
  - `response_headers`, `content_type`, `content_length`;
  - timestamp, tab id, platform guess.

### 5.3 Kenh giao tiep extension -> app

Co 2 lua chon:

1. Local HTTP server `127.0.0.1`

   Uu diem:
   - De implement trong app Python.
   - Khong can registry/native host.
   - Debug nhanh.

   Can bao mat:
   - App sinh token random moi lan chay.
   - Extension phai gui header `X-Downloader-Token`.
   - Chi bind `127.0.0.1`.
   - Validate origin/schema, rate limit.
   - Khong cho web page bat ky gui request vao queue.

2. Chrome Native Messaging

   Uu diem:
   - Kenh chinh thuc giua extension va native app.
   - Co `allowed_origins` rang buoc extension ID.
   - It bi web page local request gia mao.

   Nhuoc diem:
   - Can cai manifest/registry tren Windows.
   - Phuc tap hon khi package app.

Khuyen nghi thuc te: bat dau voi local HTTP server co token de nhanh ra MVP, sau do them Native Messaging neu muon san pham on dinh.

### 5.4 Download engine

Them mot model noi bo:

```python
DownloadCandidate = {
    "id": "...",
    "page_url": "...",
    "page_title": "...",
    "media_url": "...",
    "media_type": "hls|dash|direct|unknown",
    "headers": {
        "User-Agent": "...",
        "Referer": "...",
        "Origin": "...",
        "Cookie": "..."  # neu user cho phep, nen tranh luu disk
    },
    "expires_at": "...",
    "source": "extension|cdp|yt-dlp"
}
```

Downloader:

- Direct MP4/WebM: `yt-dlp` hoac Python requests voi headers.
- HLS `.m3u8`: `ffmpeg -headers ... -i <url> -c copy output.mp4`.
- DASH `.mpd`: uu tien `yt-dlp`; fallback `ffmpeg`.
- YouTube page URL: uu tien `yt-dlp` + cookiefile/cookies/session, neu fail thi browser detector candidate.

## 6. Sua doi toi thieu nen lam ngay

1. Sua logic private error trong `_yt_download_single(...)`.

   Nguyen tac:

   - Neu chua co cookiefile va dang o no-auth attempt, khong raise ngay voi `"private"`; tiep tuc den cookie/browser fallback.
   - Neu co cookiefile ma fail private, show: "Cookie khong hop le/het han hoac tai khoan khong co quyen xem."
   - Neu members-only/join channel, chi fail sau authenticated attempts.

2. Doi label "Auto tu Browser".

   Doi thanh "Huong dan Cookie" neu chua co auto that. Hoac them extension/CDP auto that su.

3. Khong kill Coc Coc dang chay.

   Dung profile rieng:

   ```text
   .browser-profiles/coccoc-downloader
   ```

   Hoac yeu cau user mo rieng bang nut "Open controlled browser".

4. Tach sensitive data.

   - Tao thu muc local ignored, vi du `.local_secrets/`.
   - Dua `cookies*.txt` ra ngoai repo hoac vao thu muc ignored.
   - Them rule `.gitignore` neu chua co.
   - Mask cookie path va khong log cookie value.

5. Them detect DRM.

   Neu extension/CDP thay EME/license/key-system request, hoac manifest co ContentProtection/PSSH, UI phai hien:

   "Noi dung co DRM/EME. App khong ho tro tai/decrypt noi dung DRM."

6. Cap nhat history/duplicate.

   Duplicate nen dua vao video id + file exists + size > 0, khong chi URL string.

## 7. Ke hoach trien khai de review

### Phase 1: Harden downloader hien tai

Thoi gian du kien: 0.5-1 ngay.

- Sua private/auth error classification.
- Doi text UI cookie.
- Doi Coccoc fallback de khong kill process that.
- Them thong bao DRM/no-permission ro rang.
- Chay test voi:
  - YouTube public;
  - unlisted;
  - private shared cho account test;
  - private not shared, expect fail;
  - cookie expired, expect fail ro rang.

### Phase 2: Browser Detector MVP

Thoi gian du kien: 2-4 ngay.

- Them local receiver trong Python.
- Them tab "Browser Detector" hien candidates.
- Tao extension folder rieng:
  - `extension/manifest.json`;
  - `extension/background.js`;
  - `extension/content.js`;
  - `extension/popup.html/js` neu can toggle.
- Gui candidate tu extension ve app.
- Download direct/HLS/DASH bang `ffmpeg`/`yt-dlp`.
- Khong luu cookie ra disk mac dinh.

### Phase 3: Native Messaging / packaging

Thoi gian du kien: 2-3 ngay.

- Them native host manifest.
- Register/unregister script cho Windows.
- Ky/goi extension neu can.
- Logging, diagnostics, export bug report khong chua cookie.

### Phase 4: Test matrix va release criteria

Release chi nen dat "stable" khi:

- Public/unlisted YouTube tai on dinh.
- Private shared account test tai duoc voi cookie/session hop le.
- Private not shared fail ro rang.
- DRM fail ro rang, khong treo.
- Cookie khong bi log.
- App khong dong browser cua user bat ngo.

## 8. Ranh gioi phap ly/ToS

Can them text trong UI/docs:

- Chi tai noi dung ban so huu, duoc phep tai, hoac duoc chu so huu cho phep.
- App khong vuot qua paywall, DRM, membership, hoac quyen rieng tu.
- YouTube Terms co dieu khoan han che download/content access ngoai nhung gi Service cho phep; nen can user tu chiu trach nhiem ve quyen su dung.

Day khong chi la disclaimer; no giup dinh nghia hanh vi dung cua app va tranh yeu cau "bypass".

## 9. Rui ro ky thuat chinh

| Rui ro | Muc do | Giam thieu |
| --- | --- | --- |
| Platform doi anti-bot/PO token | Cao | Cap nhat `yt-dlp`, giu fallback extension/CDP, log verbose khong co secret |
| Cookie/session het han | Cao | Huong dan refresh cookie, uu tien in-memory session tu browser |
| Chrome App-Bound Encryption | Cao | Khong doc cookie DB offline lam duong chinh; dung extension/session |
| DRM/EME | Cao | Detect va fail ro rang |
| URL media het han nhanh | Trung binh-cao | Download ngay khi detect, refresh candidate khi het han |
| Header/cookie thieu khi ffmpeg tai | Trung binh-cao | Luu headers can thiet theo candidate, truyen vao ffmpeg |
| Extension bi gioi han MV3 | Trung binh | Dung `webRequest` de observe, content-script hook cho fetch/XHR khi can |
| Bao mat cookie | Cao | Token local, khong log, khong luu disk mac dinh, ignored secrets dir |
| Coccoc/Chrome profile bi lock | Trung binh | Profile rieng, khong dung Default profile dang chay |

## 10. Cau tra loi cuoi cung cho cau hoi "co chac chan tai duoc khong?"

Khong chac chan cho "video private" noi chung.

Co the cam ket o muc san pham:

- App se tai duoc neu stream clear va user dang co quyen xem hop le.
- App se fail ro rang neu khong co quyen, cookie het han, DRM, hoac platform chan.
- App se khong co tinh nang bypass DRM/quyen truy cap.

Neu muc tieu cua ban la san pham thuc dung giong Coc Coc, huong dung la:

1. Harden `yt-dlp + cookie` hien tai.
2. Them Browser Detector extension/local receiver.
3. Dung Coccoc/CDP chi nhu fallback hoac controlled-browser mode, khong phai co che chinh.

## 11. Nguon tham khao

- Google Security Blog - Chrome App-Bound Encryption: https://security.googleblog.com/2024/07/improving-security-of-chrome-cookies-on.html
- Chrome Extensions `webRequest` API: https://developer.chrome.com/docs/extensions/reference/api/webRequest
- Chrome Native Messaging: https://developer.chrome.com/docs/extensions/develop/concepts/native-messaging
- Chrome DevTools Protocol Network domain: https://chromedevtools.github.io/devtools-protocol/tot/Network/
- W3C Encrypted Media Extensions: https://w3c.github.io/encrypted-media/
- yt-dlp README/options: https://github.com/yt-dlp/yt-dlp/blob/master/README.md
- YouTube Terms of Service: https://www.youtube.com/t/terms
