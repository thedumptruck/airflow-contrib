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

from setuptools import setup, find_packages

_ecs         = ['boto3>=1.0.0']
_iron_worker = ['iron-worker>=1.0.0']
_all         = _ecs + _iron_worker

def run_setup():
    setup(name='AirflowOnTheDumpTruck',
            author='TheDumpTruck',
            email='TheDumpTruck@EnvyGrid.com',
            url='https://github.com/thedumptruck/airflow-contrib',
            description='AirflowOnTheDumptruck bunch of airflow operators and hooks',
            license='MIT License',
            version='0.1.0',
            packages=find_packages(),
            install_requires=['airflow>=1.3.7'],
            extras_require={
                'ecs': _ecs,
                'iron_worker': _iron_worker,
                'all': _all
            })

if __name__ == "__main__":
    run_setup()
