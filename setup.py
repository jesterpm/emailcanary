#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(name='emailcanary',
      version='0.1',
      author='Jesse Morgan',
      author_email='jesse@jesterpm.net',
      url='https://jesterpm.net',
      download_url='http://www.my_program.org/files/',
      description='Email Canary sends emails to a distribution list and checks for proper distribution.',

      packages = find_packages(),
      include_package_data = True,
      exclude_package_data = { '': ['README.txt'] },

      scripts = ['bin/emailcanary'],

      license='MIT',

      #setup_requires = ['python-stdeb', 'fakeroot', 'python-all'],
      install_requires = ['setuptools'],
     )
