#!/usr/bin/env python

import sys
from setuptools import setup
sys.path.insert(0, '.')
import version


setup(name='paho-mqtt-helpers',
      version=version.getVersion(),
      description=open('README.md', 'rb').read(),
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/wheeler-microfluidics/paho-mqtt-helpers',
      install_requires=['paho-mqtt'],
      packages=['paho_mqtt_helpers'])