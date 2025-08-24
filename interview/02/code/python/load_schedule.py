# -*- coding: utf-8 -*-
"""
每日匯入資訊部提供日檔之排程。
可接受變數：
- date: 日期，格式為 yyyymmdd。例如: {"date": "20230101"}。
- skip_daily_task: 略過 daily 任務，當 skip_daily_task 等於 1 時才會略過。
- skip_ref_task: 略過 ref 任務，當 skip_ref_task 等於 1 時才會略過。
- skip_merge_task: 略過 merge 任務，當 skip_merge_task 等於 1 時才會略過。
"""
from datetime import datetime, timedelta

from airflow.models import DAG, Variable
from airflow.operators.branch_operator import BaseBranchOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.trigger_rule import TriggerRule

from airflow_operators.ssh import DISSHOperator
from airflow_utils import setup_load_cmd, FAILURE_EMAIL_PROD, DEFAULT_LOAD_FILE_TIMEOUT_SEC

# TODO: move to utils
def skip_daily_task(dag_run):
    return dag_run.conf.get("skip_daily_task") == 1


def skip_ref_task(dag_run):
    return dag_run.conf.get("skip_ref_task") == 1


def skip_merge_task(dag_run):
    return dag_run.conf.get("skip_merge_task") == 1


# TODO: fixme. cannot use as a dag args
# email_on_failure = False if "{{ dag_run.conf['email_on_failure'] }}" == "0" else True
email_on_failure = True

# default args would be pass to each task
args = {
    "owner": "Airflow",
    "start_date": datetime(2021, 2, 1),
    "catchup": True,
    "depends_on_past": False,
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "sla": timedelta(hours=1),
    "email_on_failure": email_on_failure,
    "email_on_retry": False,
    "email": FAILURE_EMAIL_PROD,
}


class MyBranchOperator(BaseBranchOperator):
    def choose_branch(self, context):
        """
        Run an extra branch on the first day of the month
        """
        conf_date_str = context["dag_run"].conf.get("date", None)
        if conf_date_str and len(conf_date_str) == 6:
            return "monthly_task"
        if conf_date_str and len(conf_date_str) == 8:
            return "daily_task"

        execution_date = context["execution_date"]
        execution_date += timedelta(hours=8)
        print("execution_date:", execution_date)
        return ["daily_task", "ref_task", "merge_task"]


