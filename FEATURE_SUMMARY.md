# 📋 FEATURE SUMMARY — Multi-Platform Video Downloader (MVP)

> **Mục đích tài liệu**: Tổng hợp toàn bộ tính năng, kiến trúc, và logic của tool MVP này để làm tài liệu tham chiếu khi tích hợp vào project chính thức.
>
> **Ngày tổng hợp**: 2026-05-24  
> **Trạng thái**: MVP (Minimum Viable Product) — đã hoạt động ổn định

---

## 1. TỔNG QUAN DỰ ÁN

| Thuộc tính | Giá trị |
|---|---|
| **Tên tool** | Multi-Platform Video Downloader |
| **Ngôn ngữ** | Python 3.8+ |
| **Platform** | Windows 10/11 |
| **GUI Framework** | Tkinter (built-in Python) |
| **Core Engine** | yt-dlp >= 2026.3.17 |
| **Video Processing** | FFmpeg (bundled trong project) |
| **Kiến trúc** | Single-file OOP (`main.py`) — class `VideoDownloader` |
| **Success rate** | ~98% cho YouTube công khai |

---

## 2. CÁC NỀN TẢNG ĐƯỢC HỖ TRỢ

### 2.1 YouTube
- URL đơn lẻ: `https://youtube.com/watch?v=...`
- Short URL: `https://youtu.be/...`
- Mobile URL: `https://m.youtube.com/...`
- **Playlist**: tự động extract tất cả video trong playlist
- Domains detect: `youtube.com`, `youtu.be`, `www.youtube.com`, `m.youtube.com`

### 2.2 TikTok
- URL chuẩn: `https://www.tiktok.com/@username/video/...`
- Short URL: `https://vm.tiktok.com/...`, `https://vt.tiktok.com/...`
- Domains detect: `tiktok.com`, `vm.tiktok.com`, `vt.tiktok.com`, `www.tiktok.com`

### 2.3 Douyin (抖音)
- URL chuẩn: `https://www.douyin.com/video/...`
- Short URL: `https://v.douyin.com/...`
- Domains detect: `douyin.com`, `www.douyin.com`

---

## 3. TÍNH NĂNG CHÍNH (CHI TIẾT)

### 3.1 Chọn Chất Lượng Video (Quality Selection)

6 mức chất lượng:

| Option | Label UI | Format Selector (YouTube) | Format Selector (Douyin/TikTok) |
|--------|----------|--------------------------|--------------------------------|
| `720p` | 720p (Fast) | `bestvideo[height<=720]+bestaudio/best[height<=720]/best` | `best[height<=720]/best` |
| `1080p` | 1080p (Balanced) — **default** | `bestvideo[height<=1080]+bestaudio/bestvideo[height<=720]+bestaudio/best` | `best[height<=1080]/best` |
| `1440p` | 1440p (High) | `bestvideo[height<=1440]+bestaudio/bestvideo[height<=1080]+bestaudio/best` | `best[height<=1440]/best` |
| `4k` | 4K (Best) | `bestvideo[height<=2160]+bestaudio/bestvideo[height<=1080]+bestaudio/best` | `best[height<=2160]/best` |
| `auto` | Auto | `bestvideo+bestaudio/best` | `best` |
| `best` | Best Available | `bestvideo+bestaudio/best` | `best` |

> **Lý do tách biệt**: YouTube dùng `bestvideo+bestaudio` (tách stream rồi merge qua FFmpeg), còn Douyin/TikTok thường có stream đã merged sẵn nên dùng `best` đơn giản hơn.

---

### 3.2 Download Video Đơn Lẻ (Single Video Download)

**Flow xử lý:**
```
User nhập URL
    → validate URL (platform detection)
    → get_video_urls() — extract actual video URL (xử lý playlist nếu có)
    → vòng lặp từng video_url:
        → kiểm tra duplicate (history.txt)
        → download_single_video()
            → get_format_for_quality() — chọn format string
            → fallback loop (3 lần):
                Attempt 1: format gốc theo quality
                Attempt 2: bestvideo+bestaudio/best
                Attempt 3: bestvideo*+bestaudio*/best*
            → _run_download() — gọi yt-dlp thực sự
            → save_to_history()
    → hiển thị kết quả (downloaded / skipped / failed)
```

