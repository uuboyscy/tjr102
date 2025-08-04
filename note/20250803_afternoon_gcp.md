# 2025/08/03 GCP 下午課程筆記

## Artifact Registry 與 Docker Image 上傳

### 1. Artifact Registry 介紹
- 類似 Docker Hub，可自建 image 倉庫。
- 支援多種倉庫格式：Docker、Python（PyPI）、Node.js（NPM）、Java（Maven）。
- 可建立 Docker 倉庫來儲存自製的映像檔。

### 2. 建立 Docker 倉庫流程
- 在 GCP Console 搜尋並進入 Artifact Registry。
- 點選「Create Repository」：
  - 命名例如：`tgr102-docker`
  - 選擇地區：台灣（`asia-east1`）

### 3. 建立並下載 Service Account 金鑰
- 進入 IAM，建立 Service Account，命名如：`artifact-registry-user`
- 賦予權限：Artifact Registry Administrator
- 下載 JSON 金鑰，存放於專案目錄，建議命名為 `artifact-registry-user.json`

### 4. Docker 登入 Artifact Registry
- 使用 JSON 金鑰透過 gcloud 工具進行登入：
  - Mac 指令：
    ```bash
    gcloud auth activate-service-account --key-file=artifact-registry-user.json
    gcloud auth configure-docker asia-east1-docker.pkg.dev
    ```
  - Windows 則使用 PowerShell 執行對應指令

### 5. 建立 Docker Image
- 尋找之前寫的 Docker 專案（含 `Dockerfile` 與 `app.py`）
- 在 VSCode terminal 中執行 build 指令：
  ```bash
  docker build -f flask.dockerfile -t asia-east1-docker.pkg.dev/專案名稱/倉庫名稱/映像名稱:latest .
  ```

### 6. 上傳 Image 到 Artifact Registry
- 透過 `docker push` 指令將 image 上傳：
  ```bash
  docker push asia-east1-docker.pkg.dev/專案名稱/倉庫名稱/映像名稱:latest
  ```
- 成功後在 Artifact Registry 介面可見該 image。

### 7. 注意事項
- 預設只有同一專案內部的人或持有金鑰者可下載此 image。
- 避免自動更新 Docker，除非發生 bug 或不能正常使用再考慮更新。
- Python 3.13 雖支援移除 GIL，但需自行編譯 Python 原始碼才能使用。

---

## Cloud Run 介紹（預告）
- 教學將進入 Cloud Run 部署。
- 並將使用 Gemini API 免費額度作為實作案例。