# https://blog.clairvoyantsoft.com/airflow-service-level-agreement-sla-2f3c91cd84cc
with DAG(
    dag_id="load_schedule",
    tags=["load"],
    default_args=args,
    schedule_interval="30 3 * * *",
    dagrun_timeout=timedelta(minutes=90),
    max_active_runs=1,
    user_defined_macros={
        "setup_load_cmd": setup_load_cmd,
        "skip_daily_task": skip_daily_task,
        "skip_ref_task": skip_ref_task,
        "skip_merge_task": skip_merge_task,
    },
) as dag:

    start = DummyOperator(task_id="start")

    common_libsonnet = Variable.get("common.libsonnet")
    table_libsonnet = Variable.get("table.libsonnet")

    save_variables_command = """
cat <<EOT > /root/workspace/jsonnet/common.libsonnet
{{ params.common_libsonnet }}
EOT

cat <<EOT > /root/workspace/jsonnet/table.libsonnet
{{ params.table_libsonnet }}
EOT
    """

    compile_jsonnet_command = """
    cd /root/workspace/jsonnet &&
    python3 gen_init.py
    """

    # read airflow variables as latest config and write to jsonnet folder
    save_variables_task = DISSHOperator(
        ssh_conn_id="ssh_fs",
        task_id=f"save_variables",
        command=save_variables_command,
        params={
            "common_libsonnet": common_libsonnet,
            "table_libsonnet": table_libsonnet,
        },
    )

    # compile gpload yaml format files
    compile_jsonnet_task = DISSHOperator(
        ssh_conn_id="ssh_fs",
        task_id=f"compile_jsonnet",
        command=compile_jsonnet_command,
    )

    organize_command = f"""
            {setup_load_cmd} &&
            python3 python/file_manager.py --source_dir=/data/samba/mart_it --target_dir=/data/raw --table_cfg_dir=/root/workspace/jsonnet run
        """
    # move files of the data exchange area to the target directory
    file_organize_task = DISSHOperator(
        ssh_conn_id="ssh_fs",
        task_id=f"organize_dir",
        command=organize_command,
    )
    daily_task = DummyOperator(task_id="daily_task")
    ref_task = DummyOperator(task_id="ref_task")
    merge_task = DummyOperator(task_id="merge_task")
    end = DummyOperator(task_id="end", trigger_rule=TriggerRule.ALL_SUCCESS)

    branching = MyBranchOperator(task_id="branching")

    load_dt = '{{ dag_run.conf.get("date") or ds_nodash }}'
    # va_ref_card file date suffix more than data data one day.
    va_ref_card_load_dt = '{{ (dag_run.conf.get("date") or macros.ds_format(macros.ds_add(ds, 1), "%Y-%m-%d", "%Y%m%d")) }}'

    left_double_brace = "{{"
    right_double_brace = "}}"

    def run_daily_tasks():
        task_names = Variable.get("task_names_daily", deserialize_json=True)
        for task_name in task_names:
            load_type = "daily"
            load_command = """
            {left_double_brace} setup_load_cmd {right_double_brace} &&
            python3 python/load_manager.py --table={task_name} --table_cfg_dir=/root/workspace/jsonnet --load_type={load_type} --load_dt={load_dt} --dry={left_double_brace} skip_daily_task(dag_run) {right_double_brace} run 
        """.format(
                left_double_brace=left_double_brace,
                right_double_brace=right_double_brace,
                task_name=task_name,
                load_type=load_type,
                load_dt=load_dt,
            )

            task = DISSHOperator(
                ssh_conn_id="ssh_fs",
                task_id=f"load_daily_{task_name}",
                command=load_command,
                conn_timeout=DEFAULT_LOAD_FILE_TIMEOUT_SEC,
            )

            daily_task >> task >> end

    def run_ref_tasks():
        ref_task_names = Variable.get("task_names_ref", deserialize_json=True)

        for task_name in ref_task_names:
            load_type = "ref"
            load_command = """
            {left_double_brace} setup_load_cmd {right_double_brace} &&
            python3 python/load_manager.py --table={task_name} --table_cfg_dir=/root/workspace/jsonnet --load_type={load_type} --dry={left_double_brace} skip_ref_task(dag_run) {right_double_brace} run 
        """.format(
                left_double_brace=left_double_brace,
                right_double_brace=right_double_brace,
                task_name=task_name,
                load_type=load_type,
            )

            task = DISSHOperator(
                ssh_conn_id="ssh_fs",
                task_id=f"load_ref_{task_name}",
                command=load_command,
                conn_timeout=DEFAULT_LOAD_FILE_TIMEOUT_SEC,
                depends_on_past=False,
            )

            ref_task >> task >> end

    def run_merge_tasks():
        merge_task_names = Variable.get("task_names_merge", deserialize_json=True)

        for task_name in merge_task_names:
            merge_load_dt = (
                va_ref_card_load_dt if task_name == "va_ref_card" else load_dt
            )
            load_type = "merge"
            load_command = """
            {left_double_brace} setup_load_cmd {right_double_brace} &&
            python3 python/load_manager.py --table={task_name} --table_cfg_dir=/root/workspace/jsonnet --load_type={load_type} --load_dt={merge_load_dt} --dry={left_double_brace} skip_merge_task(dag_run) {right_double_brace} run 
        """.format(
                left_double_brace=left_double_brace,
                right_double_brace=right_double_brace,
                task_name=task_name,
                load_type=load_type,
                merge_load_dt=merge_load_dt,
            )

            task = DISSHOperator(
                ssh_conn_id="ssh_fs",
                task_id=f"load_merge_{task_name}",
                command=load_command,
                conn_timeout=DEFAULT_LOAD_FILE_TIMEOUT_SEC,
                depends_on_past=False,
            )

            merge_task >> task >> end

    start >> save_variables_task >> compile_jsonnet_task >> file_organize_task
    file_organize_task >> branching >> daily_task
    file_organize_task >> branching >> ref_task
    file_organize_task >> branching >> merge_task

    run_daily_tasks()
    run_ref_tasks()
    run_merge_tasks()


if __name__ == "__main__":
    dag.cli()
