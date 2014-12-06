#!/bin/bash

rm -rf coverage_html
pip install nose coverage argparse
pip install -r requirements.txt
python setup.py nosetests
exit $?
