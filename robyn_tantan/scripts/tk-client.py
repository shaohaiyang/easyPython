#import ctypes
import pyttsx3
from random import randint, choice
from paho.mqtt import client as mqtt_client
from threading import Thread
from time import sleep, time
from getpass import getuser
from sys import argv, exit
from os import path, popen, getcwd, getenv, environ, mkdir
from platform import node, system
from socket import gethostname
from psutil import process_iter
from datetime import datetime
from requests import get
from io import StringIO
from configparser import ConfigParser

DEBUG = False
codename = "hzc"

server = "www.qq.com"
urlfile = f"http://{server}/tantan.config"
config = ConfigParser(allow_no_value=True) # 导入配置解析库

# get windows machine name
try:
    n1 = node()
    n2 = gethostname()
    n3 = environ["COMPUTERNAME"]
    if n1 == n2 or n1 == n3:
        computename = n1
    elif n2 == n3:
        computename = n2
    else:
        computename = getenv("COMPUTERNAME") 
except Exception as e:
    computename = "Unknown-PC"

# get disk serial number to combine mqtt client_id
if "Darwin" in system():
    import AVFoundation
    speaker = AVFoundation.AVSpeechSynthesizer.alloc().init()
    client_id = f'hzz-{computename}-{randint(0, 1000)}'
elif "Windows" in system():
    disk_info = popen('vol '+'c:', 'r').read().split()
    disk_serial = disk_info[len(disk_info)-1:][0]
    client_id = f'hzz-{computename}-{disk_serial}'
else:
    client_id = f'hzz-{computename}-{randint(0, 1000)}'

# 获取并解析远程的配置文件
def getConfig(codename, key):
    try:
        return config.get(codename, key)
    except:
        return config.get("default", key)

# 返回屏幕自适应的字体大小
def count_size(len, width, height):
    size = 36
    while size < 310:
        pix = (size * 96 / 72)
        col = width // pix
        row = height // pix
        if row < 4 or int(col * row) <= len:
            return (size - 8) if size < 300 else 250
            break
        else:
            size += 4 

# 护眼色的十六进制转RGB
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
 
# 调用系统语音接口播放消息
def say_message(message, welcome, nickname):
    hello = "您好，" + choice(nickname) + "," + choice(welcome) + "一下听个通知吧"
    if DEBUG: print(hello)

    if "Darwin" in system():
        try:
            utterance = AVFoundation.AVSpeechUtterance.speechUtteranceWithString_(message)
            # Configure the utterance.
            utterance.setRate_(0.2)
            utterance.setPitchMultiplier_( 0.8)
            voice = AVFoundation.AVSpeechSynthesisVoice.voiceWithLanguage_("zh-GB")
            utterance.setVoice_(voice)
            speaker.speakUtterance_(utterance)
        except Exception as e:
            pass
    elif "Windows" in system():
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            # 播放中英文混合文字
            engine.setProperty('voice', voices[0].id)
            engine.setProperty('rate', 220)
            engine.say(hello)
            engine.runAndWait()
            sleep(1)
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            pass
        else:
            del engine
    else:
        pass
 
