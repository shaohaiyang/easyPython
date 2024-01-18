from socketify import App, AppOptions, AppListenOptions
from prisma import Prisma
from urllib.parse import parse_qs
from jinja2_templates import Jinja2Template
import ujson
from os import path
from re import split
from random import randint
from pytz import timezone
from crontab import CronTab
from datetime import datetime
from time import mktime, strftime, strptime
from paho.mqtt import client as mqtt_client

DEBUG = False
db = Prisma(auto_register=True)

zone = "Asia/Shanghai"
server = "www.qq.com"
port = 1883
topic = "inTopic"
username = "shaohaiyang"
password = "upcom123456"
client_id = f'shy-{username}-{randint(0, 10000)}'

App = App()
App.template(Jinja2Template("./templates", encoding="utf-8", followlinks=False))
App.json_serializer(ujson)
#App.static("/static", "./static")

app = App.router()

def corksend(res, result="", status=200):
  res.cork(lambda res: res.write_status(f"{status}").end(f"{result}"))

def datetime_to_cron(dt_str):
  delimiters = "/|:| "
  dt = split(delimiters, dt_str)
  return f"{dt[4]} {dt[3]} {dt[2]} {dt[1]} *"

def connect_mqtt(topic, message):
  def on_connect(client, userdata, flags, rc):
    if rc == 0:
      if DEBUG: print(f"{rc} -> Send to topic: {topic}")
      client.publish(topic, message, qos=1, retain=True)
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
async def head(res, req):
  if not db.is_connected(): db.connect()
  try:
    posts = db.post.find_many(take=10, order={"id":'desc'}, include={"author": True} )
    context = {
      "framework": "Robyn",
      "templating_engine": "Jinja2",
      "data": posts
    }
    if DEBUG: print(context)
	
    res.render("index.html", **context)
  except Exception as e:
    pass

@app.post("/submit")
async def addpost(res, req):
  content_type = req.get_header("content-type")

  if content_type == "application/json":
    data = await res.get_json()
  elif content_type == "application/x-www-form-urlencoded":
    data = await res.get_form_urlencoded()
  else:
    data = await res.get_text()
  data = parse_qs(data)

  message = data.get("message",[None])[0]
  if DEBUG: print(f"post < {data}, message: {message}")

  if message and len(message) > 6:
    message = "".join([s for s in message.strip().splitlines(True) if s.strip()])
    msg_type = data.get("msg_type",['0'])[0]
    speak = data.get("msg_speak",['off'])[0]
    checkin = data.get("checkin",['off'])[0]
    title = data.get("title",["重要通知"])[0]
    speak = 1 if speak == "on" else 0
    checkin = 1 if checkin == "on" else 0
    author = "shan"
    crond_send = False

    # 如果不是调试模式，要记录数据库并发送消息
    if DEBUG:
      msg = f"{int(msg_type)}^{speak}^{checkin}^{title}^{message}^0"
      print(msg)
      response = "<h2>调试: 测试发布成功！</h2>"
    else:
      user = db.user.find_first(where={'name': author})
      if not user:
        user = db.user.create(
          data={  "name": author, }
        )

      created_timezone = datetime.now().astimezone(timezone(zone))
      createdAt = created_timezone.strftime("%c")
      created_timestamp = int(mktime(created_timezone.timetuple()))
      cron_time = data.get("send_time",['1979/06/18 21:45:18'])[0]
      cron_timestamp = int(mktime( strptime( cron_time, "%Y/%m/%d %H:%M:%S" )))
      data={'title':title, 'type':msg_type, 'message':message, 'authorId':user.id, 'createdAt':createdAt}

      if cron_timestamp - created_timestamp > 80:
        if DEBUG: print(f"创建定时发送任务: {createdAt} ({cron_time})")
        crond_send = True
        data={'title':title, 'type':msg_type, 'message':message, 'authorId':user.id, 'createdAt':createdAt, 'updatedAt':cron_time}

      post = db.post.create(data)
      msg = f"{int(msg_type)}^{speak}^{checkin}^{title}^{message}^{post.id}"

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
        with open(f"/tmp/mqtt-hzz-msg-{created_timestamp}", "w+") as f:
          f.write(msg)
        with CronTab(user='root') as cron:
          job = cron.new(command=f"/usr/local/sbin/cron_sendmsg.py /tmp/mqtt-hzz-msg-{created_timestamp}", comment=str(cron_timestamp))
          job.setall(datetime_to_cron(cron_time))
        response = "<h2>定时任务发布成功！</h2>"
    corksend(res, response)
  else:
    corksend(res)

###########################################
if __name__ == "__main__":
  App.listen(
    AppListenOptions(host="0.0.0.0", port=8080),
    lambda config: print( "Listening on port http://%s:%d now\n" % (config.host, config.port))
  ).run()
