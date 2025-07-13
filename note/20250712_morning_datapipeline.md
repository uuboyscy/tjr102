# Data Pipeline Lecture Notes — Connecting Python to MySQL
*Date: 2025‑07‑12 (Morning Session)*  
*Instructor: Allen Shi*

---

## 1. Course Objective  
By the end of this session, you should be able to:

1. **Create** a MySQL database and tables needed by your pipeline.  
2. **Configure** and install Python dependencies with Poetry.  
3. **Establish** a resilient MySQL connection in Python.  
4. **Insert** (and, by extension, query/update) data using a cursor.  
5. **Troubleshoot** the most common connection and SQL errors.

---

## 2. Environment Setup  

| Tool | Why we use it | Quick command |
|------|---------------|---------------|
| **Poetry** | Dependency & virtual‑env manager | `curl -sSL https://install.python-poetry.org | python3 -` |
| **mysql‑connector‑python** | Native driver to talk to MySQL | `poetry add mysql-connector-python` |
| **cryptography** | Required by the driver on some systems | `poetry add cryptography` |

> **Tip:** Run `poetry shell` before coding so that VSCode picks up the virtual environment automatically.

---

## 3. Create Database & Tables  

```sql
-- create DB (run once)
CREATE DATABASE demo_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- create table (run once)
USE demo_db;
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(50) NOT NULL,
  email VARCHAR(120) UNIQUE
);
```

*If you see `Unknown database 'demo_db'`, double‑check that the DB was created and that you used `USE demo_db;`.*

---

## 4. Connecting from Python  

```python
import mysql.connector
from mysql.connector import Error

def get_conn():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="your_password",
        database="demo_db",
        charset="utf8mb4"
    )

# Always test the connection
try:
    conn = get_conn()
    print("Connection OK")
finally:
    conn.close()
```

**☝️  Checklist**  
- Correct host / port (default 3306).  
- Correct credentials.  
- Target database exists.  
- `charset="utf8mb4"` prevents most encoding errors.

---

## 5. Executing SQL with a Cursor  

```python
def insert_user(name: str, email: str):
    conn = get_conn()
    try:
        cursor = conn.cursor()
        sql = "INSERT INTO users (name, email) VALUES (%s, %s)"
        cursor.execute(sql, (name, email))
        conn.commit()
    except Error as e:
        print(f"MySQL error: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
```

### Translation Code Pattern  
1. **Compose** the SQL as a string (optionally use placeholders `%s`).  
2. **Execute** with `cursor.execute(sql, params)`.  
3. **Commit** or **rollback**.  
4. **Close** cursor and connection.

---

## 6. Common Errors & Quick Fixes  

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| `ModuleNotFoundError: cryptography` | Missing dependency | `poetry add cryptography` |
| `Unknown database 'demo_db'` | DB not created / wrong name | Run `CREATE DATABASE` or correct `database` param |
| `Access denied for user 'root'@'localhost'` | Wrong password / privileges | Reset pw or grant privileges |
| `Incorrect string value` | Charset mismatch | Use `utf8mb4` on DB and connection |
| `Lost connection to MySQL server` | Server timeout or large packet | Increase `wait_timeout` / `max_allowed_packet` |

---

## 7. Workflow Summary  

1. **Prepare SQL scripts** (schema & sample data).  
2. **Install dependencies** with Poetry.  
3. **Write connection helper** (`get_conn`).  
4. **Write translation (SQL) functions** (`insert_user`, `fetch_users`, …).  
5. **Add error handling & logging**.  
6. **Test locally**, then integrate into your Prefect/Airflow pipeline.
