# 2025‑07‑03 Docker & DevContainer 課堂筆記

## 課程目標
- 瞭解 VS Code **DevContainer** 工作流程  
- 學會撰寫 **Dockerfile** 與 **devcontainer.json** 最小可行設定  
- 掌握容器的啟動、重建、停止與移除  
- 建立乾淨且可重現的 Python 專案結構與相依管理

---

## 1  DevContainer 基礎

### 1.1 三個核心檔案
| 檔案 | 角色 |
| ---- | ---- |
| `.devcontainer/devcontainer.json` | VS Code 建立開發容器的主要設定 |
| `Dockerfile` | 定義容器基底映像、系統套件與 Shell 環境 |
| `postCreateCommand.sh` | 容器第一次建立完成後要執行的初始化指令 |

### 1.2 devcontainer.json 最重要的三件事
1. **build** → 指定 `dockerFile` 與 `context`  
2. **runArgs** → `--name / --network` 等啟動參數  
3. **postCreateCommand** → 第一次進入容器時自動執行（安裝 Python 套件…）

> 其他如 `remoteEnv`、`customizations`（Extension 列表）屬「加分項」，可以視需求增減。

### 1.3 Network 模式
| 模式 | 行為 |
| ---- | ---- |
| `bridge` (預設) | 容器擁有私有 IP，透過 NAT 與主機溝通 |
| `host` | 共用主機網卡，容器 IP = 主機 IP |
| `none` | 完全隔離，不開網路 |

### 1.4 VS Code Extensions 推薦清單
- **ms‑python.python**：Python 語言支援  
- **charliermarsh.ruff**：靜態檢查／自動格式化  
- **eamodio.gitlens**、**donjayamanne.githistory**：圖形化 Git 歷史  
- **streetsidesoftware.code‑spell‑checker**：拼字檢查  
- 其他依專案需求新增

選擇原則：優先官方套件或下載量高、社群活躍者。

---

## 2  Dockerfile 實務與 Layer 概念
- 以官方映像（如 `python:3.12`）為 base  
- 設定時區：`ENV TZ=Asia/Taipei`  
- 單一 `RUN apt‑get update && apt‑get install …`；以 `\` 換行、`&&` 串接  
- **Layer 最佳化**：  
  - 不常改的指令（安裝系統套件）放前面  
  - 常改的指令（安裝 Python 套件）放後面  
  → 可重用快取、加速 rebuild

---

## 3  在 VS Code 開啟 / 切換 DevContainer
1. 安裝 **Remote‑SSH** 與 **Dev Containers** 擴充  
2. `⌘/Ctrl + Shift + P` → `Dev Containers: Reopen in Container`  
3. 二次啟動可選：  
   - **Reopen in Container**：直接掛載既有容器  
   - **Rebuild Container / Without Cache**：強制重建

> 進入容器判別：右下角綠色狀態列顯示 `(Dev Container: …)`，或終端機提示字不同。

---

## 4  容器管理指令（Docker CLI）

```bash
# 查看執行中容器
docker ps
# 查看全部（含已停止）
docker ps -a
# 停止容器
docker stop <CONTAINER_ID_or_NAME>
# 刪除容器
docker rm <CONTAINER_ID_or_NAME>
# 一步強制停止並刪除
docker rm -f <CONTAINER_ID_or_NAME>
```

---

## 5  專案結構建議

```
my-project/
├── .devcontainer/
│   ├── devcontainer.json
│   └── Dockerfile
├── src/            # 主要 Python 原始碼
│   ├── app/
│   └── utils/
├── requirements.txt      # （簡易）相依列表
├── Pipfile / poetry.*    # （推薦）虛擬環境與鎖檔
└── README.md
```

### 5.1 requirements.txt vs 虛擬環境管理工具
| 方法 | 優點 | 缺點 |
| ---- | ---- | ---- |
| `requirements.txt` | 操作簡單、可讀性高 | 會列出所有遞迴相依，檔案膨脹；無衝突解析 |
| `pipenv` / `poetry` | 自動解析相依、鎖定版本 hash；支援多環境 | 學習曲線較高 |

---

## 6  小抄
- 開新終端機：點 **`+`** 或 `Ctrl + \``  
- 指令面板：`Ctrl/Cmd + Shift + P`  
- 容器內外程式碼即時同步：VS Code 自動 volume bind  

---
