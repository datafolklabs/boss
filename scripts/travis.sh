#!/bin/bash

pip install nose --use-mirrors
pip install coverage --use-mirrors
pip install -r src/boss/requirements.txt --use-mirrors
python setup.py nosetests
exit $?
