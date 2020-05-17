from tools.MqttWrapper import MqttWrapper

host = '167.172.169.242'



# set up MQTT communication
mqttClient = MqttWrapper(client_id="monitor", host=host)

mqttClient.subscribe(topic='device/#', qos=2)
mqttClient.loop_forever()