**Fallback strategy (3 tầng):**
1. Format cụ thể theo quality được chọn
2. `bestvideo+bestaudio/best` — fallback chung
3. `bestvideo*+bestaudio*/best*` — fallback cuối cùng với wildcard

**Delay giữa các lần retry**: 1 giây (`time.sleep(1)`)

---

### 3.3 Download Batch (Nhiều URL cùng lúc)

**UI**: Text area, mỗi URL một dòng

**Flow:**
```
Parse URLs từ text area
    → validate từng URL → tách valid / invalid
    → nếu có invalid: confirm dialog
    → filter duplicate (so với history.txt)
    → hỏi user: parallel hay sequential?
    → chạy download worker trong thread riêng
```

**Hai chế độ batch:**

| Chế độ | Mô tả | Số workers |
|--------|-------|-----------|
| **Sequential** | Tải lần lượt, an toàn hơn | 1 |
| **Parallel** | Tải song song, nhanh hơn | `min(3, len(urls))` — tối đa 3 luồng |

---

### 3.4 Playlist Support (YouTube)

- `get_video_urls()` tự động detect playlist qua `'entries'` trong metadata
- Extract toàn bộ `webpage_url` của từng entry
- Mỗi video trong playlist được xử lý độc lập (có thể skip nếu đã tải)

---

### 3.5 Cookie Authentication (Tùy chọn)

**Mục đích**: Bypass YouTube bot-check, tải video age-restricted hoặc member-only

**Cách hoạt động:**
- User browse chọn file `cookies.txt` (export từ browser bằng extension *"Get cookies.txt LOCALLY"*)
- Path lưu vào `cookies_file_var` (tk.StringVar)
- Được inject vào `yt-dlp` options qua `cookiefile` parameter
- **KHÔNG bắt buộc** — hoàn toàn optional, chỉ dùng khi YouTube yêu cầu

**Logic kiểm tra:**
```python
# Trong get_download_options() — throw error nếu file không tồn tại
cookies_path = self.cookies_file_var.get().strip()
if cookies_path:
    if not os.path.exists(cookies_path):
        raise RuntimeError(f"Cookies file not found: {cookies_path}")
    base_opts['cookiefile'] = cookies_path

# Trong get_video_urls() — silent skip nếu file không tồn tại
cookies_path = self.cookies_file_var.get().strip()
if cookies_path and os.path.exists(cookies_path):
    opts['cookiefile'] = cookies_path
```

---

### 3.6 YouTube N-Challenge Solver (Node.js)

**Mục đích**: Bypass YouTube's throttling mechanism (n-parameter trong URL)  
**Yêu cầu**: Node.js cài đặt trên máy  
**Tự động detect Node.js từ:**
1. `C:\Program Files\nodejs\node.exe`
2. `C:\Program Files (x86)\nodejs\node.exe`
3. `shutil.which('node')` — tìm trong PATH

**Inject vào yt-dlp:**
```python
base_opts['js_runtimes'] = {'node': {'path': self.node_path}}
```

---

### 3.7 FFmpeg Integration

**Mục đích**: Merge video+audio stream, convert sang MP4

**Detect**: Tìm `ffmpeg.exe` tại `{project_dir}/ffmpeg/bin/`

**Khi có FFmpeg:**
```python
base_opts['ffmpeg_location'] = self.ffmpeg_dir
base_opts['merge_output_format'] = 'mp4'
base_opts['postprocessors'] = [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}]
```

**Khi không có FFmpeg**: Vẫn chạy được nhưng không merge stream, output có thể là `.webm` hoặc format khác

---

### 3.8 Duplicate Detection & History

**File lưu**: `history.txt` — cùng thư mục với `main.py`

**Format mỗi dòng:**
```
{video_title} | {video_url}
```

**Ví dụ thực tế (từ project):**
```
KIỂM TOÁN BUỔI 6-1 | https://www.youtube.com/watch?v=_EpLwA5_aG4
K52 - KE1 - Buổi 2 20260506 | https://www.youtube.com/watch?v=YaZ3J53w1WA
```

**Logic check duplicate**: So sánh URL substring trong toàn bộ file history

