#!/usr/bin/env python3

from setuptools import setup, find_packages

requirements = [
    'pulpcore-plugin',
]

with open('README.rst') as f:
    long_description = f.read()

setup(
    name='pulp-rpm',
    version='0.0.1a1.dev1',
    description='RPM plugin for the Pulp Project',
    long_description=long_description,
    license='GPLv2+',
    author='Pulp Project Developers',
    author_email='pulp-list@redhat.com',
    url='http://www.pulpproject.org',
    install_requires=requirements,
    include_package_data=True,
    packages=find_packages(exclude=['test']),
    entry_points={
        'pulpcore.plugin': [
            'pulp_rpm = pulp_rpm:default_app_config',
        ]
    }
)
