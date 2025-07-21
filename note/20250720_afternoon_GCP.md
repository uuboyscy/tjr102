
# 20250720 Afternoon – GCP Lecture Notes

## 1. Cloud SQL Recap & Cost Control
- **Delete unused Cloud SQL instances** immediately after labs; they continue to accrue charges even when idle.
- Backups incur additional cost; disable or delete if not needed.
- Use **Billing → Reports** to inspect yesterday’s spend and identify Cloud SQL charges.
- Large figures may be *estimates*; always cross‑check real deductions against your free tier credits.
- For future coursework, consider **creating a fresh GCP account** to reclaim the US$300 trial credit.

## 2. Cost‑Effective Database Options

| Option | Pros | Cons | Indicative cost |
| --- | --- | --- | --- |
| **Cloud SQL** | Fully‑managed, easy setup | Most expensive | $$$ |
| Self‑host MySQL/PostgreSQL on a **VM** | Flexible, root access | Must handle ops, updates | $$ |
| **Dockerised MySQL** on a small VM | Cheapest, quick snapshots | Manual container upkeep | $ |

*(Rule of thumb: managed ≈ ↑cost, self‑host ≈ ↓cost)*

## 3. Cloud Storage (GCS)

### 3.1 Core Concepts
- **Bucket** = top‑level container (think drive letter).  **Global uniqueness** required: lowercase, numbers and “-”.
- **Object** = file. Folders are a visual convenience (prefixes).

### 3.2 Creating a Bucket (Console)
1. **Create bucket** → enter *unique* name.  
2. Select **Location type**  
   - *Region* (e.g. `asia-east1`) for latency‑sensitive data  
   - *Multi‑region* for redundancy  
3. Choose **Storage class**  
   - *Standard* – frequent access  
   - *Nearline* / *Coldline* / *Archive* – progressively cheaper for infrequent access  
4. Leave default **Access control** & **Protection** unless compliance demands otherwise.  
5. Click **Create**.

### 3.3 Uploading & Organising
- Toolbar: **Create folder**, **Upload files/folder**, **Transfer service**.
- Transfer service can sync from AWS S3, another GCS bucket, on‑prem, and can be scheduled or event‑driven.

### 3.4 Command‑line with `gsutil`
```bash
# List all buckets in the active project
gsutil ls

# Upload local file -> bucket root
gsutil cp ./test_gcs.txt gs://<bucket-name>/

# Download back to local disk
gsutil cp gs://<bucket-name>/path/to/file.txt .
```
`gsutil` is installed alongside the **gcloud** SDK; no extra login needed after `gcloud init`.

## 4. Messaging Queues: Pub/Sub & Kafka (Preview)
- Pattern: **producer → broker → consumer** (decouples services, buffers spikes).
- **Kafka**: open‑source, high‑throughput log queue; **GCP Pub/Sub** offers similar managed service.
- Typical uses: log aggregation, real‑time ETL, micro‑service communication.
