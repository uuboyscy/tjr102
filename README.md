# tjr102

# Notes
## 20250629 Docker
Use "-y" to avoid pending process when `apt-get install` \
example: `apt-get install -y curl`

### Build a container
1. Get image:
   1. `docker pull` from image sources.
   2. Or `docker run` -> Docker download image if not exist
2. Run a container from a image
   1. `docker run -it [-d] [--name <container name>] <image name> [CMD]`
3. Commit an image from running container
   1. Do something in container
   2. Exit container
   3. `docker commit <container ID> <new image name>`
4. Create new image from Dockerfile
   1. Edit Dockerfile
   2. `docker build [-f <Dockerfile name>] -t <new image name> .`

### Other Docker commands
- Show docker images:
  - `docker images`
- Show running docker processes
  - `docker ps` to show running container
  - `docker ps -a` to show all existing containers

### Note from transcription
[20250629.md](note/20250629.md)

## 20250703 Docker
[20250703_morning_docker.md](note/20250703_morning_docker.md)

## 20250703 Data Pipeline
[20250703_afternoon_datapipeline.md](note/20250703_afternoon_datapipeline.md)
[20250703_night_datapipeline.md](note/20250703_night_datapipeline.md)

## 20250712 Data Pipeline
1. [Create DB and table](https://github.com/uuboyscy/basic_python_course/blob/master/part15_dbConnection/01_executeSQL_INSERT.ipynb)
2. Install cryptography
   1. `poetry add cryptography`
3. If password is incorrect
   1. `OperationalError: (1045, "Access denied for user 'root'@'192.168.65.1' (using password: YES)")`
4. `OperationalError: (1049, "Unknown database 'testdb'")`

### Note from transcription
- [20250712_morning_datapipeline.md](note/20250712_morning_datapipeline.md)
- [20250712_afternoon_datapipeline.md](note/20250712_afternoon_datapipeline.md)

## 20250719 GCP
- Generate SSH key pair
   ```
   ssh-keygen -t ed25519 -f tjr102-key -C "test-gcp-user"
   ```
- Copy public key to GCP VM instance
  - Create a ~/.ssh/authorized_keys file if it does not exist
  - Copy the content of `tjr102-key.pub` to GCP VM instance metadata
- Login to GCP VM instance
   ```
   ssh -i tjr102-key test-gcp-user@<GCP VM instance external IP>
   ```

### Note from transcription
- [20250719_morning_GCP.md](note/20250719_morning_GCP.md)


## 20250719 Data Pipeline Airflow

### Deploy Airflow on GCP VM

- [Install Docker](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)
- Add docker group
  ```
  sudo groupadd docker
  sudo usermod -aG docker $USER
  ```

### Note from transcription
- [20250719_afternoon_datapipeline.md](note/20250719_afternoon_datapipeline.md)

## 20250720 Data Pipeline

### Note from transcription
- [20250720_morning_datapipeline.md](note/20250720_morning_datapipeline.md)

## 20250720 GCP
- gsutil rsync
  - `gsutil rsync -r -d testrsync gs://tjr102-demo-allen/testrsync/`
- Mount GCS with gsfuse
  - https://cloud.google.com/storage/docs/cloud-storage-fuse/overview#use-cases

### Note from transcription
- [20250720_afternoon_GCP.md](note/20250720_afternoon_GCP.md)


## 20250803 GCP
### Query external GoogleSheets table on BigQuery
1. Share the GoogleSheets with the service account email
2. Enable GoogleSheets API in GCP project
3. Configure credential scope in Python code


# Resources
- [Docker](https://docs.uuboyscy.dev/docs/category/docker-tutorial)
- [Pandas](https://docs.uuboyscy.dev/docs/category/pandas-tutorial)
- [Airflow](https://docs.uuboyscy.dev/docs/Orchestration/AirFlow/)
- [Flask Sample code](https://github.com/uuboyscy/flask_course)
- [PyMySQL](https://github.com/uuboyscy/basic_python_course/tree/master/part15_dbConnection)
