import pygame, random,sys, os, platform
from pygame.locals import *
from threading import Thread
from queue import Queue

''' pygame库初始化'''
pygame.init()
pygame.mixer.init()

''' 变量定义 '''
display = pygame.display.Info()
size = w, h = display.current_w//2, display.current_h*3//5
title = '----  单词勇闯关  ----'
file = 'words.txt'
fps = 20
max = 10
level = 2
score = 0
font_size = 25
run = True
speak = False
dict_words = {}
showords = {}
choosed_wd = {}
cur_word = ''
result = ''
q = Queue()
if "Darwin" in platform.system():
    dir = os.path.sep.join(sys.argv[0].split(os.path.sep)[:-1])
    font_file = "/System/Library/Fonts/PingFang.ttc"
    ''' 引入发音引擎'''
    from AppKit import NSSpeechSynthesizer
    speaker = NSSpeechSynthesizer.alloc().init()
    from_voice = "com.apple.speech.synthesis.voice.Princess"
    speaker.setVoice_(from_voice)
elif "Windows" in platform.system():
    dir = os.path.dirname(__file__)
    font_file = r"C:\windows\Fonts\msyh.ttc"
    import win32com.client as wincl
    speaker = wincl.Dispatch("SAPI.SpVoice")
    speaker.Speak("", 0)
else:
    font_file = pygame.font.get_default_font()
    speaker = None

screen = pygame.display.set_mode(size)
pygame.display.set_caption(title)
pygame.key.set_repeat(3000)
pygame.mouse.set_visible(True)
clock = pygame.time.Clock()
bgimg = pygame.image.load(os.path.join(dir,'media','backdrop.jpg'))
bk_snd = pygame.mixer.Sound(os.path.join(dir,'media','endure.ogg'))
hit_snd = pygame.mixer.Sound(os.path.join(dir,'media','hit.ogg'))
miss_snd = pygame.mixer.Sound(os.path.join(dir,'media','click.ogg'))
over_snd = pygame.mixer.Sound(os.path.join(dir,'media','destroy.ogg'))

