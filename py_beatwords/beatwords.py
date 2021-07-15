# 导入相关模块
import pygame
from pygame.locals import *
from configparser import ConfigParser
from requests import get
from hashlib import md5
from math import atan2,cos,sin
from platform import system
from threading import Thread
from queue import Queue
from sys import argv
from os import path
from random import randrange,choice

''' pygame库初始化'''
pygame.init()
pygame.mixer.pre_init(44100,16,2,4096)
pygame.mixer.init()
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])

''' 变量定义 '''
title = '----  单词勇闯关  ----'
display = pygame.display.Info()
#size = w, h = display.current_w//2, display.current_h*3//5
size = w, h = display.current_w, display.current_h
screen = pygame.display.set_mode(size, DOUBLEBUF|FULLSCREEN, 8) # 根据分辨率自定义游戏画布

pygame.display.set_caption(title)       # 显示游戏外框标题
pygame.key.set_repeat(5000)             # 设置键盘响应间隔
pygame.mouse.set_visible(True)          # 设置鼠标的可视模式
clock = pygame.time.Clock()             # 设置定时器
config = ConfigParser()
dir = path.dirname(argv[0])
score = 0 # 计分数
font_size = 30 # 默认单词大小
dict_words = {} # 读取单词文本，存入字典
showords = {}   # 屏幕上出现的单词字典
choosed_wd = {} # 被选中要击打的单词
cur_word = '' # 显示击中后的不完整单词
result = '开始'   # 需要在线翻译的中文结果
run = True    # 运行状态
q = Queue()   # 开启线程队列，保存查询结果
''' 引入跨平台发音引擎'''
if "Darwin" in system():
    font_file = "/System/Library/Fonts/PingFang.ttc"
    from AppKit import NSSpeechSynthesizer
    speaker = NSSpeechSynthesizer.alloc().init()
    from_voice = "com.apple.speech.synthesis.voice.Princess"
    speaker.setVoice_(from_voice)
elif "Windows" in system():
    font_file = r"C:\windows\Fonts\msyh.ttc"
    import win32com.client as wincl
    speaker = wincl.Dispatch("SAPI.SpVoice")
    speaker.Speak("", 0)
else:
    font_file = pygame.font.get_default_font()
    speaker = None

'''从配置文件中读取相关参数'''
try:
    config.read(path.join(dir,'config.ini'),encoding='utf-8')
except Exception as e:
    print('Read Error!', e)
setting = config['setting']
file = setting.get('file','words.txt').replace("'","").replace("\"","")
fps = setting.getint('fps',15)
max = setting.getint('max',15)
level = setting.getint('level',1)
counter = setting.getint('counter',100) * 10
speak = setting.getboolean('speak',False)

'''导入背景图片和音效文件'''
bgimg = pygame.image.load(path.join(dir,'media','backdrop.jpg')).convert_alpha()
bk_snd = pygame.mixer.Sound(path.join(dir,'media','endure.ogg'))
hit_snd = pygame.mixer.Sound(path.join(dir,'media','hit.ogg'))
miss_snd = pygame.mixer.Sound(path.join(dir,'media','click.ogg'))

