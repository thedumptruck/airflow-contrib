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

import unittest, logging

import iron_core
from thedumptruck.airflow.contrib.iron_worker import *
from airflow import DAG
from airflow.utils.db import provide_session, initdb, resetdb
from airflow.exceptions import AirflowException
from datetime import datetime

class IronClientStub(iron_core.IronClient):
    def __init__(*args, **kwargs):
        pass

iron_core.IronClient = IronClientStub

class TestSimpleDagWithIronWorker(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        initdb()

    @classmethod
    def tearDownClass(cls):
        resetdb()

    @provide_session
    def setupConnection(self, session=None):
        from airflow import models
        conn = models.Connection(
                conn_id='iron_worker_default', conn_type='http',
                login=':project_id', password=':oauth_key')
        session.add(conn)
        session.commit()

    def setUp(self):
        self.setupConnection()
        args = {
                    'owner': 'the_dump_truck',
                    'start_date': datetime(2015, 4, 4),
        }

        f = {'body':{'tasks':[{'id':':task_id','created_at':'2016-09-11T11:53:20Z','updated_at':'2016-09-11T11:53:26.817Z','project_id':':project_id','code_id':':project_name','code_history_id':':hostory_project_id','status':'error','code_name':'HelloWorkerRuby','code_rev':'1','start_time':'2016-09-11T11:53:21Z','end_time':'2016-09-11T11:53:26Z','duration':5387,'timeout':3600,'log_size':19,'message_id':':message_id','cluster':'default'}]}}

        r = {'body':{'tasks':[{'id':':task_id','created_at':'2016-09-11T11:53:20Z','updated_at':'2016-09-11T11:53:26.817Z','project_id':':project_id','code_id':':project_name','code_history_id':':hostory_project_id','status':'complete','code_name':'HelloWorkerRuby','code_rev':'1','start_time':'2016-09-11T11:53:21Z','end_time':'2016-09-11T11:53:26Z','duration':5387,'timeout':3600,'log_size':19,'message_id':':message_id','cluster':'default'}]}}

        self.successResponses = {
                'tasks': r,
                'tasks/:task_id': {'body': r['body']['tasks'][0]},
                'tasks/:task_id/log': {"body": """
                    Hello!
                    Payload: {}
                """.strip}
                }
        self.failResponses = {
                'tasks': f,
                'tasks/:task_id': {'body': f['body']['tasks'][0]},
                'tasks/:task_id/log': {'body': """
                    You Sould See Errors
                    Payload: {}
                """.strip}
                }
        self.__retry_count = None

        self.dag = DAG('test_iron_worker', default_args=args)

    def success(self, *args, **kwargs):
        return self.successResponses.get(args[0], None)

    def fail(self, *args, **kwargs):
        return self.failResponses.get(args[0], None)

    def wait(self, *args, **kwargs):
        if self.__retry_count is None:
            self.__retry_count = 1

        waitResponse = self.successResponses.copy()
        waitResponse['tasks/:task_id'] = {
                'body': {
                    'status': 'running'
                }
        }
        if self.__retry_count % 3 == 0:
            return self.success(*args, **kwargs)
        else:
            self.__retry_count += 1
            return waitResponse.get(args[0], None)

    def test_iron_worker_task_run_successfuly(self):
        hook = IronWorkerHook('iron_worker_default')
        hook.worker.client.post = self.success
        hook.worker.client.get  = self.success
        t = IronWorkerOperator(
                task_id='test-iron-worker-run-task',
                hook=hook,
                code_name='HelloWorkerRuby',
                dag=self.dag)

        t.execute(None)

    def test_iron_worker_task_run_successfuly_with_wait(self):
        hook = IronWorkerHook('iron_worker_default')
        hook.worker.client.post = self.wait
        hook.worker.client.get  = self.wait
        t = IronWorkerOperator(
                task_id='test-iron-worker-run-task',
                hook=hook,
                code_name='HelloWorkerRuby',
                dag=self.dag)

        t.execute(None)

    def test_iron_worker_task_run_failed(self):
        hook = IronWorkerHook('iron_worker_default')
        hook.worker.client.post = self.fail
        hook.worker.client.get  = self.fail
        t = IronWorkerOperator(
                task_id='test-iron-worker-run-task',
                hook=hook,
                code_name='HelloWorkerRuby',
                dag=self.dag)

        self.assertRaises(AirflowException, t.execute, None)


if __name__ == '__main__':
    unittest.main()
