#!/usr/bin/env python
from setuptools import setup

import versioneer


setup(name='paho-mqtt-helpers',
      version=versioneer.get_version(),
      cmdclass=versioneer.get_cmdclass(),
      description=open('README.md', 'rb').read(),
      author='Christian Fobel',
      author_email='christian@fobel.net',
      url='https://github.com/Lucaszw/paho-mqtt-helpers',
      install_requires=['paho-mqtt', 'wheezy.routing', 'pandas-helpers',
                        'mqtt-messages'],
      packages=['paho_mqtt_helpers'])
