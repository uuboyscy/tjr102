from typing import Union
from airflow.providers.ssh.hooks.ssh import SSHHook
from airflow.providers.ssh.operators.ssh import SSHOperator as AirflowSSHOperator
from airflow.exceptions import AirflowException


class DISSHOperator(AirflowSSHOperator):
    def __init__(
        self,
        *,
        ssh_hook: Union[SSHHook, None] = None,
        ssh_conn_id: Union[str, None] = None,
        remote_host: Union[str, None] = None,
        command: Union[str, None] = None,
        conn_timeout: Union[int, None] = None,
        cmd_timeout: Union[int, None] = None,
        environment: Union[dict, None] = None,
        get_pty: bool = False,
        banner_timeout: float = 30.0,
        **kwargs,
    ) -> None:
        super().__init__(
            ssh_hook=ssh_hook,
            ssh_conn_id=ssh_conn_id,
            remote_host=remote_host,
            command=command,
            conn_timeout=conn_timeout,
            cmd_timeout=cmd_timeout,
            environment=environment,
            get_pty=get_pty,
            banner_timeout=banner_timeout,
            **kwargs,
        )
        if cmd_timeout is None:
            self.cmd_timeout = cmd_timeout

    def raise_for_status(self, exit_status: int, stderr: bytes, **kwargs) -> None:
        if exit_status != 0:
            error_msg = stderr.decode("utf-8")
            raise AirflowException(
                f"SSH operator error:\ncmd: {self.command}\nexit status = {exit_status}\nerror: {error_msg}"
            )
