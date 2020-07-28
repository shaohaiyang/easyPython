import pygame, random,sys, os, platform
from threading import Thread
from pygame.locals import *
from queue import Queue

''' 变量定义 '''
size = w, h = 1000, 2000
title = '---  单词勇闯关  ---'
file = 'words.txt'
fps = 40      buil
max = 15
level = 2
score = 0
font_size = 25
run = True
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
else:
    dir = os.path.dirname(__file__)
    font_file = r"C:\windows\Fonts\msyh.ttc"
    import win32com.client as wincl
    speaker = wincl.Dispatch("SAPI.SpVoice")

''' 引入google在线翻译引擎'''
from googletrans import Translator
translator= Translator()
def translat(word,q):
    res = translator.translate(word,src='en', dest='zh-cn').text
    q.put_nowait(res)

''' 包装一个字体函数 '''
def showtext(text,size=25,color=(255,0,0)):
    _font = pygame.font.Font(font_file, size)
    _text = _font.render(text,True,color)
    return _text

''' 初始化单词类'''
class Enemy(pygame.sprite.Sprite):
    def __init__(self, text, x=0, y=0 , size=25,color=(255,0,0)):
        super().__init__()
        self._text = text
        self._speed = 1
        self.image = showtext(text,size,color)
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

''' pygame库初始化'''
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode(size)
pygame.display.set_caption(title)
pygame.key.set_repeat(5000)
pygame.mouse.set_visible(False)
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
    screen.blit(pygame.transform.scale(bgimg, size), (0, 0))  # 背景伸缩
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
            if e.key == K_ESCAPE: # 暂停5秒休息
                pygame.time.set_timer(ADDWORD, 0)
                pygame.time.wait(3000)
                pygame.time.set_timer(ADDWORD, 5000 // level)
            if not choosed_wd: # 如果没有选中单词，则挑选一个
                for k, v in showords.items(): # 遍历去找哪一个匹配首字母
                    if k.lower().startswith(chr(e.key)):
                        hit_snd.play(1,250)
                        font_size += 5
                        x = v[0].rect.centerx
                        y = v[0].rect.centery
                        cur_word = k
                        if "Darwin" in platform.system():
                            speaker.startSpeakingString_(cur_word)
                        else:
                            speaker.Speak(cur_word)
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
            else:
                for k, v in choosed_wd.items():
                    hit = False # 假设没有击中
                    if k.lower().startswith(chr(e.key)):
                        hit = True
                        x = v[0].rect.centerx
                        y = v[0].rect.centery
                        k = k[1:]
                        v[0].kill()
                        if k == '':
                            #over_snd.play(1,1100)
                            score += 10
                            font_size = 25
                        else:
                            hit_snd.play(1, 250)
                    else: # 如果不是正确按键，则无效，可加音效
                        miss_snd.play(1,250)
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
    score_text = showtext(
        f'\t\t得分：{score:<5d}\t\t当前单词：{cur_word:<15s}\t翻译：{result}',
        25,color=(255,255,255)
    )
    yiwen = showtext(result,80,color=(120,120,120))
    screen.blit(score_text, (10, h-50))
    screen.blit(yiwen, (w//2 - 100, h//3))
    enemys.draw(screen)
    enemys.update()
    clock.tick(fps)
    pygame.display.update()