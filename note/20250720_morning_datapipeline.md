# 晨間資料管線課堂筆記（2025/07/20）

## 1. 環境準備

### 1.1 開啟 GCP Console 與 Cloud Shell

1. 先登入 **GCP Console**（任一服務頁面皆可）。
2. 點擊右上角 **Activate Cloud Shell**，開啟雲端終端機並接受所需權限。

### 1.2 複製一鍵部署指令

1. 講師在聊天室提供一段 *setup* Script 連結，點進頁面 → 右上角 **Copy raw file** 以複製完整指令。
2. 在本地 **VS Code** 貼上指令，利用 <kbd>Ctrl/⌘</kbd>+<kbd>D</kbd> 多游標功能，一次改完：

   * `PROJECT_ID`（2 處）
   * `SERVICE_ACCOUNT`（1 處）
3. 全選複製後，貼回 Cloud Shell 執行。

## 2. 執行安裝腳本

* 腳本會：

  1. 開啟/啟動一台 VM。
  2. 安裝 **Docker** 與 **Docker Compose**。
  3. 拉取講師事先配置的 **Apache Airflow** image。
  4. 自動建立 Airflow 使用者帳密（`airflow/airflow`）。
* 執行過程中 Cloud Shell 會顯示 VM 位置與 External IP，稍候約 3–5 分鐘即可完成。

## 3. 連線至 Airflow UI

1. 複製 **External IP**，以瀏覽器開啟 `http://<External IP>:8080`。
2. 輸入預設帳號密碼 `airflow / airflow`，即可進入 **Airflow Web UI**。

## 4. 常見問題排解

| 症狀                            | 原因與解法                                             |
| ----------------------------- | ------------------------------------------------- |
| 瀏覽器一直 loading，無 404/503       | 檢查網址是否誤用 `https://…`; 移除 `s` 改為 `http`。           |
| ERR\_CONNECTION\_REFUSED      | 確認 VM Firewall 已開放 **TCP 8080**，或等待容器 fully ready |
| Airflow UI 顯示 502 Bad Gateway | Docker Compose 尚未全部起來，`docker ps` 應至少有 5 個服務      |

## 5. VS Code Remote Tips

* 在 **VS Code** 左側 *Remote Explorer* 找到 `Airflow AMO`，點選 **Connecting in New Window** 進入 VM 開發環境。
* 修改 DAG 後可 `git commit & push`；容器會自動 reload DAG 檔案。

## 6. 後續課程預告

* 從昨日進度繼續：

  1. 解析範例 DAG (`sync_cpu_model_result_to_pg`) 流程。
  2. 示範以 **Prefect 2** 重寫並比較差異。
  3. 介紹以 **BigQuery** + **Cloud Functions** 形成 ELT 流程。
