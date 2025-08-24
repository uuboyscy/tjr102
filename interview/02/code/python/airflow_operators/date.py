#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

from typing import Dict, Iterable, Union

from airflow.operators.branch import BaseBranchOperator
from airflow.utils import timezone


class BranchDayOperator(BaseBranchOperator):
    """
    Branches into one of two lists of tasks depending on the current day.
    For more information on how to use this operator, take a look at the guide:
    :ref:`howto/operator:BranchDayOfWeekOperator`

    :param follow_task_ids_if_true: task id or task ids to follow if criteria met
    :type follow_task_ids_if_true: str or list[str]
    :param follow_task_ids_if_false: task id or task ids to follow if criteria does not met
    :type follow_task_ids_if_false: str or list[str]
    :param week_day: Day of the week to check (full name). Optionally, a set
        of days can also be provided using a set.
        Example values:

            * ``1``,
            * ``{1, 2, 3}``

    :type week_day: set or str or airflow.utils.weekday.WeekDay
    :param use_task_execution_day: If ``True``, uses task's execution day to compare
        with is_today. Execution Date is Useful for backfilling.
        If ``False``, uses system's day of the week.
    :type use_task_execution_day: bool
    """

    def __init__(
        self,
        *,
        follow_task_ids_if_true: Union[str, Iterable[str]],
        follow_task_ids_if_false: Union[str, Iterable[str]],
        day: Union[int, Iterable[int]],
        use_task_execution_day: bool = False,
        **kwargs,
    ) -> None:
        super().__init__(**kwargs)
        self.follow_task_ids_if_true = follow_task_ids_if_true
        self.follow_task_ids_if_false = follow_task_ids_if_false
        self.day = day
        self.use_task_execution_day = use_task_execution_day

        if isinstance(self.day, int):
            pass
        elif isinstance(self.day, set):
            if all(isinstance(e, int) for e in self.day):
                pass
        else:
            raise TypeError(
                "Unsupported Type for day parameter: {}. It should be one of int"
                ", ".format(type(day))
            )

    def choose_branch(self, context: Dict) -> Union[str, Iterable[str]]:
        if self.use_task_execution_day:
            now = context["execution_date"]
        else:
            now = timezone.make_naive(timezone.utcnow(), self.dag.timezone)

        if now.day in self.day:
            return self.follow_task_ids_if_true
        return self.follow_task_ids_if_false
