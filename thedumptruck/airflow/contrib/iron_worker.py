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

import logging, time, random

from airflow import settings
from airflow.exceptions import AirflowException
from airflow.models import BaseOperator
from airflow.utils import apply_defaults
from airflow.hooks import BaseHook

from iron_worker import IronWorker, Task

class IronWorkerHook(BaseHook):
    def __init__(self, conn_id='iron_worker_default'):
        conn = self.get_connection(conn_id)
        self.worker = IronWorker(project_id=conn.login, token=conn.password)

class IronWorkerOperator(BaseOperator):
    ui_color = "#f0ede4"

    @apply_defaults
    def __init__(
            self,
            hook,
            code_name=None,
            cluster='default',
            priority=0,
            timeout=3600,
            delay=0,
            payload={},
            task=None,
            *args, **kwargs):
        super(IronWorkerOperator, self).__init__(*args, **kwargs)

        if task != None:
            self.task = task
        elif code_name != None:
            self.task = Task(
                        code_name=code_name,
                        cluser=cluster,
                        priority=priority,
                        timeout=timeout,
                        delay=delay,
                        payload=payload)
        else:
            raise AirflowException("either task or code name must be set")

        self.worker = hook.worker

    def is_not_running(self):
        result = self.worker.task(id=self.task.id)
        logging.info("IronWorker {} status {}".format(self.task.id, result.status))
        return result.status != 'queued' and result.status != 'running'


    def wait(self):
        attempt = 0
        while True:
            if self.is_not_running():
                break

            time.sleep(min((2 ** attempt) + (random.randint(0, 1000) / 1000), 15))
            attempt += 1
            continue

    def execute(self, context):
        logging.info("IronWorker Run {} with {}".format(self.task.code_name, self.task.payload))
        self.task = self.worker.queue(self.task)
        logging.info("IronWorker task {} queued".format(self.task.id))

        self.wait()
        logging.info(self.worker.log(id=self.task.id))

        result = self.worker.task(id=self.task.id)
        if result.status != 'complete':
            raise AirflowException("IronWorker {}".format(result.status))


