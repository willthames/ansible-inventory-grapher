#!/usr/bin/env python

import os
import sys

from setuptools import setup

sys.path.insert(0, os.path.abspath('lib'))

exec(open('lib/ansibleinventorygrapher/version.py').read())

setup(
    name='ansible-inventory-grapher',
    version=__version__,
    description='Creates graphs representing ansible inventory',
    author='Will Thames',
    author_email='will@thames.id.au',
    url='http://github.com/willthames/ansible-inventory-grapher',
    license='GPLv3',
    install_requires=['ansible >= 1.9'],
    package_dir={'ansibleinventorygrapher': 'lib/ansibleinventorygrapher'},
    packages=['ansibleinventorygrapher'],
    scripts=['bin/ansible-inventory-grapher'],
    test_suite="test",
)