'''增加自定义事件监听'''
ADDWORD = USEREVENT + 1
pygame.time.set_timer(ADDWORD, 5000 // level)
enemys = pygame.sprite.Group()
bk_snd.play(-1)

''' 引入百度在线翻译引擎'''
# 导入相关模块
import hashlib, requests
# 你的APP ID
appID = '20210324000740987'
# 你的密钥
secretKey = 'AQoxdv0Uhz1VmTtUhngu'
# 百度翻译 API 的 HTTP 接口
apiURL = "http://api.fanyi.baidu.com/api/trans/vip/translate"

def baiduAPI_translate(query_str, to_lang):
    '''
    传入待翻译的字符串和目标语言类型，请求 apiURL，自动检测传入的语言类型获得翻译结果
    :param query_str: 待翻译的字符串
    :param to_lang: 目标语言类型
    :return: 翻译结果字典
    '''
    # 生成随机的 salt 值
    salt = str(random.randint(32768, 65536))
    # 准备计算 sign 值需要的字符串
    pre_sign = appID + query_str + salt + secretKey
    # 计算 md5 生成 sign
    sign = hashlib.md5(pre_sign.encode()).hexdigest()
    # 请求 apiURL 所有需要的参数
    params = {
        'q': query_str,
        'from': 'auto',
        'to': to_lang,
        'appid': appID,
        'salt':salt,
        'sign': sign
    }
    try:
        # 直接将 params 和 apiURL 一起传入 requests.get() 函数
        response = requests.get(apiURL, params=params)
        # 获取返回的 json 数据
        result_dict = response.json()
        # 得到的结果正常则 return
        if 'trans_result' in result_dict:
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
        # 指定了目标语言类型，则直接翻译成指定语言
        result_dict = baiduAPI_translate(query_str, dst_lang)
    else:
        # 未指定目标语言类型，则默认进行英汉互译
        result_dict = baiduAPI_translate(query_str, 'zh')
        if result_dict['from'] == 'zh':
            result_dict = baiduAPI_translate(query_str, 'en')
    # 提取翻译结果字符串，并输出返回
    dst = result_dict['trans_result'][0]['dst']
    q.put_nowait(dst)

''' 包装一个字体函数 '''
def showtext(text,size=25,color=(255,0,0)):
    if not text:
        size = 0
    _font = pygame.font.Font(font_file, size)
    _text = _font.render(text,True,color)
    return _text, _text.get_rect()

def button(msg, x, y, w, h, ic, ac, action=None):
    mouse =pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    if x + w > mouse[0] > x and y + h > mouse[1] > y:
        pygame.draw.rect(screen, ac, (x,y,w,h))
        if click[0] == 1 and action != None:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONUP:
                    action()
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

''' 初始化单词类'''
class Enemy(pygame.sprite.Sprite):
    def __init__(self, text, x=0, y=0 , size=25,color=(255,0,0)):
        super().__init__()
        self._text = text
        self._speed = 1
        self.image,_ = showtext(text,size,color)
        if x == 0 and y == 0:
            self.rect = self.image.get_rect(
                center=(random.randrange(100, w - 100, 100), 0)
            )
        else:
            self.rect = self.image.get_rect(
                center=(x, y-3)
            )

    def update(self):
        if self.rect.top < h: # 在屏幕范围内下降
            self.rect.move_ip(0, self._speed)
        else:  # 超过屏幕就销毁实例
            self.kill()
            if self._text in showords.keys():
                showords.pop(self._text)
            if self._text in choosed_wd.keys():
                choosed_wd.clear() # 丢失一个单词就清理

''' 遍历文件分解成字典并处理异常 '''
with open(os.path.join(dir, file), 'r',encoding='utf-8') as f:
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
                word = random.choice( list( dict_words.keys() ) )
                if word not in showords.keys(): # 屏幕上不要出现重复单词
                    enemy = Enemy(word)
                    showords[word] = [enemy] # 保存实例到字典中
                    enemys.add(enemy)
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_0 or e.key == K_LSHIFT or e.key == K_RSHIFT or e.key == K_RCTRL or e.key == K_LCTRL:
                speak = not speak
            if e.key == K_ESCAPE : # 暂停5秒休息
                pygame.time.set_timer(ADDWORD, 0)
                pygame.time.wait(3000)
                pygame.time.set_timer(ADDWORD, 5000 // level)
            if not choosed_wd: # 如果没有选中单词，则挑选一个
                for k, v in showords.items(): # 遍历去找哪一个匹配首字母
                    try:
                        if k.lower().startswith(chr(e.key)):
                            hit_snd.play(1, 300)
                            font_size += 5
                            x = v[0].rect.centerx
                            y = v[0].rect.centery
                            cur_word = k
                            if speak and speaker and "Darwin" in platform.system():
                                speaker.startSpeakingString_(cur_word)
                            elif speak and speaker and "Windows" in platform.system():
                                speaker.Speak(cur_word)
                            else:
                                pass
                            if dict_words[cur_word]: # 如果有内置翻译,就直接用
                                result = dict_words[cur_word]
                            else: # 否则就开启一个线程查询
                                result = ''
                                t = Thread(target=translat,args=(cur_word,q))
                                t.start()
                            showords.pop(k) # 及时从实例字典里清理掉
                            k = k[1:]
                            v[0].kill()
                            enemy = Enemy(k, x, y, font_size,(255,255,0))
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
                            if k == '':
                                #over_snd.play(1,600)
                                score += 10
                                font_size = 25
                            else:
                                hit_snd.play(1, 200)
                        else: # 如果不是正确按键，则无效，可加音效
                            miss_snd.play(1,200)
                    except Exception as e:
                        pass
                if hit: # 如果击中，则重新生成剩余字母
                    font_size += 5
                    enemy = Enemy(k, x, y, font_size, (255, 255, 0))
                    choosed_wd[k] = [enemy]
                    enemys.add(enemy)
                if k == '': # 如果单词打光了，则加分并初始化
                    choosed_wd.clear()  # 打光单词就清理

    if  result == '' and cur_word :
        try:
            result = q.get_nowait()
        except:
            pass
    score_text,_ = showtext(
        f'    得分：{score:<5d}    当前单词：{cur_word:<15s}  翻译：{result}',
        25,color=(255,255,255)
    )
    screen.blit(pygame.transform.scale(bgimg, size), (0, 0))  # 背景伸缩
    yiwen,yiwen_rect = showtext(result,100,color=(150,150,150))
    screen.blit(score_text, (50, h-50))
    screen.blit(yiwen, (w//2 - yiwen_rect.width//2, h//3))
    if speak:
        button("朗读:ON", w - 100, h - 50, 100, 50, (0, 0, 255), (0, 0, 255), offspeak)
    else:
        button("朗读:OFF", w - 100, h - 50, 100, 50, (255, 0, 0), (255, 0, 0), onspeak)
    enemys.draw(screen)
    enemys.update()
    clock.tick(fps)
    pygame.display.update() 