---

### 3.9 Progress Tracking (Real-time)

**Hook yt-dlp**: `progress_hook(d)` — được gọi liên tục trong quá trình download

**Track 2 state:**
- `downloading`: tính % từ `total_bytes` hoặc `_percent_str`
- `finished`: set 100%

**Update UI**: Polling mỗi 1 giây qua `root.after(1000, update_progress_display)`

**Display format**: `Downloading: {filename_30chars}... ({percent:.1f}%)`

---

### 3.10 Output Configuration

**Thư mục output mặc định:**
```
E:\Tool\DownLoadVideo\DownLoadYoutube\output\2026\KeToan
```
> ⚠️ **Hard-coded** — đây là điểm cần refactor khi tích hợp vào project chính

**Naming convention**: `%(title)s.%(ext)s` — tên theo tiêu đề video gốc

**Auto-create**: `os.makedirs(self.output_dir, exist_ok=True)`

---

### 3.11 HTTP Headers (Anti-bot)

Tất cả request đều dùng User-Agent giả lập Chrome:
```
Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 
(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36
```

---

### 3.12 Retry Configuration

```python
'retries': 3,           # Retry toàn bộ download
'fragment_retries': 3,  # Retry từng fragment (HLS/DASH)
'nocheckcertificate': True,  # Bỏ qua SSL errors
```

---

## 4. GIAO DIỆN NGƯỜI DÙNG (GUI)

### Layout tổng thể (760x620 px):
```
┌─────────────────────────────────────────┐
│  Quality Options                         │
│  [720p] [1080p*] [1440p] [4K] [Auto] [Best] │
├─────────────────────────────────────────┤
│  YouTube Cookies (optional)              │
│  cookies.txt: [________________] [Browse] [Clear] │
├─────────────────────────────────────────┤
│  Single Video Download                   │
│  [URL input field                      ] │
│           [Download Video]               │
├─────────────────────────────────────────┤
│  Batch Download                          │
│  [URL 1                                ] │
│  [URL 2                                ] │
│  [URL 3...]                              │
│  [Download All] [Clear List] [Sample URLs]│
├─────────────────────────────────────────┤
│  [View History]                          │
│  Status: Ready to download               │
│  Tip: If YouTube says 'Sign in...'       │
└─────────────────────────────────────────┘
```

### Các widget chính:
| Widget | Variable | Mô tả |
|--------|----------|-------|
| `url_entry` | — | Single URL input |
| `url_list_entry` | — | ScrolledText cho batch |
| `quality_var` | `tk.StringVar(value="1080p")` | Radio button quality |
| `cookies_file_var` | `tk.StringVar(value="")` | Path cookies.txt |
| `btn_download` | — | Trigger single download |
| `btn_download_list` | — | Trigger batch download |
| `status_label` | — | Real-time status text |

### Thread Safety:
- Mọi download chạy trong **background thread** (`threading.Thread(daemon=True)`)
- UI update qua `root.after(0, lambda: ...)` — thread-safe
- Disable/enable buttons trong quá trình download

---

## 5. CÁC PHƯƠNG THỨC QUAN TRỌNG (API Reference)

### Core Methods:

```python
# Kiểm tra platform từ URL
get_platform_type(url: str) -> str  # 'youtube' | 'douyin' | 'unknown'
is_valid_url(url: str) -> bool

# Lấy format selector string
get_format_for_quality(quality_choice: str, platform: str) -> str

# Build yt-dlp options dict
get_download_options(format_selector: str) -> dict
    # Raises RuntimeError nếu cookies file được chỉ định nhưng không tồn tại

# Extract danh sách URL từ link (hỗ trợ playlist)
get_video_urls(url: str) -> list[str]
    # Raises RuntimeError nếu không extract được

# Thực thi download (low-level)
_run_download(ydl_opts: dict, url: str) -> str  # returns "title.ext"
    # Saves to history sau khi thành công

# Download 1 video với fallback
download_single_video(url: str, quality_choice: str = None) -> str
    # Raises RuntimeError nếu tất cả fallback đều thất bại

# Batch download
download_parallel(urls, downloaded, failed, quality_choice)  # max 3 threads
download_sequential(urls, downloaded, failed, quality_choice)  # 1 by 1

# History
save_to_history(video_title: str, video_url: str)
is_duplicate_download(video_url: str) -> bool
```

