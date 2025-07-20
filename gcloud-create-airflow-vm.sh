gcloud compute instances create airflow-test-1 \
  --project=notional-zephyr-229707 \
  --zone=asia-east1-a \
  --machine-type=e2-standard-2 \
  --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
  --metadata=startup-script='#!/bin/bash
apt-get update
apt-get install -y ca-certificates curl gnupg lsb-release
install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo ${UBUNTU_CODENAME:-$VERSION_CODENAME}) stable" > /etc/apt/sources.list.d/docker.list
apt-get update -y
apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
useradd -m test-gcp-user
cd /home/test-gcp-user
git clone --branch v2 --depth 1 https://github.com/uuboyscy/airflow-demo.git
chmod -R 777 airflow-demo
usermod -aG docker test-gcp-user
docker run -it -d \
  --name airflow-server \
  -p 8080:8080 \
  -v /home/test-gcp-user/airflow-demo/dags:/opt/airflow/dags \
  -v /home/test-gcp-user/airflow-demo/logs:/opt/airflow/logs \
  -v /home/test-gcp-user/airflow-demo/utils:/opt/airflow/utils \
  -v /home/test-gcp-user/airflow-demo/tasks:/opt/airflow/tasks \
  -e PYTHONPATH=/opt/airflow \
  apache/airflow:2.11.0-python3.12 airflow standalone
sleep 15
docker exec airflow-server airflow users create \
  --username airflow \
  --firstname airflow \
  --password airflow \
  --lastname airflow \
  --role Admin \
  --email your_email@example.com' \
  --no-restart-on-failure \
  --maintenance-policy=TERMINATE \
  --provisioning-model=SPOT \
  --instance-termination-action=DELETE \
  --max-run-duration=28800s \
  --service-account=30300274673-compute@developer.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform \
  --tags=http-server,https-server \
  --create-disk=auto-delete=yes,boot=yes,device-name=airflow-test-1,disk-resource-policy=projects/notional-zephyr-229707/regions/asia-east1/resourcePolicies/default-schedule-1,image=projects/ubuntu-os-cloud/global/images/ubuntu-minimal-2410-oracular-amd64-v20250709,mode=rw,size=32,type=pd-ssd \
  --no-shielded-secure-boot \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --labels=goog-ops-agent-policy=v2-x86-template-1-4-0,goog-ec-src=vm_add-gcloud \
  --reservation-affinity=none