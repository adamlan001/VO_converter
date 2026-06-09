# VO Converter v0.1.0 - 發布說明

## 📦 發布包

**檔案名稱**: `VO_Converter_v0.1.0_win64_portable.zip`  
**大小**: 36 MB  
**平台**: Windows 11/10 (64-bit)

## 🚀 快速開始

### 安裝步驟

1. **解壓縮** ZIP 檔案到任意位置
   ```
   VO_Converter_v0.1.0_win64_portable.zip
   └── VO Converter/
       ├── VO Converter.exe          ← 執行此檔案
       ├── bin/                      ← ffmpeg 會自動下載到此
       ├── _internal/                ← Python 運行環境
       └── ...
   ```

2. **執行** `VO Converter.exe`
   - 首次啟動若無 ffmpeg，會自動彈出下載對話框
   - 下載後 ffmpeg 存放在 `bin/` 資料夾，之後啟動不再重複下載

3. **開始轉檔** - 拖放檔案或點「+ Add Files」新增來源

## ✨ 功能清單

### 核心功能
- ✓ 多格式轉檔 (MP4, MKV, MOV, AVI, WebM, GIF, MP3, AAC, WAV, FLAC, OGG, M4A)
- ✓ 多檔同時轉檔（可設定並行數量）
- ✓ 拖放檔案新增
- ✓ 自訂解析度、幀率、音訊參數

### 進階功能
- ✓ **GPU 加速** - NVIDIA NVENC、AMD AMF、Intel QSV 支援
- ✓ **自訂檔案命名** - 支援變數 {name}, {ext}, {format}, {timestamp}
- ✓ **可縮放 UI** - Settings 和 Progress 框高度可調，Settings 內容可捲動
- ✓ **刪除檔案** - 右鍵菜單刪除單一來源檔案
- ✓ **Custom 設定** - 解析度、幀率支援自訂輸入
- ✓ **轉檔進度** - 即時進度條、Log 輸出

## 📋 系統需求

- Windows 10/11 (64-bit)
- 2 GB+ RAM
- 500 MB+ 硬碟空間（不含輸出檔案）

## ⚙️ 配置說明

### ffmpeg 管理
- **自動下載**: 首次缺少 ffmpeg 時自動彈出下載選項
- **手動指定**: 若已安裝 ffmpeg，系統會自動找到 PATH 中的版本
- **位置**: 便攜版本會存放在 `bin/ffmpeg.exe`

### 轉檔設定
| 設定項 | 說明 |
|-------|------|
| Output Type | Video 或 Audio 轉檔 |
| Output Format | 輸出格式選擇 |
| Video Codec | 軟體編碼或 GPU 加速 |
| Resolution | 預設或自訂解析度 (e.g. 1920x1080) |
| Frame Rate | 預設或自訂幀率 (e.g. 23.976) |
| Video/Audio Bitrate | 自動或指定位元率 |
| Sample Rate | 原始或指定取樣率 |
| Channels | 原始、單聲道或立體聲 |

### 檔案命名規則
**預設**: `{name}_converted`

**支援變數**:
- `{name}` - 原始檔名（不含副檔名）
- `{ext}` - 原始副檔名
- `{format}` - 輸出格式 (MP4, MP3 等)
- `{timestamp}` - 時間戳 (YYYYMMDD-HHMMSS)

**範例**:
- `{name}_{format}` → `video_MP4.mp4`
- `archive_{timestamp}` → `archive_20260602-143022.mp3`

## 🐛 已知事項

- 首次啟動下載 ffmpeg 需要網路連線（約 70 MB）
- GIF 轉檔會自動調整解析度和幀率以控制檔案大小
- GPU 加速可用性取決於硬體和驅動

## 📝 License

ffmpeg 使用 GPL build，應用發布時需附上 ffmpeg 授權聲明

---

**版本**: 0.1.0  
**發布日期**: 2026-06-02
