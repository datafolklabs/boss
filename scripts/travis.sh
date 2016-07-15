#!/bin/bash

rm -rf coverage_html
pip install -r requirements-dev.txt
python setup.py develop
python setup.py nosetests
exit $?
