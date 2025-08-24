"""
Airflow DAG 常用變數與指令。
"""

from airflow.models import Variable

setup_load_cmd = f"""
    cd ~/workspace/airflow/load"""

DEFAULT_LOAD_FILE_TIMEOUT_SEC = 60*60

FAILURE_EMAIL_PROD = Variable.get("production_mail_list", deserialize_json=True)