'''增加自定义事件监听'''
ADDWORD = USEREVENT + 1
pygame.time.set_timer(ADDWORD, 10000 // level)
enemys = pygame.sprite.Group()
bullets = pygame.sprite.Group()
bk_snd.play(-1)

''' 引入百度在线翻译引擎'''
appID = setting.get('appID','0000000000000').replace("'","").replace("\"","") # 你的APP ID
secretKey = setting.get('secretKey','abcdq').replace("'","").replace("\"","") # 你的密钥
apiURL = setting.get('apiURL','http://api.fanyi.baidu.com/api/trans/vip/translate').replace("'","").replace("\"","") # 百度翻译 API 的 HTTP 接口

def baiduAPI_translate(query_str, to_lang):
    '''
    传入待翻译的字符串和目标语言类型，请求 apiURL，自动检测传入的语言类型获得翻译结果
    :param query_str: 待翻译的字符串
    :param to_lang: 目标语言类型
    :return: 翻译结果字典
    '''
    salt = str(randrange(32768, 65536,3)) # 生成随机的 salt 值
    pre_sign = appID + query_str + salt + secretKey # 准备计算 sign 值需要的字符串
    sign = md5(pre_sign.encode()).hexdigest() # 计算 md5 生成 sign
    params = { # 请求 apiURL 所有需要的参数
        'q': query_str,
        'from': 'auto',
        'to': to_lang,
        'appid': appID,
        'salt':salt,
        'sign': sign
    }
    try:
        response = get(apiURL, params=params)
        result_dict = response.json() # 获取返回的 json 数据
        if 'trans_result' in result_dict: # 得到的结果正常则 return
            return result_dict
        else:
            print('Some errors occured:\n', result_dict)
    except Exception as e:
        print('Some errors occured: ', e)

def translat(query_str, q, dst_lang='zh'):
    '''
    解析翻译结果后输出，默认实现英汉互译
    :param query_str: 待翻译的字符串，必填
    :param dst_lang: 目标语言类型，可缺省
    :return: 翻译后的字符串
    '''
    if dst_lang:
        result_dict = baiduAPI_translate(query_str, dst_lang) # 指定了目标语言类型，则直接翻译成指定语言
    else:
        result_dict = baiduAPI_translate(query_str, 'zh') # 未指定目标语言类型，则默认进行英汉互译
        if result_dict['from'] == 'zh':
            result_dict = baiduAPI_translate(query_str, 'en')
    dst = result_dict['trans_result'][0]['dst'] # 提取翻译结果字符串，并输出返回
    q.put_nowait(dst)

'''单独封装一个发音函数供线程使用'''
def speakout(speaker, word):
    if "Darwin" in system():
        speaker.startSpeakingString_(word)
    elif "Windows" in system():
        speaker.Speak(word)
    else:
        pass

''' 包装一个字体函数 '''
def showtext(text,size=25,color=(255,0,0)):
    _font = pygame.font.Font(font_file, size)
    _text = _font.render(text,True,color)
    return _text, _text.get_rect()

def button(msg, x, y, w, h, ic, ac, action=None):
    mouse =pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x,y,w,h))
        if action != None and click[0] == 1:
            for event in pygame.event.get():
                event.type == MOUSEBUTTONUP and action()
    else:
        pygame.draw.rect(screen, ic, (x,y,w,h))
    text,text_rect = showtext(msg,22,(255,255,255))
    text_rect.center = (x + w//2, y + h//2)
    screen.blit(text, text_rect)
def onspeak():
    global speak
    speak = True
def offspeak():
    global speak
    speak = False

''' 初始化子弹类'''
class Bullet(pygame.sprite.Sprite):
    def __init__(self,*args):
        super().__init__()
        self.dx, self.dy = args
        self.speed = 60
        self.plus = 3
        self.image = pygame.Surface((12,12),SRCALPHA)
        pygame.draw.circle(self.image,(250,0,0),(6,6),6)
        self.rect = self.image.get_rect(center=(w//2, h))
        self.diffX = self.dx - self.rect.x
        self.diffY = self.dy - self.rect.y
        self.angle = atan2(self.diffY, self.diffX)
    def update(self):
        self.rect.x += int(cos(self.angle) * self.speed) * self.plus
        self.rect.y += int(sin(self.angle) * self.speed) * self.plus
        if self.rect.top < self.dy or self.rect.y < 0 :
            self.kill()

''' 初始化单词类'''
class Enemy(pygame.sprite.Sprite):
    def __init__(self, text, x=0, y=0 , size=30, color=None,speed=1):
        super().__init__()
        if color is None:
            color = (randrange(150,250, 25),
                     randrange(25,200, 25),
                     randrange(50,225, 25))
        self._text = text
        self._speed = speed
        self.image,_ = showtext(text,size,color)
        if x == 0 and y == 0:
            self.rect = self.image.get_rect( center=(randrange(100, w - 100, 100), 0) )
        else:
            self.rect = self.image.get_rect( center=(x, y-2*speed) ) # 击中有拖延的效果
    def update(self):
        if self._text !='' and self.rect.bottom < h: # 在屏幕范围内下降
            self.rect.move_ip(0, self._speed)
        else:  # 超过屏幕就销毁实例
            if self._text in showords.keys():
                showords.pop(self._text)
            if self._text in choosed_wd.keys():
                choosed_wd.clear() # 丢失一个单词就清理
            self.kill()

''' 遍历文件分解成字典并处理异常 '''
with open(path.join(dir, file), 'r',encoding='utf-8') as f:
    for line in f:
        line = line.strip()
        try:
            line = line.split(':')
            dict_words[line[0]] = line[1]
        except:
            dict_words[line[0]] = ""

''' 主循环事件 '''
while run:
    for e in pygame.event.get():
        if e.type == ADDWORD:
            if len(showords) < max: # 屏幕上的单词数量最多max个
                word = choice( list( dict_words.keys() ) )
                if word not in showords.keys(): # 屏幕上不要出现重复单词
                    enemy = Enemy(word,speed=level)
                    showords[word] = [enemy] # 保存实例到字典中
                    enemys.add(enemy)
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_F1:
                run = False
            if e.key == K_UP:
                if level < 10:
                    level += 1
                    pygame.time.set_timer(ADDWORD, 10000 // level)
            if e.key == K_DOWN:
                if level > 1 :
                    level -= 1
                    pygame.time.set_timer(ADDWORD, 10000 // level)
            if e.key == K_0 or e.key == K_RALT or e.key == K_RCTRL or e.key == K_TAB:
                speak = not speak
            if e.key == K_ESCAPE : # 暂停生成新的单词并清屏
                font_size = 30
                showords = {}  # 屏幕上出现的单词字典
                choosed_wd = {}  # 被选中要击打的单词
                cur_word = ''  # 清理当前选中的单词
                result = "Tab: 打开/关闭语音  上下: 加速/减速  Esc: 清屏  F1: 退出"
                for _ in enemys:
                    _.kill()
            if not choosed_wd: # 如果没有选好单词，则挑选一个
                for k, v in showords.items(): # 遍历去找哪一个匹配首字母
                    try:
                        if k.lower().startswith(chr(e.key)):
                            hit_snd.play(1, 300)
                            font_size += 5
                            x = v[0].rect.centerx
                            y = v[0].rect.centery
                            bullet = Bullet(x, y)
                            bullets.add(bullet)
                            cur_word = k
                            if speak and speaker:
                                t = Thread(target=speakout, args=(speaker,cur_word))
                                t.start()
                            if dict_words[cur_word]: # 如果有内置翻译,就直接用
                                result = dict_words[cur_word]
                            else: # 否则就开启一个线程查询
                                result = ''
                                t = Thread(target=translat,args=(cur_word,q))
                                t.start()
                            showords.pop(k) # 及时从实例字典里清理掉
                            k = k[1:]
                            v[0].kill()
                            enemy = Enemy(k, x, y, font_size, (255, 255, 0), speed=level)
                            choosed_wd[k] = [enemy]
                            enemys.add(enemy)
                            break
                    except Exception as e:
                        pass
            else:
                for k, v in choosed_wd.items():
                    hit = False # 假设没有击中
                    try:
                        if k.lower().startswith(chr(e.key)):
                            hit = True
                            x = v[0].rect.centerx
                            y = v[0].rect.centery
                            k = k[1:]
                            v[0].kill()
                            bullet = Bullet(x, y)
                            bullets.add(bullet)
                            if k == '':
                                score += 10
                                font_size = 30
                            else:
                                hit_snd.play(1, 200)
                        else: # 如果不是正确按键，则无效，可加音效
                            miss_snd.play(1,200)
                    except Exception as e:
                        pass
                if hit: # 如果击中，则重新生成剩余字母
                    font_size += 5
                    enemy = Enemy(k, x, y, font_size, (255, 255, 0),speed=level)
                    choosed_wd[k] = [enemy]
                    enemys.add(enemy)
                if k == '': # 如果单词打光了，则加分并初始化
                    choosed_wd.clear()  # 打光单词就清理
    if  result == '' and cur_word :
        try:
            result = q.get_nowait()
        except:
            pass
    score_text,_ = showtext(f' 得分：{score:<5d} 单词：{cur_word:<15s} 翻译：{result:<10s} 速度：{level:<1d}',
                            25,color=(255,255,255))

    if score // counter + 1 > level: # 如果得分越高，难度自然增加
        level = score // counter + 1

    screen.blit(pygame.transform.scale(bgimg, size), (0, 0))  # 背景伸缩
    yiwen,yiwen_rect = showtext(result, font_size*2, color=(80,80,80))
    screen.blit(score_text, (50, h-32))
    screen.blit(yiwen, (w//2 - yiwen_rect.width//2, h//3))
    if speak:
        button("朗读:开", w - 100, h - 32, 100, 32, (0, 0, 255), (0, 0, 255), offspeak)
    else:
        button("朗读:关", w - 100, h - 32, 100, 32, (255, 0, 0), (255, 0, 0), onspeak)
    clock.tick(fps)
    bullets.draw(screen)
    bullets.update()
    enemys.draw(screen)
    enemys.update()
    pygame.display.update()