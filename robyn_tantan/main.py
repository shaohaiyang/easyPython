from robyn import Robyn, serve_file, serve_html, jsonify, WebSocket
from robyn.robyn import Response, Request
from robyn.templating import JinjaTemplate
from random import randint
from urllib.parse import parse_qs
from prisma import Prisma
from os import path
from pytz import timezone
from datetime import datetime
from paho.mqtt import client as mqtt_client

DEBUG=False
db = Prisma(auto_register=True)
db.connect()

app = Robyn(__file__)
websocket = WebSocket(app, "/webst")

current_dir = path.dirname(__file__)
jinja_template = JinjaTemplate(path.join(current_dir, "templates"))
static_dir = path.join(current_dir, "static")
zone = "Asia/Shanghai"
server = "www.qq.com"
port = 1883
topic = "inTopic"
username = "shaohaiyang"
password = "upcom123456"
client_id = f'shy-{username}-{randint(0, 10000)}'

def connect_mqtt(topic, message):
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      if DEBUG: print(f"{rc} -> Send to topic: {topic}")
      client.publish(topic, message)
    else:
      if DEBUG: print(f"{rc} -> Failed to Send to topic: {topic}")
      pass
 
  # Set Connecting Client ID 设置clean_session为False表示要建立一个持久性会话
  client = mqtt_client.Client(client_id,clean_session=False)
  client.username_pw_set(username, password)
  client.on_connect = on_connect
  client.connect(server, port, keepalive=300)
  return client

@app.get("/")
async def head(req):
  try:
    posts = db.post.find_many(take=10, order={"id":'desc'}, include={"author": True} )
    context = {
      "framework": "Robyn",
      "templating_engine": "Jinja2",
      "data": posts
    }
    if DEBUG: print(context)
	
    response = jinja_template.render_template(template_name="index.html", **context)
    return response
  except Exception as e:
    return


@app.post("/submit")
async def addpost(req: Request):
  data = parse_qs(req.body) # (bytearray(req.get("body")).decode("utf-8")) unused
  if DEBUG: print("post <", data)
  try:
    message = data.get("message")[0]
  except Exception as e:
    raise(e)

  msg_type = data.get("msg_type",['0'])[0]
  speak = data.get("msg_speak",['off'])[0]
  title = data.get("title",["重要通知"])[0]
  author = "shan"
  speak = 1 if speak == "on" else 0

  user = db.user.find_first(where={'name': author})
  if user is None:
    user = db.user.create(
      data={  "name": author, }
      )

  createdAt = datetime.now().astimezone(timezone(zone)).strftime("%c")
  if DEBUG: print("post <", data, " -> ", title, createdAt)
  post = db.post.create(
      data={
	'title': title,
	'type': msg_type,
	'message': message,
	'authorId': user.id,
	'createdAt': createdAt,
	}
      )

  msg = f"{int(msg_type)}^{speak}^^{title}^{message}"
  if DEBUG: print(msg)
  client = connect_mqtt(topic, msg)
  client.loop_start()
  client.loop_stop()

  response = f"""<tr>
    <td>{post.title}</td>
    <td>{post.message}</td>
    <td>{post.views}</td>
    <td>{createdAt}</td>
    </tr>"""
  return response

###########################################
if __name__ == "__main__":
  app.add_directory(route="/static", directory_path=static_dir, index_file="index.html")
  app.start(port=5555, host="0.0.0.0") # host defaults to 127.0.0.1
