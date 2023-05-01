import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='ahri-rest',
    version='0.1',
    packages=['app', 'models', 'util'],
    include_package_data=True,
    description='Rest service for ml models',
    author='Victor Scherbackov'
)
