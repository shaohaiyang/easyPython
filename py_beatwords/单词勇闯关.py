# 导入相关模块
import pygame
from pygame.locals import *
from configparser import ConfigParser
from requests import get
from hashlib import md5
from math import atan2, cos, sin, degrees
from platform import system
from threading import Thread
from queue import Queue
from sys import argv
from os import path, listdir
from random import randint, randrange, choice
 
''' pygame库初始化和性能优化及安全设置'''
pygame.init()
pygame.event.set_allowed([QUIT, KEYDOWN, KEYUP])
try:
    pygame.mixer.pre_init(44100, 16, 2, 4096)
    pygame.mixer.init()
except Exception as e:
    pass
 
''' 变量定义 by邵东俊'''
title = '- 打单词勇闯关@邵东俊(金帆初中803) -'
display = pygame.display.Info()
size = w, h = display.current_w, display.current_h  # 获取屏幕分辨率
pygame.display.set_caption(title)  # 显示游戏外框标题
pygame.key.set_repeat(5000)  # 设置键盘响应间隔
pygame.mouse.set_visible(True)  # 设置鼠标的可视模式
clock = pygame.time.Clock()  # 设置定时器
config = ConfigParser()  # 导入配置解析库
dir = path.dirname(argv[0])
score = 0  # 计分数
font_size = 30  # 默认单词大小
dict_words = {}  # 读取单词文本，存入字典
showords = {}  # 屏幕上出现的单词字典
choosed_wd = {}  # 被选中要击打的单词
cur_word = ''  # 显示击中后的不完整单词
result = '开始挑战吧!'  # 需要在线翻译的中文结果
run = True  # 运行状态
q = Queue()  # 开启线程队列，保存查询结果
reopen = False  # 是否重新读取新文件
in_times = 10000 # 定时时间10s内的单词下降频率
 
''' 引入跨平台发音引擎'''
if "Darwin" in system():
    font_file = "/System/Library/Fonts/PingFang.ttc"
    from AppKit import NSScreen, NSEvent, NSMouseInRect, NSSpeechSynthesizer
 
    for screen in NSScreen.screens():
        if NSMouseInRect(NSEvent.mouseLocation(), screen.frame(), False):  # 获取当前鼠标的屏幕
            size = w, h = int(screen.frame().size.width), int(screen.frame().size.height)
    speaker = NSSpeechSynthesizer.alloc().init()
    from_voice = "com.apple.speech.synthesis.voice.Princess"
    speaker.setVoice_(from_voice)
elif "Windows" in system():
    font_file = r"C:\windows\Fonts\msyh.ttc"
    from win32com.client import Dispatch
    from win32api import GetSystemMetrics
    from win32con import SM_CXSCREEN, SM_CYSCREEN
 
    size = w, h = int(GetSystemMetrics(SM_CXSCREEN)), int(GetSystemMetrics(SM_CYSCREEN))
    try:
        speaker = Dispatch("SAPI.SpVoice")
        speaker.Speak("", 0)
    except Exception as e:
        pass
else:
    font_file = pygame.font.get_default_font()
    speaker = None
 
try:
    config.read(path.join(dir, 'config.ini'), encoding='utf-8')
except Exception as e:
    print('config.ini Read Error!', e)
 
setting = config['setting']
file = eval(setting.get('file', 'words.txt'))
fps = setting.getint('fps', 15)
max = setting.getint('max', 10)
high_score = setting.getint('score', 0)
level = setting.getint('level', 1)
counter = setting.getint('counter', 100) * 10
speak = setting.getboolean('speak', False)
bg_sound = setting.getint('music_volume', 1)
author = setting.get('author', '创作者: 邵东俊 (金帆初中803)')
 
screen = pygame.display.set_mode(size, DOUBLEBUF | FULLSCREEN, 8)  # 根据分辨率自定义游戏画布
'''导入背景图片和音效文件'''
bgimg = pygame.image.load(path.join(dir, 'media', 'space.jpeg')).convert_alpha()
if w >= h:
    bgimg = pygame.transform.rotate(bgimg, 90)
