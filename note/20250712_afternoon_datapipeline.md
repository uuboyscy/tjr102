
# 2025/07/12 資料管線（下午場）課堂筆記
> **講者：Allen Shi**  
> **主題：從資料爬取到 API 與資料服務的完整流程實作**  
> **檔案產生時間：2025-07-13 12:26:33**

---

## 1. 課程目標
- 了解資料從外部來源（Web/API）到內部資料庫的整體流向  
- 實作爬蟲、資料清洗、資料庫寫入及提供 API 服務  
- 學會使用 **Flask** 快速打造 RESTful API  
- 建立 CRUD 與驗證機制，確保資料正確性與安全性  
- 理解日常開發中常見的問題（跨域、併發、排程、部署）

---

## 2. 爬蟲與資料擷取
### 2‑1 取得 API Endpoint
1. **瀏覽器 Network 面板**：觀察前端對後端的請求  
2. **分析 Request Method**：`GET` vs `POST`、Header、Querystring、Body／Payload  
3. **動態網站**：以 Selenium/Playwright 模擬使用者行為

### 2‑2 Requests 範例
```py
import requests, pandas as pd

url = "https://example.com/api/v1/orders"
payload = {"start_dt": "2025-07-01", "end_dt": "2025-07-12"}
df = pd.json_normalize(requests.post(url, json=payload).json())
```

### 2‑3 資料清理
- 格式統一（日期、大小寫、空白）  
- 缺值處理與型別轉換  
- 使用 **Pandas** pipe / assign 提升可讀性  

---

## 3. 資料庫設計 & 寫入
| 層級 | 關鍵重點 | 工具 |
| ---- | -------- | ---- |
| **Raw / Staging** | 原始資料一次性入庫，保留追溯性 | PostgreSQL / S3 |
| **ODS / Base** | 清理後的 “單表” 狀態，方便 Join | dbt `staging` 模型 |
| **Mart / DW** | 商業指標、寬表、聚合 | dbt `mart` 模型 |

- **主鍵（PK）設計**：自然鍵 vs 代理鍵  
- **索引**：常用查詢欄位加 Index，避免過度索引  
- **批次寫入**：`COPY` / `INSERT ... VALUES ...` 批次化

---

## 4. 使用 Flask 打造 API 服務
### 4‑1 專案結構
```
app/
├── models.py      # SQLAlchemy ORM
├── routes.py      # Blueprint
├── templates/     # Jinja2
└── app.py         # create_app()
```

### 4‑2 CRUD 範例
```py
from flask import Flask, request, jsonify
from models import Order, db

@app.route("/orders/<int:order_id>", methods=["GET"])
def get_order(order_id):
    return jsonify(Order.query.get_or_404(order_id).to_dict())

@app.route("/orders", methods=["POST"])
def create_order():
    data = request.get_json()
    order = Order(**data)
    db.session.add(order)
    db.session.commit()
    return jsonify(order.to_dict()), 201
```

### 4‑3 驗證與安全
- `pydantic` / `marshmallow` schema 驗證  
- JWT / Session 驗證、角色權限（RBAC）  
- CORS、Rate‑Limit、Helmet‑style Header

---

## 5. 排程與自動化
| 目標 | 工具 | 範例 |
| ---- | ---- | ---- |
| 定時抓資料 | **Prefect 2.x** flow | `@flow(schedule=IntervalSchedule(...))` |
| 重新整理 Materialized View | **dbt Cloud** / GitHub Actions | cron‑trigger |
| 監控失敗流程 | Prefect / Slack Webhook | 任務重試 + 通知 |

---

## 6. 部署與維運
1. **WSGI**：Gunicorn + Uvicorn，啟動多工  
2. **容器化**：Dockerfile → `docker compose up -d`  
3. **環境設定**：`.env` / Secrets Manager  
4. **觀測性**：Logging（structlog）、Tracing（OpenTelemetry）、Metrics（Prometheus + Grafana）  

---

## 7. 常見問題與 Q&A
| 題目 | 關鍵回答 |
| ---- | -------- |
| VM vs Container 差異 | Kernel 共用、啟動速度、資源隔離 |
| Python GIL 對多執行緒影響 | CPU‑bound 受限，I/O‑bound OK；可用 multiprocessing / asyncio |
| Kafka 原理 | 分區、ISR、Leader/Follower、LOG replica |
| 體驗 Flask 與 FastAPI 差異 | Typing 支援、效能、依賴注入 |
