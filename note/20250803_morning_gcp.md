# 課堂筆記：2025/08/03 GCP 課程（上午場）

## 一、BigQuery 使用介紹

### 🔹 BigQuery 是什麼
- Google Cloud Platform（GCP）上的資料倉儲服務
- 支援 SQL 查詢與分析
- 適合用來處理大型資料集與報表工作

### 🔹 儲存與計費方式
- 分為儲存費用（Storage）與查詢費用（Query）
- 預設為 On-Demand Query，每查一次收一次費
- 可改用 Flat-rate 定額查詢方案（適合高頻率查詢）

## 二、Table 的類型

### 🔸 Native Table（BigQuery table）
- 存在 BigQuery 本身的 Table
- 有 Schema、欄位類型，支援壓縮與分區
- 儲存在 GCP 內部系統中

### 🔸 External Table（外部資料表）
- 來源可能是 GCS（Google Cloud Storage）或 Google Drive
- 不會佔用 BigQuery 儲存空間
- 查詢時會讀取來源檔案，效能較低、功能限制較多
- 通常用來處理非結構化資料（如 CSV、JSON、Parquet）

## 三、Partition Table（分區表）

### 📌 分區的目的是為了加速查詢
- 將資料按時間或數值區間劃分成多個區塊（partition）
- 查詢時只掃描有需要的 partition，節省成本與時間

### 🔹 支援三種分區方式：
1. **Date Partition**：最常見，適合 log、event 類資料
2. **Integer Range Partition**
3. **Ingestion Time Partition**

### 🔹 分區注意事項：
- 資料量大才需要分區，小資料用不到
- `partition by` 寫法影響未來查詢方式與表結構

## 四、Cluster Table（叢集表）

### ✅ 與分區不同，是「索引方式的優化」
- 將資料依欄位排序，提升條件查詢效能
- 每個分區內部可以再做 cluster

### 📌 注意事項：
- cluster 效益來自查詢範圍集中
- 最多可指定 4 個欄位做 clustering

## 五、BigQuery 儲存格式與 Schema

### 🔸 Schema 的定義：
- 需明確定義欄位名稱與資料型別（如 STRING、INT64、BOOLEAN 等）
- 支援 Nested 與 Repeated（Array）

### 🔸 儲存格式
- 可使用 CSV、JSON、Parquet、ORC 等
- Parquet / ORC 效能佳，建議使用

## 六、SQL 使用小技巧與注意事項

### ✨ 常用功能
- `SELECT * EXCEPT(column)` 避免撈某些欄位
- `WHERE _PARTITIONTIME BETWEEN ...` 做分區範圍查詢
- `WITH` 子句可寫 Common Table Expression（CTE）
- `UNNEST()` 處理 ARRAY 欄位

### ⚠️ 注意事項
- 避免 SELECT *，會導致查詢成本上升
- 無論是否有 `LIMIT`，查詢費用依照實際掃描的資料量計費

## 七、其他補充概念

### 🔹 View 與 Materialized View
- View：儲存 SQL 語句，不儲存資料
- Materialized View：儲存資料，查詢快、適合高頻查詢場景

### 🔹 Temporary Table
- 在 Query Runtime 中存在，查完即消失