---

## 6. XỬ LÝ LỖI

### Các lỗi được handle:

| Lỗi | Xử lý |
|-----|-------|
| URL không hợp lệ | Validate trước khi download, show error dialog |
| Cookies file không tồn tại | `RuntimeError` với message rõ ràng |
| Download thất bại | 3-level fallback format, log từng lần thất bại |
| Video đã tải | Skip, không báo lỗi, ghi vào skipped count |
| Playlist extraction thất bại | `RuntimeError`, bubble lên UI |
| Batch có URL không hợp lệ | Confirm dialog, tiếp tục với URL hợp lệ |
| FFmpeg không có | Graceful degradation (vẫn tải được, không merge) |
| Node.js không có | Graceful degradation (không dùng n-challenge solver) |

### Error display:
- **Dialog**: `messagebox.showerror()` cho lỗi nghiêm trọng
- **Status label**: Update text màu blue/red theo trạng thái
- **Console**: `print()` log chi tiết cho debugging

---

## 7. DEPENDENCIES

```
yt-dlp >= 2026.3.17     # REQUIRED — core downloader
tkinter                  # REQUIRED — built-in Python
threading                # REQUIRED — built-in Python
concurrent.futures       # REQUIRED — built-in Python
subprocess               # REQUIRED — built-in Python
os, time, shutil         # REQUIRED — built-in Python
ffmpeg (binary)          # OPTIONAL — merge/convert video
Node.js                  # OPTIONAL — YouTube n-challenge solver
```

---

## 8. CẤU TRÚC FILE

```
DownLoadYoutube/
├── main.py                     # Toàn bộ source code (~585 lines)
├── requirements.txt            # chỉ có yt-dlp
├── history.txt                 # Log các video đã tải (auto-generated)
├── README.md                   # Tài liệu gốc
├── FEATURE_SUMMARY.md          # File này
├── ffmpeg/
│   └── bin/
│       ├── ffmpeg.exe          # Video processing
│       ├── ffplay.exe          # Media player
│       └── ffprobe.exe         # Media info
├── output/
│   └── 2026/
│       └── KeToan/             # Nơi lưu video (hard-coded)
└── .venv/                      # Python virtual environment
```

---

## 9. GIỚI HẠN HIỆN TẠI CỦA MVP

> Những điểm này cần được giải quyết khi tích hợp vào project chính

| # | Hạn chế | Mức độ ưu tiên |
|---|---------|---------------|
| 1 | **Output path hard-coded**: `E:\Tool\DownLoadVideo\DownLoadYoutube\output\2026\KeToan` | 🔴 Critical |
| 2 | **Single-file architecture**: Toàn bộ logic trong `main.py` — khó maintain khi scale | 🟠 High |
| 3 | **Không có config file**: Mọi setting đều hard-coded hoặc chỉ tồn tại trong session | 🟠 High |
| 4 | **Tkinter GUI**: Không phù hợp cho web app hoặc API service | 🟡 Medium |
| 5 | **Không có queue management**: Không thể pause/resume/cancel đang tải | 🟡 Medium |
| 6 | **No logging system**: Dùng `print()` thuần, không có log file | 🟡 Medium |
| 7 | **History dạng flat file**: `history.txt` không phù hợp khi cần query phức tạp | 🟡 Medium |
| 8 | **Không hỗ trợ proxy**: Không có cơ chế proxy rotation | 🟢 Low |
| 9 | **Không có download speed limiter** | 🟢 Low |
| 10 | **Không có subtitle download** | 🟢 Low |

---

## 10. GỢI Ý KHI TÍCH HỢP VÀO PROJECT CHÍNH

### 10.1 Tách module (Recommended architecture)

```
project/
├── services/
│   └── video_downloader/
│       ├── __init__.py
│       ├── downloader.py       # Core logic (tách từ VideoDownloader class)
│       ├── validators.py       # URL validation methods
│       ├── history.py          # History management (nên dùng DB)
│       └── config.py           # Download options builder
├── models/
│   └── download_job.py         # DownloadJob model
└── ...
```

