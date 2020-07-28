import pygame,random
from pygame.locals import *
from sys import argv
from os import path
from os.path import sep

size = w, h = 800,600
title = '里约大冒险'
run = True
fps = 20
score = 0
dir = sep.join(argv[0].split(sep)[:-1]+['resources'])

pygame.init()
pygame.mixer.init()
pygame.display.set_caption(title)
pygame.mouse.set_visible(False)
pygame.key.set_repeat(50)
clock = pygame.time.Clock()
screen = pygame.display.set_mode(size)
score_font = pygame.font.Font('/System/Library/Fonts/PingFang.ttc',25)
bg_img = pygame.image.load(path.join(dir,'images','background.png'))
bg_snd = pygame.mixer.Sound(path.join(dir,'sounds','background.ogg'))
bg_snd.set_volume(0.1)
die_snd = pygame.mixer.Sound(path.join(dir,'sounds','bird_die.ogg'))
die_snd.set_volume(0.1)
die_snd = pygame.mixer.Sound(path.join(dir,'sounds','bird_die.ogg'))
die_snd.set_volume(0.1)

class Bird(pygame.sprite.Sprite):
    def __init__(self,frames=1,speed=1):
        super().__init__()
        self.frames = frames
        self.speed = speed
        self.mast_image = pygame.image.load(path.join(dir,'images','bird.png'))
        self.rect = self.mast_image.get_rect()
        self.frame_rect = self.rect
        self.frame_rect.width /= self.frames
        self.frame = 0
        self.old_frame = -1
        self.last_time = 0
        self.height = h//2
    def update(self):
        global fps
        self.current_time = pygame.time.get_ticks()
        if self.old_frame != self.frame:
            self.frame_rect.x = (self.frame % self.frames) * self.rect.width
            self.old_frame = self.frame

        if self.current_time >= self.last_time + fps:
            self.frame  = self.frame % self.frames
            self.frame += 1
            self.last_time = self.current_time
        self.image = self.mast_image.subsurface(self.frame_rect)  # 这里就是在生成子表面
        self.height += self.speed
        self.rect = self.image.get_rect(
            center=(self.frame_rect.width//2, self.height)
        )
    def move(self,speed):
        self.height -= speed

class Pillar(pygame.sprite.Sprite):
    def __init__(self,x,y,up=1):
        self.width = 30
        self.up = up
        super().__init__()
        self.image = pygame.Surface((self.width, y))
        self.image.fill((100, 150, 50))
        if self.up == 1:
            self.rect = self.image.get_rect(
                topleft = (x,0)
            )
        else:
            self.rect = self.image.get_rect(
                bottomleft = (x,h)
            )
    def update(self,speed=3):
        global score
        self.rect.move_ip(- speed,0)
        if self.up == 1 and self.rect.right < bird.rect.left:
            score += 1
        if self.rect.right < 0:
            self.kill()

bird_group = pygame.sprite.Group()
pillar_grp = pygame.sprite.Group()
bird = Bird(frames=3,speed=2)
bird_group.add(bird)

hit = False
x = 0
z = 120
for i in range(1,100):
    x += 300
    y = random.randrange((h - z) // 4, 2 * (h - z) // 3, 10)
    pillar = Pillar(x,y)
    pillar1 = Pillar(x,h-y-z,0)
    pillar_grp.add(pillar)
    pillar_grp.add(pillar1)

while run:
    screen.blit( pygame.transform.scale(bg_img,size) ,(0,0))
    bg_snd.play(-1)

    for e in pygame.event.get():
        if e.type == QUIT:
            run = False
        if e.type == KEYDOWN:
            if e.key == K_SPACE:
                bird.move(10)
            if e.key == K_ESCAPE:
                run = False

    if pygame.sprite.groupcollide(bird_group,pillar_grp,False,False):
        hit = True

    bird_group.update()
    bird_group.draw(screen)
    pillar_grp.draw(screen)

    if hit :
        screen.blit(pygame.image.load(path.join(dir,'images','over.png')),(w//2-100,h//3))
        bg_snd.stop()
        die_snd.play(1)
        bird.speed = 0
        pillar_grp.update(0)
    else:
        pillar_grp.update()

    score_text = score_font.render(
        f'得分: {score}',True,(255,0,0)
    )
    screen.blit(score_text,(w//2-50,10))
    clock.tick(fps)
    pygame.display.update()