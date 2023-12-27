import sys, os, getpass
import ctypes
import pyttsx3
from random import randint, choice
from paho.mqtt import client as mqtt_client
from threading import Thread
from time import sleep
 
DEBUG = True
# mqtt server address and listen port
server = "www.qq.com"
port = 1883
# mqtt receive channel topic name
topic = "school/hzz"
# mqtt identity username/password verification
username = "hzc"
password = "hzc87612487"
colors = [ "#C7EDCC", "#FFFFFF", "#FAF9DE", "#FFF2E2", "#FDE6E0", "#DCE2F1", "#E9EBFE", "#EAEAEF", "#E3EDCD", "#CCE8CF" ]
# icons
WS_TOPMOST = 0x1000
ICON_EXCLAIM = 0x30
ICON_INFO = 0x40
ICON_STOP = 0x10
 
 # get windows machine name
try:
    kernel32 = ctypes.WinDLL("kernel32")
    kernel32.GetComputerNameW.restype = ctypes.c_bool
    kernel32.GetComputerNameW.argtypes = (ctypes.c_wchar_p,ctypes.POINTER(ctypes.c_uint32))
    lenComputerName = ctypes.c_uint32()
    kernel32.GetComputerNameW(None, lenComputerName)
    computerName = ctypes.create_unicode_buffer(lenComputerName.value)
    kernel32.GetComputerNameW(computerName, lenComputerName)
    computename = computerName.value
except Exception as e:
    computename = "Unknown-PC"

# get disk serial number to combine mqtt client_id
try:
    disk_info = os.popen('vol '+'c:', 'r').read().split()
    disk_serial = disk_info[len(disk_info)-1:][0]
    client_id = f'hzz-{computename}-{disk_serial}'
except Exception as e:
    client_id = f'hzz-{computename}-{randint(0, 1000)}'

# 返回屏幕自适应的字体大小
def count_size(len, width, height):
    size = 36
    while size < 310:
        pix = (size * 96 / 72)
        col = width // pix
        row = height // pix
        if row < 4 or int(col * row) <= len:
            return (size - 2) if size < 300 else 300
            break
        else:
            size += 2 

# 护眼色的十六进制转RGB
def hex_to_rgb(value):
    value = value.lstrip('#')
    lv = len(value)
    return tuple(int(value[i:i + lv // 3], 16) for i in range(0, lv, lv // 3))
 
# 调用系统语音接口播放消息
def say_message(message):
    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        # 播放中英文混合文字
        engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 220)
        engine.say(message)
        engine.runAndWait()
        del engine
    except Exception as e:
        pass
 
# 使用tkinter显示消息
def tk_message(title,message,font_size, type=2):
    import tkinter as tk
    from tkinter.font import Font
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
        if not font_size:
            font_size = count_size(word_count, screen_w, screen_h)
    else:
        left = screen_w // 4
        right = screen_h // 4 
        screen_size = f"{screen_w // 2 }x{screen_h // 2 }+{left}+{right}"
        root.geometry(screen_size)
        if not font_size:
            font_size = count_size(word_count, screen_w // 2, screen_h // 2)

    if DEBUG: print(screen_w, screen_h, word_count, font_size )
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
 
# 使用turtle模块动画出消息，太幼稚了，不用了
def tt_message(title, message, font_size):
    import turtle as tt
    w, h = 1000, 800
    win = tt.Screen()
    win.colormode(255)
    win.title(title)
    win.setup(w,h)
    bgcolor = hex_to_rgb(choice(colors))
    win.bgcolor(bgcolor[0], bgcolor[1], bgcolor[2])
    if not font_size:
        font_size = "35"
 
    pen = tt.Pen()
    pen.hideturtle()
    pen.up()
    pen.speed(8)
 
    x, y = -w/2 + 60, h/2 - 50
    i, l = 0, 0
    for word in message:
        i += 1
        pen.goto(x,y)
        pen.write(word, font=("楷体", int(font_size)))
        x += 50
        num = 18 if l == 0 else 20
        if i == num:
            i = 1
            x, y, l = -w/2 + 10, y - 60, l + 1
 
    win.exitonclick()
 
# 主程序，与mqtt通讯 
def connect_mqtt(topic):
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            while True:
                try:
                    client.subscribe(topic, qos=1)
                    if DEBUG: print(f"[{client_id}] Connected to MQTT Server! SessionID: {flags['session present']}")
                    break
                except Exception as e:
                    sleep(3)
        else:
            client.reconnect()
 
    def on_message(client, userdata, msg):
        recv_msg = msg.payload.decode().split('^')
        emegy = int(recv_msg[0])
        speak = int(recv_msg[1])
        size = str(recv_msg[2])
        title = str(recv_msg[3])
        body_Str = str(recv_msg[4])
 
        if DEBUG: print(f"模式：{emegy} | 语音：{speak} | 标题：{title} | 消息: {body_Str}, 字体大小: {size}") 
 
        if speak == 1:
            t = Thread(target=say_message, args=(body_Str,))
            t.start()
 
        if emegy == 0:
            try:
                user32 = ctypes.WinDLL("user32")
                messagebox = lambda info, title="重要消息", style=0: user32.MessageBoxW(0, str(info), str(title), style)
                messagebox(body_Str,title, ICON_INFO | WS_TOPMOST)
            except Exception as e:
                pass
        elif emegy == 2:
            tk_message(title, body_Str, size, type=2)
        else:
            tk_message(title, body_Str, size, type=1)
 
    # Set Connecting Client ID 设置clean_session为False表示要建立一个持久性会话
    client = mqtt_client.Client(client_id,clean_session=False)
    client.username_pw_set(username, password)
    client.on_connect = on_connect
    client.connect(server, port, keepalive=300)
    client.on_message = on_message
    return client
 
# 加入自动启动菜单
def add_to_startup():
    file_name =  os.path.basename(sys.argv[0])
    _, file_extension = os.path.splitext(file_name)
 
    if  file_extension.lower() == ".exe":
        try:
            USER_NAME = getpass.getuser()
        except Exception as e:
            USER_NAME = "Administrator"
        bat_path = r"C:\Users\%s\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Startup" % USER_NAME
        bat_file = os.path.join(bat_path, "popnotify.bat")
        with open(bat_file, "w+") as _file:
            _file.write(r'start "" "%s"' % os.path.join(os.getcwd(), file_name))
                
 
def run():
    while True:
        try:
            client = connect_mqtt(topic)
            break
        except Exception as e:
            sleep(5)
    client.loop_forever()
 
 
if __name__ == '__main__':
    add_to_startup()
    run()
