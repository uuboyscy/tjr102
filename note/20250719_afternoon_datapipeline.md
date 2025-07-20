# Tibame – GCP 雲端基礎（2025‑07‑19 早上）

> **本筆記整理自課堂逐字稿，僅摘要重點，供同學複習與實作。**

## 1. 本次課程目標
- 熟悉 **Google Cloud Platform (GCP)** 介面與專案(Project)概念  
- 建立並設定第一台 **Compute Engine 虛擬主機 (VM)**  
- 了解定價與 **Spot Instance** 省費技巧  
- 練習三種連線方式：  
  1. Browser Console  
  2. 本機終端機 SSH  
  3. `gcloud` CLI  
- 預覽下午課程：**Cloud SQL** 與 **Data Pipeline / Airflow**

---

## 2. 事前準備
1. 註冊/登入 Google 帳號並啟用 GCP Free Trial  
2. 進入 **Cloud Console** → 右上角「☰」→ `New Project` 建立專案  
   - 專案名稱可自訂，之後團隊開發可共用同一專案  
3. 建議把 UI 語系切換成英文，方便對照官方文件

---

## 3. 建立 Compute Engine VM
| 步驟 | 主要設定 | 小貼士 |
|------|----------|--------|
| 1 | `Compute Engine → VM instances → Create instance` | 第一次使用會自動開啟 API |
| 2 | **Zone**: `asia-east1‑a` (台灣) 或就近地區 | 延遲低但成本差異小 |
| 3 | **Machine family**: `E2`, **Machine type**: `e2-standard‑2` (2 vCPU / 8 GB) | 之後跑 Airflow 夠用 |
| 4 | **Boot disk**: Ubuntu 24.04 LTS, 32 GB SSD | SSD + swap → 效能佳 |
| 5 | **Firewall**: 勾選 `Allow HTTP`、`Allow HTTPS` | 之後架服務免手動開埠 |
| 6 | **Security** → `Service Account`: 預設 │ `Access Scopes`: *Allow full API access* | VM 內程式可存取 GCP 服務 |
| 7 | **Advanced options** → `Provisioning Model`: `Spot` | 價格可降 ~70 %<br>可設 `Termination time` 最長 24 hr |
| 8 | （選擇性）取消 `Deletion protection` 方便實驗 | 正式環境建議打開 |

⚠️ **Spot VM** 隨時可能被回收，僅適合短期實驗／可中斷工作。

---

## 4. 三種連線方式

### 4.1 Browser Console  
- Console 直接開啟瀏覽器終端機，適合緊急登入  
- 正式環境常被權限政策禁止

### 4.2 SSH（本機終端機）
1. **產生金鑰**（Windows 可用 *Git Bash* / *MobaXterm*）  
   ```bash
   ssh-keygen -t ed25519 -C "tjr102-demo@2025-07-19" -f ~/.ssh/tjr102_demo
   ```  
   產生：  
   - `tjr102_demo`     ▷ **私鑰**，務必保管  
   - `tjr102_demo.pub` ▷ **公鑰**

2. **將公鑰鎖進 VM**  
   ```bash
   # 在 VM（Browser Console）中
   mkdir -p ~/.ssh
   vi ~/.ssh/authorized_keys   # 貼上 .pub 內容，:wq 儲存
   ```

3. **從本機登入**  
   ```bash
   ssh -i ~/.ssh/tjr102_demo <USERNAME>@<EXTERNAL_IP>
   ```

### 4.3 `gcloud` CLI  
```bash
gcloud compute ssh <INSTANCE_NAME>   --zone asia-east1-a --project <PROJECT_ID>
```
`gcloud` 會自動管理金鑰並更新防火牆。

---

## 5. 專案層級 SSH Key 管理
> **Console → Compute Engine → Metadata → SSH Keys**

- 將團隊所有公鑰加入，即可 **自動下發** 至後續每台新 VM  
- 免去逐機貼公鑰的麻煩  
- 每把金鑰最後的 comment 即為建立的 Linux 使用者名稱

---

## 6. 成本最佳化心得
| 方法 | 效益 | 注意事項 |
|------|------|----------|
| **Spot VM** | 價格最低 | 最多 24 hr，隨時關機 |
| **關機/刪除不用的 VM** | 直接停計費 | 可留磁碟快照 |
| **選擇低階 E‑family 機型** | CP 值高 | CPU 不可突增 |
| **使用 SSD 作為 swap** | 省 RAM 成本 | 效能仍低於真 RAM |

---

## 7. 工具與建議
- **Git Bash / MobaXterm**：Windows 上模擬 Linux Shell  
- **AI 助手**：ChatGPT (OpenAI)、Claude (Anthropic)、Gemini (Google)  
  - 寫程式時 Claude 表現佳  
  - Google AI 與自家雲端整合度高  
- 文件學習時優先看 **英文官方文件**，避免機翻名詞混淆

---

## 8. 午後課程前瞻
- **Cloud SQL**：雲端 RDB（MySQL、PostgreSQL…）  
- **Airflow on GCE**：建立資料管線、自動排程

---

## 9. 常用指令速查
```bash
# 查看目前身分
whoami

# 系統更新（Ubuntu）
sudo apt update && sudo apt upgrade

# 查看硬體資源
lscpu
free -h
df -h

# 開啟 / 停止 VM
gcloud compute instances stop|start <INSTANCE_NAME> --zone <ZONE>
```
