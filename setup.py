#!/usr/bin/env python

import os
import sys

from setuptools import find_packages, setup

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
    install_requires=['ansible >= 2.4'],
    package_dir={'': 'lib'},
    packages=find_packages('lib'),
    include_package_data=True,
    zip_safe=True,
    entry_points={
        'console_scripts': [
             'ansible-inventory-grapher = ansibleinventorygrapher.__main__:main'
        ]
    },
    test_suite="test",
)
