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

"""
### Tutorial Documentation
Documentation that goes along with the Airflow tutorial located
[here](https://airflow.apache.org/tutorial.html)
"""
# [START tutorial]
# [START import_module]
from datetime import datetime, timedelta
from textwrap import dedent

# The DAG object; we'll need this to instantiate a DAG
import os
from airflow import DAG

# Operators; we need this to operate!
from airflow.operators.python import PythonOperator

from airflow.example_dags.libs.helper import print_stuff
from kubernetes.client import models as k8s

# [END import_module]

# [START instantiate_dag]
with DAG(
    'tutorial2',
    # [START default_args]
    # These args will get passed on to each operator
    # You can override them on a per-task basis during operator initialization
    default_args={
        'depends_on_past': False,
        'email': ['airflow@example.com'],
        'email_on_failure': False,
        'email_on_retry': False,
        'retries': 1,
        'retry_delay': timedelta(minutes=5),
        # 'queue': 'bash_queue',
        # 'pool': 'backfill',
        # 'priority_weight': 10,
        # 'end_date': datetime(2016, 1, 1),
        # 'wait_for_downstream': False,
        # 'sla': timedelta(hours=2),
        # 'execution_timeout': timedelta(seconds=300),
        # 'on_failure_callback': some_function,
        # 'on_success_callback': some_other_function,
        # 'on_retry_callback': another_function,
        # 'sla_miss_callback': yet_another_function,
        # 'trigger_rule': 'all_success'
    },
    # [END default_args]
    description='A simple tutorial DAG',
    schedule_interval=timedelta(days=1),
    start_date=datetime(2021, 1, 1),
    catchup=False,
    tags=['example'],
) as dag:
    # [END instantiate_dag]

    def test_volume_mount():
        """
        Tests whether the volume has been mounted.
        """
        with open('/foo/volume_mount_test.txt', 'w') as foo:
            foo.write('Hello')

        return_code = os.system("cat /foo/volume_mount_test.txt")
        if return_code != 0:
            raise ValueError(f"Error when checking volume mount. Return code {return_code}")

    def test_volume_mount2():
        """
        Tests whether the volume has been mounted.
        """
        return_code = os.system("cat /foo/volume_mount_test.txt")
        if return_code != 0:
            raise ValueError(f"Error when checking volume mount. Return code {return_code}")
        print(return_code)

    # t1, t2 and t3 are examples of tasks created by instantiating operators
    # [START basic_task]
    t1 = PythonOperator(
        task_id="start_task",
        python_callable=print_stuff,
        executor_config={
            "pod_override": k8s.V1Pod(metadata=k8s.V1ObjectMeta(annotations={"test": "annotation"}))
        },
    )

    volume_task = PythonOperator(
        task_id="task_with_volume",
        python_callable=test_volume_mount,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            volume_mounts=[
                                k8s.V1VolumeMount(
                                    mount_path="/foo/", name="example-kubernetes-test-volume"
                                )
                            ],
                        )
                    ],
                    volumes=[
                        k8s.V1Volume(
                            name="example-kubernetes-test-volume",
                            host_path=k8s.V1HostPathVolumeSource(path="/tmp/"),
                        )
                    ],
                )
            ),
        },
    )

    volume_task2 = PythonOperator(
        task_id="task_with_volume2",
        python_callable=test_volume_mount2,
        executor_config={
            "pod_override": k8s.V1Pod(
                spec=k8s.V1PodSpec(
                    containers=[
                        k8s.V1Container(
                            name="base",
                            volume_mounts=[
                                k8s.V1VolumeMount(
                                    mount_path="/foo/", name="example-kubernetes-test-volume"
                                )
                            ],
                        )
                    ],
                    volumes=[
                        k8s.V1Volume(
                            name="example-kubernetes-test-volume",
                            host_path=k8s.V1HostPathVolumeSource(path="/tmp/"),
                        )
                    ],
                )
            ),
        },
    )

    t1 >> volume_task >> volume_task2

# [END tutorial]