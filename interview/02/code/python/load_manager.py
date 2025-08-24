import json
import os
import re
import sys
import time
from datetime import datetime
from glob import glob
from itertools import chain
from pathlib import Path
from subprocess import PIPE, Popen, check_output

import _jsonnet
import jinja2
import yaml
from dateutil.relativedelta import relativedelta
from fire import Fire
from sqlalchemy.sql import text

sys.path.append("/root/workspace")

from airflow.db.models.ops import Task
from airflow.db.session import SessionLocal, engine


TASK_STATUS_FILE_COUNTED = 1
TASK_STATUS_DB_COUNTED = 2
TASK_STATUS_COMPLETE = 3

class EnvVarLoader(yaml.SafeLoader):
    pass

class LoadManager:
    """
    負責根據資料類型以 GPLOAD 搭配 YAML 設定檔匯入資料到資料庫，並處理與檔案相關疑難雜症。
    """

    def __init__(self, table, table_cfg_dir, load_type, load_dt=None, dry=False):
        self.table = table
        self.target_schema = "raw"
        self.not_exist_white_list = ["pay_rotary_history"]
        self.inconsistent_white_list = [
            "pay_ref_online_member",
            "va_ref_item_dt",
            "pay_ref_freeca",
        ]
        self.dry = dry

        self.table_shcema_cfg_path = Path(table_cfg_dir) / "table.libsonnet"
        self.table_config = json.loads(
            _jsonnet.evaluate_file(f"{self.table_shcema_cfg_path.expanduser()}")
        )[table]
        self.date_col = self.table_config.get("date_col")

        self.table_cfg_dir = Path(table_cfg_dir)
        self.table_load_cfg_path = os.path.expanduser(
            f"{table_cfg_dir}/out/{self.target_schema}.{self.table}.yml"
        )
        self.load_type = load_type
        self.file_subdir = "ref" if load_type == "merge" else load_type
        if load_type == "monthly":
            self.load_dt = str(load_dt)[:6]
        elif not load_dt:
            self.load_dt = load_dt
        else:
            self.load_dt = str(load_dt)
        self.db = SessionLocal()
        self.engine = engine

        self.ddl_dir = "/root/workspace/ddl_template"
        self.tmp_schema = "tmp"

        self.load_config = self.get_load_config(self.table_load_cfg_path)

        # only accept one input source
        self.filep_list = self.load_config["GPLOAD"]["INPUT"][0]["SOURCE"]["FILE"]

    def get_load_config(self, table_load_cfg_path):
        path_matcher = re.compile(r".*\$\{([^}^{]+)\}.*")

        def path_constructor(loader, node):
            return os.path.expandvars(node.value)

        EnvVarLoader.add_implicit_resolver("!path", path_matcher, None)
        EnvVarLoader.add_constructor("!path", path_constructor)
        with open(table_load_cfg_path, "r") as f:
            # TODO: improve
            os.environ["LOAD_TYPE"] = str(self.file_subdir)
            os.environ["EXECUTION_DATE"] = str(self.load_dt)
            return yaml.load(f, Loader=EnvVarLoader)

    def get_file_lists(self):
        nested_list = [list(glob(filep)) for filep in self.filep_list]
        return list(chain(*nested_list))

    def pre_load_hook(self):
        """
        pre-process issued files before loading to database.
        """
        for filep in self.filep_list:
            if not Path(filep).exists():
                raise Exception(f"檔案不存在: {filep}")
            if self.table in ("va_txn_dp4k", "va_txn_dp4ksb"):
                # remove utf8 BOM
                result = check_output(
                    f"sed -i '1s/^\xEF\xBB\xBF//' {filep}", shell=True
                )
                print("pre_load_hook:", result)
            elif self.table == "va_txn_detail":
                result = check_output(f"sed -i '/^[[:space:]]*$/d' {filep}", shell=True)
                print("pre_load_hook:", result)

    def count_from_wc(self, file_list):
        total = 0
        for single_file in file_list:
            try:
                filep = Path(single_file)
                if not filep.parent.exists():
                    raise Exception(f"資料夾不存在: {filep.parent}")
                if not filep.exists():
                    raise Exception(f"檔案不存在: {filep}")
                result = check_output(f"wc -l {filep} | tail -1", shell=True)
                total += int(result.split()[0])
                
                if self.table_config.get("header"):
                    total -= 1
            except Exception as e:
                raise e
        return total

    def get_ddl_statement(self, table, schema=None, suffix=None):
        templateLoader = jinja2.FileSystemLoader(searchpath=self.ddl_dir)
        templateEnv = jinja2.Environment(loader=templateLoader)
        TEMPLATE_FILE = f"{table.lower()}.sql.j2"
        template = templateEnv.get_template(TEMPLATE_FILE)
        suffix = f"_{suffix}" if suffix else ""
        outputText = template.render(
            schema=schema, suffix=suffix
        )  # this is where to put args to the template renderer

        return outputText

    def generate_ddl_statement(self):
        table_config = self.table_config
        compresstype = "zstd"
        compresslevel = 5
        columns = [
            " ".join(list(col_pair.items())[0]) + ","
            for col_pair in table_config["schema"]
        ]
        columns_str = "\n  ".join(columns)
        distributed_mode = table_config.get("distributed_mode")
        distributed_by = table_config.get("distributed_by")
        distributed_clause = ""
        if distributed_mode:
            distributed_clause = f"distributed {distributed_mode}"
        elif distributed_by:
            distributed_clause = f"distributed by ({distributed_by})"
        ddl = """
drop external table if exists "ext"."{table_name}{{{{ suffix|default('', true) }}}}";
drop table if exists "{{{{ schema|default('raw', true) }}}}"."{table_name}{{{{ suffix|default('', true) }}}}";
create table if not exists "{{{{ schema|default('raw', true) }}}}"."{table_name}{{{{ suffix|default('', true) }}}}" (
  {columns_str}
  created_at timestamp default now()
) with (
  appendonly=true, orientation=row, compresstype={compresstype}, compresslevel={compresslevel}
) {distributed_clause}
;
""".format(
            table_name=self.table,
            columns_str=columns_str,
            distributed_clause=distributed_clause,
            compresstype=compresstype,
            compresslevel=compresslevel,
        )
        return ddl

    def save_ddl_j2_tpl(self):
        ddl_statement = self.generate_ddl_statement()
        
        
        with open(f"{self.ddl_dir}/{self.table.lower()}.sql.j2", "w") as f:
            f.write(ddl_statement)

    def create_output_table(self):
        """
        create gpload staging table
        """
        self.save_ddl_j2_tpl()

        ddl_sql = self.get_ddl_statement(self.table, self.tmp_schema, self.load_dt)
        result = self.db.execute(ddl_sql)
        self.db.commit()
        print(result)

    def run_gpload(self):
        """
        LOAD_TYPE: YAML
        EXECUTION_DATE: YAML
        GPHOME: gpload3.py
        """
        command = f"""
        export LOAD_TYPE={self.file_subdir} &&
        export EXECUTION_DATE={self.load_dt} &&
        export GPHOME=/usr/local/greenplum-db-6.12.1 &&
        python3 /root/gpload3.py -f {self.table_load_cfg_path}"""
        process = Popen(command, stdout=PIPE, shell=True)
        while True:
            output = process.stdout.readline().decode("utf8")
            if output == "" and process.poll() is not None:
                break
            if output:
                print(output.strip())
            if 'invalid byte sequence for encoding "UTF8"' in output:
                raise Exception(f"編碼異常: {','.join(self.filep_list)}")
            if "could not connect to database" in output:
                raise Exception("網路異常")
            if "ERROR:  permission denied" in output:
                raise Exception("權限錯誤")
        rc = process.poll()
        if rc != 0:
            raise Exception(f"資料匯入失敗，可能為欄位錯誤: {','.join(self.filep_list)}")

    def get_tmp_table_name(self, table, suffix):
        if suffix:
            return f"{table}_{suffix}"
        return table

    def count_from_db(self, schema, table):
        sql = f"select count(1) as cnt from {schema}.{table}"
        result = self.db.execute(sql).fetchall()
        print("result:", result)
        if result and len(result) > 0:
            return result[0][0]

    def clean_and_insert_for_ref(
        self, source_schema, source_table, target_schema, target_table
    ):
        """
        truncate the target table and insert new data of the staging table to the target table.
        """
        clean_sql = text(f"truncate {target_schema}.{target_table}")
        insert_sql = text(
            f"insert into {target_schema}.{target_table} select * from {source_schema}.{source_table}"
        )

        clean_rs = self.db.execute(clean_sql)
        insert_rs = self.db.execute(insert_sql)

        clean_cnt = clean_rs.rowcount
        insert_cnt = insert_rs.rowcount

        self.db.commit()
        print(f"clean_cnt: {clean_cnt}")
        print(f"insert_cnt: {insert_cnt}")
        return {"clean_cnt": clean_cnt, "insert_cnt": insert_cnt}

    def clean_and_insert_for_merge(
        self, source_schema, source_table, target_schema, target_table
    ):
        """
        delete the intersection data of target and staging table by matched column, and insert staging table data to the target table.
        """
        # TODO: backup origin table
        match_columns = self.table_config["match_columns"]
        match_column = match_columns[0]
        clean_cnt = clean_sql = text(
            f"delete from {target_schema}.{target_table} where {match_column} in (select {match_column} from {source_schema}.{source_table})"
        )
        insert_sql = text(
            f"insert into {target_schema}.{target_table} select * from {source_schema}.{source_table}"
        )

        clean_rs = self.db.execute(clean_sql)
        insert_rs = self.db.execute(insert_sql)

        clean_cnt = clean_rs.rowcount
        insert_cnt = insert_rs.rowcount

        self.db.commit()
        # TODO: affected row count
        print(f"clean_cnt: {clean_cnt}")
        print(f"insert_cnt: {insert_cnt}")
        return {"clean_cnt": clean_cnt, "insert_cnt": insert_cnt}

    def clean_and_insert(
        self,
        source_schema,
        source_table,
        target_schema,
        target_table,
        date_col,
        start_date,
        end_date,
    ):
        """
        delete data from start_date to end_date and insert data of the staging table to the target table.
        """
        clean_sql = text(
            f"delete from {target_schema}.{target_table} where {date_col} >= :start_date and {date_col} < :end_date"
        )
        insert_sql = text(
            f"insert into {target_schema}.{target_table} select * from {source_schema}.{source_table}"
        )

        clean_rs = self.db.execute(
            clean_sql, {"start_date": start_date, "end_date": end_date}
        )
        insert_rs = self.db.execute(insert_sql)

        clean_cnt = clean_rs.rowcount
        insert_cnt = insert_rs.rowcount

        self.db.commit()
        print(f"clean_cnt: {clean_cnt}")
        print(f"insert_cnt: {insert_cnt}")
        return {"clean_cnt": clean_cnt, "insert_cnt": insert_cnt}


    # load_type: daily, monthly, ref, merge, init
    # load_name: table name
    # load_dt: if load types are daily (20200101) or monthly (202001) need to fill
    def run(self):
        print(
            f"load_name: {self.table}, load_type: {self.load_type}, load_dt: {self.load_dt}"
        )
        if self.dry:
            return

        if self.load_type not in ["monthly", "daily", "ref", "merge"]:
            raise Exception(f"Cannot accept the load type: {self.load_type}")

        new_task = Task(
            table_name=self.table, task_type=self.load_type, task_args=f"{self.load_dt}"
        )
        self.db.add(new_task)
        self.db.commit()

        file_lists = self.get_file_lists()
        new_task.file_count = len(file_lists)
        new_task.file_names = ",".join(file_lists)

        try:
            self.pre_load_hook()
        except Exception as e:
            if "檔案不存在:" in str(e) and self.table in self.not_exist_white_list:
                print(e)
                return
            else:
                raise

        new_task.wc_count = self.count_from_wc(self.filep_list)
        new_task.task_status = TASK_STATUS_FILE_COUNTED
        self.db.add(new_task)
        self.db.commit()

        if new_task.file_count == 0:
            raise Exception(
                f"Cannot find the file by the pattern: {self.table}_{self.load_dt}"
            )

        if new_task.wc_count == 0:
            raise Exception(f"檔案為空故略過: {new_task.file_names}")

        self.create_output_table()

        self.run_gpload()

        tmp_table = self.get_tmp_table_name(self.table, self.load_dt)

        count_result = self.count_from_db(self.tmp_schema, tmp_table)
        print("count_result:", count_result)
        new_task.db_count = count_result
        new_task.task_status = TASK_STATUS_DB_COUNTED
        self.db.add(new_task)
        self.db.commit()

        if (
            new_task.wc_count != new_task.db_count
            and self.table not in self.inconsistent_white_list
        ):
            raise Exception(
                f"暫存表與檔案筆數不一致。分別為: {new_task.db_count} 和 {new_task.wc_count}"
            )

        if self.load_type == "ref":
            self.clean_and_insert_for_ref(
                source_schema=self.tmp_schema,
                source_table=tmp_table,
                target_schema="raw",
                target_table=self.table,
            )
        elif self.load_type == "merge":
            self.clean_and_insert_for_merge(
                source_schema=self.tmp_schema,
                source_table=tmp_table,
                target_schema="raw",
                target_table=self.table,
            )
        else:
            if self.load_type == "monthly":
                start_date = datetime.strptime(self.load_dt, "%Y%m")
                end_date = start_date + relativedelta(months=1)
            else:
                start_date = datetime.strptime(self.load_dt, "%Y%m%d")
                end_date = start_date + relativedelta(days=1)
            self.clean_and_insert(
                source_schema=self.tmp_schema,
                source_table=tmp_table,
                target_schema="raw",
                target_table=self.table,
                date_col=self.date_col,
                start_date=start_date.strftime("%Y-%m-%d"),
                end_date=end_date.strftime("%Y-%m-%d"),
            )
        new_task.task_status = TASK_STATUS_COMPLETE
        self.db.add(new_task)
        self.db.commit()


if __name__ == "__main__":
    Fire(LoadManager)
