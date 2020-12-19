#!python

import os

from setuptools import find_packages, setup

def local_file(name):
    return os.path.relpath(os.path.join(os.path.dirname(__file__), name))

SOURCE = local_file('src')

setup(
    name='random_str_gen',
    version='1.0.0',
    packages=find_packages(SOURCE),
    package_dir={"": SOURCE},
    install_requires=['requests', 'flask',
                      'flask_restful', 'flask-restplus'
                      ],
    scripts=['bin/randomgen']
)
