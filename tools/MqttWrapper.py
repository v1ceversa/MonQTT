import datetime
import paho.mqtt.client as mqtt
from entities import Schedule
from .MediaPlayer import TaskManager


class MqttWrapper:
    def __init__(self, client_id, host, port=1883, keep_alive=60):
        self.client = mqtt.Client(client_id)
        # Setting callbacks
        self.client.on_connect = self._on_connect_callback
        self.client.on_disconnect = self._on_disconnect_callback
        self.client.on_message = self._on_message_callback
        self.client.on_publish = self._on_publish_callback
        self.client.on_subscribe = self._on_subscribe_callback
        self.client.on_unsubscribe = self._on_unsubscribe_callback
        self.client.connect(host, port, keep_alive)
        self.schedule = Schedule()
        self.task_manager = TaskManager(self.schedule)

    # callbacks
    @staticmethod
    def _on_connect_callback(client, userdata, flags, rc):
        print(f'Connected with result code {str(rc)}')

    @staticmethod
    def _on_disconnect_callback(client, userdata, rc):
        print(f'Disconnected with result code {str(rc)}')

    def _on_message_callback(self, client, userdata, message):
        print(f'Got message {message.payload} from tube {message.topic}')
        landing = str(message.payload, 'utf-8')
        self.schedule.set_landing(landing)




    @staticmethod
    def _on_publish_callback(client, userdata, mid):
        print(f'Message published userdata: {userdata}')

    @staticmethod
    def _on_subscribe_callback(client, userdata, mid, granted_qos):
        print(f'Client subscribed')

    @staticmethod
    def _on_unsubscribe_callback(client, userdata, mid):
        print(f'Client unsubscribed')

    def publish(self, topic, payload=None, qos=0, retain=False):
        print(f'Publishing message {str(payload)} to {str(topic)}')
        self.client.publish(topic, payload, qos, retain)

    def subscribe(self, topic, qos=0):
        print(f'Trying subscribe to topic {topic} with qos {qos}')
        self.client.subscribe(topic, qos)

    def loop_forever(self, timeout=1.0, max_packets=1, retry_first_connection=False):
        self.client.loop_forever(timeout, max_packets, retry_first_connection)