# 2025‑07‑03 Data Pipeline 課堂筆記

> **主題概覽**  
> 本次課程聚焦於以 **Pandas** 為核心的資料前處理流程，從 DataFrame 基礎操作、檔案讀寫，到 VS Code 實務技巧。 

## 1. DataFrame 基礎
- DataFrame 由多個 **Series** 組成，可視為二維表格結構。  
- 建立方式  
  ```python
  df = pd.DataFrame(data, columns=cols)
  ``` 

## 2. 刪除欄位與列（drop）
- `df.drop(columns=[...])` 刪欄位，`df.drop(index=[...])` 刪列。  
- `df = df.drop(... )` 或 `df.drop(..., inplace=True)` 才會真正修改原始 df。 

## 3. 安全指派 (SettingWithCopy) 與 `loc`
- 直接以 `df["col"][i] = v` 可能觸發 **SettingWithCopyWarning**。  
- 建議使用  
  ```python
  df.loc[i, "col"] = v
  ``` 

## 4. 合併資料表
- **縱向** → `pd.concat([df1, df2], ignore_index=True)`（對應 SQL `UNION`）。  
- **橫向** → `df1.join(df2, on=..., how='left')` 或 `pd.merge(...)`。 

## 5. Series
- Series 為一維資料結構，擁有自己的 `index` 與 `name`；DataFrame 可視為 Series 的集合。 

## 6. 深複製 vs. 參照
- `df2 = df` 只複製「參照」。  
- 需獨立記憶體請使用 `df.copy()`。 

## 7. 處理檔案與文字
### 7.1 使用 **pathlib**
```python
from pathlib import Path
p = Path("res_gossiping")
txt_files = p.glob("*.txt")
```
- `Path.open(encoding="utf-8")` 讀檔較 `open(path)` 更物件導向。 

### 7.2 將 PTT 文章整理為 DataFrame
1. 迴圈讀取每個 `.txt`。  
2. 以自訂分隔符 `-----split-----` 切出推噓文段落。  
3. 以 `str.splitlines()` 產生列表，再用 slice 去掉空行。  
4. 收集為 `data` list，再建 DataFrame。 

## 8. 匯出資料
| 格式 | 方法 | 常用參數 |
|-----|------|-----------|
| CSV | `df.to_csv("file.csv", index=False, header=False)` | `sep`, `encoding` |
| JSON (columns) | `df.to_json("file.json", orient="columns", indent=2)` | 預設 |
| JSON (records) | `df.to_json("file.json", orient="records", lines=True)` | 適合 JSONL | 

## 9. VS Code 快捷鍵
- **多游標**：Alt/Option + Click  
- **連選重複**：Ctrl/Cmd + D  
- **註解/反註解**：Ctrl/Cmd + /  
- **格式化**：Shift + Alt + F  
這些技巧可加速程式撰寫與筆記整理。 

---

### 課後提醒
- 熟悉 `loc`/`iloc`，避免隱含複製問題。  
- 儲存大型檔案前先確認是否需要 `index` 與 `header`，可降低檔案體積。  
- 在 ETL 管線中建議使用 **JSON Lines** 或 **Parquet** 以利分散式查詢。 
