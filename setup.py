
from setuptools import setup, find_packages
import sys, os
from boss import VERSION

LONG = """
Boss is a development utility that provides quick access to reusable project
templates for any language.  
"""

setup(name='boss',
    version=VERSION,
    description="Baseline Open Source Software Templates",
    long_description=LONG,
    classifiers=[], 
    keywords='',
    author='BJ Dierkes',
    author_email='derks@datafolklabs.com',
    url='http://boss.rtfd.org',
    license='BSD',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        ### Required to build documentation
        # 'sphinx',
        #
        ### Required for testing
        # 'nose',
        # 'coverage',
        #
        ### Required to function
        'cement',
        ],
    setup_requires=[],
    entry_points="""
    [console_scripts]
    boss = boss.cli.main:main
    """,
    namespace_packages=[],
    )
