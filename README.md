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

# Resources
- [Docker](https://docs.uuboyscy.dev/docs/category/docker-tutorial)
- [Pandas](https://docs.uuboyscy.dev/docs/category/pandas-tutorial)
- [Airflow](https://docs.uuboyscy.dev/docs/Orchestration/AirFlow/)
