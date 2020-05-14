
from tools import MqttWrapper

host = '#.#.#.#'



# set up MQTT communication
mqttClient = MqttWrapper(client_id="monitor", host=host)

mqttClient.subscribe(topic='device/#', qos=2)
mqttClient.loop_forever()
