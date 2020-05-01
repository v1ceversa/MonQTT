import os
from tools import MqttWrapper

host = '#.#.#.#'

if not os.path.exists(download_path):
    os.mkdir(download_path)


# set up MQTT communication
mqttClient = MqttWrapper(client_id="monitor", host=host)

mqttClient.subscribe(topic='device/#', qos=2)
mqttClient.loop_forever()