# 使用tkinter显示消息
def tk_message(title,message,checkin=0, type=2, colors=["#FFFFFF"]):
    import tkinter as tk
    from tkinter.font import Font
    from tkinter import messagebox
    #from tkhtmlview import HTMLText, RenderHTML
 
    def quit(dummy=None):
        root.destroy()
 
    def toggle_fs(dummy=None):
        state = False if root.attributes('-fullscreen') else True
        root.attributes('-fullscreen', state)
        if not state:
            root.geometry(screen_size)
 
    root = tk.Tk()
    root.title(title)
    # 获取屏幕的大小，测试了 winfo_这个函数好使
    screen_w = root.winfo_screenwidth()
    screen_h = root.winfo_screenheight()
    word_count = len(message)
    # 区分类型，2为全屏显示，1为屏幕一半居中显示
    if type == 2:
        screen_size = f"{screen_w}x{screen_h}+0+0"
        root.attributes('-fullscreen', True)
        font_size = count_size(word_count, screen_w, screen_h)
    elif type == 1:
        left = screen_w // 4
        right = screen_h // 4 
        screen_size = f"{screen_w // 2 }x{screen_h // 2 }+{left}+{right}"
        root.geometry(screen_size)
        font_size = count_size(word_count, screen_w // 2, screen_h // 2)
    else:
        root.withdraw() # 实现主窗口隐藏 root.geometry('0x0+999999+0')
        textto = tk.Toplevel(root)
        textto.withdraw()
        res = messagebox.showinfo(title, message, parent=textto)
        textto.attributes('-topmost', True)
        root.destroy()

    if type != 0:
        font_size = 200 if font_size is None else int(font_size)
        font_type = Font(family="楷体", size=font_size)
        root.attributes('-topmost', True) 
        # bind shortcut key
        root.bind('<Escape>', toggle_fs)
        root.bind('<BackSpace>', quit)
        #with open("message.html","w+") as f:
        #    f.write(message)
        #html_label = HTMLText(root, html=RenderHTML('message.html'))
        #html_label.pack(fill="both", expand=True)
        #html_label.fit_height()

        text = tk.Text(root, undo=True, autoseparators=False, wrap=tk.WORD)
        text.insert(tk.INSERT, message)
        text.configure(font=font_type, background=choice(colors))
        text.configure(state='disabled')
        text.pack(expand=True, fill=tk.BOTH)
        # 窗口聚焦点
        root.focus_force()
    root.mainloop()
    if DEBUG: print(screen_w, screen_h, word_count, font_size, checkin )

# 主程序，与mqtt通讯 
def connect_mqtt(topic):
    def on_connect(client, userdata, flags, rc):
        while True:
            if rc == 0:
                client.subscribe(topic, qos=1)
                if DEBUG: print(f"[{client_id}] Connected to MQTT Server! SessionID: {flags['session present']}")
                break
            else:
                sleep(3)
                client.reconnect()

    def on_message(client, userdata, msg):
        config.readfp(StringIO(get(urlfile).text))
        colors = eval(getConfig(codename,"colors"))
        hello = "主人，休息一下吧 :)"
        recv_msg = msg.payload.decode().split('^')
        emegy = int(recv_msg[0])
        speak = int(recv_msg[1])
        checkin = int(recv_msg[2])
        title = str(recv_msg[3])
        body_Str = str(recv_msg[4])
        try:
            msg_id = int(recv_msg[5])
        except Exception as e:
            msg_id = 0
        if DEBUG: print(f"模式：{emegy} | 语音：{speak} | 标题ID:{msg_id}：{title} | 消息: {body_Str}, 签到: {checkin}")

        if speak == 1:
            welcome = eval(getConfig(codename,"welcome"))
            nickname = eval(getConfig(codename,"nickname"))
            t = Thread(target=say_message, args=(body_Str, welcome, nickname))
            t.start()

        currentDatetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        currentDate, _ = currentDatetime.split()
        save_path = path.expanduser("~\\Desktop")
        if path.exists(save_path):
            save_path = path.join(save_path, "学校通知")
        else:
            save_path = path.join(getcwd(), "学校通知")
        try:
            mkdir(save_path)
        except Exception as e:
            pass

        save_file = f"学校通知-{currentDate}.txt"
        with open(path.join(save_path, save_file), encoding="utf-8", mode="a+") as fp:
            fp.write(f"----------- {currentDatetime} -----------\n标题： {title}\n-----------------------------------------------\n{body_Str}\n\n")

        title = f"{hello:<16}【{title}】{currentDatetime:>30}"
        tk_message(title, body_Str, checkin, emegy, colors)
 
    # Set Connecting Client ID 设置clean_session为False表示要建立一个持久性会话，这个很重要
    client = mqtt_client.Client(client_id,clean_session=False)
    client.on_connect = on_connect
    client.on_message = on_message
    return client

i = 0
# 加入自动启动菜单
def add_to_startup():
    global i
    file_name =  path.join(getcwd(), path.basename(argv[0]))
    _, file_extension = path.splitext(file_name)
 
    if  file_extension.lower() == ".exe":
        try:
            USER_NAME = getuser()
        except Exception as e:
            USER_NAME = "Administrator"
        bat_path = r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" % USER_NAME
        bat_file = path.join(bat_path, "popnotify.bat")
        try:
            if path.getsize(file_name) > 8000000:
                with open(bat_file, 'w') as _file:
                    _file.write(r'start "" "%s"' % file_name)
        except Exception as e:
            pass

# 判断是否有进程存在，存在就不能重复运行
        for proc in process_iter():
            if proc.name() == "点点通.exe":
                i += 1
        if i >= 3: exit(-1)

def run():
    try:
        config.readfp(StringIO(get(urlfile).text))
        server = str(getConfig(codename,"server").replace('"',''))
        port = int(getConfig(codename,"port").replace('"',''))
        topic = str(getConfig(codename,"topic").replace('"',''))
        username = str(getConfig(codename,"username").replace('"',''))
        password = str(getConfig(codename,"password").replace('"',''))
    except Exception as e:
        server = "www.qq.com"
        port = 8888
        topic = "school/hzc"
        username = "hzc"
        password = "hzx2487"
    if DEBUG: print(topic, username, password)

    try:
        client = connect_mqtt(topic)
        client.username_pw_set(username, password)
        client.connect(server, port, keepalive=300)
    except Exception as e:
        sleep(3)
    else:
        client.loop_forever()

if __name__ == '__main__':
    if "Windows" in system():
        add_to_startup()
    run()
