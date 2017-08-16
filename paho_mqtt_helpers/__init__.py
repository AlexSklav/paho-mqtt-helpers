import logging
import socket

import paho.mqtt.client as mqtt

logger = logging.getLogger(__name__)


class BaseMqttReactor(object):
    """
    Base class for MQTT-based plugins.
    """
    def __init__(self, host='localhost', port=1883, keepalive=60):
        self._host = host
        self._port = port
        self._keepalive = keepalive
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message

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
        '''
        Callback for when the client receives a ``CONNACK`` response from the
        broker.

        Parameters
        ----------
        client : paho.mqtt.client.Client
            The client instance for this callback.
        userdata : object
            The private user data as set in :class:`paho.mqtt.client.Client`
            constructor or :func:`paho.mqtt.client.Client.userdata_set`.
        flags : dict
            Response flags sent by the broker.

            The flag ``flags['session present']`` is useful for clients that
            are using clean session set to 0 only.

            If a client with clean session=0, that reconnects to a broker that
            it has previously connected to, this flag indicates whether the
            broker still has the session information for the client.

            If 1, the session still exists.
        rc : int
            The connection result.

            The value of rc indicates success or not:

              - 0: Connection successful
              - 1: Connection refused - incorrect protocol version
              - 2: Connection refused - invalid client identifier
              - 3: Connection refused - server unavailable
              - 4: Connection refused - bad username or password
              - 5: Connection refused - not authorised
              - 6-255: Currently unused.

        Notes
        -----

        Subscriptions should be defined in this method to ensure subscriptions
        will be renewed upon reconnecting after a loss of connection.
        '''
        logger.info('Connected to MQTT broker with result code: %s', rc)

    def on_disconnect(self, *args, **kwargs):
        '''
        Attempt to reconnect when disconnected.
        '''
        # XXX: loop_start() shuould automatically call reconnect
        # Try to reconnect
        # self.mqtt_client.loop_stop()
        # self._connect()
        # self.mqtt_client.loop_start()
        pass


    def on_message(self, client, userdata, msg):
        '''
        Callback for when a ``PUBLISH`` message is received from the broker.
        '''
        logger.info('[on_message] %s: "%s"', msg.topic, msg.payload)

    ###########################################################################
    # Control API
    # ===========
    def start(self):
        '''
        Start plugin thread.
        '''
        # Connect to MQTT broker.
        self._connect()
        # Start loop in background thread.
        self.mqtt_client.loop_start()

    def stop(self):
        '''
        Stop plugin thread.
        '''
        # Stop client loop background thread (if running).
        self.mqtt_client.loop_stop()
