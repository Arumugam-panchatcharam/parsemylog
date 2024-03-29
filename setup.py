#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import subprocess
from setuptools import setup, find_packages

version_py = os.path.join(os.path.dirname(__file__), 'version.py')

try:
    version_git = subprocess.check_output(
        ["git", "describe", "--tags"]).rstrip()
except:
    with open(version_py, 'r') as fh:
        version_git = open(version_py).read().strip().split(
            '=')[-1].replace('"', '').replace("'", "")

version_msg = "# Do not edit this file, pipeline versioning is governed by git tags"
with open(version_py, 'w') as fh:
    fh.write(version_msg + os.linesep +
             "__version__='" + str(version_git) + "'")

setup(
    name="parsemylog",
    version="{ver}".format(ver=version_git),
    url='http://',
    download_url='',
    license='Commercial',
    description="A Simple GUI App to read RDK log files and display the insights to the developer.",
    author='Arumugam Panchatcharam',
    author_email='arumugamece2013@gmail.com',
    entry_points={
        'console_scripts': [
            'parsemylog = parsemylog.parsemylog:main'
        ]
    },
    package_data={'parsemylog': [
        'README.md', 'version.py', 'LICENSE', 'parsemylog/configs/config.yaml', 'parsemylog/core/logging_conf.yaml']},
    tests_require=['pytest'],
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'numpy == 1.21.0',
        'pandas == 1.2.5',
        'Pillow == 8.2.0',
        'PySimpleGUI == 4.45.0',
        'matplotlib == 3.4.2',
        'PyYAML == 5.4.1',
        'py7zr == 0.16.1',
        'tables == 3.6.1',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    packages=find_packages('.', exclude=['tests']),
    keywords='A Simple GUI App to read RDK log files and display the insights to the developer.',
)
