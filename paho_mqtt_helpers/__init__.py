from __future__ import print_function

import datetime
import inspect
import json
import logging
import os
import re
import signal
import socket
import sys

from mqtt_messages import MqttMessages
from pandas_helpers import pandas_object_hook, PandasJsonEncoder
from wheezy.routing import PathRouter
import paho.mqtt.client as mqtt
import six.moves

from ._version import get_versions
__version__ = get_versions()['version']
del get_versions

logger = logging.getLogger(__name__)


class BaseMqttReactor(MqttMessages):
    """
    Base class for MQTT-based plugins.
    """
    def __init__(self, host='localhost', port=1883, keepalive=60,
                 base="microdrop"):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self.mqtt_client = mqtt.Client(client_id=self.client_id)
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message
        self.should_exit = False
        self.router = PathRouter()
        self.subscriptions = []
        self.base = base

    ###########################################################################
    # Attributes
    # ==========
    @property
    def host(self):
        return self._host

    @host.setter
    def host(self, value):
        self._host = value
        self._connect()

    @property
    def port(self):
        return self._port

    @port.setter
    def port(self, value):
        self._port = value
        self._connect()

    @property
    def keepalive(self):
        return self._keepalive

    @keepalive.setter
    def keepalive(self, value):
        self._keepalive = value
        self._connect()

    @property
    def plugin_path(self):
        """Get parent directory of class location"""
        return os.path.dirname(os.path.realpath(
            inspect.getfile(self.__class__)))

    @property
    def plugin_name(self):
        """Get plugin name via the basname of the plugin path """
        return os.path.basename(self.plugin_path)

    @property
    def url_safe_plugin_name(self):
        """Make plugin name safe for mqtt and http requests"""
        return six.moves.urllib.parse.quote_plus(self.plugin_name)

    @property
    def client_id(self):
        """ ID used for mqtt client """
        return (self.url_safe_plugin_name + ">>"
                + self.plugin_path + ">>"
                + datetime.datetime.now().isoformat().replace(">>", ""))

    def addGetRoute(self, route, handler):
        """Adds route along with corresponding subscription"""
        self.router.add_route(route, handler)
        # Replace characters between curly brackets with "+" wildcard
        self.subscriptions.append(re.sub(r"\{(.+?)\}", "+", route))

    def sendMessage(self, topic, msg, retain=False, qos=0, dup=False):
        message = json.dumps(msg, cls=PandasJsonEncoder)
        self.mqtt_client.publish(topic, message, retain=retain, qos=qos)

    def subscribe(self):
        for subscription in self.subscriptions:
            self.mqtt_client.subscribe(subscription)

    ###########################################################################
    # Private methods
    # ===============
    def _connect(self):
        try:
            # Connect to MQTT broker.
            # TODO: Make connection parameters configurable.
            self.mqtt_client.connect(host=self.host, port=self.port,
                                     keepalive=self.keepalive)
        except socket.error:
            pass
            # logger.error('Error connecting to MQTT broker.')

    ###########################################################################
    # MQTT client handlers
    # ====================
    def on_connect(self, client, userdata, flags, rc):
        self.addGetRoute("microdrop/"+self.url_safe_plugin_name+"/exit",
                         self.exit)
        self.listen()
        self.subscribe()

    def on_disconnect(self, *args, **kwargs):
        # Startup Mqtt Loop after disconnected (unless should terminate)
        if self.should_exit:
            sys.exit()
        self._connect()
        self.mqtt_client.loop_forever()

    def on_message(self, client, userdata, msg):
        '''
        Callback for when a ``PUBLISH`` message is received from the broker.
        '''
        method, args = self.router.match(msg.topic)

        try:
            payload = json.loads(msg.payload, object_hook=pandas_object_hook)
        except ValueError:
            print("Message contains invalid json")
            print("topic: " + msg.topic)
            payload = None

        if method:
            method(payload, args)

    ###########################################################################
    # Control API
    # ===========
    def start(self):
        # Connect to MQTT broker.
        self._connect()
        # Start loop in background thread.
        signal.signal(signal.SIGINT, self.exit)
        self.mqtt_client.loop_forever()

    def exit(self, a=None, b=None):
        self.should_exit = True
        self.mqtt_client.disconnect()

    def stop(self):
        '''
        Stop plugin thread.
        '''
        # Stop client loop background thread (if running).
        self.mqtt_client.loop_stop()
