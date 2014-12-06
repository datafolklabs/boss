#!/bin/bash

rm -rf coverage_html
# for python < 2.7
pip install argparse
pip install -r requirements.txt
pip install -r requirements-dev.txt
python setup.py nosetests
exit $?
