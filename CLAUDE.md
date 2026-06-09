# VO Converter — 開發筆記

## 專案簡介

PyQt6 桌面影音格式轉換工具，底層使用 ffmpeg。

## 技術棧

- Python 3.11 + PyQt6
- ffmpeg（外部執行檔，透過 subprocess 呼叫）
- uv 管理套件
- PyInstaller 6.x（打包）

## 目錄結構

```
VO_converter/
├── main.py                  # 入口點，含 ffmpeg 啟動檢查
├── core/
│   ├── ffmpeg_resolver.py   # 解析 ffmpeg/ffprobe 路徑（bin/ 優先，再找 PATH）
│   ├── converter.py         # 建構 ffmpeg 指令
│   ├── worker.py            # QThread 背景轉換
│   ├── presets.py           # 格式、解析度、聲道設定
│   └── hw_detect.py         # 硬體加速偵測
├── ui/
│   ├── main_window.py       # 主視窗
│   ├── file_list_widget.py  # 檔案列表（支援拖放）
│   ├── format_panel.py      # 格式/參數設定面板
│   ├── progress_widget.py   # 轉換進度
│   └── setup_dialog.py      # 首次啟動下載 ffmpeg 的對話框
├── assets/
│   └── app.ico              # 應用程式圖示（16/32/48/256px）
├── vo_converter.spec        # PyInstaller 設定
└── build.ps1                # 一鍵建置腳本
```

## 開發環境

```powershell
uv sync              # 安裝所有依賴
uv run python main.py  # 執行開發版
```

## 打包發布（Windows Portable ZIP）

```powershell
powershell -ExecutionPolicy Bypass -File .\build.ps1
# 輸出：dist\VO_Converter_v0.1.0_win64_portable.zip
```

### 打包流程說明

1. 清除 `dist/`、`build/`
2. PyInstaller 以 `onedir` 模式打包（不用 `onefile`，啟動較快）
3. 建立空的 `bin/` 資料夾（供 ffmpeg 使用）
4. 壓縮成 ZIP

### 使用者體驗

- 解壓縮 → 執行 `VO Converter.exe`
- 若無 ffmpeg，自動彈出下載對話框（從 GitHub BtbN/FFmpeg-Builds 下載，約 70 MB）
- 下載後 ffmpeg.exe / ffprobe.exe 存放在 `bin/`，之後啟動不再重複下載

## 已知注意事項

- **ZIP 時的檔案鎖定**：PyInstaller 完成後 Windows Defender 可能仍在掃描，`build.ps1` 已加入 5 秒等待
- **ffmpeg 授權**：使用 GPL build，應用發布時需附上 ffmpeg 授權聲明
- **PowerShell 執行原則**：若無法直接執行 `.ps1`，改用 `powershell -ExecutionPolicy Bypass -File .\build.ps1`
