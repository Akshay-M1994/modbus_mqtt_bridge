import paho.mqtt.client as mqtt
import json
import logging
import sys
import time

#MQTT broker details
MQTT_BROKER_IP_ADDRESS = '192.168.1.100'
MQTT_BROKER_PORT = 1884

#Modbus Mqtt Topics
MODBUS_CMD_TOPIC =  "modbus_mqtt/cmd_request"
MODBUS_RESP_TOPIC = "modbus_mqtt/cmd_response"

#Message Queue Size
MQTT_MSG_QUEUE_SIZE = 256

def on_disconnect(self,client, userdata, reason_code, properties):
    #Log error code
    logging.debug('Connection result code ' + str(reason_code))  
    logging.debug('MQTT Client Disconnected.Attempting Reconnection...')

def on_publish(client, userdata, mid, reason_code, properties):
    # reason_code and properties will only be present in MQTTv5. It's always unset in MQTTv3
    logging.debug(f"on_publish callback triggered with reason code :{reason_code}")

def on_subscribe(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[-1].is_failure:
        logging.debug(f"Broker rejected you subscription: {reason_code_list[-1]}")
    else:
        logging.debug(f"Broker granted the following QoS: {reason_code_list[-1].value}")

def on_unsubscribe(client, userdata, mid, reason_code_list, properties):
    # Be careful, the reason_code_list is only present in MQTTv5.
    if len(reason_code_list) == 0 or not reason_code_list[-1].is_failure:
        logging.debug("unsubscribe succeeded (if SUBACK is received in MQTTv3 it success)")
    else:
        logging.debug(f"Broker replied with failure: {reason_code_list[-1]}")

    client.disconnect()    

def on_connect(client, userdata, flags, reason_code, properties):
    logging.debug(f"Connected with result code : {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe(MODBUS_RESP_TOPIC)

# The callback for when a PUBLISH message is received from the server.
def on_message(client, userdata, msg):
    
    #Log receipt of msg
    logging.debug(f"Msg received on topic:"+msg.topic+" Payload:" +str(msg.payload))
    

#Setting up logging module
logging.basicConfig(format='%(asctime)s - %(message)s - %(levelname)s', datefmt='%d-%b-%y %H:%M:%S',level=logging.DEBUG)

#Log startup info
logging.debug("[Starting Modbus Mqtt Bridge]")

#Setting up MQTT comms
mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message
mqttc.on_disconnect = on_disconnect
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe
mqttc.on_publish = on_publish
mqttc.connect(MQTT_BROKER_IP_ADDRESS, MQTT_BROKER_PORT, 60)

#Start paho mqtt background thread
mqttc.loop_start()

while True:
            #create dummy command
            mqttMsg = {"cmdName":"Voltage","uuid":"3bf11-00a1","devAdd":1,"devProfile":"DME111","regData":[]}

            #publish response
            mqttc.publish(MODBUS_CMD_TOPIC,json.dumps(mqttMsg))

            #put thread to sleep for 100ms
            time.sleep(0.5)