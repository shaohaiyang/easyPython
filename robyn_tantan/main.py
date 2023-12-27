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
from crontab import CronTab
from time import mktime, strftime, strptime
from re import split

DEBUG = False
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

def datetime_to_cron(dt_str):
  delimiters = "/|:| "
  dt = split(delimiters, dt_str)
  return f"{dt[4]} {dt[3]} {dt[2]} {dt[1]} *"

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
  message = data.get("message",[None])[0]
  if not message:
    return

  msg_type = data.get("msg_type",['0'])[0]
  speak = data.get("msg_speak",['off'])[0]
  title = data.get("title",["重要通知"])[0]
  speak = 1 if speak == "on" else 0
  author = "shan"
  crond_send = False

  cron_time = data.get("send_time",[None])[0]
  created_timezone = datetime.now().astimezone(timezone(zone))
  createdAt = created_timezone.strftime("%c")
  created_timestamp = int(mktime(created_timezone.timetuple()))

  msg = f"{int(msg_type)}^{speak}^^{title}^{message}"
  if DEBUG:
    print(msg)
  else:
    with open(f"/tmp/mqtt-hzz-msg-{created_timestamp}", "w+") as f:
      f.write(msg)

  if cron_time:
    cron_timestamp = int(mktime( strptime(cron_time, "%Y/%m/%d %H:%M:%S"))) 
    if cron_timestamp - created_timestamp > 60:
      if DEBUG: print(f"创建定时发送任务:{createdAt}({created_timestamp}), {cron_time}({cron_timestamp})")
      crond_send = True
      with CronTab(user='root') as cron:
        job = cron.new(command=f"/usr/local/sbin/cron_sendmsg.py /tmp/mqtt-hzz-msg-{created_timestamp}", comment=str(cron_timestamp))
        job.setall(datetime_to_cron(cron_time))

# 如果不是调试模式，要记录数据库并发送消息
  if not DEBUG:
    user = db.user.find_first(where={'name': author})
    if not user:
      user = db.user.create(
        data={  "name": author, }
      )

    post = db.post.create(
      data={
        'title': title,
        'type': msg_type,
        'message': message,
        'authorId': user.id,
        'createdAt': createdAt,
        }
      )

    # 如果不是定时发送，则直接发送
    if not crond_send:
      client = connect_mqtt(topic, msg)
      client.loop_start()
      client.loop_stop()

      response = f"""<tr>
	<td>{post.title}</td>
	<td>{post.message}</td>
	<td>{post.views}</td>
	<td>{createdAt}</td>
	</tr>"""
    else:
      response = "<h2>定时任务发布成功！</h2>"
  else:
    response = "<h2>调试: 测试发布成功！</h2>"
  return response

###########################################
if __name__ == "__main__":
  app.add_directory(route="/static", directory_path=static_dir, index_file="index.html")
  app.start(port=5555, host="0.0.0.0") # host defaults to 127.0.0.1