### 10.2 Core logic cần giữ nguyên (đã proven)

```python
# ✅ Giữ nguyên — logic đã ổn định
get_format_for_quality()    # Format selector per platform
get_download_options()      # yt-dlp options builder
_run_download()             # Core download execution
download_single_video()     # Fallback strategy (3 levels)
progress_hook()             # Progress tracking
```

### 10.3 Phần cần refactor

```python
# ❌ Cần refactor
setup_paths()               # Hard-coded paths → config file / env vars
get_download_options()      # cookies_file_var phụ thuộc vào GUI tkinter
                            # → tách thành parameter thuần Python
download_parallel()         # max_workers hard-coded = 3 → configurable
```

### 10.4 Config nên externalize

```python
# Nên đưa ra config.py hoặc .env
OUTPUT_DIR = os.environ.get('DOWNLOAD_OUTPUT_DIR', './output')
FFMPEG_DIR = os.environ.get('FFMPEG_DIR', './ffmpeg/bin')
MAX_PARALLEL_DOWNLOADS = int(os.environ.get('MAX_PARALLEL', '3'))
HISTORY_FILE = os.environ.get('HISTORY_FILE', './history.txt')
DEFAULT_QUALITY = os.environ.get('DEFAULT_QUALITY', '1080p')
```

### 10.5 History nên chuyển sang DB

```sql
-- SQLite schema gợi ý
CREATE TABLE download_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    title       TEXT NOT NULL,
    url         TEXT NOT NULL UNIQUE,
    platform    TEXT,           -- 'youtube' | 'tiktok' | 'douyin'
    quality     TEXT,
    file_path   TEXT,
    file_size   INTEGER,
    downloaded_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

### 10.6 Nếu tích hợp vào web backend

```python
# Thay vì Tkinter, expose qua API
class VideoDownloadService:
    def download(self, url: str, quality: str = '1080p',
                 output_dir: str = None, cookies: str = None) -> dict:
        """
        Returns: {
            'success': bool,
            'filename': str,
            'title': str,
            'error': str | None
        }
        """
```

---

## 11. DATA FLOW DIAGRAM

```
User Input (URL + Quality + [Cookies])
          │
          ▼
    Validate URL
    (is_valid_url)
          │
          ▼
   Extract Video URLs
   (get_video_urls)
   ┌──── yt-dlp extract_info ────┐
   │  playlist? → list of URLs   │
   │  single?   → [url]          │
   └─────────────────────────────┘
          │
          ▼
   For each video_url:
   ┌──── Check Duplicate ────┐
   │  in history.txt? → SKIP │
   └─────────────────────────┘
          │ (not duplicate)
          ▼
   download_single_video()
   ┌──────────────────────────────────┐
   │  Attempt 1: quality format       │
   │  Attempt 2: bestvideo+bestaudio  │
   │  Attempt 3: bestvideo*+bestaudio*│
   └──────────────────────────────────┘
          │
          ▼
   _run_download()
   ┌──────────────────────────────────┐
   │  yt-dlp download                 │
   │  → progress_hook (real-time %)   │
   │  → FFmpeg merge (if available)   │
   │  → save to output_dir            │
   │  → save_to_history()             │
   └──────────────────────────────────┘
          │
          ▼
   Show Results Dialog
   (downloaded / skipped / failed counts)
```

---

## 12. THÔNG TIN BỔ SUNG

### Tested với (từ history.txt):
- ✅ YouTube lecture videos (VACPA, KIỂM TOÁN, TỔNG ÔN LUẬT)
- ✅ YouTube series videos (K42 - KE2, K52 - KE1)
- ✅ Videos với tên tiếng Việt (UTF-8)
- ✅ 45+ videos đã download thành công

### Browser Cookies Export:
- Extension: **"Get cookies.txt LOCALLY"** (Chrome/Firefox)
- Tên file output: `www.youtube.com_cookies.txt`
- Format: Netscape cookies format (tương thích với yt-dlp)

### Version thư viện đang dùng:
```
yt-dlp==2026.3.17
Python 3.x (Windows)
FFmpeg bundled
```

---

*Tài liệu này được tổng hợp tự động từ source code và tài liệu dự án.*  
*Last updated: 2026-05-24*
