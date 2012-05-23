
from setuptools import setup, find_packages
import sys, os

setup(name='@module_name@',
    version=@version@,
    description="@description@",
    long_description="@description@",
    classifiers=[], 
    keywords='',
    author='@project_creator@',
    author_email='@project_creator_email@',
    url='@url@',
    license='@license@',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    install_requires=[
        ### Required to build documentation
        # "Sphinx >= 1.0",
        ### Required for testing
        # "nose",
        # "coverage",
        ],
    setup_requires=[],
    entry_points="""
    """,
    namespace_packages=[],
    )
