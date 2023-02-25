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
"""Example DAG demonstrating the usage of dynamic task mapping with non-TaskFlow operators."""
from __future__ import annotations

from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator


def add_one(x: int):
    return x + 1


def sum_it(values):
    total = sum(values)
    print(f"Total was {total}")


with DAG(
    dag_id="example_dynamic_task_mapping_with_no_taskflow_operators", start_date=datetime(2022, 3, 4)
) as dag:

    add_one_task = PythonOperator.partial(task_id="add_one", python_callable=add_one,).expand(
        op_kwargs=[
            {"x": 1},
            {"x": 2},
            {"x": 3},
        ]
    )

    sum_it_task = PythonOperator(
        task_id="sum_it",
        python_callable=sum_it,
        op_kwargs={"values": add_one_task.output},
    )
