#!/bin/bash

rm -rf coverage_html
pip install nose coverage argparse --use-mirrors
pip install -r requirements.txt --use-mirrors
python setup.py nosetests
exit $?
