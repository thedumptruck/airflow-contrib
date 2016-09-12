# Copyright (c) 2016 The Dump Truck <thedumptruck@envygrid.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of
# the Software, and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

import unittest

from thedumptruck.airflow.contrib.ecs import ECSRunTaskOperator
from airflow import DAG
from airflow.exceptions import AirflowException
from datetime import datetime

from botocore.stub import Stubber
from botocore.waiter import Waiter

class TestSimpleDagWithECSRunTask(unittest.TestCase):
    def setUp(self):
        args = {
                    'owner': 'the_dump_truck',
                    'start_date': datetime(2015, 4, 4),
        }

        Waiter.wait = self.wait

        self.dag = DAG("test_ecs", default_args=args)


    def wait(self, *args, **kwargs):
        pass

    def test_ecs_task_run_successfuly(self):
        t = ECSRunTaskOperator(
                task_id="test-ecs-run-task",
                taskDefinition="test-cluster-task-bash",
                cluster="test-cluster",
                dag=self.dag)
        run_response = {"tasks": [{"taskArn": "arn:me:me:me"}]}
        describe_response = {"tasks": [{
                "containers": [{
                    "exitCode": 0,
                    "reason": "Stubbed success"
                }]}
            ]}
        stub = Stubber(t.client)
        stub.add_response('run_task', run_response, None)
        stub.add_response('describe_tasks', describe_response, None)
        stub.activate()

        t.execute(None)

    def test_ecs_task_run_failed(self):
        t = ECSRunTaskOperator(
                task_id="test-ecs-run-task",
                taskDefinition="test-cluster-task-bash",
                cluster="test-cluster",
                dag=self.dag)
        run_response = {"tasks": [{"taskArn": "arn:me:me:me"}]}
        describe_response = {"tasks": [{
                "containers": [{
                    "exitCode": 2,
                    "reason": "Stubbed failed"
                }]}
            ]}
        stub = Stubber(t.client)
        stub.add_response('run_task', run_response, None)
        stub.add_response('describe_tasks', describe_response, None)
        stub.activate()

        self.assertRaises(AirflowException, t.execute, None)

if __name__ == '__main__':
    unittest.main()
