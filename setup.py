#!/usr/bin/env python
# -*- coding: utf-8 -*-
import ast
import re
from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'slugify',
    'parsedatetime',
    'humanize',
    'appdirs',
    'anyconfig',
    'PyYAML'
]

test_requirements = [
    # TODO: put package test requirements here
]

_version_re = re.compile(r'__version__\s+=\s+(.*)')
with open('mbot/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))

setup(
    name='mbot',
    version=version,
    description="Yet another Bot implemented in pure Python.",
    long_description=readme + '\n\n' + history,
    author="Michael Kutý",
    author_email='6du1ro.n@gmail.com',
    url='https://github.com/michaelkuty/sbot',
    packages=[
        'mbot',
    ],
    package_dir={'mbot':
                 'mbot'},
    entry_points={
        'console_scripts': [
            'mbot=mbot.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='mbot',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
