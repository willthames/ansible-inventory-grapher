#!/usr/bin/env python

import os
import sys

from setuptools import setup

sys.path.insert(0, os.path.abspath('lib'))

setup(
    name='ansible-inventory-grapher',
    version='1.0.3',
    description='Creates graphs representing ansible inventory',
    author='Will Thames',
    author_email='will@thames.id.au',
    url='http://github.com/willthames/ansible-inventory-grapher',
    license='GPLv3',
    install_requires=['ansible >= 1.7'],
    package_dir={'ansibleinventorygrapher': 'lib/ansibleinventorygrapher'},
    packages=['ansibleinventorygrapher'],
    scripts=['bin/ansible-inventory-grapher'],
)
