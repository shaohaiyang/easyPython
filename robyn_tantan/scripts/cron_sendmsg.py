#!/opt/python3.10.6/bin/python3.10
from sys import argv
from time import sleep
from random import randint
from paho.mqtt import client as mqtt_client
 
server = "www.qq.com"
port = 1883
topic = "inTopic"
username = "shaohaiyang"
password = "upcom123456"
client_id = f'shy-{username}-{randint(0, 10000)}'

def md5hash(msg):
  from hashlib import md5
  return md5(msg.encode("utf-8")).hexdigest()
 
def connect_mqtt(topic):
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      outopic = f"{topic}"
      client.publish(outopic, message, qos=1, retain=True)

  # Set Connecting Client ID 设置clean_session为False表示要建立一个持久性会话
  client = mqtt_client.Client(client_id,clean_session=True)
  client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(server, port)
  return client

def run():
  while True:
    try:
      client = connect_mqtt(topic)
      client.loop_start()
      break
    except Exception as e:
      sleep(3)
  client.loop_stop()


if __name__ == '__main__':
  with open(argv[1], "r") as f:
    message = f.read()
    if message:
      run()