if pygame.mixer.get_init() is not None:
    bk_snd = pygame.mixer.Sound(path.join(dir, 'media', 'endure.ogg'))
    hit_snd = pygame.mixer.Sound(path.join(dir, 'media', 'hit.ogg'))
    miss_snd = pygame.mixer.Sound(path.join(dir, 'media', 'click.ogg'))
    bomb_snd = pygame.mixer.Sound(path.join(dir, 'media', 'bomb.ogg'))
    bk_snd.set_volume(bg_sound // 10)
    hit_snd.set_volume(bg_sound // 10)
    miss_snd.set_volume(bg_sound // 10)
    bomb_snd.set_volume(bg_sound // 10)
    bk_snd.play(-1)
 
# 载入爆炸图片
Bombs = []
for i in range(1, 5):  # 一共载入4张图片
    filename = f'bomb{i}.png'  # 用f-string将文件名格式化，:04指定了宽度为4位数字，左侧以0补齐
    img = pygame.image.load(path.join(dir, 'media', filename)).convert_alpha()  # 载入图片，返回Surface对象
    Bombs.append(img)  # 将Surface对象添加到列表中备用
 
'''增加自定义事件监听'''
ADDWORD = USEREVENT + 1
pygame.time.set_timer(ADDWORD, in_times // level)
enemys = pygame.sprite.Group()
bullets = pygame.sprite.Group()
 
''' 引入百度在线翻译引擎'''
appID = eval(setting.get('appID', '0000000000000'))  # 你的APP ID
secretKey = eval(setting.get('secretKey', 'abcdq'))  # 你的密钥
apiURL = eval(setting.get('apiURL', 'http://api.fanyi.baidu.com/translate'))  # 百度翻译API接口
 
 
def baiduAPI_translate(query_str, to_lang):
    '''
    传入待翻译的字符串和目标语言类型，自动检测传入的语言类型获得翻译结果
    :param query_str: 待翻译的字符串
    :param to_lang: 目标语言类型
    :return: 翻译结果字典
    '''
    salt = str(randrange(32768, 65536, 3))  # 生成随机的 salt 值
    pre_sign = appID + query_str + salt + secretKey  # 准备计算 sign 值需要的字符串
    sign = md5(pre_sign.encode()).hexdigest()  # 计算 md5 生成 sign
    params = {  # 请求 apiURL 所有需要的参数
        'q': query_str,
        'from': 'auto',
        'to': to_lang,
        'appid': appID,
        'salt': salt,
        'sign': sign
    }
    try:
        response = get(apiURL, params=params)
        result_dict = response.json()  # 获取返回的 json 数据
        if 'trans_result' in result_dict:  # 得到的结果正常则 return
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
        result_dict = baiduAPI_translate(query_str, dst_lang)  # 指定了目标语言类型，则直接翻译成指定语言
    else:
        result_dict = baiduAPI_translate(query_str, 'zh')  # 未指定目标语言类型，则默认进行英汉互译
        if result_dict['from'] == 'zh':
            result_dict = baiduAPI_translate(query_str, 'en')
    try:
        dst = result_dict['trans_result'][0]['dst']  # 提取翻译结果字符串，并输出返回
        q.put_nowait(dst)
    except Exception as e:
        pass
 
 
'''单独封装一个发音函数供线程使用'''
 
 
def speakout(speaker, word):
    if "Darwin" in system():
        speaker.startSpeakingString_(word)
    elif "Windows" in system():
        if pygame.mixer.get_init() is not None: speaker.Speak(word)
    else:
        pass
 
 
''' 包装一个字体函数 '''
 
 
def showtext(text, size=25, color=(255, 0, 0)):
    _font = pygame.font.Font(font_file, size)
    _text = _font.render(text, True, color)
    return _text, _text.get_rect()
 
 
def button(msg, x, y, w, h, ic, ac, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x, y, w, h))
        if action != None and click[0] == 1:
            for event in pygame.event.get():
                if event.type == MOUSEBUTTONUP:
                    if action.__name__ == "open_dict":  # 调用重新读取单词本
                        global dict_words, file, cur_word, choosed_wd, showords
                        for _ in enemys:
                            _.kill()
                        showords = {}  # 屏幕上出现的单词字典
                        choosed_wd = {}  # 被选中要击打的单词
                        cur_word = ''  # 清理当前选中的单词
                        dict_words = {}
                        file = msg
                    else:
                        action()
    else:
        pygame.draw.rect(screen, ic, (x, y, w, h))
    text, text_rect = showtext(msg, 22, (255, 255, 255))
    text_rect.center = (x + w // 2, y + h // 2)
    screen.blit(text, text_rect)
 
 
def onspeak():
    global speak
    speak = True
 
 
def offspeak():
    global speak
    speak = False
 
 
''' 初始化子弹类'''
 
 
class Bullet(pygame.sprite.Sprite):
    def __init__(self, *args):
        super().__init__()
        self.dx, self.dy = args
        self.dy += level
        self.speed = 20
        self.plus = 5
        # self.image = pygame.Surface((12, 12), SRCALPHA)
        # pygame.draw.circle(self.image, (250, 0, 0), (6, 6), 6)
        # 设置子弹比例
        ratio = 1
        self.image = pygame.image.load(path.join(dir, 'media', 'bullet.png')).convert_alpha()
        size = (self.image.get_width() * ratio, self.image.get_height() * ratio)
        self.image = pygame.transform.scale(self.image, size)
        # 计算角度
        self.degrees = degrees(atan2(w // 2 - self.dx, h - self.dy))
        self.image = pygame.transform.rotate(self.image, self.degrees)
        self.rect = self.image.get_rect(center=((w - 30) // 2, h - 50))
        self.diffX = self.dx - self.rect.x
        self.diffY = self.dy - self.rect.y
        self.angle = atan2(self.diffY, self.diffX)
 
    def update(self):
        self.rect.x += int(cos(self.angle) * self.speed) * self.plus
        self.rect.y += int(sin(self.angle) * self.speed) * self.plus
        if self.rect.top <= self.dy - self.speed or self.rect.y < 0:
            self.kill()
 
 
''' 初始化单词类'''
 
 
class Enemy(pygame.sprite.Sprite):
    def __init__(self, text, x=0, y=0, size=30, color=None, speed=1):
        super().__init__()
        if color is None:
            color = (randrange(200, 250, 10),
                     randrange(0, 50, 10),
                     randrange(0, 50, 10))
            color = self.Hex_to_RGB(self.getBrightColor())
        self._text = text
        self._speed = speed
        self.image, _ = showtext(text, size, color)
        if x == 0 and y == 0:
            self.rect = self.image.get_rect(center=(randrange(100, w - 100, 100), 0))
        else:
            self.rect = self.image.get_rect(center=(x, y - speed))  # 击中有拖延的效果
 
    def getBrightColor(self):
        # 获得亮色，保证其中两色分别90和ff，第三色为任意值即可
        full_range = ["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "a", "b", "c", "d", "e", "f"]
        combination = ["90"]
        # 将 ff 随机插入 90 前或后
        combination.insert(randint(0, 1), "ff")
        third_color = "{0}{1}".format(full_range[randint(0, 15)], full_range[randint(0, 15)])
        combination.insert(randint(0, 2), third_color)
        color = "#" + "".join(combination)
        return color
 
    def Hex_to_RGB(self, hex):
        r = int(hex[1:3], 16)
        g = int(hex[3:5], 16)
        b = int(hex[5:7], 16)
        return (r, g, b)
 
    def update(self):
        if self._text != '' and self.rect.bottom < h:  # 在屏幕范围内下降
            self.rect.move_ip(0, self._speed)
        else:  # 超过屏幕就销毁实例
            if self._text in showords.keys():
                showords.pop(self._text)
            if self._text in choosed_wd.keys():
                choosed_wd.clear()  # 丢失一个单词就清理
            self.kill()
 
 
class Bomb(pygame.sprite.Sprite):
    def __init__(self, center, imgs):
        super().__init__()
        self.imgs = imgs
        self.image = imgs[0]
        self.rect = self.image.get_rect()
        self.rect.center = center
        self.frame = 0
        self.last_update = pygame.time.get_ticks()  # 获取最近刷新时间
        self.frame_rate = 180 // len(self.imgs)  # 设定爆炸图片显示的间隔时间
 
    def update(self):
        now = pygame.time.get_ticks()  # 获取当前时间
        if now - self.last_update > self.frame_rate:  # 本帧与上一帧的时间差达到fram_rate时，显示1帧爆炸图片
            self.last_update = now  # 记录最近刷新时间
            self.frame += 1  # 帧数+1，这样下次才会调用下一张图片
            if self.frame == len(self.imgs):  # 当爆炸图片到达最后一帧时，爆炸对象自杀(不再占用内存)
                self.kill()
            else:
                self.image = self.imgs[self.frame]  # 指定要显示的爆炸图片(Surface对象)
 
 
class AddScore(pygame.sprite.Sprite):
    def __init__(self, center, score=0):
        super().__init__()
        self.last_update = pygame.time.get_ticks()  # 获取最近刷新时间
        self.frame_rate = 250
        self.size = 50
        self.image, _ = showtext("+" + str(score), self.size, (255, 0, 0))
        self.rect = self.image.get_rect(center=center)  # 击中有拖延的效果
 
    def update(self):
        now = pygame.time.get_ticks()  # 获取当前时间
        if now - self.last_update > self.frame_rate:  # 本帧与上一帧的时间差达到fram_rate时，销毁对象
            self.kill()
 
 
def open_dict(f=None):
    ''' 遍历文件分解成字典并处理异常 '''
    with open(path.join(dir, file), 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            try:
                line = line.split(':')
                dict_words[line[0]] = line[1]
            except:
                dict_words[line[0]] = ""
 
if __name__ == "__main__":
    ''' 主循环事件 '''
    while run:
        battery_img = pygame.image.load(path.join(dir, 'media', 'battery.png')).convert_alpha()
        battery_img_size = 130
        battery_img = pygame.transform.scale(battery_img, (battery_img_size, battery_img_size))
 
        if len(dict_words) == 0:
            reopen = False
            open_dict()
        for e in pygame.event.get():
            if e.type == ADDWORD:
                if len(showords) < max:  # 屏幕上的单词数量最多max个
                    word = choice(list(dict_words.keys()))
                    if word not in showords.keys():  # 屏幕上不要出现重复单词
                        enemy = Enemy(word, speed=level)
                        showords[word] = [enemy]  # 保存实例到字典中
                        enemys.add(enemy)
            if e.type == QUIT:
                run = False
            if e.type == KEYDOWN:
                start_time = pygame.time.get_ticks()
                reopen = False
                if e.key == K_F1:
                    run = False
                if e.key == K_LEFT and pygame.mixer.get_init() is not None:
                    bg_sound = bg_sound - 1 if bg_sound > 0 else 0
                    bk_snd.set_volume(bg_sound / 10)
                    hit_snd.set_volume(bg_sound / 10)
                    miss_snd.set_volume(bg_sound / 10)
                if e.key == K_RIGHT and pygame.mixer.get_init() is not None:
                    bg_sound = bg_sound + 1 if bg_sound < 10 else 10
                    bk_snd.set_volume(bg_sound / 10)
                    hit_snd.set_volume(bg_sound / 10)
                    miss_snd.set_volume(bg_sound / 10)
                if e.key == K_UP:
                    level = level + 1 if level < 5 else 5
                    pygame.time.set_timer(ADDWORD, in_times // level)
                if e.key == K_DOWN:
                    level = level - 1 if level > 1 else 1
                    pygame.time.set_timer(ADDWORD, in_times // level)
                if e.key == K_0 or e.key == K_RALT or e.key == K_RCTRL or e.key == K_TAB:
                    speak = not speak
                if e.key == K_ESCAPE:  # 暂停生成新的单词并清屏
                    font_size = 30
                    showords = {}  # 屏幕上出现的单词字典
                    choosed_wd = {}  # 被选中要击打的单词
                    cur_word = ''  # 清理当前选中的单词
                    result = "Tab: 打开/关闭语音  上下键: 加速/减速  左右键:加/减音量  Esc: 清屏  F1: 退出"
                    reopen = True
                    for _ in enemys:
                        _.kill()
                if not choosed_wd:  # 如果没有选好单词，则挑选一个
                    font_size = 30  # 重置翻译字体大小
                    for k, v in showords.items():  # 遍历去找哪一个匹配首字母
                        try:
                            if k.lower().startswith(chr(e.key)):
                                if pygame.mixer.get_init() is not None: hit_snd.play(1, 300)
                                font_size += 1
                                x = v[0].rect.centerx
                                y = v[0].rect.centery
                                bullet = Bullet(x, y)
                                bullets.add(bullet)
                                battery_degrees = degrees(atan2(w // 2 - x, h - y))
                                battery_img = pygame.transform.rotate(battery_img, battery_degrees)
                                cur_word = k
                                if speak and speaker:
                                    t = Thread(target=speakout, args=(speaker, cur_word))
                                    t.start()
                                if dict_words[cur_word]:  # 如果有内置翻译,就直接用
                                    result = dict_words[cur_word]
                                else:  # 否则就开启一个线程查询
                                    result = ''
                                    t = Thread(target=translat, args=(cur_word, q))
                                    t.start()
                                showords.pop(k)  # 及时从实例字典里清理掉
                                k = k[1:]
                                v[0].kill()
                                enemy = Enemy(k, x, y, font_size, (255, 255, 0), speed=level)
                                enemys.add(enemy)
                                choosed_wd.clear()
                                choosed_wd[k] = [enemy]
                                break
                        except Exception as e:
                            pass
                else:
                    for k, v in choosed_wd.items():
                        hit = False  # 假设没有击中
                        try:
                            if k.lower().startswith(chr(e.key)):
                                hit = True
                                x = v[0].rect.centerx
                                y = v[0].rect.centery
                                k = k[1:]
                                v[0].kill()
                                if len(k) > 0:
                                    bullet = Bullet(x, y)
                                    bullets.add(bullet)
                                    if pygame.mixer.get_init() is not None: hit_snd.play(1, 300)
                                    battery_degrees = degrees(atan2(w // 2 - x, h - y))
                                    battery_img = pygame.transform.rotate(battery_img, battery_degrees)
                            else:  # 如果不是正确按键，则无效，可加音效
                                if pygame.mixer.get_init() is not None: miss_snd.play(1, 250)
                        except Exception as e:
                            pass
                    if hit:  # 如果击中，则重新生成剩余字母
                        font_size += 2
                        enemy = Enemy(k, x, y, font_size, (255, 255, 0), speed=level)
                        choosed_wd.clear()
                        choosed_wd[k] = [enemy]
                        enemys.add(enemy)
                    if k == '':  # 如果单词打光了，则加分并初始化
                        score += len(cur_word)
                        if pygame.mixer.get_init() is not None: bomb_snd.play()
                        bomb = Bomb(choosed_wd.get(k)[0].rect.center, Bombs)  # 实例化爆炸对象，爆炸中心=敌人中心位置
                        add_score = AddScore(choosed_wd.get(k)[0].rect.center, len(cur_word))
                        enemys.add(bomb)
                        enemys.add(add_score)
                        choosed_wd.clear()  # 打光单词就清理
        if result == '' and cur_word:
            try:
                result = q.get_nowait()
            except:
                pass
        high_score = score if score > high_score else high_score
        high_score_text, _ = showtext(f'最高分: {high_score:<6d}', 30, color=(200, 50, 50))
        score_text, _ = showtext(f'得分：{score:<6d} 速度：{level:<1d} 音量：{bg_sound:<2d} 单词：{cur_word:<24s} 翻译：{result:<14s}',
                                 20, color=(255, 255, 255))
        help_text, _ = showtext(f'ESC: 清屏/更多帮助 ', 20, color=(255, 255, 255))
 
        if score // counter + 1 > level:  # 如果得分越高，难度自然增加
            level = score // counter + 1
 
        screen.blit(pygame.transform.scale(bgimg, size), (0, 0))  # 背景伸缩
        battery_rect = battery_img.get_rect(center=((w - 30) // 2, h - battery_img.get_height()//4))
        if len(result) > 50:
            yiwen, yiwen_rect = showtext(result, int(font_size * 1.2), color=(110, 110, 110))
        else:
            yiwen, yiwen_rect = showtext(result + " " + cur_word, int(font_size * 1.8), color=(110, 110, 110))
        screen.blit(high_score_text, (w // 2 - 50, 20))
        screen.blit(score_text, (10, h - 32))
        screen.blit(help_text, (w - 300, h - 32))
        screen.blit(yiwen, (w // 2 - yiwen_rect.width // 2, h // 3))
        if speak:
            button("朗读:开", w - 100, h - 32, 100, 32, (0, 0, 255), (255, 0, 0), offspeak)
        else:
            button("朗读:关", w - 100, h - 32, 100, 32, (255, 0, 0), (0, 0, 255), onspeak)
 
        if reopen:
            lists = [f for f in listdir(dir) if f.endswith(".txt")]
            num = (w // 200 - 1)
            for i, f in enumerate(lists):
                button(f, w // 5 + i % num * 200, h // 2 + i // num * 100, len(f) * 16, 50, (0, 0, 255), (255, 0, 0),
                       action=open_dict)
        clock.tick(fps)
        bullets.draw(screen)
        bullets.update()
        enemys.draw(screen)
        enemys.update()
        screen.blit(battery_img, battery_rect)
        pygame.display.update()
    else:
        with open(path.join(dir, 'config.ini'), encoding='utf-8', mode='w') as configfile:
            if score >= high_score:
                config['setting']['score'] = str(score)
            config['setting']['author'] = str('创作者: 邵东俊 (金帆初中803)')
            config.write(configfile)