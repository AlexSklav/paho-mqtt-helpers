#!/usr/bin/env python
from setuptools import setup

import versioneer

with open('README.md', 'r', encoding='utf-8') as f:
    description = f.read().strip()

setup(name='paho-mqtt-helpers',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description=description,
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/Lucaszw/paho-mqtt-helpers',
      install_requires=['paho-mqtt', 'wheezy.routing', 'pandas-helpers',
                        'mqtt-messages'],
      packages=['paho_mqtt_helpers'])
