import re
import os
import json
from pathlib import Path
from subprocess import run
from typing import List

import smtplib, ssl
from email.mime.text import MIMEText
from email.header import Header

import _jsonnet
from fire import Fire
from dotenv import load_dotenv


class File:
    """
    判定檔案類型，可從檔案名稱或設定檔 table.libsonnet 確認。
    """

    def __init__(self, filep):
        self.filep = str(filep)
        self.p = Path(self.filep)
        self.stem = self.p.stem
        load_dotenv()

    def __str__(self):
        return str(self.p)

    def is_file(self):
        return self.p.is_file()

    def is_daily(self):
        pattern = re.compile(r".+_[0-9]{8}$")
        return pattern.match(self.stem)

    def is_monthly(self):
        pattern = re.compile(r".+_[0-9]{6}$")
        return pattern.match(self.stem)

    # mode: merge / ref: truncate and insert
    def is_ref(self, table):
        # filename contains ref
        explicit_pattern = re.compile(r".+_Ref_.+")
        # filename without date number
        implicit_pattern = re.compile(r"^[^0-9]+$")
        if explicit_pattern.match(self.stem):
            return True
        if implicit_pattern.match(self.stem):
            return True
        if table.get("mode") in ("merge", "ref"):
            return True
        return False

    def basename(self):
        pattern = re.compile(r"(.+)_[0-9]+$")
        m = pattern.search(self.stem)
        if m:
            return m.group(1).lower()
        return self.stem.lower()

    def load_dt(self):
        pattern = re.compile(r"[^_]+_([0-9]+)$")
        m = pattern.search(self.stem)
        if m:
            return m.group(1).lower()
        return None

    def load_type(self, table):
        if self.is_ref(table):
            return "ref"
        if self.is_daily():
            return "daily"
        if self.is_monthly():
            return "monthly"
        return None

class FileManager:
    """
    負責將資料交換區檔案移動歸檔。
    """

    def __init__(self, source_dir, target_dir, table_cfg_dir, dry=False):
        self.task_id = None
        self.source_dir = Path(source_dir)
        self.target_dir = Path(target_dir)
        self.table_cfg_dir = Path(table_cfg_dir)
        self.table_cfg_path = Path(self.table_cfg_dir) / "table.libsonnet"
        self.tables = json.loads(_jsonnet.evaluate_file(f"{self.table_cfg_path}"))
        self.dry = dry

        self.setup()

    def validate(self):
        if not (self.source_dir.is_dir() and self.target_dir.is_dir()):
            raise Exception("Source dir or Target dir is not valid.")
        if not self.table_cfg_path.is_file():
            raise Exception(
                f"Table config file {self.table_cfg_path} doesn't exist or not a file."
            )
        return True

    # create directories by config
    def setup_target_dir_structure(self):
        all_done = True
        commands = []
        for table in self.tables:
            commands.append(f"mkdir -p {self.target_dir / table}/{{daily,monthly,ref}}")

        for command in commands:
            if not self.dry:
                try:
                    self.execute_cmd(command)
                    print(f"[info] {command}")
                except Exception as e:
                    print(f"[error] {e}")
                    all_done = False
            else:
                print(f"[dry run] {command}")
        if not all_done:
            raise Exception("Setup target directories failed.")

    def setup(self):
        self.validate()
        self.setup_target_dir_structure()

    def execute_cmd(self, command):
        rs = run(command, shell=True, check=True)
        rs.check_returncode()
        return rs

    def get_mv_command(self, filep):
        f = File(filep)
        if not f.is_file():
            print(f"skip dir: {f}")
            return

        file_basename = f.basename()
        if not file_basename in self.tables:
            print(
                f"skip file {f}. Since the base name '{file_basename}' is not in the table config"
            )
            return

        command_tpl = f"mv {f} {self.target_dir / file_basename}"
        load_type = f.load_type(table=self.tables[file_basename])
        print(f"{load_type}: {f}")
        return f"{command_tpl}/{load_type}/"

    # re-organize files. move source files to target directories
    def run(self):
        commands = []
        print("\n=== Scan Start ===")

        for filep in self.source_dir.glob("*.csv"):
            command = self.get_mv_command(filep)
            if command:
                commands.append(command)

        print("=== Scan End ===\n")

        all_done = True
        for command in commands:
            if not self.dry:
                try:
                    self.execute_cmd(command)
                    print(f"[info] {command}")
                except Exception as e:
                    print(f"[error] {e}")
                    all_done = False
            else:
                print(f"[dry run] {command}")
        if not all_done:
            raise Exception("Re-Organize source directory failed.")
        print("\nTask complete!")

if __name__ == "__main__":
    Fire(FileManager)
