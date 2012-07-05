#!/bin/bash

rm -rf coverage_html
pip install nose coverage argparse cement --use-mirrors
pip install -r requirements.txt --use-mirrors --upgrade
python setup.py nosetests
exit $?
