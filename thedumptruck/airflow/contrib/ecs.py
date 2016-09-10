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

import logging

from airflow import settings
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils import apply_defaults

import boto3 as boto

class ECSRunTaskOperator(BaseOperator):
    ui_color = '#f0ede4'

    @apply_defaults
    def __init__(
            self,
            taskDefinition,
            cluster,
            region="us-west-1",
            overrides={},
            *args, **kwargs):
        super(ECSRunTaskOperator, self).__init__(*args, **kwargs)
        self.taskDefinition = taskDefinition
        self.cluster = cluster
        self.overrides = overrides
        self.client = boto.client("ecs", region_name=region)

    def execute(self, context):
        logging.info("ECS RunTask {} on {} cluster".format(self.taskDefinition, self.cluster))
        logging.info("Command: {}".format(self.overrides))

        run_task_outpout = self.client.run_task(taskDefinition=self.taskDefinition, cluster=self.cluster, overrides=self.overrides)
        logging.info("ECS RunTask Started: {}".format(run_task_outpout))

        arn = run_task_outpout["tasks"][0]['taskArn']
        waiter = self.client.get_waiter('tasks_stopped')
        waiter.wait(cluster=self.cluster, tasks=[arn])

        describe_task_outpout = self.client.describe_tasks(cluster=self.cluster,tasks=[arn])
        logging.info("ECS RunTask Stoped: {}".format(describe_task_outpout))
        c = describe_task_outpout["tasks"][0]['containers'][0]
        if c['exitCode']:
            raise AirflowException("ECS RunTask Failed: {}".format(c['reason']))
