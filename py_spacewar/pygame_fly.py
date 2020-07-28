import pygame,os,sys,random
from pygame.locals import *

size = x, y = 1000,800
title = '太空大战'
running = True
autofire = True
life = 3
score = 0
dir = os.path.dirname(__file__)

pygame.init()
pygame.mixer.init()
pygame.display.set_caption(title)
pygame.mouse.set_visible(False)
pygame.key.set_repeat(300)
screen = pygame.display.set_mode(size)
background = pygame.image.load(dir + '/earth.gif')
snd_over = pygame.mixer.Sound(dir + '/gameover.ogg')

class Plane(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(dir + '/spaceship.png')
        self.rect = self.image.get_rect(
            center=(
               0,random.randint(0,y)
            )
        )
        self.speed = 10
        self.hit = False
    def update(self,key):
        if key[K_UP]:
            self.rect.move_ip(0,-self.speed)
        if key[K_DOWN]:
            self.rect.move_ip(0,self.speed)
        if key[K_LEFT]:
            self.rect.move_ip(-self.speed,0)
        if key[K_RIGHT]:
            self.rect.move_ip(self.speed,0)
        if self.rect.left <= 0:
            self.rect.left = 0
        if self.rect.right >= x:
            self.rect.right = x
        if self.rect.top <=0:
            self.rect.top = 0
        if self.rect.bottom >=y:
            self.rect.bottom = y
class Shit(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load(dir + '/poop.png')
        self.rect = self.image.get_rect(
            center = (
                x, random.randint(0,y)
            )
        )
    def update(self):
        global score
        self.rect.move_ip(- random.randint(4,8),0)
        if self.rect.right <=0:
            self.kill()
            score += 10
class Bullet(pygame.sprite.Sprite):
    def __init__(self,x,y,size=1):
        super().__init__()
        self.image = pygame.Surface((15*size,15*size))
        self.image.fill((255,0,0))
        self.rect = self.image.get_rect( center =(x,y) )
    def update(self):
        self.rect.move_ip(8,0)
        if self.rect.left >=x:
            self.kill()

plane = Plane()
planes = pygame.sprite.GroupSingle(plane)
shits = pygame.sprite.Group()
bullets = pygame.sprite.Group()
score_font = pygame.font.Font('/System/Library/Fonts/PingFang.ttc',22)
ADDSHIT = pygame.USEREVENT + 1
pygame.time.set_timer(ADDSHIT,200)
ADDBULLET = pygame.USEREVENT + 1
pygame.time.set_timer(ADDBULLET,200)

while running:
    screen.blit(background, (0, 0))

    for e in pygame.event.get():
        if e.type == ADDBULLET:
            if autofire:
                new_bullet = Bullet(plane.rect.centerx+50,plane.rect.centery)
                bullets.add(new_bullet)
        if e.type == ADDSHIT:
            new_shit = Shit()
            shits.add(new_shit)
        if e.type == QUIT:
            running = False
        if e.type == KEYDOWN:
            if e.key  == K_ESCAPE:
                running = False
            if e.key == K_SPACE:
                new_bullet = Bullet(plane.rect.centerx + 50, plane.rect.centery,size=5)
                bullets.add(new_bullet)

    if pygame.sprite.groupcollide(shits,bullets,True,True):
       score += 20
    if pygame.sprite.spritecollideany(plane,shits):
        life -=1
        if life <0:
            snd_over.play(1)
            pygame.time.delay(1000)
            running = False
        else:
            plane.kill()
            plane = Plane()
            planes = pygame.sprite.GroupSingle(plane)

    score_text = score_font.render(
        f'得分：{score:6d} 生命力：{life:3d}',
        True,(255,0,0)
    )
    screen.blit(score_text,(x//3,10))

    planes.draw(screen)
    shits.draw(screen)
    bullets.draw(screen)

    planes.update(pygame.key.get_pressed())
    shits.update()
    bullets.update()
    pygame.display.update()
