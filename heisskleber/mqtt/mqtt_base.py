import ssl
import sys
import threading

from paho.mqtt.client import Client as mqtt_client

from .config import MqttConf


class ThreadDiedError(RuntimeError):
    pass


_thread_died = threading.Event()

_default_excepthook = threading.excepthook


def _set_thread_died_excepthook(args, /):
    _default_excepthook(args)
    global _thread_died
    _thread_died.set()


threading.excepthook = _set_thread_died_excepthook


class MqttBase:
    """
    Wrapper around eclipse paho mqtt client.
    Handles connection and callbacks.
    Callbacks may be overwritten in subclasses.
    """

    def __init__(self, config: MqttConf) -> None:
        self.config = config
        self.client = mqtt_client()
        self.is_connected = False

    def start(self) -> None:
        if not self.is_connected:
            self.connect()

    def stop(self) -> None:
        if self.client:
            self.client.loop_stop()
        self.is_connected = False

    def connect(self) -> None:
        self.client.username_pw_set(self.config.user, self.config.password)

        # Add callbacks
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        self.client.on_message = self._on_message

        if self.config.ssl:
            # By default, on Python 2.7.9+ or 3.4+,
            # the default certification authority of the system is used.
            self.client.tls_set(tls_version=ssl.PROTOCOL_TLS_CLIENT)

        self.client.connect(self.config.host, self.config.port)
        self.client.loop_start()
        self.is_connected = True

    @staticmethod
    def _raise_if_thread_died() -> None:
        global _thread_died
        if _thread_died.is_set():
            raise ThreadDiedError()

    # MQTT callbacks
    def _on_connect(self, client, userdata, flags, return_code) -> None:
        if return_code == 0:
            print(f"MQTT node connected to {self.config.host}:{self.config.port}")
        else:
            print("Connection failed!")
        if self.config.verbose:
            print(flags)

    def _on_disconnect(self, client, userdata, return_code) -> None:
        print(f"Disconnected from broker with return code {return_code}")
        if return_code != 0:
            print("Killing this service")
            sys.exit(-1)

    def _on_publish(self, client, userdata, message_id) -> None:
        if self.config.verbose:
            print(f"Published message with id {message_id}, qos={self.config.qos}")

    def _on_message(self, client, userdata, message) -> None:
        if self.config.verbose:
            print(f"Received message: {message.payload!s}, topic: {message.topic}, qos: {message.qos}")

    def __del__(self) -> None:
        self.stop()
